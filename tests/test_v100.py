"""Offline v100 regressions: extracted code, isolated HOME and fake engines only."""
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


def source(name):
    return (ROOT / f"dev-{name}-chromebook.sh").read_text()


def helper():
    return source("setup").split("<< 'DEVRETRO_EOF'\n", 1)[1].split("\nDEVRETRO_EOF", 1)[0] + "\n"


def definitions():
    return helper().rsplit('main "$@"; exit $?', 1)[0]


class Fixture(unittest.TestCase):
    def setUp(self):
        self.tmp = tempfile.TemporaryDirectory(prefix="v100-", dir=ROOT / "assets")
        self.addCleanup(self.tmp.cleanup)
        self.work = Path(self.tmp.name)
        (self.work / "home").mkdir()
        (self.work / "bin").mkdir()
        # Executable guards cover timeout/env/exec too; shell-function stubs do not.
        for engine in ('dosbox-x', 'qemu-system-i386', 'wine', 'wineboot', 'wineserver', 'godot-mono', 'dotnet', 'pwsh'):
            self.fake(engine, 'echo "Unexpected real-engine path" >&2; exit 97')
        self.env = {
            "PATH": f"{self.work}/bin:/usr/bin:/bin", "HOME": str(self.work / "home"),
            "LC_ALL": "C.UTF-8", "WORK": str(self.work), "ASSETS": str(self.work),
            "XDG_CACHE_HOME": str(self.work / "cache"),
        }

    def fake(self, name, body):
        path = self.work / "bin" / name
        path.write_text("#!/bin/bash\n" + body + "\n")
        path.chmod(0o755)

    def bash(self, code, good=True):
        result = subprocess.run(
            ["bash", "--noprofile", "--norc", "-o", "pipefail", "-c", code],
            cwd=self.work, env=self.env, text=True, capture_output=True, timeout=30,
        )
        if good:
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)
        return result


class Nuget(Fixture):
    def setUp(self):
        super().setUp()
        self.fake("dotnet", '''
printf '%s %s\n' "${DOTNET_SYSTEM_NET_DISABLEIPV6:-unset}" "$*" >> "$WORK/dotnet.log"
if [ "$1 $2" = 'new console' ]; then
    while [ $# -gt 0 ]; do
        if [ "$1" = -o ]; then mkdir -p "$2"; touch "$2/VbSpectre.vbproj"; break; fi
        shift
    done
fi
if [ "$1 $2" = 'new reqnroll-project' ]; then mkdir -p reqnroll/Features reqnroll/StepDefinitions; fi
if [ "$1 $2" = 'new list' ]; then exit "${LIST_STATUS:-0}"; fi
exit "${DOTNET_STATUS:-0}"
''')
        self.fake("pwsh", 'printf "%s\\n" "${DOTNET_SYSTEM_NET_DISABLEIPV6:-unset}" > "$WORK/pwsh.log"')

    def test_demo_acquisition_and_generated_runners_do_not_leak_environment(self):
        functions = 'demo_dotnet() {' + source("demo").split('demo_dotnet() {', 1)[1].split('\ndemo_java()', 1)[0]
        self.bash('''
begin() { DIR="$WORK/$1-$2"; mkdir -p "$DIR"; }
need() { :; }; demo_need() { :; }; fetch_repo() { mkdir -p "$DIR/examples/Console/Showcase"; }
write_run() { cat > "$DIR/run.sh"; }; done_demo() { :; }; stash_old() { :; }
fail() { echo "$*"; exit 9; }
REFRESH=0
''' + functions + '''
demo_dotnet && demo_pwsh || exit 1
[ -z "${DOTNET_SYSTEM_NET_DISABLEIPV6+x}" ] || exit 2
demo_menu() { DEMO_CHOICE=Showcase; return 0; }
( set -- once; cd "$WORK/dotnet-spectre-examples"; . ./run.sh ) || exit 3
( cd "$WORK/dotnet-vb-spectre"; . ./run.sh ) || exit 4
''')
        calls = (self.work / "dotnet.log").read_text().splitlines()
        self.assertEqual(len(calls), 4)
        self.assertTrue(all(line.startswith("1 ") for line in calls), calls)
        self.assertEqual((self.work / "pwsh.log").read_text().strip(), "1")

    def test_setup_template_install_and_update_preserve_status_and_scope(self):
        text = source("setup").split('    echo "--- Gherkin / BDD runners (install-bdd)"\n', 1)[1].split('    echo "Per project, nothing to install here:', 1)[0]
        for status, verb in ((0, "update"), (1, "install")):
            self.env["LIST_STATUS"] = str(status)
            self.env["DOTNET_STATUS"] = "42"
            result = self.bash(text + '\n[ -z "${DOTNET_SYSTEM_NET_DISABLEIPV6+x}" ]')
            self.assertIn("NOTICE:", result.stdout)
            calls = (self.work / "dotnet.log").read_text()
            self.assertIn(f"1 new {verb}", calls)
            self.assertIn("unset new list", calls)

    def test_test_commands_scope_every_restore_child(self):
        import re
        text = source("test")
        labels = ["C#: dotnet new console + build + run", "VB.NET: dotnet new console -lang VB + build + run", "VB app calling a C# class library (mixed-language build)", "C# project builds with godot-mono and runs headless", "Reqnroll (C#, NUnit): dotnet new reqnroll-project, links.feature passes"]
        for label in labels:
            command = re.search(r'"' + re.escape(label) + r'"\s+\'(.*?)\' \d+', text, re.S).group(1)
            # Execute the actual environment prelude before a stand-in restore-capable child.
            prelude = command.split(";", 1)[0]
            self.bash(prelude + "; dotnet restore")
        self.assertTrue(all(line.startswith("1 ") for line in (self.work / "dotnet.log").read_text().splitlines()))

    def test_reqnroll_subshell_covers_children_and_preserves_failure(self):
        function = 'run_reqnroll() (' + source("demo").split('run_reqnroll() (', 1)[1].split('\nrun_selenium()', 1)[0]
        self.bash('''
demo_need() { :; }; demo_step() { :; }; sync_feature() { :; }
timed() { shift 4; "$@"; }
mkdir -p reqnroll-src; touch reqnroll-src/LinksSteps.cs
DEMO_LOGS="$WORK"
''' + function + '''
run_reqnroll || exit 1
[ -z "${DOTNET_SYSTEM_NET_DISABLEIPV6+x}" ] || exit 2
''')
        self.assertTrue(all(x.startswith("1 ") for x in (self.work / "dotnet.log").read_text().splitlines()))
        self.env["DOTNET_STATUS"] = "42"
        self.assertNotEqual(self.bash('demo_need() { :; }; ' + function + '\nrun_reqnroll', good=False).returncode, 0)


