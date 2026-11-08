"""v101 portable regressions. No real bundle run, guest, network or installed helper mutation."""
import io
import stat
import tarfile
import unittest
import zipfile

import check_release_archive as archive_check


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


if __name__ == "__main__":
    unittest.main()
