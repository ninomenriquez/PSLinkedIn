import contextlib
import io
import plistlib
import struct
import tempfile
import unittest
import zipfile
from pathlib import Path

from check_ipa import check_executable, main


def executable(cryptid=0):
    header = struct.pack("<8I", 0xFEEDFACF, 0x0100000C, 0, 2, 1, 24, 0, 0)
    return header + struct.pack("<6I", 0x2C, 24, 0, 0, cryptid, 0)


class PreflightTests(unittest.TestCase):
    def test_decrypted_arm64(self):
        check_executable(executable())

    def test_encrypted_rejected(self):
        with self.assertRaisesRegex(ValueError, "encrypted"):
            check_executable(executable(1))

    def test_fat_arm64(self):
        binary = executable()
        fat = struct.pack(">7I", 0xCAFEBABE, 1, 0x0100000C, 0, 28, len(binary), 0)
        check_executable(fat + binary)

    def test_truncated_commands_rejected(self):
        with self.assertRaises(ValueError):
            check_executable(executable()[:-1])

    def test_metadata_version_gate(self):
        for version in ("9.1.555", "9.1.556"):
            with self.subTest(version=version), tempfile.TemporaryDirectory() as folder:
                path = Path(folder) / "synthetic.ipa"
                info = {"CFBundleIdentifier": "com.linkedin.LinkedIn",
                        "CFBundleShortVersionString": version,
                        "CFBundleExecutable": "Synthetic"}
                with zipfile.ZipFile(path, "w") as ipa:
                    ipa.writestr("Payload/Synthetic.app/Info.plist", plistlib.dumps(info, fmt=plistlib.FMT_BINARY))
                    ipa.writestr("Payload/Synthetic.app/Synthetic", executable())
                with contextlib.redirect_stdout(io.StringIO()):
                    if version == "9.1.555":
                        main(path)
                    else:
                        with self.assertRaisesRegex(ValueError, "unverified"):
                            main(path)


if __name__ == "__main__":
    unittest.main()
