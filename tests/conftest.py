"""Fixtures for the soliddriver-checks tests.

The tests that build packages, install them or scan the system are marked
"container". They only run where SDC_TEST_CONTAINER=1, which the test image
sets (tests/container_env/Dockerfile): they install packages and write to
/lib/modules, which must not happen on a real system. Run the suite with
tests/run_tests.sh.
"""

import os
import shutil
import subprocess
import sys
from pathlib import Path

import pytest

REPO = Path(__file__).resolve().parents[1]
DATA = REPO / "tests" / "data"

# test the source tree, not an installed copy
sys.path.insert(0, str(REPO / "src"))

IN_CONTAINER = os.environ.get("SDC_TEST_CONTAINER") == "1"

# packages tests/data/build.sh builds
PACKAGES = [
    "sdc-good-kmp-default",
    "sdc-unsigned-kmp-default",
    "sdc-novendor-kmp-default",
    "sdc-proprietary-kmp-default",
    "sdc-spdx-kmp-default",
    "sdc-spdx-mit-kmp-default",
    "sdc-nosupported-kmp-default",
    "sdc-supported-yes-kmp-default",
    "sdc-supported-bad-kmp-default",
    "sdc-supported-multi-kmp-default",
    "sdc-nowm2-kmp-default",
    "sdc-badksym-kmp-default",
    "sdc-allalias-kmp-default",
    "sdc-xz-kmp-default",
    "sdc-zst-kmp-default",
    "sdc-nomodule-kmp-default",
    "sdc-debug-kmp-default-debuginfo",
]

# packages the "system" fixture installs, and the modules they contain
INSTALLED = {
    "sdc-good-kmp-default": "sdc_good.ko",
    "sdc-unsigned-kmp-default": "sdc_unsigned.ko",
    "sdc-proprietary-kmp-default": "sdc_proprietary.ko",
    "sdc-nosupported-kmp-default": "sdc_nosupported.ko",
    "sdc-supported-yes-kmp-default": "sdc_supported_yes.ko",
    "sdc-supported-bad-kmp-default": "sdc_supported_bad.ko",
    "sdc-supported-multi-kmp-default": "sdc_supported_multi.ko",
    "sdc-xz-kmp-default": "sdc_xz.ko.xz",
    "sdc-zst-kmp-default": "sdc_zst.ko.zst",
}


def pytest_configure(config):
    config.addinivalue_line(
        "markers", "container: needs the test container (tests/run_tests.sh)"
    )


def pytest_collection_modifyitems(config, items):
    if IN_CONTAINER:
        return

    skip = pytest.mark.skip(reason="needs the test container, run tests/run_tests.sh")
    for item in items:
        if "container" in item.keywords:
            item.add_marker(skip)


def run(cmd):
    return subprocess.run(
        cmd, shell=True, check=True, capture_output=True, text=True
    ).stdout


def rows_by(df, column):
    """The rows of a check result as plain dicts, keyed by a column's value."""
    return {row[column]["value"]: row for row in df.to_dict("records")}


def grades(row, columns):
    return tuple(row[c]["level"]["level"] for c in columns) + (row["level"]["level"],)


@pytest.fixture(scope="session")
def kmp_dir(tmp_path_factory):
    """Directory with the test KMPs, built from tests/data."""
    out = tmp_path_factory.mktemp("kmps")
    subprocess.run(["bash", str(DATA / "build.sh"), str(out)], check=True)
    return out


def kmp_file(kmp_dir, package):
    (path,) = kmp_dir.glob(package + "-1.0*.rpm")
    return path


@pytest.fixture(scope="session")
def kmps(kmp_dir):
    """Directory check result, keyed by package name."""
    from soliddriver_checks.api.analysis import kmps_to_dataframe

    return rows_by(kmps_to_dataframe(kmp_dir), "name")


@pytest.fixture(scope="session")
def system(kmp_dir):
    """Install test KMPs and broken modules, and remove them afterwards.

    Yields the modules directory of the installed kernel. Besides the modules
    from INSTALLED, it adds:
      extra/sdc_orphan.ko             a module no package owns
      weak-updates/sdc_good.ko        a link to updates/sdc_good.ko
      weak-updates/sdc_broken.ko      a link to a missing module
      weak-updates/sdc_notalink.ko    a file where a link is expected
    """
    (kver,) = os.listdir("/lib/modules")
    moddir = Path("/lib/modules") / kver
    files = " ".join(str(kmp_file(kmp_dir, pkg)) for pkg in INSTALLED)
    # no scriptlets: weak-modules2 would regenerate the initrd. --replace*
    # recovers from an earlier run that was interrupted before the cleanup.
    run("rpm -U --replacepkgs --replacefiles --nodeps --noscripts %s" % files)

    (moddir / "extra").mkdir(exist_ok=True)
    (moddir / "weak-updates").mkdir(exist_ok=True)
    added = [
        moddir / "extra" / "sdc_orphan.ko",
        moddir / "weak-updates" / "sdc_good.ko",
        moddir / "weak-updates" / "sdc_broken.ko",
        moddir / "weak-updates" / "sdc_notalink.ko",
    ]
    for path in added:
        if path.is_symlink() or path.exists():
            path.unlink()
    shutil.copy(moddir / "updates" / "sdc_unsigned.ko", added[0])
    added[1].symlink_to("../updates/sdc_good.ko")
    added[2].symlink_to("../updates/does-not-exist.ko")
    shutil.copy(moddir / "updates" / "sdc_unsigned.ko", added[3])

    yield moddir

    for path in added:
        path.unlink()
    run("rpm -e --nodeps --noscripts %s" % " ".join(INSTALLED))


@pytest.fixture(scope="session")
def kms(system):
    """System check result, keyed by module file path."""
    from soliddriver_checks.api.analysis import kms_to_dataframe

    return rows_by(kms_to_dataframe(), "filename")
