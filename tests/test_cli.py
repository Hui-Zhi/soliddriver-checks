"""The soliddriver-checks command: targets, options, output and errors."""

import json
import os
import socket
import subprocess
import sys

import pytest

from conftest import INSTALLED, PACKAGES, REPO, kmp_file

pytestmark = pytest.mark.container


def sdc(*args, cwd, input=None):
    env = dict(os.environ, PYTHONPATH=str(REPO / "src"), PYTHONDONTWRITEBYTECODE="1")
    return subprocess.run(
        [sys.executable, "-m", "soliddriver_checks.cli.cli", *map(str, args)],
        cwd=cwd,
        env=env,
        input=input,
        capture_output=True,
        text=True,
    )


def names(report):
    return sorted(r["name"]["value"] for r in json.loads(report.read_text()))


def test_version(tmp_path):
    from soliddriver_checks.version import __VERSION__

    result = sdc("--version", cwd=tmp_path)
    assert result.returncode == 0
    assert result.stdout.strip() == __VERSION__


def test_help_lists_targets_and_formats(tmp_path):
    result = sdc("--help", cwd=tmp_path)
    assert result.returncode == 0
    assert '"system"' in result.stdout
    assert "[html|json]" in result.stdout


def test_unknown_format(tmp_path):
    result = sdc("system", "-f", "xlsx", cwd=tmp_path)
    assert result.returncode == 2
    assert "xlsx" in result.stderr


def test_unknown_target(tmp_path):
    result = sdc("no-such-target", cwd=tmp_path)
    assert result.returncode == 2
    assert 'is not a KMP file (.rpm), a directory or "system"' in result.stderr
    assert list(tmp_path.iterdir()) == []


@pytest.mark.parametrize(
    "target, filter, message",
    [
        ("system", '"license" == "GPL"', "Invalid filter"),
        ("system", '"vendor" = "x"', 'Unknown filter key: "vendor"'),
        ("system", '"modulename" match "("', "Invalid regular expression"),
        ("dir", '"modulename" = "x"', 'Unknown filter key: "modulename"'),
    ],
)
def test_invalid_filter_stops_before_the_scan(tmp_path, target, filter, message):
    target = tmp_path if target == "dir" else target
    result = sdc(target, "-i", filter, "-o", tmp_path / "out", cwd=tmp_path)
    assert result.returncode == 2
    assert message in result.stderr
    assert not (tmp_path / "out.json").exists()


def test_directory_json(kmp_dir, tmp_path):
    from soliddriver_checks.api.kmp import KMP_COLUMNS

    result = sdc(kmp_dir, cwd=tmp_path)  # json in the current directory by default
    assert result.returncode == 0, result.stderr
    records = json.loads((tmp_path / "check_result.json").read_text())
    assert sorted(r["name"]["value"] for r in records) == sorted(PACKAGES)
    assert all(sorted(r) == sorted(KMP_COLUMNS) for r in records)
    # one progress line per KMP on stderr
    assert "Checking %d KMP(s)..." % len(PACKAGES) in result.stderr
    assert "PASS    %s" % kmp_file(kmp_dir, "sdc-good-kmp-default") in result.stderr


