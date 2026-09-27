"""Single-owner Unix-socket server for a persistent physical session."""

from __future__ import annotations

import argparse
import importlib
import json
import os
import socket
import threading
import uuid
from pathlib import Path
from typing import Any, Protocol

from .contracts import ContractError, Request, now_ns, response


class Backend(Protocol):
    observation_mode: str

    def dispatch(self, command: str, args: dict[str, Any]) -> Any: ...

    def close(self) -> None: ...


class SessionServer:
    """Own one backend and serialize all commands against its live state."""

    def __init__(self, backend: Backend, *, socket_path: Path, trace_path: Path) -> None:
        self.backend = backend
        self.socket_path = socket_path
        self.trace_path = trace_path
        self.session_id = str(uuid.uuid4())
        self.sequence = 0
        self._lock = threading.Lock()
        self._stop = False

    def _append_trace(self, entry: dict[str, Any]) -> None:
        self.trace_path.parent.mkdir(parents=True, exist_ok=True)
        with self.trace_path.open("a", encoding="utf-8") as stream:
            stream.write(json.dumps(entry, separators=(",", ":"), sort_keys=True) + "\n")
            stream.flush()
            os.fsync(stream.fileno())

    def handle(self, payload: Any) -> dict[str, Any]:
        started_ns = now_ns()
        try:
            request = Request.parse(payload)
        except ContractError as exc:
            request = Request(request_id=str(uuid.uuid4()), command="status", args={})
            receipt = response(
                request,
                session_id=self.session_id,
                sequence=self.sequence,
                started_ns=started_ns,
                error=str(exc),
            )
            self._append_trace({"request": payload, "receipt": receipt})
            return receipt

        with self._lock:
            self.sequence += 1
            try:
                args = request.validated_args()
                if request.command == "status":
                    result = {
                        "session_id": self.session_id,
                        "sequence": self.sequence,
                        "observation_mode": self.backend.observation_mode,
                        "stopping": self._stop,
                    }
                else:
                    result = self.backend.dispatch(request.command, args)
                receipt = response(
                    request,
                    session_id=self.session_id,
                    sequence=self.sequence,
                    started_ns=started_ns,
                    result=result,
                )
                if request.command == "stop":
                    self._stop = True
            except Exception as exc:  # preserve a receipt even when the backend rejects an action
                receipt = response(
                    request,
                    session_id=self.session_id,
                    sequence=self.sequence,
                    started_ns=started_ns,
                    error=f"{type(exc).__name__}: {exc}",
                )
            self._append_trace({"request": payload, "receipt": receipt})
            return receipt

    def serve(self) -> None:
        self.socket_path.parent.mkdir(parents=True, exist_ok=True)
        self.socket_path.unlink(missing_ok=True)
        listener = socket.socket(socket.AF_UNIX, socket.SOCK_STREAM)
        listener.bind(str(self.socket_path))
        os.chmod(self.socket_path, 0o600)
        listener.listen(8)
        listener.settimeout(0.5)
        try:
            while not self._stop:
                try:
                    connection, _ = listener.accept()
                except TimeoutError:
                    continue
                with connection:
                    stream = connection.makefile("rwb")
                    line = stream.readline()
                    if not line:
                        continue
                    try:
                        payload = json.loads(line)
                    except (json.JSONDecodeError, UnicodeDecodeError) as exc:
                        payload = {"command": "status", "args": {}, "decode_error": str(exc)}
                    receipt = self.handle(payload)
                    stream.write(json.dumps(receipt).encode("utf-8") + b"\n")
                    stream.flush()
        finally:
            listener.close()
            self.socket_path.unlink(missing_ok=True)
            # Isaac/Kit can block while tearing down a headless app.  All receipts have already
            # been flushed at this point, so do not leave a rented GPU pinned after ``stop``.
            try:
                self.backend.close()
            finally:
                os._exit(0)


def load_backend(spec: str, kwargs: dict[str, Any]) -> Backend:
    module_name, separator, factory_name = spec.partition(":")
    if not separator:
        raise ValueError("backend must be MODULE:FACTORY")
    factory = getattr(importlib.import_module(module_name), factory_name)
    return factory(**kwargs)


def main() -> None:
    parser = argparse.ArgumentParser()
    parser.add_argument("--backend", required=True, help="MODULE:FACTORY")
    parser.add_argument("--backend-kwargs", default="{}", help="JSON object")
    parser.add_argument("--socket", type=Path, required=True)
    parser.add_argument("--trace", type=Path, required=True)
    args = parser.parse_args()
    kwargs = json.loads(args.backend_kwargs)
    if not isinstance(kwargs, dict):
        parser.error("--backend-kwargs must decode to a JSON object")
    SessionServer(
        load_backend(args.backend, kwargs), socket_path=args.socket, trace_path=args.trace
    ).serve()


if __name__ == "__main__":
    main()
