"""Database-layer contracts proven with a test double.

The interesting behaviour here is not SQL text but two failure paths the real
database produces: a page limit that silently hides rows, and a unique-violation
race where the conflicting run finishes before the lookup.
"""
from __future__ import annotations

import uuid

import asyncpg
import pytest

from pod_pipeline import db


class _Txn:
    async def __aenter__(self) -> "_Txn":
        return self

    async def __aexit__(self, *exc: object) -> bool:
        return False


class FakeConn:
    """Minimal asyncpg.Connection stand-in. Only the methods db.py calls."""

    def __init__(self, *, fetch=None, fetchval=None, execute=None) -> None:
        self._fetch = fetch
        self._fetchval = fetchval
        self._execute = execute

    def transaction(self) -> _Txn:
        return _Txn()

    async def fetch(self, *args, **kwargs):
        return self._fetch(*args, **kwargs) if self._fetch else []

    async def fetchval(self, *args, **kwargs):
        return self._fetchval(*args, **kwargs) if self._fetchval else None

    async def execute(self, *args, **kwargs):
        return self._execute(*args, **kwargs) if self._execute else "OK"


class _Acquire:
    def __init__(self, conn: FakeConn) -> None:
        self._conn = conn

    async def __aenter__(self) -> FakeConn:
        return self._conn

    async def __aexit__(self, *exc: object) -> bool:
        return False


class FakePool:
    """Yields the supplied connections in order, one per acquire()."""

    def __init__(self, *conns: FakeConn) -> None:
        self._conns = list(conns)
        self.acquires = 0

    def acquire(self) -> _Acquire:
        self.acquires += 1
        if not self._conns:
            raise AssertionError("FakePool ran out of connections — an unexpected extra acquire")
        return _Acquire(self._conns.pop(0))


async def test_pending_assets_reports_truncation_instead_of_hiding_rows() -> None:
    rows = [{"id": i} for i in range(201)]
    pool = FakePool(FakeConn(fetch=lambda *a, **k: rows))
    got, truncated = await db.pending_assets(pool, stuck_after_s=60, limit=200)
    assert len(got) == 200
    assert truncated is True, "a full page must say there are more rows"


async def test_pending_assets_a_short_page_is_not_truncated() -> None:
    pool = FakePool(FakeConn(fetch=lambda *a, **k: [{"id": 1}]))
    got, truncated = await db.pending_assets(pool, stuck_after_s=60, limit=200)
    assert got == [{"id": 1}]
    assert truncated is False


async def test_enqueue_returns_the_existing_run_on_conflict() -> None:
    existing = uuid.uuid4()
    pool = FakePool(
        FakeConn(execute=_raise_unique),
        FakeConn(fetchval=lambda *a, **k: existing),
    )
    run_id, created = await db.enqueue_run(pool, account_id=1, asset_id=2, product_type="apparel")
    assert (run_id, created) == (existing, False)


async def test_enqueue_retries_when_the_conflicting_run_just_finished() -> None:
    """Conflict -> lookup finds nothing (run became terminal) -> insert again, not a null run id."""
    pool = FakePool(
        FakeConn(execute=_raise_unique),
        FakeConn(fetchval=lambda *a, **k: None),
        FakeConn(execute=lambda *a, **k: "INSERT 0 1"),
    )
    run_id, created = await db.enqueue_run(pool, account_id=1, asset_id=2, product_type="apparel")
    assert created is True
    assert isinstance(run_id, uuid.UUID)


async def test_enqueue_refuses_by_name_when_it_loses_the_race_twice() -> None:
    pool = FakePool(
        FakeConn(execute=_raise_unique),
        FakeConn(fetchval=lambda *a, **k: None),
        FakeConn(execute=_raise_unique),
        FakeConn(fetchval=lambda *a, **k: None),
    )
    with pytest.raises(RuntimeError) as exc:
        await db.enqueue_run(pool, account_id=1, asset_id=2, product_type="apparel")
    assert "retry" in str(exc.value)
    # A caller must never receive a fabricated run id.
    assert "None" not in str(exc.value)


def _raise_unique(*args: object, **kwargs: object) -> None:
    """Synchronous on purpose: FakeConn.execute calls it directly, mirroring asyncpg's awaited call."""
    raise asyncpg.UniqueViolationError("duplicate live run")