def test_directory_html(kmp_dir, tmp_path):
    result = sdc(kmp_dir, "-f", "html", "-o", tmp_path / "report", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    html = (tmp_path / "report.html").read_text()
    assert "<title>Kernel Module Packages Check Report</title>" in html
    for package in PACKAGES:
        assert package in html


def test_directory_with_filter(kmp_dir, tmp_path):
    sdc(kmp_dir, "-i", '"level.level" = "PASS"', "-o", "pass", cwd=tmp_path)
    assert names(tmp_path / "pass.json") == ["sdc-good-kmp-default"]

    sdc(kmp_dir, "-i", '"modalias.level" = "ERROR"', "-o", "alias", cwd=tmp_path)
    assert names(tmp_path / "alias.json") == sorted(
        [
            "sdc-nowm2-kmp-default",
            "sdc-badksym-kmp-default",
            "sdc-allalias-kmp-default",
            "sdc-xz-kmp-default",
            "sdc-zst-kmp-default",
            "sdc-debug-kmp-default-debuginfo",
        ]
    )

    sdc(
        kmp_dir,
        "-f",
        "html",
        "-i",
        '"supported_flag" match "(?i)EXTERNAL" and "wm2_invoked" = "True"',
        "-o",
        "supported",
        cwd=tmp_path,
    )
    html = (tmp_path / "supported.html").read_text()
    assert "sdc-supported-yes-kmp-default" in html
    assert "sdc-good-kmp-default" not in html


def test_empty_directory(tmp_path):
    empty = tmp_path / "empty"
    empty.mkdir()
    for fmt in ("json", "html"):
        result = sdc(empty, "-f", fmt, "-o", "out", cwd=tmp_path)
        assert result.returncode == 0, result.stderr
    assert json.loads((tmp_path / "out.json").read_text()) == []
    assert "<title>" in (tmp_path / "out.html").read_text()


def test_single_kmp(kmp_dir, tmp_path):
    rpm = kmp_file(kmp_dir, "sdc-nosupported-kmp-default")
    # --format, --output and --filter are ignored
    result = sdc(rpm, "-f", "html", "-i", '"nope" = "x"', cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    lines = result.stdout.splitlines()
    assert lines[0] == "sdc-nosupported-kmp-default: ERROR"
    assert any(
        line.split()[:2] == ["supported_flag", "ERROR"]
        and "No 'supported' flag" in line
        for line in lines
    )
    assert any(line.split()[:2] == ["vendor", "PASS"] for line in lines)
    assert list(tmp_path.iterdir()) == []


def test_output_into_existing_directory(kmp_dir, tmp_path):
    out = tmp_path / "out"
    out.mkdir()
    result = sdc(kmp_dir, "-f", "html", "-o", out, cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert (out / "check_result.html").is_file()


def test_output_extension_is_not_doubled(kmp_dir, tmp_path):
    result = sdc(kmp_dir, "-o", "report.json", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    assert (tmp_path / "report.json").is_file()
    assert not (tmp_path / "report.json.json").exists()


def test_overwrite_prompt(kmp_dir, tmp_path):
    report = tmp_path / "report.json"
    report.write_text("old")

    result = sdc(kmp_dir, "-o", report, cwd=tmp_path, input="n\n")
    assert result.returncode == 1
    assert "Not overwriting" in result.stderr
    assert report.read_text() == "old"

    result = sdc(kmp_dir, "-o", report, cwd=tmp_path, input="y\n")
    assert result.returncode == 0, result.stderr
    assert len(json.loads(report.read_text())) == len(PACKAGES)


def test_system_json(system, tmp_path):
    result = sdc("system", "-i", '"kmp" match "^sdc-"', "-o", "km", cwd=tmp_path)
    assert result.returncode == 0, result.stderr
    records = json.loads((tmp_path / "km.json").read_text())
    # the weak-updates link belongs to the package of its target
    expected = [system / "updates" / m for m in INSTALLED.values()]
    expected.append(system / "weak-updates" / "sdc_good.ko")
    assert sorted(r["filename"]["value"] for r in records) == sorted(map(str, expected))


@pytest.mark.usefixtures("system")
def test_system_html(tmp_path):
    result = sdc(
        "-f", "html", "-i", '"level.level" = "ERROR"', "-o", "km", cwd=tmp_path
    )
    assert result.returncode == 0, result.stderr
    html = (tmp_path / "km.html").read_text()
    assert "System information: %s (" % socket.gethostname() in html
    assert "sdc_nosupported.ko" in html
    assert "sdc_broken.ko" in html
    assert "sdc_good.ko" not in html
