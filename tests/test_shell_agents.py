"""Exercise extracted supervision with fake agents; never read real profiles or credentials."""
import os
from pathlib import Path
import signal
import subprocess
import sys
import tempfile
import time
import unittest

ROOT = Path(__file__).resolve().parents[1]
SOURCE = (ROOT / "dev-test-chromebook.sh").read_text().split(
    "<< 'SHELL_START_PY'\n", 1
)[1].split("\nSHELL_START_PY", 1)[0]

# A detached double-fork with ssh-agent's comm name, without running a real agent.
FAKE = '''import ctypes, os, signal, sys, time
if os.fork():
    sys.exit()
os.setsid()
if os.fork():
    sys.exit()
ctypes.CDLL(None).prctl(15, b"ssh-agent", 0, 0, 0)
if sys.argv[2] == "ignore":
    signal.signal(signal.SIGTERM, signal.SIG_IGN)
with open(sys.argv[1], "w") as f:
    f.write(str(os.getpid()))
while True:
    time.sleep(1)
'''


def wait_file(path):
    end = time.monotonic() + 3
    while not path.exists() and time.monotonic() < end:
        time.sleep(0.01)
    return int(path.read_text())


class ShellAgents(unittest.TestCase):
    def test_owned_agents_cleaned_and_existing_agent_untouched(self):
        with tempfile.TemporaryDirectory(dir=ROOT / "assets") as tmp:
            work = Path(tmp)
            supervisor = work / "shell_start.py"
            supervisor.write_text(SOURCE)
            fake = work / "fake.py"
            fake.write_text(FAKE)
            ledger = work / "agents.tsv"
            ledger.touch()
            env = dict(os.environ, SHELL_AGENT_LEDGER=str(ledger))
            # The pre-existing fake daemon is outside the supervisor's descendant tree.
            subprocess.run([sys.executable, str(fake), str(work / "existing"), "normal"],
                           check=True, stdout=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
            existing = wait_file(work / "existing")
            owned_pids = []
            try:
                for label, status, timeout, ignore in (
                    ("success", 0, False, False), ("failure", 42, False, False),
                    ("timeout", 124, True, False), ("stubborn", 0, False, True),
                ):
                    with self.subTest(label=label):
                        pidfile = work / label
                        command = ["bash", "--noprofile", "--norc", "-c", '''
"$1" "$2" "$3" "$4"
while [ ! -s "$3" ]; do sleep 0.01; done
if [ "$5" = yes ]; then sleep 30; fi
exit "$6"
''', "_", sys.executable, str(fake), str(pidfile),
                            "ignore" if ignore else "normal", "yes" if timeout else "no", str(status)]
                        if timeout:
                            command = ["timeout", "-k", "1", "0.3"] + command
                        result = subprocess.run([sys.executable, str(supervisor)] + command,
                                                env=env, capture_output=True, text=True, timeout=8)
                        self.assertEqual(result.returncode, status, result.stderr)
                        pid = wait_file(pidfile)
                        owned_pids.append(pid)
                        self.assertFalse(Path(f"/proc/{pid}").exists(), f"owned agent {pid} leaked")
                        os.kill(existing, 0)
                # A terminal/outer timeout may interrupt the supervisor itself.
                pidfile = work / "interrupted"
                command = ["bash", "--noprofile", "--norc", "-c", '''
"$1" "$2" "$3" normal
while [ ! -s "$3" ]; do sleep 0.01; done
exec sleep 30
''', "_", sys.executable, str(fake), str(pidfile)]
                proc = subprocess.Popen([sys.executable, str(supervisor)] + command,
                                        env=env, stdout=subprocess.PIPE, stderr=subprocess.PIPE)
                pid = wait_file(pidfile)
                owned_pids.append(pid)
                proc.terminate()
                proc.communicate(timeout=5)
                self.assertEqual(proc.returncode, 143)
                self.assertFalse(Path(f"/proc/{pid}").exists())
                os.kill(existing, 0)
                check = subprocess.run([sys.executable, str(supervisor), "--check"],
                                       env=env, capture_output=True, text=True, timeout=3)
                self.assertEqual(check.returncode, 0, check.stdout + check.stderr)
                self.assertEqual({int(row.split()[0]) for row in ledger.read_text().splitlines()},
                                 set(owned_pids))
                # Prove final verification detects a real live recorded identity.
                fields = Path(f"/proc/{existing}/stat").read_text().rsplit(")", 1)[1].split()
                ledger.write_text(f"{existing}\t{fields[19]}\n")
                check = subprocess.run([sys.executable, str(supervisor), "--check"],
                                       env=env, capture_output=True, text=True, timeout=3)
                self.assertEqual(check.returncode, 1)
                os.kill(existing, 0)  # verification itself never kills
            finally:
                for pid in [existing] + owned_pids:
                    try:
                        os.kill(pid, signal.SIGKILL)
                    except ProcessLookupError:
                        pass


if __name__ == "__main__":
    unittest.main()
