"""Recorder regression: extract the wrapper; never run a bundle script or user profile."""
import os
from pathlib import Path
import pty
import signal
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def wrapper(name):
    return (ROOT / f"dev-{name}-chromebook.sh").read_text().split(
        "# >>> dev-bundle screen output >>>\n", 1
    )[1].split("# <<< dev-bundle screen output <<<", 1)[0]


class ScreenOutput(unittest.TestCase):
    def test_failed_setup_summary_recognized_without_complete_line(self):
        for summary in (True, False):
            with self.subTest(summary=summary), tempfile.TemporaryDirectory(dir=ROOT / "assets") as tmp:
                fixture = Path(tmp) / "dev-fixture-chromebook.sh"
                message = "Setup stage summary (Version 99)" if summary else "Stopped during setup"
                fixture.write_text("#!/bin/bash\n" + wrapper("setup") +
                                   f"\necho '{message}'\necho '{'=' * 65}'\nexit 42\n")
                env = dict(os.environ, DEV_SCREEN_SAVE="1")
                env.pop("DEV_SCREEN_OUTPUT", None)
                result = subprocess.run(["bash", str(fixture)], env=env,
                                        capture_output=True, text=True, timeout=5)
                self.assertEqual(result.returncode, 42)
                self.assertEqual("stopped before the summary" in result.stderr, not summary)

    def test_detached_child_cannot_hold_recorder_open(self):
        source = wrapper("test")
        self.assertEqual(source, wrapper("setup"))
        for terminal in (False, True):
            for status in (0, 1, 42):
                with self.subTest(terminal=terminal, status=status):
                    self.run_fixture(source, terminal, status)

    def run_fixture(self, source, terminal, status):
        with tempfile.TemporaryDirectory(dir=ROOT / "assets") as tmp:
            work = Path(tmp)
            fixture = work / "dev-fixture-chromebook.sh"
            fixture.write_text("#!/bin/bash\n" + source + r'''
# Stand in for an agent started by a new-shell check, including inherited extra fds.
# Wait for its handshake so script(1)'s terminal hangup cannot win the startup race.
setsid bash --noprofile --norc -c '
    trap "" HUP
    echo $$ > "$1/daemon.pid"
    ls -l /proc/$$/fd > "$1/daemon.fds"
    exec sleep 30
' _ "$(dirname "$0")" > /dev/null 2>&1 < /dev/null &
while [ ! -s "$(dirname "$0")/daemon.fds" ]; do sleep 0.01; done
echo 'Test Version 99 complete: PASS 1 FAIL 0'
echo '================================================================='
exit ''' + str(status) + "\n")
            env = os.environ.copy()
            env.pop("DEV_SCREEN_OUTPUT", None)
            env.pop("DEV_RUN_STAMP", None)
            env["DEV_SCREEN_SAVE"] = "1"
            master = slave = None
            if terminal:
                master, slave = pty.openpty()
            proc = subprocess.Popen(
                ["bash", str(fixture)], env=env, start_new_session=True,
                stdin=slave if terminal else subprocess.DEVNULL,
                stdout=slave if terminal else subprocess.DEVNULL,
                stderr=slave if terminal else subprocess.DEVNULL,
            )
            if slave is not None:
                os.close(slave)
            try:
                self.assertEqual(proc.wait(timeout=5), status)
                daemon = int((work / "daemon.pid").read_text())
                os.kill(daemon, 0)  # recorder ended while the child was still alive
                fds = (work / "daemon.fds").read_text()
                self.assertNotIn("pipe:[", fds)
                saved, = (work / "assets/logs").glob("*.output")
                self.assertEqual(saved.read_text().splitlines(), [
                    "Test Version 99 complete: PASS 1 FAIL 0", "=" * 65,
                ])
            finally:
                pidfile = work / "daemon.pid"
                if pidfile.exists():
                    try:
                        os.kill(int(pidfile.read_text()), signal.SIGTERM)
                    except ProcessLookupError:
                        pass
                try:
                    proc.wait(timeout=5)
                except subprocess.TimeoutExpired:
                    os.killpg(proc.pid, signal.SIGKILL)
                    proc.wait(timeout=5)
                if master is not None:
                    os.close(master)


if __name__ == "__main__":
    unittest.main()
