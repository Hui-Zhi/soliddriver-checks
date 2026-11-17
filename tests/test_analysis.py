"""Grading rules of KMPAnalysis and KMAnalysis, on hand-made input.

These cover cases the test packages can't produce, such as a module outside
/lib/modules or a KMP without a license.
"""

import pytest

from soliddriver_checks.api.km import KM_COLUMNS, KMAnalysis
from soliddriver_checks.api.kmp import (
    KMP_COLUMNS,
    KMPAnalysis,
    analysis_kmps_to_dataframe,
)

P, W, E = "PASS", "WARNING", "ERROR"


def level(evaluation):
    return evaluation[0]["level"]


@pytest.mark.parametrize(
    "license, parts",
    [
        ("GPL-2.0-only", ["GPL-2.0-only"]),
        ("GPL-2.0-only AND MIT", ["GPL-2.0-only", "MIT"]),
        ("GPL-2.0-only OR BSD-2-Clause", ["GPL-2.0-only", "BSD-2-Clause"]),
        ("GPL-2.0-only WITH Linux-syscall-note", ["GPL-2.0-only"]),
        (
            "(GPL-2.0-only OR MIT) AND BSD-3-Clause",
            ["GPL-2.0-only", "MIT", "BSD-3-Clause"],
        ),
        # old style names with spaces stay whole
        ("GPL v2", ["GPL v2"]),
        ("GPL-2.0 or BSD-2-Clause", ["GPL-2.0 or BSD-2-Clause"]),
        ("", [""]),
    ],
)
def test_split_license_expression(license, parts):
    assert KMPAnalysis._split_license_expression(license) == parts


@pytest.mark.parametrize(
    "licenses, expected",
    [
        (["GPL-2.0-only"], P),
        (["GPL-2.0-only", "GPL-2.0-or-later"], P),
        (["GPL-2.0-only", "MIT"], W),
        (["Proprietary"], W),
        ([""], W),
        ([], W),
    ],
)
def test_kmp_licenses(licenses, expected):
    assert level(KMPAnalysis()._licenses_analysis(licenses)) == expected


@pytest.mark.parametrize(
    "signature, expected",
    [
        ("RSA/SHA256, Mon 01 Jan 2024, Key ID 0123456789abcdef", P),
        ("", W),
        ("(none)", W),
        (None, W),
    ],
)
def test_kmp_signature(signature, expected):
    assert level(KMPAnalysis()._kmp_signature_analysis(signature)) == expected


def test_kmp_vendor():
    assert level(KMPAnalysis()._kmp_vendor_analysis("ACME")) == P
    assert level(KMPAnalysis()._kmp_vendor_analysis("")) == W


@pytest.mark.parametrize(
    "values, expected",
    [(["external"], P), ([], E), (["yes"], E), (["no"], E), (["external", "yes"], E)],
)
def test_kmp_supported_flag(values, expected):
    assert level(KMPAnalysis()._km_supported_analysis(values)) == expected


def test_kmp_weak_modules2():
    anls = KMPAnalysis()
    assert level(anls._kmp_wm2_invoked_analysis(True, "foo-kmp-default")) == P
    assert level(anls._kmp_wm2_invoked_analysis(False, "foo-kmp-default")) == E
    assert (
        level(anls._kmp_wm2_invoked_analysis(False, "foo-kmp-default-debuginfo")) == P
    )


def test_kmp_modalias_wildcards():
    anls = KMPAnalysis()
    km_info = {"/a.ko": {"alias": ["pci:v00008086d00001234sv*sd*bc*sc*i*"]}}
    package = ["pci:v00008086d*sv*sd*bc*sc*i*"]
    assert level(anls._kms_modalias_analysis(package, km_info)) == P
    assert level(anls._kms_modalias_analysis(["*"], km_info)) == E
    assert level(anls._kms_modalias_analysis([], km_info)) == E
    # an alias in the package that no module has
    extra = package + ["pci:v000010DEd*sv*sd*bc*sc*i*"]
    assert (
        "no match in it's kernel module"
        in anls._kms_modalias_analysis(extra, km_info)[1]
    )


def test_empty_kmp_result_has_columns():
    df = analysis_kmps_to_dataframe([])
    assert len(df.index) == 0
    assert list(df.columns) == KMP_COLUMNS


