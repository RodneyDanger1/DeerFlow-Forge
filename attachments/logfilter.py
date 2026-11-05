"""Streaming log filter.

Craft binaries can emit many megabytes of progress output. We never hold that in memory and never
hand it to the LLM. Every byte is (optionally) copied to a size-capped log file on disk, while an
in-memory digest keeps only: de-duplicated lines matching an error regex, plus the last few lines.
`render()` returns a small, fixed-size string that is safe to store in Postgres and feed to DeepSeek.
"""
from __future__ import annotations

import asyncio
import re
from collections import OrderedDict, deque
from pathlib import Path
from typing import BinaryIO

ERROR_RE = re.compile(
    r"(?i)\b(error|fatal|exception|traceback|failed|failure|panic|segfault|segmentation|"
    r"abort(?:ed)?|denied|killed|out of memory|oom|cannot|unable to|invalid|unsupported)\b"
)
_DIGITS = re.compile(r"\d+")
_MAX_PENDING = 64 * 1024          # a "line" longer than this without a newline is cut here


class StreamDigest:
    def __init__(
        self,
        *,
        log_path: Path | None = None,
        max_log_bytes: int = 5 * 1024 * 1024,
        max_error_entries: int = 20,
        tail_lines: int = 12,
        max_line_chars: int = 300,
    ) -> None:
        self._max_error_entries = max_error_entries
        self._max_line_chars = max_line_chars
        self._tail: deque[str] = deque(maxlen=tail_lines)
        self._errors: "OrderedDict[str, list]" = OrderedDict()   # key -> [first_line, count]
        self._dropped_errors = 0
        self._pending = bytearray()
        self.total_bytes = 0
        self.total_lines = 0
        self.log_truncated = False
        self._log_budget = max_log_bytes
        self._log: BinaryIO | None = None
        if log_path is not None:
            log_path.parent.mkdir(parents=True, exist_ok=True)
            self._log = open(log_path, "wb")

    # ------------------------------------------------------------------ input
    def feed(self, data: bytes) -> None:
        if not data:
            return
        self.total_bytes += len(data)
        self._write_log(data)
        self._pending.extend(data)
        # split on \n and \r: progress bars redraw with \r and would otherwise form one giant "line"
        while True:
            cut = self._find_delim(self._pending)
            if cut < 0:
                if len(self._pending) > _MAX_PENDING:
                    self._emit(bytes(self._pending))
                    self._pending.clear()
                return
            line = bytes(self._pending[:cut])
            del self._pending[: cut + 1]
            if line:
                self._emit(line)

    @staticmethod
    def _find_delim(buf: bytearray) -> int:
        n, r = buf.find(b"\n"), buf.find(b"\r")
        if n < 0:
            return r
        if r < 0:
            return n
        return min(n, r)

    def finish(self) -> None:
        if self._pending:
            self._emit(bytes(self._pending))
            self._pending.clear()
        if self._log is not None:
            self._log.flush()
            self._log.close()
            self._log = None

    async def consume(self, stream: asyncio.StreamReader) -> None:
        try:
            while True:
                chunk = await stream.read(65536)
                if not chunk:
                    break
                self.feed(chunk)
        finally:
            self.finish()

    # ----------------------------------------------------------------- output
    def render(self, max_chars: int = 2000) -> str:
        parts = [f"[{self.total_lines} lines, {self.total_bytes} bytes"
                 + (", log truncated on disk" if self.log_truncated else "") + "]"]
        for first, count in self._errors.values():
            parts.append(f"(x{count}) {first}" if count > 1 else first)
        if self._dropped_errors:
            parts.append(f"... {self._dropped_errors} more distinct error lines omitted")
        seen = {first for first, _ in self._errors.values()}
        tail = [t for t in self._tail if t not in seen]
        if tail:
            parts.append("-- last lines --")
            parts.extend(tail)
        text = "\n".join(parts)
        if len(text) > max_chars:
            text = text[: max_chars - 15].rstrip() + "\n...[truncated]"
        return text

    # --------------------------------------------------------------- internals
    def _emit(self, raw: bytes) -> None:
        line = raw.decode("utf-8", errors="replace").strip()
        if not line:
            return
        self.total_lines += 1
        if len(line) > self._max_line_chars:
            line = line[: self._max_line_chars] + "..."
        self._tail.append(line)
        if ERROR_RE.search(line):
            key = _DIGITS.sub("#", line)[:120]
            hit = self._errors.get(key)
            if hit is not None:
                hit[1] += 1
            elif len(self._errors) < self._max_error_entries:
                self._errors[key] = [line, 1]
            else:
                self._dropped_errors += 1

    def _write_log(self, data: bytes) -> None:
        if self._log is None or self._log_budget <= 0:
            if self._log is not None and not self.log_truncated:
                self._log.write(b"\n[log truncated: size cap reached]\n")
                self.log_truncated = True
            return
        piece = data[: self._log_budget]
        self._log.write(piece)
        self._log_budget -= len(piece)
        if len(piece) < len(data):
            self._log.write(b"\n[log truncated: size cap reached]\n")
            self.log_truncated = True
