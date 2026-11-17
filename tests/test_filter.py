"""The --filter expression language (api/filter.py), on hand-made rows."""

import pandas as pd
import pytest

from soliddriver_checks.api.filter import check_filter, km_filter
from soliddriver_checks.api.km import KM_COLUMNS
from soliddriver_checks.api.kmp import KMP_COLUMNS

LEVELS = {"PASS": 1, "WARNING": 2, "ERROR": 3}


def cell(value, level="PASS"):
    return {"value": value, "level": {"level": level, "value": LEVELS[level]}}


def km(
    name,
    license="GPL",
    signature="Yes",
    supported="external",
    running=False,
    kmp="kernel-default",
    level="PASS",
    **levels
):
    """A kernel module row. Set a field's grade with <column>_level="..."."""
    values = {
        "modulename": name,
        "filename": "/lib/modules/6.4.0-default/updates/%s.ko" % name,
        "license": license,
        "signature": signature,
        "supported": supported,
        "running": running,
        "kmp": kmp,
    }
    row = {c: cell(v, levels.get(c + "_level", "PASS")) for c, v in values.items()}
    row["level"] = {"level": level, "value": LEVELS[level]}
    return row


ROWS = pd.DataFrame(
    [
        km("e1000", running=True),
        km("igb", signature="No", level="WARNING", signature_level="WARNING"),
        km(
            "nvidia",
            license="NVIDIA",
            running=True,
            kmp="Not owned by any package",
            level="WARNING",
            license_level="WARNING",
            kmp_level="WARNING",
        ),
        km("Nv_Bridge", supported="", level="ERROR", supported_level="ERROR"),
    ],
    columns=KM_COLUMNS,
)


def matches(expression):
    return sorted(
        r["modulename"]["value"] for r in km_filter(expression, ROWS).to_dict("records")
    )


def test_rows_have_expected_grades():
    assert ROWS.at[1, "signature"]["level"]["level"] == "WARNING"
    assert ROWS.at[3, "level"]["level"] == "ERROR"


@pytest.mark.parametrize(
    "expression, expected",
    [
        ('"modulename" = "igb"', ["igb"]),
        ('"modulename" != "igb"', ["Nv_Bridge", "e1000", "nvidia"]),
        # comparisons are exact and case-sensitive
        ('"modulename" = "IGB"', []),
        ('"modulename" = "ig"', []),
        # booleans compare as "True" / "False"
        ('"running" = "True"', ["e1000", "nvidia"]),
        ('"running" = "False"', ["Nv_Bridge", "igb"]),
        # match is re.search: anywhere in the value, unless anchored
        ('"modulename" match "v"', ["Nv_Bridge", "nvidia"]),
        ('"modulename" match "^nv"', ["nvidia"]),
        ('"modulename" match "(?i)^nv"', ["Nv_Bridge", "nvidia"]),
        # backslashes reach the regular expression as written
        ('"filename" match "/updates/e1000\\.ko$"', ["e1000"]),
        # no: the value is empty
        ('no "supported"', ["Nv_Bridge"]),
        # key.level is a field's grade, level.level the row's grade
        ('"signature.level" = "WARNING"', ["igb"]),
        ('"license.level" != "PASS"', ["nvidia"]),
        ('"level.level" = "PASS"', ["e1000"]),
        ('"level.level" != "PASS"', ["Nv_Bridge", "igb", "nvidia"]),
        # and / or / parentheses
        ('"running" = "True" and "signature" = "Yes"', ["e1000", "nvidia"]),
        ('"modulename" = "igb" or "modulename" = "e1000"', ["e1000", "igb"]),
        # and binds more tightly than or
        (
            '"modulename" = "igb" or "running" = "True" and "license" = "NVIDIA"',
            ["igb", "nvidia"],
        ),
        (
            '("modulename" = "igb" or "running" = "True") and "license" = "GPL"',
            ["e1000", "igb"],
        ),
        (
            '("modulename" = "igb" or "modulename" = "e1000") and ("running" = "True")',
            ["e1000"],
        ),
        (
            '"level.level" = "ERROR" or "level.level" = "WARNING" and no "supported"',
            ["Nv_Bridge"],
        ),
        # extra white space is ignored
        ('  "modulename"="igb"  ', ["igb"]),
    ],
)
def test_expressions(expression, expected):
    assert matches(expression) == expected


def test_empty_filter_keeps_every_row():
    assert km_filter("", ROWS) is ROWS


def test_filter_on_empty_result_keeps_columns():
    empty = pd.DataFrame(columns=KM_COLUMNS)
    assert list(km_filter('"modulename" = "x"', empty).columns) == KM_COLUMNS


def test_result_index_is_reset():
    assert list(km_filter('"modulename" = "nvidia"', ROWS).index) == [0]


@pytest.mark.parametrize(
    "expression, message",
    [
        ('"modulename" == "igb"', "Invalid filter"),
        ("modulename = igb", "Invalid filter"),
        ('"modulename" = "igb" and', "Invalid filter"),
        ("“modulename” = “igb”", "Invalid filter"),
        (
            '"vendor" = "x"',
            'Unknown filter key: "vendor". Valid keys: modulename, '
            "filename, license, signature, supported, running, kmp",
        ),
        ('"vendor.level" = "PASS"', 'Unknown filter key: "vendor.level"'),
        ('"modulename" match "["', "Invalid regular expression in filter"),
    ],
)
def test_invalid_filters(expression, message):
    with pytest.raises(ValueError) as error:
        check_filter(expression, KM_COLUMNS)
    assert message in str(error.value)


def test_check_filter_uses_the_target_columns():
    check_filter('"vendor" = "x" and "symbols.level" = "ERROR"', KMP_COLUMNS)
    with pytest.raises(ValueError):
        check_filter('"vendor" = "x"', KM_COLUMNS)
    check_filter("", KM_COLUMNS)
