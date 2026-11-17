"""KMP checks (directory and single .rpm targets) against the test KMPs."""

import shutil

import pytest

from conftest import PACKAGES, grades, kmp_file

pytestmark = pytest.mark.container

P, W, E = "PASS", "WARNING", "ERROR"

COLUMNS = (
    "vendor",
    "signature",
    "license",
    "wm2_invoked",
    "supported_flag",
    "km_signatures",
    "km_licenses",
    "symbols",
    "modalias",
)

# Only sdc-good is a signed RPM with a signed module, so every other package
# has a WARNING for signature and km_signatures.
# fmt: off
EXPECTED = {
    # package                           vendor sig lic wm2 supp kmsig kmlic sym alias  row
    "sdc-good-kmp-default":             (P, P, P, P, P, P, P, P, P, P),
    "sdc-unsigned-kmp-default":         (P, W, P, P, P, W, P, P, P, W),
    "sdc-novendor-kmp-default":         (W, W, P, P, P, W, P, P, P, W),
    "sdc-proprietary-kmp-default":      (P, W, W, P, P, W, W, P, P, W),
    "sdc-spdx-kmp-default":             (P, W, P, P, P, W, P, P, P, W),
    "sdc-spdx-mit-kmp-default":         (P, W, W, P, P, W, P, P, P, W),
    "sdc-nosupported-kmp-default":      (P, W, P, P, E, W, P, P, P, E),
    "sdc-supported-yes-kmp-default":    (P, W, P, P, E, W, P, P, P, E),
    "sdc-supported-bad-kmp-default":    (P, W, P, P, E, W, P, P, P, E),
    "sdc-supported-multi-kmp-default":  (P, W, P, P, E, W, P, P, P, E),
    "sdc-nowm2-kmp-default":            (P, W, P, E, P, W, P, E, E, E),
    "sdc-badksym-kmp-default":          (P, W, P, E, P, W, P, E, E, E),
    "sdc-allalias-kmp-default":         (P, W, P, E, P, W, P, E, E, E),
    "sdc-xz-kmp-default":               (P, W, P, E, P, W, P, E, E, E),
    "sdc-zst-kmp-default":              (P, W, P, E, P, W, P, E, E, E),
    "sdc-nomodule-kmp-default":         (P, W, P, E, P, P, P, P, P, E),
    "sdc-debug-kmp-default-debuginfo":  (P, W, P, P, P, W, P, E, E, E),
}
# fmt: on


def test_finds_every_kmp(kmps):
    assert sorted(kmps) == sorted(PACKAGES)


@pytest.mark.parametrize("package", sorted(EXPECTED))
def test_grades(kmps, package):
    assert grades(kmps[package], COLUMNS) == EXPECTED[package]


def test_good_kmp(kmps):
    row = kmps["sdc-good-kmp-default"]
    assert row["vendor"]["value"] == "SDC Test Vendor"
    assert "Key ID" in row["signature"]["value"]
    assert row["license"]["value"] == "GPL-2.0-only"
    assert row["wm2_invoked"]["value"] is True
    assert row["km_signatures"]["value"] == "Exist"
    assert row["km_licenses"]["value"] == "GPL"
    assert row["symbols"]["value"] == "All passed"
    assert row["modalias"]["value"] == "All passed"
    assert row["path"]["value"].endswith(".rpm")


def test_unsigned(kmps):
    row = kmps["sdc-unsigned-kmp-default"]
    assert row["signature"]["value"] == "Signature should not be empty"
    assert row["km_signatures"]["value"] == "No signature found"


def test_no_vendor(kmps):
    assert kmps["sdc-novendor-kmp-default"]["vendor"]["value"] == (
        "Vendor should not be empty"
    )


def test_licenses(kmps):
    row = kmps["sdc-proprietary-kmp-default"]
    assert row["license"]["value"].endswith(": Proprietary")
    assert row["km_licenses"]["value"].endswith(": Proprietary")
    # SPDX expressions are checked license by license, WITH exceptions dropped
    assert kmps["sdc-spdx-kmp-default"]["license"]["value"] == (
        "GPL-2.0-only GPL-2.0-or-later"
    )
    assert kmps["sdc-spdx-mit-kmp-default"]["license"]["value"].endswith(": MIT")


