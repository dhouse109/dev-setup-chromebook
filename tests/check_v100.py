"""Static validation only; never execute bundle scripts or the generated helper."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
for path in sorted(ROOT.glob("dev-*-chromebook*.sh")):
    subprocess.run(["bash", "-n", str(path)], check=True)
    subprocess.run(["shellcheck", "-S", "error", str(path)], check=True)
print("PASS: all four scripts, bash -n and ShellCheck -S error")
helper = (ROOT / "dev-setup-chromebook.sh").read_text().split("<< 'DEVRETRO_EOF'\n", 1)[1].split("\nDEVRETRO_EOF", 1)[0] + "\n"
for command in (["bash", "-n"], ["shellcheck", "-S", "error", "-"]):
    subprocess.run(command, input=helper, text=True, check=True)
print("PASS: extracted dev-retro, bash -n and ShellCheck -S error")
versions = set()
for path in ROOT.glob("dev-*-chromebook*.sh"):
    versions.update(re.findall(r"Version (\d+)|^VERSION=(\d+)", path.read_text(), re.M))
assert {part for pair in versions for part in pair if part} == {"100"}, versions
assert "Current version: v100." in (ROOT / "README.md").read_text()
subprocess.run(["git", "diff", "--check"], cwd=ROOT, check=True)
diff = subprocess.check_output(["git", "diff", "HEAD"], cwd=ROOT, text=True)
for pattern in (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", r"gh[pousr]_[A-Za-z0-9]{30,}", r"github_pat_[A-Za-z0-9_]{40,}", r"AKIA[A-Z0-9]{16}", r"sk-(?:proj-)?[A-Za-z0-9_-]{30,}"):
    assert not re.search(pattern, diff), "Secret-pattern review failed"
print("PASS: bundle version, whitespace and diff secret-pattern checks; gitleaks remains a CI check")
