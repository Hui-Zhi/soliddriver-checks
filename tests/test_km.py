"""Kernel module checks ("system" target) against installed test KMPs."""

import json

import pytest

from conftest import INSTALLED, grades, run

pytestmark = pytest.mark.container

P, W, E = "PASS", "WARNING", "ERROR"

COLUMNS = ("filename", "license", "signature", "supported", "running", "kmp")

# Only sdc-good is a signed RPM with a signed module.
# fmt: off
EXPECTED = {
    # module file, under /lib/modules/<kver>/   file lic sig supp run kmp  row
    "updates/sdc_good.ko":                      (P, P, P, P, P, P, P),
    "updates/sdc_unsigned.ko":                  (P, P, W, P, P, W, W),
    "updates/sdc_proprietary.ko":               (P, W, W, P, P, W, W),
    "updates/sdc_nosupported.ko":               (P, P, W, E, P, W, E),
    "updates/sdc_supported_yes.ko":             (P, P, W, P, P, W, W),
    "updates/sdc_supported_bad.ko":             (P, P, W, E, P, W, E),
    "updates/sdc_supported_multi.ko":           (P, P, W, W, P, W, W),
    "updates/sdc_xz.ko.xz":                     (P, P, W, P, P, W, W),
    "updates/sdc_zst.ko.zst":                   (P, P, W, P, P, W, W),
    "extra/sdc_orphan.ko":                      (P, P, W, P, P, W, W),
    "weak-updates/sdc_good.ko":                 (P, P, P, P, P, P, P),
    "weak-updates/sdc_broken.ko":               (E, W, W, E, P, W, E),
    "weak-updates/sdc_notalink.ko":             (E, P, W, P, P, W, E),
}
# fmt: on


@pytest.mark.parametrize("module", sorted(EXPECTED))
def test_grades(kms, system, module):
    assert grades(kms[str(system / module)], COLUMNS) == EXPECTED[module]


def test_finds_every_module(kms, system):
    files = run(r'find /lib/modules/ -regex ".*\.\(ko\|ko.xz\|ko.zst\)$"').split()
    assert sorted(kms) == sorted(files)
    assert all(str(system / m) in kms for m in EXPECTED)


@pytest.mark.parametrize("package", sorted(INSTALLED))
def test_owner(kms, system, package):
    row = kms[str(system / "updates" / INSTALLED[package])]
    name = run("rpm -q %s" % package).strip()
    if package == "sdc-good-kmp-default":
        assert row["kmp"]["value"] == name
    else:
        assert row["kmp"]["value"] == name + ": has no signature"


def test_weak_updates_link_belongs_to_target_package(kms, system):
    link = kms[str(system / "weak-updates" / "sdc_good.ko")]
    target = kms[str(system / "updates" / "sdc_good.ko")]
    assert link["kmp"]["value"] == target["kmp"]["value"]
    assert link["modulename"]["value"] == "sdc_good"


@pytest.mark.parametrize(
    "module",
    [
        "extra/sdc_orphan.ko",
        "weak-updates/sdc_broken.ko",
        "weak-updates/sdc_notalink.ko",
    ],
)
def test_not_owned(kms, system, module):
    assert kms[str(system / module)]["kmp"]["value"] == "Not owned by any package"


def test_module_info(kms, system):
    good = kms[str(system / "updates" / "sdc_good.ko")]
    assert good["modulename"]["value"] == "sdc_good"
    assert good["license"]["value"] == "GPL"
    assert good["signature"]["value"] == "Yes"
    assert good["supported"]["value"] == "external"

    def value(module, column):
        return kms[str(system / module)][column]["value"]

    assert value("updates/sdc_unsigned.ko", "signature") == "No"
    assert value("updates/sdc_proprietary.ko", "license") == "Proprietary"
    assert value("updates/sdc_nosupported.ko", "supported") == ""
    assert value("updates/sdc_supported_bad.ko", "supported") == "vendor"
    assert value("updates/sdc_supported_multi.ko", "supported") == "yes external"
    assert value("updates/sdc_xz.ko.xz", "modulename") == "sdc_xz"
    assert value("updates/sdc_zst.ko.zst", "modulename") == "sdc_zst"


def test_broken_link_has_no_module_info(kms, system):
    row = kms[str(system / "weak-updates" / "sdc_broken.ko")]
    assert row["modulename"]["value"] == ""
    assert row["license"]["value"] == ""


def test_test_modules_are_not_running(kms, system):
    # they can't be loaded in a container; /proc/modules is the host's
    for module in EXPECTED:
        assert kms[str(system / module)]["running"]["value"] is False


def test_kernel_modules(kms, system):
    kernel = [row for f, row in kms.items() if f.startswith(str(system / "kernel"))]
    assert kernel, "kernel-default must be installed in the test container"
    for row in kernel:
        assert row["kmp"]["value"].startswith("kernel-default-")
        assert row["signature"]["value"] == "Yes"
        assert row["level"]["level"] == P


def test_json(system):
    from soliddriver_checks.api.analysis import kms_to_json

    records = json.loads(kms_to_json())
    files = [r["filename"]["value"] for r in records]
    assert str(system / "updates" / "sdc_good.ko") in files
    assert len(files) == len(set(files))


def test_json_with_filter(system):
    from soliddriver_checks.api.analysis import kms_to_json

    records = json.loads(kms_to_json(filter='"filename" match "/updates/sdc_"'))
    files = sorted(r["filename"]["value"] for r in records)
    assert files == sorted(str(system / "updates" / m) for m in INSTALLED.values())
