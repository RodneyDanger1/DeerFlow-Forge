"""CLI and guarded-finish tests for forge_worker (no DB, no network).

Run: python -m pytest tests/test_forge_worker_cli.py -q
 or: python -m unittest tests.test_forge_worker_cli -v
"""
from __future__ import annotations

import asyncio
import contextlib
import io
import json
import unittest
from unittest import mock

from forge_worker import FinishRefused, ForgeWorker, WorkerError, main


class FakeRepo:
    def __init__(self, jobs=None, finish_exc: Exception | None = None):
        self.jobs = list(jobs or [])
        self.finish_exc = finish_exc
        self.finished: list[dict] = []
        self.closed = False

    async def claim_job(self, worker, *, lease_s=300):
        return self.jobs.pop(0) if self.jobs else None

    async def finish_job(self, job_id, *, ok, error=None):
        if self.finish_exc is not None:
            raise self.finish_exc
        self.finished.append({"id": job_id, "ok": ok, "error": error})
        return {"id": job_id, "state": "succeeded" if ok else "failed"}

    async def reap_expired_jobs(self):
        return 0

    async def close(self):
        self.closed = True


async def _noop(_payload):
    return None


async def _boom(_payload):
    raise RuntimeError("handler broke")


def _run_main(argv, **kwargs):
    out, err = io.StringIO(), io.StringIO()
    with contextlib.redirect_stdout(out), contextlib.redirect_stderr(err):
        code = main(argv, **kwargs)
    return code, out.getvalue(), err.getvalue()


class GuardedFinishTests(unittest.IsolatedAsyncioTestCase):
    async def test_refused_finish_is_named_and_not_swallowed(self):
        repo = FakeRepo([{"id": 7, "payload": {}}],
                        finish_exc=RuntimeError("E_JOB_STATE: job 7 is not claimed/running"))
        worker = ForgeWorker(repo, _noop)
        with self.assertRaises(FinishRefused) as caught:
            await worker.run_once()
        self.assertEqual(caught.exception.code, "E_JOB_STATE")

    async def test_finish_driver_error_becomes_bounded_code(self):
        repo = FakeRepo([{"id": 8, "payload": {}}], finish_exc=OSError("connection lost"))
        worker = ForgeWorker(repo, _noop)
        with self.assertRaises(WorkerError) as caught:
            await worker.run_once()
        self.assertEqual(caught.exception.code, "E_REPO")

    async def test_handler_failure_records_failed_finish(self):
        repo = FakeRepo([{"id": 9, "payload": {}}])
        worker = ForgeWorker(repo, _boom)
        result = await worker.run_once()
        self.assertFalse(result["ok"])
        self.assertEqual(repo.finished, [{"id": 9, "ok": False, "error": "RuntimeError: handler broke"}])

    async def test_empty_queue_claims_nothing(self):
        repo = FakeRepo([])
        self.assertIsNone(await ForgeWorker(repo, _noop).run_once())
        self.assertEqual(repo.finished, [])


class CliTests(unittest.TestCase):
    def test_missing_once_flag_is_config_error(self):
        code, _, err = _run_main([], handler=_noop)
        payload = json.loads(err)
        self.assertEqual((code, payload["code"]), (2, "E_INVALID_ARG"))

    def test_lease_out_of_range_is_config_error(self):
        code, _, err = _run_main(["--once", "--lease-s", "0"], handler=_noop)
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(err)["code"], "E_INVALID_ARG")

    def test_missing_dsn_is_config_error(self):
        with mock.patch.dict("os.environ", {}, clear=True):
            code, _, err = _run_main(["--once"], handler=_noop)
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(err)["code"], "E_DSN_MISSING")

    def test_missing_handler_is_config_error(self):
        code, _, err = _run_main(["--once", "--dsn", "postgresql://x/y"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(err)["code"], "E_HANDLER_MISSING")

    def test_invalid_handler_spec_is_config_error(self):
        code, _, err = _run_main(["--once", "--dsn", "postgresql://x/y", "--handler", "nocolon"])
        self.assertEqual(code, 2)
        self.assertEqual(json.loads(err)["code"], "E_HANDLER_INVALID")

    def test_empty_queue_success_json(self):
        repo = FakeRepo([])

        async def factory(_dsn):
            return repo

        code, out, _ = _run_main(["--once", "--dsn", "postgresql://x/y"],
                                 handler=_noop, repo_factory=factory)
        payload = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual((payload["ok"], payload["claimed"], payload["finished"]), (True, 0, 0))
        self.assertTrue(repo.closed)

    def test_claimed_job_success_json(self):
        repo = FakeRepo([{"id": 11, "payload": {"x": 1}}])

        async def factory(_dsn):
            return repo

        code, out, _ = _run_main(["--once", "--dsn", "postgresql://x/y"],
                                 handler=_noop, repo_factory=factory)
        payload = json.loads(out)
        self.assertEqual(code, 0)
        self.assertEqual((payload["claimed"], payload["finished"], payload["job_id"]), (1, 1, 11))
        self.assertEqual(repo.finished, [{"id": 11, "ok": True, "error": None}])

    def test_refused_finish_exits_runtime_not_config(self):
        repo = FakeRepo([{"id": 12, "payload": {}}],
                        finish_exc=RuntimeError("E_JOB_STATE: not claimed"))

        async def factory(_dsn):
            return repo

        code, _, err = _run_main(["--once", "--dsn", "postgresql://x/y"],
                                 handler=_noop, repo_factory=factory)
        payload = json.loads(err)
        self.assertEqual((code, payload["code"]), (1, "E_JOB_STATE"))


if __name__ == "__main__":
    unittest.main(verbosity=2)
