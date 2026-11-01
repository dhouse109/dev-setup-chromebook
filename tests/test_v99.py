"""Three offline helper tests. Extract definitions; never source/run a bundle script."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def block(name):
    source = (ROOT / "dev-setup-chromebook.sh").read_text()
    return source.split(f"# >>> dev-bundle {name} >>>\n", 1)[1].split(
        f"# <<< dev-bundle {name} <<<", 1
    )[0]


def bash(definitions, commands):
    result = subprocess.run(
        ["bash", "-e", "-o", "pipefail", "-c", definitions + "\n" + commands],
        text=True, capture_output=True, cwd=ROOT,
    )
    if result.returncode:
        # Do not print captured output: the generator test intentionally handles fresh secrets.
        raise AssertionError(f"offline shell assertion failed (exit {result.returncode})")
    return result


class V99Helpers(unittest.TestCase):
    def test_net_retry(self):
        definitions = "net_retry() {" + block("network policy").split("net_retry() {", 1)[1]
        # Each standalone script must carry the identical implementation.
        for name in ("init", "test", "demo"):
            source = (ROOT / f"dev-{name}-chromebook.sh").read_text()
            peer = source.split("net_retry() {", 1)[1].split(
                "# <<< dev-bundle network policy <<<", 1
            )[0]
            self.assertEqual(definitions, "net_retry() {" + peer)
        with tempfile.TemporaryDirectory() as work:
            for succeed_at, expected_calls, expected_sleep in (
                (1, 1, ""), (2, 2, "2"), (3, 3, "25"), (4, 3, "25")
            ):
                result = bash(definitions, f'''
cd '{work}'
: > sleeps
n=0
sleep() {{ printf %s "$1" >> sleeps; }}
operation() {{ n=$((n+1)); [ "$n" -ge {succeed_at} ] || return 42; }}
rc=0
net_retry 'safe label' operation || rc=$?
[ "$n" = {expected_calls} ]
[ "$(cat sleeps)" = '{expected_sleep}' ]
if [ {succeed_at} = 4 ]; then
    [ "$rc" = 42 ] && [ "$NET_RETRY_EXHAUSTED" = 1 ]
else
    [ "$rc" = 0 ] && [ "$NET_RETRY_EXHAUSTED" = 0 ]
fi
''')
                self.assertIn("safe label: attempt 1/3", result.stderr)
                self.assertNotIn("operation", result.stderr)

    def test_apt_dedupe(self):
        definitions = block("apt output")
        warning = "W: Tried to start delayed item https://example.invalid/font all 1, but failed"
        payload = (warning + "\n") * 64364 + "W: unrelated warning\nE: install failed\n"
        result = subprocess.run(
            ["bash", "-e", "-o", "pipefail", "-c", definitions + "\napt_dedupe"],
            input=payload, text=True, capture_output=True, check=True,
        )
        self.assertEqual(result.stdout.splitlines(), [
            warning, "[apt] warning repeated 64363 more times (64364 total)",
            "W: unrelated warning", "E: install failed",
        ])
        # Exercise the real wrapper with an unprivileged fake sudo/apt producer.
        bash(definitions, '''
sudo() { echo 'E: producer failed'; return 42; }
rc=0; apt_get install example >/dev/null || rc=$?
[ "$rc" = 42 ]
sudo() { echo normal; }
apt_dedupe() { cat >/dev/null; return 43; }
rc=0; apt_get install example >/dev/null || rc=$?
[ "$rc" = 43 ]
''')

    def test_password_generator(self):
        definitions = block("random generator")
        bash(definitions, '''
for n in 1 16 20 32; do
    v=$(random_chars "$n")
    [ "${#v}" = "$n" ]
    [[ "$v" != *[!A-Za-z0-9]* ]]
done
for _ in {1..20}; do
    v=$(dev_password)
    [[ "$v" =~ ^Dev_[A-Za-z0-9]{16}_[A-Z]9$ ]]
done
if random_chars 0 >/dev/null 2>&1; then exit 1; fi
random_chars() { return 44; }
if dev_password >/dev/null 2>&1; then exit 1; fi
''')


if __name__ == "__main__":
    unittest.main()
