"""v101 portable regressions. No real bundle run, guest, network or installed helper mutation."""
import ast
import io
import json
import os
import shlex
from pathlib import Path
import stat
import subprocess
import tarfile
import tempfile
import time
import unittest
import zipfile

import check_release_archive as archive_check

ROOT = Path(__file__).resolve().parents[1]


def embedded(name, marker):
    source = (ROOT / f'dev-{name}-chromebook.sh').read_text()
    return source.split("<< '" + marker + "'\n", 1)[1].split('\n' + marker, 1)[0] + '\n'


class Archives(unittest.TestCase):
    def zip_bytes(self, members):
        result = io.BytesIO()
        with zipfile.ZipFile(result, "w") as archive:
            for name, body, mode in members:
                item = zipfile.ZipInfo(name)
                item.create_system = 3
                item.external_attr = mode << 16
                archive.writestr(item, body)
        return result.getvalue()

    def test_index_link_guard_handles_nul_delimited_names(self):
        archive_check.reject_links(b"100644 abc 0\tordinary name\0")
        with self.assertRaisesRegex(ValueError, "tracked symlink"):
            archive_check.reject_links(b"120000 abc 0\todd\nname\0")

    def test_zip_rejects_symlink_and_unsafe_members(self):
        for name, mode in (("bundle/CLAUDE.md", stat.S_IFLNK | 0o777), ("bundle/../escape", stat.S_IFREG | 0o644)):
            with self.subTest(name=name), self.assertRaises(ValueError):
                archive_check.archive_files(self.zip_bytes([(name, b"AGENTS.md", mode)]), "zip")

    def test_tar_rejects_hardlinks(self):
        data = io.BytesIO()
        with tarfile.open(fileobj=data, mode="w") as archive:
            member = tarfile.TarInfo("bundle/CLAUDE.md")
            member.type = tarfile.LNKTYPE
            member.linkname = "bundle/AGENTS.md"
            archive.addfile(member)
        with self.assertRaisesRegex(ValueError, "non-regular"):
            archive_check.archive_files(data.getvalue(), "tar")

    def test_git_dos_entry_is_regular_and_write_umask_does_not_change_execute_contract(self):
        for mode in (0, stat.S_IFREG | 0o644, stat.S_IFREG | 0o664):
            result = archive_check.archive_files(self.zip_bytes([("bundle/CLAUDE.md", b"@AGENTS.md\n", mode)]), "zip")
            self.assertEqual(result["CLAUDE.md"], (b"@AGENTS.md\n", 0o644))

    def test_archive_manifest_detects_missing_changed_modes_and_extra_files(self):
        expected = {name: (b"x", 0o755 if name.endswith(".sh") else 0o644) for name in archive_check.REQUIRED}
        expected["CLAUDE.md"] = (b"@AGENTS.md\n", 0o644)
        members = [("github-prefix/" + name, body, stat.S_IFREG | mode) for name, (body, mode) in expected.items()]
        actual = archive_check.archive_files(self.zip_bytes(members), "zip")
        archive_check.validate(actual, expected)
        for change in ("missing", "extra", "content", "mode"):
            altered = dict(actual)
            if change == "missing":
                altered.pop("AGENTS.md")
            elif change == "extra":
                altered["loose-secret.txt"] = (b"fixture only", 0o644)
            elif change == "content":
                altered["CLAUDE.md"] = (b"duplicate rules", 0o644)
            else:
                altered["dev-setup-chromebook.sh"] = (b"x", 0o644)
            with self.subTest(change=change), self.assertRaises(ValueError):
                archive_check.validate(altered, expected)


