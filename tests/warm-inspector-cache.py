"""Owner-approved targeted replay of setup's Inspector cache warm-up, without global/package setup."""
import os
from pathlib import Path
import subprocess

root = Path(__file__).resolve().parents[1]
source = (root / "dev-setup-chromebook.sh").read_text()
start = source.index('            INSPECTOR_PROBE="$ASSETS/tools/mcp-inspector/cache-check.py"')
end = source.index('\n        else\n            stage_failed', start)
code = source[start:end]
env = dict(os.environ, ASSETS=str(root / "assets"))
subprocess.run(["bash", "-n"], input=code, text=True, check=True)
# Match setup's managed Node activation; the agent's noninteractive PATH need not include npx.
activate = '''
if [ -d "$HOME/.config/nvm" ]; then export NVM_DIR="$HOME/.config/nvm"; else export NVM_DIR="$HOME/.nvm"; fi
[ -s "$NVM_DIR/nvm.sh" ] && . "$NVM_DIR/nvm.sh" > /dev/null 2>&1
export PATH="$HOME/.local/bin:$PATH"
'''
subprocess.run(["bash", "-c", activate + code], env=env, cwd=root, check=True)
