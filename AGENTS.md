# AGENTS.md

Guidance for AI coding agents working on `soliddriver-checks`.

## What this project is

A Python CLI that checks whether **KMPs** (Kernel Module Packages, `*-kmp-*.rpm`) and **KMs** (installed/running kernel modules) are built according to SUSE's requirements. It looks at packaging metadata only, not at module source code. Output is a report in `html` or `json`. Each field is graded `PASS` / `WARNING` / `ERROR`.

User-facing docs, including the filter syntax, are in `README.md`. Update it whenever CLI options, filter keys or report columns change.

## Layout

```
src/soliddriver_checks/
  version.py            # __VERSION__ — the only version source (setup.py parses it)
  config.py             # SDCConf: loads config/soliddriver-checks.conf (JSON)
  config/
    soliddriver-checks.conf   # valid licenses, known signing keys, html styles
    templates/                # *.html.jinja report templates
  api/                  # data collection + evaluation (no presentation)
    kmp.py              # KMPReader (rpm queries, rpm2cpio extraction) + KMPAnalysis
    km.py               # KMReader (modinfo over /proc/modules and /lib/modules) + KMAnalysis
    analysis.py         # public entry points: kmps_to_dataframe, kmp_analysis, kms_to_dataframe, kms_to_json
    filter.py           # lark grammar (EBNF); the Transformer evaluates it to a row mask (-i/--filter)
    raw_data.py         # legacy helpers, currently unused
    utils/cmd.py        # run_cmd / async_run_cmd: shell=True subprocess wrappers
    utils/scripts/check-links.sh  # checks weak-updates symlinks, prints JSON
  cli/
    cli.py              # click entry point `soliddriver-checks` (soliddriver_checks.cli.cli:run)
    kmp_report.py       # KMPReporter: to_html / to_json
    km_report.py        # KMReporter:  to_html / to_json
    terminal_logs.py    # per-KMP progress lines and the single-KMP table (click.style colors)
tests/
  run_tests.sh          # builds the container image and runs pytest in it
  conftest.py           # fixtures: build the test KMPs, install them, scan the system
  test_*.py             # kmp / km / cli (in the container), filter / analysis (unit)
  data/                 # module source, spec files and build.sh for the test KMPs
  container_env/        # Dockerfile of the development and test image
```

Data flow: a reader gathers raw data from shell commands, the analysis class turns each field into a `(value, level)` evaluation, the results go into a pandas DataFrame, an optional filter is applied, and a reporter writes the output file.

CLI target dispatch is in `Check_Target` (`cli/cli.py`):
- a single `.rpm` file prints a terminal summary only, with no report file
- a directory checks every `*-kmp-*.rpm` found under it
- `system` (the default) checks the kernel modules on the local host

## Runtime requirements

The tool runs external Linux tools through `run_cmd` (`shell=True`): `rpm`, `rpm2cpio`, `cpio`, `find`, `bash`, `/usr/sbin/modinfo`, `/usr/sbin/modprobe`, and it reads `/proc/modules` and `/lib/modules`. **These checks can't run on macOS.** Use the openSUSE container under `tests/container_env/`:

```sh
cd tests/container_env && ./build_env.sh            # builds opensuse-leap-soliddriver-checks image
# then run the container, bind-mounting the repo at /root/source_codes
# (see create_container_mac.sh for an example) and inside it:
./build_install.sh                                   # pip-installs a copy of the source (Python 3.13)
soliddriver-checks /root/rpms -f html -o /root/output_dir/
```

The image is openSUSE Leap 16.1 (usr-merged: `/lib` is a link to `usr/lib`) with `kernel-default` and the tools to build KMPs. `docs/workflow.md` explains the tests, manual test data, comparing against `HEAD`, and releasing. `docs/architecture.md` describes the components, the data model and the check flows.

## Development

```sh
pip install -e .            # Python >= 3.7
python -m build             # sdist + wheel
```

- **Run `tests/run_tests.sh`** (pytest in the container) after every change; there is no CI. Never run the `container` tests on a real system: they install packages and write to `/lib/modules`, so they are skipped unless `SDC_TEST_CONTAINER=1`.
- Test KMPs are built from source by `tests/data/build.sh`: every `sdc-<scenario>` package differs from `sdc-good` in one property. A new check or scenario needs a `build` line there and its expected grades in the `EXPECTED` tables of `tests/test_kmp.py` / `tests/test_km.py`. Grading rules that no package can trigger go in `tests/test_analysis.py`.
- Also verify by hand when output changes: run the CLI and check both output formats if you touched a reporter. Follow the checklist in `docs/workflow.md`.
- No linter or formatter is configured. The code is roughly Black-formatted (double quotes, 88 cols), so match it.
- Non-Python files that ship in the package must be covered by `MANIFEST.in` (currently `config/` and `api/utils/scripts/`). Load them relative to the package directory, as `config.py` does.

## Conventions and gotchas

- To add a new check, you usually need to change several layers together: the reader (collect the field), the analysis class (grade it with `KMPEvaluation`/`KMEvaluation`), the DataFrame columns, every reporter (HTML template/columns, JSON), and the filter keys listed in `README.md`.
- Filter keys are the DataFrame/JSON column names (`KM_COLUMNS` in `api/km.py`, `KMP_COLUMNS` in `api/kmp.py`); the CLI validates a filter against them before scanning. `key.level` filters on a field's grade, and `level.level` filters on the row's overall grade. The grammar is in the `grammar` string at the top of `api/filter.py`.
- Shell commands are built with string interpolation and run with `shell=True`. Wrap every path in `shlex.quote()`, since KMP paths come from user input and may contain spaces.
- `KMReader._split_cmd_args` runs a command over module files in batches of 300 to stay under the argument length limit. Use it for commands that take many module files.
- Kernel modules can be `.ko`, `.ko.xz` or `.ko.zst` (SLE 15 SP6 ships `.ko.zst`). The extension pattern appears in `api/km.py` (find, rpm owner query), `api/kmp.py` (`_get_km_all_info`) and `utils/scripts/check-links.sh`. Keep them in sync.
- Don't match the output of separate commands by position (e.g. `modinfo` and `rpm -qf` over the same file list). Broken links and errors drop lines; key results by file path or package name instead.
- Signing keys that the tool recognizes and the list of valid licenses live in `config/soliddriver-checks.conf`, not in code.
- For a release, bump `__VERSION__` in `src/soliddriver_checks/version.py` in its own commit (e.g. "increase version to 3.0.10"). Packages are published to PyPI and to OBS (`home:huizhizhao:soliddriver-checks`).
- License: GPLv2.