class QemuProbe(unittest.TestCase):
    def setUp(self):
        (ROOT / 'assets').mkdir(exist_ok=True)
        self.temp = tempfile.TemporaryDirectory(prefix='v101-probe-', dir=ROOT / 'assets')
        self.addCleanup(self.temp.cleanup)
        self.root = Path(self.temp.name)
        self.bin = self.root / 'bin'
        self.bin.mkdir()
        self.probe = self.root / 'probe.py'
        self.probe.write_text(embedded('test', 'RETRO_QEMU_PROBE_PY'))
        self.fake('qemu-img', 'from pathlib import Path\nimport sys\nPath(sys.argv[-2]).touch()')
        self.fake('qemu-system-i386', '''import json,os,signal,socket,sys,time
from pathlib import Path
if '--version' in sys.argv:
    print('fixture QEMU'); raise SystemExit(0)
Path('fake.pid').write_text(str(os.getpid()))
mode=os.environ['FAKE_QEMU_MODE']
print('fixture stderr before wait', file=sys.stderr, flush=True)
if mode == 'exit': raise SystemExit(23)
if mode == 'no-socket':
    time.sleep(30); raise SystemExit(0)
if mode == 'ignore-quit': signal.signal(signal.SIGTERM, signal.SIG_IGN)
s=socket.socket(socket.AF_UNIX); s.bind('qmp.sock'); s.listen(1)
c,_=s.accept(); f=c.makefile('rwb')
if mode == 'bad-greeting':
    f.write(b'not json\\n'); f.flush(); time.sleep(30)
if mode == 'silent-greeting': time.sleep(30)
f.write(json.dumps({'QMP': {'version': {}, 'capabilities': []}}).encode()+b'\\n'); f.flush()
for line in f:
    request=json.loads(line)
    command=request['execute']
    if command=='quit':
        if mode=='ignore-quit': continue
        break
    if mode=='silent-query' and command=='query-status': time.sleep(30)
    if mode=='error': reply={'error': {'desc':'fixture protocol failure'}, 'id':request['id']}
    else: reply={'return': {} if command=='qmp_capabilities' else {'status':'paused' if mode=='paused' else 'running'}, 'id':request['id']}
    # Events and an unrelated response must not be mistaken for this command's reply.
    f.write(json.dumps({'event':'fixture-event'}).encode()+b'\\n')
    f.write(json.dumps({'return':{}, 'id':-1}).encode()+b'\\n')
    f.write(json.dumps(reply).encode()+b'\\n'); f.flush()
''')
        self.env = dict(PATH=f'{self.bin}:/usr/bin:/bin', HOME=str(self.root), LC_ALL='C.UTF-8')

    def fake(self, name, body):
        p = self.bin / name
        p.write_text('#!/usr/bin/python3\n' + body + '\n')
        p.chmod(0o755)

    def run_probe(self, mode, signal_parent=False):
        work, diag = self.root / 'work', self.root / 'diag'
        process = subprocess.Popen(['/usr/bin/python3', str(self.probe), '--work', str(work), '--diag', str(diag), '--seconds', '0.8'], env=dict(self.env, FAKE_QEMU_MODE=mode), stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
        if signal_parent:
            until = time.monotonic() + 5
            while not (work / 'fake.pid').exists() and time.monotonic() < until:
                time.sleep(0.02)
            process.terminate()
        out, err = process.communicate(timeout=10)
        result = json.loads((diag / 'result.json').read_text())
        self.assertIn('Persistent diagnostics:', out, out + err)
        self.assertIn('fixture stderr before wait', (diag / 'stderr.log').read_text())
        self.assertTrue((diag / 'events.jsonl').stat().st_size)
        self.assertFalse((work / 'qmp.sock').exists())
        pid = int((work / 'fake.pid').read_text())
        with self.assertRaises(ProcessLookupError):
            os.kill(pid, 0)
        return process.returncode, result, (diag / 'events.jsonl').read_text()

    def test_qmp_events_and_response_ids_then_clean_quit(self):
        rc, result, events = self.run_probe('normal')
        self.assertEqual(rc, 0)
        self.assertTrue(result['clean'])
        self.assertEqual(result['status'], 'running')
        self.assertIn('fixture-event', events)

    def test_startup_protocol_and_status_failures_are_retained(self):
        for mode in ('exit', 'no-socket', 'bad-greeting', 'silent-greeting', 'silent-query', 'error', 'paused'):
            with self.subTest(mode=mode):
                # Each case needs an independent persistent diagnostic directory.
                case = QemuProbe('test_qmp_events_and_response_ids_then_clean_quit')
                case.setUp()
                try:
                    rc, result, _ = case.run_probe(mode)
                    self.assertNotEqual(rc, 0)
                    self.assertTrue(result['error'])
                finally:
                    case.doCleanups()

    def test_ignored_quit_and_term_escalate_to_kill_without_success(self):
        rc, result, events = self.run_probe('ignore-quit')
        self.assertNotEqual(rc, 0)
        self.assertFalse(result['clean'])
        self.assertIn('"kill"', events)

    def test_parent_term_flushes_and_reaps_child(self):
        rc, result, events = self.run_probe('silent-query', signal_parent=True)
        self.assertNotEqual(rc, 0)
        self.assertIn('InterruptedError', result['error'])
        self.assertIn('cleanup-complete', events)


class RetroDefaults(unittest.TestCase):
    def test_captured_v100_template_matches_shared_regression_input(self):
        tree = ast.parse(embedded('test', 'RETRO_DEFAULTS_V101_PY'))
        assignment = next(node for node in tree.body if isinstance(node, ast.Assign)
                          and any(isinstance(target, ast.Name) and target.id == 'V100_NT_CONFIG' for target in node.targets))
        self.assertEqual(ast.literal_eval(assignment.value),
                         (ROOT / 'tests/fixtures/v100-winnt40.config').read_bytes())

    def test_shared_installed_helper_contract_in_scratch_home(self):
        with tempfile.TemporaryDirectory(prefix='v101-defaults-', dir=ROOT / 'assets') as tmp:
            root = Path(tmp)
            helper = root / 'helper'
            helper.write_text(embedded('setup', 'DEVRETRO_EOF'))
            env = dict(PATH='/usr/bin:/bin', HOME=str(root), WORK=str(root), RETRO_HELPER=str(helper))
            result = subprocess.run(['/usr/bin/python3', '-c', embedded('test', 'RETRO_DEFAULTS_V101_PY')], env=env, text=True, capture_output=True, timeout=60)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class Inspector(unittest.TestCase):
    def test_global_release_node_status_metadata_and_cleanup_contracts(self):
        with tempfile.TemporaryDirectory(prefix='v101-inspector-', dir=ROOT / 'assets') as tmp:
            root = Path(tmp)
            helper = root / 'inspector-check.py'
            helper.write_text(embedded('test', 'INSPECTOR_CHECK_V101_PY'))
            clean = root / 'devclean'
            clean.write_text(embedded('setup', 'DEVCLEAN_EOF'))
            env = dict(PATH='/usr/bin:/bin', HOME=str(root), WORK=str(root),
                       INSPECTOR_CHECK=str(helper), DEVCLEAN_HELPER=str(clean))
            result = subprocess.run(['/usr/bin/python3', '-c', embedded('test', 'INSPECTOR_FIXTURES_V101_PY')],
                                    env=env, text=True, capture_output=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class GuestLan(unittest.TestCase):
    def test_shared_local_pair_editing_status_and_adoption_contracts(self):
        with tempfile.TemporaryDirectory(prefix='v101-lan-', dir=ROOT / 'assets') as tmp:
            root = Path(tmp)
            helper = root / 'helper'
            helper.write_text(embedded('setup', 'DEVRETRO_EOF'))
            env = dict(PATH='/usr/bin:/bin', HOME=str(root), WORK=str(root), RETRO_HELPER=str(helper))
            result = subprocess.run(['/usr/bin/python3', '-c', embedded('test', 'RETRO_LAN_FIXTURES_V101_PY')],
                                    env=env, text=True, capture_output=True, timeout=120)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


class DemoFoundation(unittest.TestCase):
    def test_nested_scaffold_refresh_index_and_clean(self):
        with tempfile.TemporaryDirectory(prefix='v101-scaffold-', dir=ROOT / 'assets') as tmp:
            root = Path(tmp)
            fixture = root / 'retro-scaffold-v101.py'
            fixture.write_text(embedded('test', 'RETRO_SCAFFOLD_V101_PY'))
            script = ROOT / 'dev-test-chromebook.sh'
            source = script.read_text()
            line = next(line for line in source.splitlines()
                        if line.lstrip().startswith('check "Advanced-demo scaffold/lifecycle contracts'))
            command = shlex.split(line)[2]
            # Start without SCRIPT_DIR, then execute the production path setup and
            # _run's child-shell boundary. Removing its export must break this check.
            preamble = 'SCRIPT_DIR=' + source.split('SCRIPT_DIR=', 1)[1].split(
                'export ASSETS="$SCRIPT_DIR/assets"', 1)[0] + 'export ASSETS="$SCRIPT_DIR/assets"\n'
            env = dict(PATH='/usr/bin:/bin', HOME=str(root), WORK=str(root))
            result = subprocess.run(['bash', '-c', preamble + 'bash -c ' + shlex.quote(command), str(script)],
                                    cwd=root, env=env, text=True, capture_output=True, timeout=90)
            self.assertEqual(result.returncode, 0, result.stdout + result.stderr)


if __name__ == "__main__":
    unittest.main()
