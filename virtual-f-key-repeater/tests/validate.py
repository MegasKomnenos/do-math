from pathlib import Path
import re
import os
import shutil
import subprocess
import tempfile


ROOT = Path(__file__).resolve().parents[1]
DRIVER = (ROOT / "driver" / "vhidmini.c").read_text(encoding="utf-8")
COMMON = (ROOT / "driver" / "inc" / "common.h").read_text(encoding="utf-8")
CONTROLLER = (ROOT / "controller" / "Program.cs").read_text(encoding="utf-8")


def descriptor_bytes() -> list[int]:
    match = re.search(
        r"G_DefaultReportDescriptor\[\]\s*=\s*\{(?P<body>.*?)\n\};",
        DRIVER,
        re.DOTALL,
    )
    assert match, "HID report descriptor was not found"
    body = re.sub(r"//.*", "", match.group("body"))
    constants = {
        "KEYBOARD_REPORT_ID": 1,
        "CONTROL_REPORT_ID": 2,
        "CONTROL_FEATURE_REPORT_SIZE_CB": 3,
    }
    result: list[int] = []
    for raw_token in body.split(","):
        token = raw_token.strip()
        if not token:
            continue
        result.append(constants[token] if token in constants else int(token, 0))
    return result


def report_widths(descriptor: list[int]) -> dict[str, dict[int, int]]:
    widths = {"input": {}, "output": {}, "feature": {}}
    report_size = 0
    report_count = 0
    report_id = 0
    main_tags = {8: "input", 9: "output", 11: "feature"}
    offset = 0

    while offset < len(descriptor):
        prefix = descriptor[offset]
        offset += 1
        assert prefix != 0xFE, "long HID items are not expected"
        size = (0, 1, 2, 4)[prefix & 0x03]
        item_type = (prefix >> 2) & 0x03
        tag = (prefix >> 4) & 0x0F
        data = descriptor[offset : offset + size]
        assert len(data) == size, "truncated HID item"
        value = sum(byte << (8 * index) for index, byte in enumerate(data))
        offset += size

        if item_type == 1 and tag == 7:
            report_size = value
        elif item_type == 1 and tag == 8:
            report_id = value
        elif item_type == 1 and tag == 9:
            report_count = value
        elif item_type == 0 and tag in main_tags:
            kind = main_tags[tag]
            widths[kind][report_id] = (
                widths[kind].get(report_id, 0) + report_size * report_count
            )

    return widths


def main() -> None:
    descriptor = descriptor_bytes()
    widths = report_widths(descriptor)

    assert widths["input"] == {1: 64}, widths["input"]
    assert widths["output"] == {1: 8}, widths["output"]
    assert widths["feature"] == {2: 24}, widths["feature"]
    assert "RepeatNext(&deviceContext->Cycle, now)" in DRIVER
    assert "RepeatCommit(&deviceContext->Cycle, nextKey, now)" in DRIVER
    assert "RepeatKeys((unsigned char)nextKey, readReport.Keys)" in DRIVER
    assert "WdfSynchronizationScopeDevice" in DRIVER
    assert "#define VIRTUAL_F_VID      0xCAFE" in COMMON
    assert "#define VIRTUAL_F_PID      0xF001" in COMMON
    assert "private const ushort VendorId = 0xCAFE" in CONTROLLER
    assert "private const ushort ProductId = 0xF001" in CONTROLLER
    assert "caps.FeatureReportByteLength == 4" in CONTROLLER
    version = re.search(r"#define VIRTUAL_F_VERSION\s+(0x[0-9A-Fa-f]+)", COMMON)
    assert version
    assert f"private const ushort DeviceVersion = {version[1]}" in CONTROLLER
    assert "attributes.VersionNumber != DeviceVersion" in CONTROLLER

    print("HID descriptor and driver/controller contracts: PASS")
    compiler = shutil.which("cl" if os.name == "nt" else "cc") or shutil.which("gcc")
    assert compiler, "A C compiler is required for the cycle behavior tests"
    with tempfile.TemporaryDirectory(prefix="virtual-f-cycle-") as directory:
        executable = Path(directory) / ("test_cycle.exe" if os.name == "nt" else "test_cycle")
        source = ROOT / "tests" / "test_cycle.c"
        if Path(compiler).stem.lower() == "cl":
            command = [compiler, "/nologo", "/W4", "/WX", str(source), f"/Fe:{executable}"]
            vcvars = Path(compiler).parents[6] / "Auxiliary" / "Build" / "vcvars64.bat"
            if vcvars.is_file():
                command = (f'cmd.exe /d /s /c "call "{vcvars}" >nul && '
                           f'{subprocess.list2cmdline(command)}"')
        else:
            command = [compiler, "-std=c99", "-Wall", "-Wextra", "-Werror", str(source), "-o", str(executable)]
        subprocess.run(command, cwd=directory, check=True)
        subprocess.run([str(executable)], check=True)


if __name__ == "__main__":
    main()