@pytest.mark.parametrize(
    "package, message",
    [
        (
            "sdc-nosupported-kmp-default",
            "sdc_nosupported.ko: No 'supported' flag found",
        ),
        (
            "sdc-supported-yes-kmp-default",
            'sdc_supported_yes.ko: \'supported\' flag is "yes", it should be "external"',
        ),
        (
            "sdc-supported-bad-kmp-default",
            'sdc_supported_bad.ko: \'supported\' flag is "vendor", it should be "external"',
        ),
        (
            "sdc-supported-multi-kmp-default",
            "sdc_supported_multi.ko: Multiple values found, they're yes external",
        ),
    ],
)
def test_supported_flag(kmps, package, message):
    assert kmps[package]["supported_flag"]["value"] == message


def test_weak_modules2_not_invoked(kmps):
    assert kmps["sdc-nowm2-kmp-default"]["wm2_invoked"]["value"] is False


def test_debuginfo_skips_weak_modules2_check(kmps):
    row = kmps["sdc-debug-kmp-default-debuginfo"]
    assert row["wm2_invoked"]["value"] is False
    assert row["wm2_invoked"]["level"]["level"] == P


def test_symbols(kmps):
    # the module uses _printk and module_layout
    assert kmps["sdc-nowm2-kmp-default"]["symbols"]["value"] == (
        "Number of symbols can not be found in KMP: 2"
    )
    # the package requires _printk with a wrong checksum
    assert kmps["sdc-badksym-kmp-default"]["symbols"]["value"] == (
        "Number of symbols can not be found in KMP: 1 "
        "Number of symbols checksum does not match: 1"
    )


def test_modalias(kmps):
    assert kmps["sdc-allalias-kmp-default"]["modalias"]["value"] == (
        "KMP can match all the devices! Highly not recommended!"
    )
    assert kmps["sdc-nowm2-kmp-default"]["modalias"]["value"].startswith(
        "Alias found in kernel module but no match in it's package: "
        "pci:v00001AF4d000010FFsv*sd*bc*sc*i*"
    )


@pytest.mark.parametrize("package", ["sdc-xz-kmp-default", "sdc-zst-kmp-default"])
def test_compressed_modules(kmps, package):
    row = kmps[package]
    assert row["km_licenses"]["value"] == "GPL"
    assert row["supported_flag"]["level"]["level"] == P
    assert row["km_signatures"]["value"] == "No signature found"


def test_no_module(kmps):
    row = kmps["sdc-nomodule-kmp-default"]
    for column in ("supported_flag", "km_signatures", "km_licenses", "symbols"):
        assert row[column]["value"] == ""


def test_single_kmp_matches_directory_check(kmp_dir, kmps):
    from soliddriver_checks.api.analysis import kmp_analysis

    df = kmp_analysis(str(kmp_file(kmp_dir, "sdc-good-kmp-default")))
    assert len(df.index) == 1
    row = df.to_dict("records")[0]
    assert {c: row[c] for c in COLUMNS} == {
        c: kmps["sdc-good-kmp-default"][c] for c in COLUMNS
    }


def test_path_with_spaces(kmp_dir, tmp_path):
    from soliddriver_checks.api.analysis import kmps_to_dataframe

    target = tmp_path / "dir with space" / "sub dir"
    target.mkdir(parents=True)
    shutil.copy(
        kmp_file(kmp_dir, "sdc-good-kmp-default"),
        target / "sdc good-kmp-default copy.rpm",
    )
    rows = kmps_to_dataframe(tmp_path / "dir with space").to_dict("records")
    assert len(rows) == 1
    assert rows[0]["path"]["value"] == str(target / "sdc good-kmp-default copy.rpm")
    assert rows[0]["level"]["level"] == P


def test_only_kmp_files_are_checked(kmp_dir, tmp_path):
    from soliddriver_checks.api.analysis import kmps_to_dataframe

    shutil.copy(kmp_file(kmp_dir, "sdc-good-kmp-default"), tmp_path / "sdc-good.rpm")
    (tmp_path / "notes-kmp-default.txt").write_text("not a package")
    assert len(kmps_to_dataframe(tmp_path).index) == 0


def test_empty_directory(tmp_path):
    from soliddriver_checks.api.analysis import kmps_to_dataframe
    from soliddriver_checks.api.kmp import KMP_COLUMNS

    df = kmps_to_dataframe(tmp_path)
    assert len(df.index) == 0
    assert list(df.columns) == KMP_COLUMNS
