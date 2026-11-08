"""v101: validate committed source archives without extracting or executing their contents."""
import argparse
import io
from pathlib import Path, PurePosixPath
import stat
import subprocess
import tarfile
import zipfile

ROOT = Path(__file__).resolve().parents[1]
REQUIRED = {f"dev-{name}-chromebook.sh" for name in ("setup", "init", "test", "demo")} | {"AGENTS.md", "CLAUDE.md"}


def reject_links(index):
    for entry in index.split(b"\0"):
        if entry and entry.split(b" ", 1)[0] == b"120000":
            raise ValueError("tracked symlink: " + entry.split(b"\t", 1)[1].decode(errors="replace"))


def archive_files(data, kind):
    """Return prefix-free regular files; reject links, special files, duplicates and unsafe paths."""
    files = {}
    prefix = None

    def add(name, body, mode, directory=False):
        nonlocal prefix
        path = PurePosixPath(name)
        if path.is_absolute() or ".." in path.parts or "\\" in name or not path.parts:
            raise ValueError("unsafe archive member: " + name)
        parts = path.parts
        if prefix is None:
            prefix = parts[0]
        if parts[0] != prefix:
            raise ValueError("archive must have one root directory")
        if directory:
            return
        if len(parts) < 2 or not stat.S_ISREG(mode):
            raise ValueError("non-regular archive member: " + name)
        relative = "/".join(parts[1:])
        if relative in files:
            raise ValueError("duplicate archive member: " + relative)
        if mode & 0o6000:
            raise ValueError("set-id archive member: " + name)
        # Git tar's umask changes writable bits; zip omits mode entirely for ordinary files.
        # Compare the portable executable contract rather than incidental group-write bits.
        files[relative] = (body, 0o755 if mode & 0o111 else 0o644)

    if kind == "zip":
        with zipfile.ZipFile(io.BytesIO(data)) as archive:
            bad = archive.testzip()
            if bad:
                raise ValueError("zip integrity failure: " + bad)
            for member in archive.infolist():
                mode = member.external_attr >> 16
                if member.is_dir():
                    if stat.S_ISLNK(mode):
                        raise ValueError("symlink directory")
                    add(member.filename, b"", mode, True)
                else:
                    # Git zip uses DOS entries with mode 0 for ordinary, non-executable files.
                    if not stat.S_IFMT(mode):
                        mode |= stat.S_IFREG
                    add(member.filename, archive.read(member), mode)
    else:
        with tarfile.open(fileobj=io.BytesIO(data), mode="r:*") as archive:
            for member in archive:
                if member.isdir():
                    add(member.name, b"", stat.S_IFDIR | member.mode, True)
                elif member.isfile():
                    add(member.name, archive.extractfile(member).read(), stat.S_IFREG | member.mode)
                else:
                    raise ValueError("non-regular archive member: " + member.name)
    return files


def validate(actual, expected):
    if actual != expected:
        missing = sorted(expected.keys() - actual.keys())
        extra = sorted(actual.keys() - expected.keys())
        changed = sorted(k for k in actual.keys() & expected.keys() if actual[k] != expected[k])
        raise ValueError(f"archive mismatch: missing={missing}, extra={extra}, changed={changed}")
    if not REQUIRED <= actual.keys():
        raise ValueError("archive omits required bundle files")
    if b"@AGENTS.md" not in actual["CLAUDE.md"][0].splitlines():
        raise ValueError("CLAUDE.md must import adjacent AGENTS.md")


def expected_files(ref):
    tree = subprocess.check_output(["git", "ls-tree", "-rz", ref], cwd=ROOT)
    reject_links(tree)
    # git archive applies committed export-ignore attributes; no loose files enter this manifest.
    data = subprocess.check_output(["git", "archive", "--format=tar", "--prefix=bundle/", ref], cwd=ROOT)
    return archive_files(data, "tar")


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--index", action="store_true", help="reject any tracked mode-120000 entry")
    parser.add_argument("--ref", help="committed tree to validate (also builds in-memory zip/tar fixtures)")
    parser.add_argument("--archive", type=Path, help="also validate an actual local/GitHub zip or tar against --ref")
    args = parser.parse_args()
    if args.index:
        reject_links(subprocess.check_output(["git", "ls-files", "-s", "-z"], cwd=ROOT))
        print("PASS: no tracked symlinks")
    if args.ref:
        expected = expected_files(args.ref)
        for kind in ("zip", "tar"):
            data = subprocess.check_output(["git", "archive", f"--format={kind}", "--prefix=bundle/", args.ref], cwd=ROOT)
            validate(archive_files(data, kind), expected)
        if args.archive:
            data = args.archive.read_bytes()
            kind = "zip" if zipfile.is_zipfile(io.BytesIO(data)) else "tar"
            validate(archive_files(data, kind), expected)
        print("PASS: archive integrity, regular modes, import and committed manifest")
    elif args.archive or not args.index:
        parser.error("use --index and/or --ref; --archive requires --ref")


if __name__ == "__main__":
    main()
