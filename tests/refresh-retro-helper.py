"""Owner-approved targeted refresh: install only setup's generated retro helper, no packages/services."""
from datetime import datetime
import os
from pathlib import Path
import shutil
import subprocess

root = Path(__file__).resolve().parents[1]
source = (root / "dev-setup-chromebook.sh").read_text()
helper = source.split("<< 'DEVRETRO_EOF'\n", 1)[1].split("\nDEVRETRO_EOF", 1)[0] + "\n"
subprocess.run(["bash", "-n"], input=helper, text=True, check=True)
subprocess.run(["shellcheck", "-S", "error", "-"], input=helper, text=True, check=True)
target = Path.home() / ".local/lib/dev-retro/dev-retro"
if not target.is_file() or target.is_symlink():
    raise SystemExit("Expected an existing regular installed retro helper; run setup instead")
if target.read_text() == helper:
    print("Installed retro helper already matches setup")
else:
    backups = root / "assets/downloads/helper-backups"
    backups.mkdir(parents=True, exist_ok=True)
    backup = backups / ("dev-retro-" + datetime.now().strftime("%Y%m%d-%H%M%S"))
    shutil.copy2(target, backup)
    temporary = target.with_name("dev-retro.new")
    with temporary.open("x") as output:
        output.write(helper)
    temporary.chmod(target.stat().st_mode & 0o777)
    os.replace(temporary, target)
    print(f"Refreshed {target}; previous helper retained at {backup}")
