"""v101 pre-push static gate; never run the four bundle scripts or installed helper."""
from pathlib import Path
import re
import subprocess

ROOT = Path(__file__).resolve().parents[1]
scripts = sorted(ROOT.glob("dev-*-chromebook*.sh"))
versions = set()
expansions = []
for path in scripts:
    source = path.read_text()
    for command in (["bash", "-n", str(path)], ["shellcheck", "-S", "error", str(path)]):
        subprocess.run(command, check=True)
    versions.update(x for pair in re.findall(r"Version (\d+)|^VERSION=(\d+)", source, re.M) for x in pair if x)
    block = source.split("# FLAG EXPANSION", 1)[1].split('FLAGS=" $* "', 1)[1].split('# =================================================================', 1)[0]
    # Compare the actual shell statements, ignoring explanatory comments and blank lines.
    expansions.append([line.strip() for line in block.splitlines() if line.strip() and not line.lstrip().startswith(("#", "echo "))])
assert len(versions) == 1 and versions <= {"100", "101"}, versions
version = next(iter(versions))
assert f"Current version: v{version}." in (ROOT / "README.md").read_text()
assert all(block == expansions[0] for block in expansions), "flag-expansion statements differ"
helper = (ROOT / "dev-setup-chromebook.sh").read_text().split("<< 'DEVRETRO_EOF'\n", 1)[1].split("\nDEVRETRO_EOF", 1)[0] + "\n"
for command in (["bash", "-n"], ["shellcheck", "-S", "error", "-"]):
    subprocess.run(command, input=helper, text=True, check=True)
subprocess.run(["git", "diff", "--check", "origin/main"], cwd=ROOT, check=True)
diff = subprocess.check_output(["git", "diff", "origin/main"], cwd=ROOT, text=True)
for pattern in (r"-----BEGIN (?:RSA |EC |OPENSSH )?PRIVATE KEY-----", r"gh[pousr]_[A-Za-z0-9]{30,}", r"github_pat_[A-Za-z0-9_]{40,}", r"AKIA[A-Z0-9]{16}", r"sk-(?:proj-)?[A-Za-z0-9_-]{30,}"):
    assert not re.search(pattern, diff), "Secret-pattern review failed"
print(f"PASS: all-four/extracted-helper syntax and ShellCheck; v{version}; flag parity; whitespace/secret patterns", flush=True)
subprocess.run(["python3", "tests/check_release_archive.py", "--index"], cwd=ROOT, check=True)
subprocess.run(["python3", "tests/test_v101.py"], cwd=ROOT, check=True)
