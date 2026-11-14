"""Read-only, offline preflight. Usage: py -3 tools/check_ipa.py LinkedIn.ipa"""
import plistlib
import struct
import sys
import zipfile

EXPECTED_VERSION = "9.1.555"


def arm64_slice(data):
    magic = data[:4]
    if magic in (b"\xca\xfe\xba\xbe", b"\xca\xfe\xba\xbf"):
        wide = magic[-1] == 0xBF
        count = struct.unpack_from(">I", data, 4)[0]
        for index in range(count):
            pos = 8 + index * (32 if wide else 20)
            cpu, subtype = struct.unpack_from(">II", data, pos)
            offset, size = struct.unpack_from(">QQ" if wide else ">II", data, pos + 8)
            if cpu == 0x0100000C and subtype & 0xFFFFFF == 0:
                return data[offset:offset + size]
        raise ValueError("No regular arm64 slice found")
    return data


def check_executable(data):
    data = arm64_slice(data)
    if data[:4] != b"\xcf\xfa\xed\xfe":
        raise ValueError("Expected little-endian 64-bit Mach-O")
    cpu, subtype = struct.unpack_from("<II", data, 4)
    if cpu != 0x0100000C or subtype & 0xFFFFFF != 0:
        raise ValueError("Expected regular arm64 executable")
    commands, command_bytes = struct.unpack_from("<II", data, 16)
    pos = 32
    limit = pos + command_bytes
    if limit > len(data):
        raise ValueError("Truncated Mach-O commands")
    for _ in range(commands):
        if pos + 8 > limit:
            raise ValueError("Invalid Mach-O command table")
        command, size = struct.unpack_from("<II", data, pos)
        if size < 8 or pos + size > limit:
            raise ValueError("Invalid Mach-O command size")
        if command in (0x21, 0x2C):
            if size < 20:
                raise ValueError("Truncated encryption command")
            cryptid = struct.unpack_from("<I", data, pos + 16)[0]
            if cryptid:
                raise ValueError("Executable is encrypted (cryptid=%d)" % cryptid)
        pos += size


def main(path):
    with zipfile.ZipFile(path) as ipa:
        matches = [name for name in ipa.namelist()
                   if name.startswith("Payload/") and name.count("/") == 2
                   and name.endswith(".app/Info.plist")]
        if len(matches) != 1:
            raise ValueError("Expected exactly one top-level application")
        info_path = matches[0]
        info = plistlib.loads(ipa.read(info_path))
        version = info.get("CFBundleShortVersionString")
        print("Bundle ID:", info.get("CFBundleIdentifier"))
        print("LinkedIn version:", version)
        print("Build number:", info.get("CFBundleVersion"))
        print("Minimum iOS:", info.get("MinimumOSVersion"))
        if info.get("CFBundleIdentifier") != "com.linkedin.LinkedIn":
            raise ValueError("Use the original decrypted LinkedIn IPA as input")
        if version != EXPECTED_VERSION:
            raise ValueError("Baseline requires LinkedIn %s; this IPA is unverified" % EXPECTED_VERSION)
        executable = info_path.rsplit("/", 1)[0] + "/" + info["CFBundleExecutable"]
        check_executable(ipa.read(executable))
        print("PASS: expected version and unencrypted arm64 main executable.")
        print("This does not prove all embedded code is decrypted, authenticity,")
        print("or runtime compatibility. Verify features on the phone after installation.")


if __name__ == "__main__":
    try:
        if len(sys.argv) != 2:
            raise ValueError("Usage: py -3 tools/check_ipa.py PATH_TO_IPA")
        main(sys.argv[1])
    except (ValueError, KeyError, OSError, zipfile.BadZipFile, struct.error,
            plistlib.InvalidFileException) as error:
        print("STOP:", error, file=sys.stderr)
        sys.exit(1)
