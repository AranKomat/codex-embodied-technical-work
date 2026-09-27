from __future__ import annotations

import json
import subprocess
import sys
import tempfile
import time
import unittest
from pathlib import Path

from live_session.client import RobotClient


class LiveSessionTest(unittest.TestCase):
    def test_two_clients_continue_same_state(self) -> None:
        with tempfile.TemporaryDirectory() as directory:
            root = Path(directory)
            socket_path = root / "session.sock"
            trace_path = root / "trace.jsonl"
            process = subprocess.Popen(
                [
                    sys.executable,
                    "-m",
                    "live_session.server",
                    "--backend",
                    "live_session.fake_backend:build_fake",
                    "--socket",
                    str(socket_path),
                    "--trace",
                    str(trace_path),
                ]
            )
            try:
                deadline = time.monotonic() + 5
                while not socket_path.exists() and time.monotonic() < deadline:
                    time.sleep(0.01)
                self.assertTrue(socket_path.exists())

                first = RobotClient(socket_path)
                status = first.status()
                first.move_delta([0.1, -0.2, 0.3, 0.0, 0.0, 0.0], steps=2)

                second = RobotClient(socket_path)
                state = second.state()
                self.assertEqual(state["session_id"], status["session_id"])
                self.assertEqual(state["result"]["position_m"], [0.2, -0.4, 0.6])
                self.assertEqual(state["result"]["action_count"], 2)
                second.stop()
                process.wait(timeout=5)

                entries = [json.loads(line) for line in trace_path.read_text().splitlines()]
                self.assertEqual([entry["receipt"]["sequence"] for entry in entries], [1, 2, 3, 4])
                self.assertTrue(all(entry["receipt"]["session_id"] == status["session_id"] for entry in entries))
            finally:
                if process.poll() is None:
                    process.terminate()
                    process.wait(timeout=5)


if __name__ == "__main__":
    unittest.main()
