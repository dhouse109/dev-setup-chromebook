"""Extract/compile the embedded compatibility shim; no Docker, profiles or service starts."""
import os
from pathlib import Path
import subprocess
import tempfile
import unittest

ROOT = Path(__file__).resolve().parents[1]


class TypesenseCompat(unittest.TestCase):
    def test_only_missing_readonly_proc_io_gets_zero_counters(self):
        source = (ROOT / "dev-setup-chromebook.sh").read_text().split(
            "<< 'TS_PROC_IO_C'\n", 1)[1].split("\nTS_PROC_IO_C", 1)[0]
        with tempfile.TemporaryDirectory(dir=ROOT / "assets") as tmp:
            work = Path(tmp)
            (work / "shim.c").write_text(source)
            (work / "read.c").write_text(r'''
#include <errno.h>
#include <stdio.h>
int main(int argc, char **argv) {
    if (argc != 3) return 99;
    FILE *f = fopen(argv[1], argv[2]);
    if (!f) { printf("errno=%d\n", errno); return 1; }
    char data[512]; size_t n = fread(data, 1, sizeof(data), f);
    fwrite(data, 1, n, stdout); fclose(f); return 0;
}
''')
            subprocess.run(["gcc", "-std=c11", "-shared", "-fPIC", "-O2", "-Wall", "-Wextra", "-Werror",
                            "-o", str(work / "shim.so"), str(work / "shim.c"), "-ldl"], check=True)
            subprocess.run(["gcc", "-o", str(work / "read"), str(work / "read.c")], check=True)
            env = dict(os.environ, LD_PRELOAD=str(work / "shim.so"))
            def read(path, mode="r"):
                return subprocess.run([str(work / "read"), str(path), mode], env=env,
                                      capture_output=True, text=True, timeout=5)
            real = work / "real"
            real.write_text("real file remains real\n")
            result = read(real)
            self.assertEqual(result.returncode, 0)
            self.assertEqual(result.stdout, real.read_text())
            self.assertEqual(result.stderr, "")
            result = read(work / "does-not-exist")
            self.assertEqual(result.returncode, 1)
            self.assertEqual(result.stdout, "errno=2\n")
            self.assertEqual(result.stderr, "")
            result = read("/proc/self/io")
            self.assertEqual(result.returncode, 0, result.stderr)
            self.assertEqual(len(result.stdout.splitlines()), 7)
            if not Path("/proc/self/io").exists():
                self.assertTrue(all(row.endswith(": 0") for row in result.stdout.splitlines()))
                self.assertIn("process-I/O counters report zero", result.stderr)
                result = read("/proc/self/io", "r+")
                self.assertEqual(result.returncode, 1)
                self.assertEqual(result.stderr, "")


if __name__ == "__main__":
    unittest.main()