def modinfo(**fields):
    info = {
        "name": "foo",
        "license": "GPL",
        "signature": "AB:CD",
        "supported": "external",
        "running": False,
        "kmp": {"name": "foo-kmp-default-1.0-1.x86_64", "signature": "RSA/SHA256"},
    }
    info.update(fields)
    return info


def analyse(kms):
    return {
        r["filename"]["value"]: r
        for r in KMAnalysis().kms_analysis(kms).to_dict("records")
    }


@pytest.mark.parametrize(
    "filename, weak_updates, expected",
    [
        ("/lib/modules/6.4.0-default/updates/foo.ko", 0, P),
        ("/usr/lib/modules/6.4.0-default/updates/foo.ko", 0, P),
        ("/opt/vendor/foo.ko", 0, W),
        ("/lib/modules-old/foo.ko", 0, W),
        ("/lib/modules/6.4.0-default/weak-updates/foo.ko", 1, P),
        ("/lib/modules/6.4.0-default/weak-updates/foo.ko", 2, E),
        ("/lib/modules/6.4.0-default/weak-updates/foo.ko", 3, E),
    ],
)
def test_km_filename(filename, weak_updates, expected):
    row = analyse({filename: modinfo(**{"weak-updates": weak_updates})})[filename]
    assert row["filename"]["level"]["level"] == expected


@pytest.mark.parametrize(
    "supported, expected",
    [
        ("external", P),
        ("yes", P),
        ("no", P),
        ("", E),
        ("vendor", E),
        ("yes\nexternal", W),
        ("yes\nvendor", E),
    ],
)
def test_km_supported(supported, expected):
    row = analyse({"/lib/modules/k/foo.ko": modinfo(supported=supported)})
    assert row["/lib/modules/k/foo.ko"]["supported"]["level"]["level"] == expected


@pytest.mark.parametrize(
    "license, expected",
    [
        ("GPL", P),
        ("Dual BSD/GPL", P),
        ("GPL\nGPL v2", P),
        ("GPL\nProprietary", W),
        ("", W),
    ],
)
def test_km_license(license, expected):
    row = analyse({"/lib/modules/k/foo.ko": modinfo(license=license)})
    assert row["/lib/modules/k/foo.ko"]["license"]["level"]["level"] == expected


@pytest.mark.parametrize(
    "kmp, expected, value",
    [
        ({"name": "foo-1-1.x86_64", "signature": "RSA"}, P, "foo-1-1.x86_64"),
        (
            {"name": "foo-1-1.x86_64", "signature": ""},
            W,
            "foo-1-1.x86_64: has no signature",
        ),
        (
            {"name": "file /x.ko is not owned by any package", "signature": ""},
            W,
            "Not owned by any package",
        ),
        (None, P, ""),
    ],
)
def test_km_owner(kmp, expected, value):
    row = analyse({"/lib/modules/k/foo.ko": modinfo(kmp=kmp)})["/lib/modules/k/foo.ko"]
    assert row["kmp"]["level"]["level"] == expected
    assert row["kmp"]["value"] == value


def test_km_signature():
    rows = analyse(
        {
            "/lib/modules/k/signed.ko": modinfo(),
            "/lib/modules/k/unsigned.ko": modinfo(signature=""),
        }
    )
    assert rows["/lib/modules/k/signed.ko"]["signature"]["value"] == "Yes"
    assert rows["/lib/modules/k/unsigned.ko"]["signature"]["value"] == "No"
    assert rows["/lib/modules/k/unsigned.ko"]["signature"]["level"]["level"] == W


def test_km_row_level_is_per_module():
    # a bad module must not make the next module's row worse
    rows = analyse(
        {
            "/lib/modules/k/bad.ko": modinfo(supported=""),
            "/lib/modules/k/good.ko": modinfo(),
        }
    )
    assert rows["/lib/modules/k/bad.ko"]["level"]["level"] == E
    assert rows["/lib/modules/k/good.ko"]["level"]["level"] == P


def test_km_row_level_is_the_worst_field():
    rows = analyse({"/lib/modules/k/foo.ko": modinfo(signature="", license="MIT")})
    assert rows["/lib/modules/k/foo.ko"]["level"]["level"] == W


def test_empty_km_result_has_columns():
    df = KMAnalysis().kms_analysis({})
    assert len(df.index) == 0
    assert list(df.columns) == KM_COLUMNS