class Dosbox(Fixture):
    def test_shared_devtest_migration_fixture(self):
        h = self.work / 'helper'; h.write_text(helper())
        script = source('test').split("<< 'RETRO_CONFIG_CHECK_PY'\n", 1)[1].split('\nRETRO_CONFIG_CHECK_PY', 1)[0]
        self.env['RETRO_HELPER'] = str(h)
        result = subprocess.run(['/usr/bin/python3', '-c', script], env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_guest_argument_arrays_keep_imgmake_separate(self):
        h = self.work / 'helper'; h.write_text(helper())
        script = source('test').split("<< 'RETRO_ARGS_CHECK_PY'\n", 1)[1].split('\nRETRO_ARGS_CHECK_PY', 1)[0]
        self.env['RETRO_HELPER'] = str(h)
        result = subprocess.run(['/usr/bin/python3', '-c', script], env=self.env, text=True, capture_output=True)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class Qemu(Fixture):
    def test_setup_template_matches_guest_specific_defaults(self):
        loop = "    for RETRO_G in winnt40 win2000; do" + source('setup').split("    for RETRO_G in winnt40 win2000; do", 1)[1].split("    # v100 (Nov 5 2026): migrate existing configs", 1)[0]
        self.bash('mkdir -p "$HOME/winnt40" "$HOME/win2000"\n' + loop + '\nfor g in winnt40 win2000; do . "$HOME/$g/config"; printf "%s %s %s %s\\n" "$g" "$ACCEL" "$SOUND" "$DISPLAY_OPTS"; done > "$WORK/defaults"')
        self.assertEqual((self.work / 'defaults').read_text().splitlines(), ['winnt40 auto sb16 gtk,zoom-to-fit=on', 'win2000 tcg none gtk,zoom-to-fit=off'])

    def test_shared_devtest_qemu_fixture(self):
        h = self.work / 'helper'; h.write_text(helper())
        script = source('test').split("<< 'RETRO_QEMU_CHECK_PY'\n", 1)[1].split('\nRETRO_QEMU_CHECK_PY', 1)[0]
        self.env['RETRO_HELPER'] = str(h)
        result = subprocess.run(['/usr/bin/python3', '-c', script], env=self.env, text=True, capture_output=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class FontsAndMedia(Fixture):
    def test_shared_devtest_font_fixture(self):
        h = self.work / 'helper'; h.write_text(helper())
        script = source('test').split("<< 'RETRO_FONT_CHECK_PY'\n", 1)[1].split('\nRETRO_FONT_CHECK_PY', 1)[0]
        self.env['RETRO_HELPER'] = str(h)
        result = subprocess.run(['/usr/bin/python3', '-c', script], env=self.env, text=True, capture_output=True, timeout=90)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)

    def test_tiny_iso_roundtrip(self):
        import re
        command = re.search(r'check "genisoimage Joliet/Rock Ridge filename round-trip" \'(.*?)\'\n', source('test')).group(1)
        self.bash(command)


class Colors(Fixture):
    def test_shared_devtest_color_fixture(self):
        h = self.work / 'helper'; h.write_text(helper())
        reset = self.work / 'default.reg'
        reset.write_text("Windows Registry Editor Version 5.00\n\n" + source('setup').split("<< 'RETRO_COLOR_DEFAULT'\n", 1)[1].split('\nRETRO_COLOR_DEFAULT', 1)[0])
        script = source('test').split("<< 'RETRO_COLOR_CHECK_PY'\n", 1)[1].split('\nRETRO_COLOR_CHECK_PY', 1)[0]
        self.env.update(RETRO_HELPER=str(h), RETRO_DEFAULT=str(reset))
        result = subprocess.run(['/usr/bin/python3', '-c', script], env=self.env, text=True, capture_output=True, timeout=180)
        self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
