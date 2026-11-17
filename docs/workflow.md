# Development workflow

How to set up a development environment, test a change against real packages, add a check, and publish a release. For how the code is organised, see [architecture.md](architecture.md).

## Repository and branches

- The upstream repository is [SUSE/soliddriver-checks](https://github.com/SUSE/soliddriver-checks). Its `main` branch is what gets released.
- Changes are made in a fork and sent to upstream as pull requests. Small changes come from the fork's `main`, bigger ones from a feature branch (for example `feature-filter`).
- Keep the fork in sync with upstream before starting new work:

  ```sh
  git remote add upstream git@github.com:SUSE/soliddriver-checks.git   # once
  git fetch upstream
  git merge upstream/main
  ```

There is no CI. Run the test suite before every pull request, and verify the change by hand as described below.

## Development environment

The checks run Linux tools (`rpm`, `rpm2cpio`, `cpio`, `modinfo`, `modprobe`), so they only work on SUSE Linux Enterprise or openSUSE.

### On SUSE Linux or openSUSE

```sh
pip install -e .
soliddriver-checks --help
```

### On macOS (or any other OS): the development container

`tests/container_env/` builds an openSUSE Leap 16.1 image with Python 3.13, the required tools, a kernel (`kernel-default`), the tools to build KMPs, and pytest:

```sh
cd tests/container_env
./build_env.sh                # builds the image opensuse-leap-soliddriver-checks
```

Start a container with the repository mounted at `/root/source_codes`. It can be mounted read-only:

```sh
docker run -it --rm \
  --mount type=bind,source="$PWD",target=/root/source_codes,readonly \
  opensuse-leap-soliddriver-checks /bin/bash
```

`create_container_mac.sh` is an example with more mounts (KMP and output directories). Adjust its paths to your machine.

Inside the container:

```sh
./build_install.sh            # installs the package and its dependencies from a copy of the source
soliddriver-checks --help
```

`build_install.sh` installs from a copy so it doesn't leave `build/` or `*.egg-info` in your checkout. Only `dist/` is in `.gitignore`.

After the first install, you can run the source tree directly without reinstalling after every edit:

```sh
cd /tmp
PYTHONPATH=/root/source_codes/src python3.13 -m soliddriver_checks.cli.cli /path/to/kmps -f html -o report
```

## Running the tests

```sh
tests/run_tests.sh                 # the whole suite, about a minute once the image is built
tests/run_tests.sh -k filter -v    # arguments are passed to pytest
```

The script builds the image, mounts the repository read-only, and runs pytest in a throw-away container. The tests test the source tree (`src/`), not the installed copy.

| File | What it tests |
| --- | --- |
| `tests/test_kmp.py` | KMP checks against the test KMPs: the grade of every column for every package, the messages, paths with spaces, empty directories |
| `tests/test_km.py` | Kernel module checks: installs test KMPs and broken modules, then checks the grade of every column for every module |
| `tests/test_cli.py` | The command: targets, `--format`, `--output`, the overwrite prompt, `--filter`, errors and exit codes |
| `tests/test_filter.py` | The filter language, on hand-made rows |
| `tests/test_analysis.py` | The grading rules, on hand-made input, including cases no package can produce (a module outside `/lib/modules`, a KMP without a license) |

Tests that build packages, install them or scan the system are marked `container`. They only run where `SDC_TEST_CONTAINER=1`, which the image sets, because they write to `/lib/modules` and the RPM database. Elsewhere they are skipped.

### Test packages

`tests/data/build.sh OUTDIR` builds the test KMPs from source. The tests run it once per session.

- `tests/data/module/` is one kernel module source. Its license, `supported` flags and PCI ID are set on the `make` command line (see `Kbuild`).
- `tests/data/specs/sdc-kmp.spec` builds a KMP the way SUSE requires, with the `kernel_module_package` macro.
- `tests/data/specs/sdc-manual.spec` packages a module by hand, without scriptlets, `ksym()` requirements or `modalias()` supplements.

`build.sh` builds both specs several times with different `--define` options, so each package (`sdc-<scenario>-kmp-default`) differs from `sdc-good` in one property. Only `sdc-good` is a signed RPM with a signed module; `build.sh` creates throw-away keys for both.

To add a scenario, add a `build` line to `build.sh` (and a `--define` option to a spec if needed), add the package to `PACKAGES` in `tests/conftest.py`, and add its expected grades to `EXPECTED` in `tests/test_kmp.py`. To install it for the kernel module tests, also add it to `INSTALLED` and to `EXPECTED` in `tests/test_km.py`.

## Manual test data

For checks by hand, build the test packages in the container:

```sh
/root/source_codes/tests/data/build.sh /kmps
soliddriver-checks /kmps -f html -o /tmp/kmps
```

Real KMPs from the openSUSE repositories are also useful, because they come from a real build service:

```sh
zypper se -t package -- -kmp-default                 # list available KMPs
zypper --non-interactive download <package>...
mkdir -p /kmps-real && find /var/cache/zypp/packages -name '*-kmp-*.rpm' -exec cp {} /kmps-real/ \;
```

For the `system` target, the image already has `kernel-default`. Install test KMPs without their scriptlets, which would regenerate the initrd, and add broken modules:

```sh
rpm -i --nodeps --noscripts /kmps/sdc-good-kmp-*.rpm /kmps/sdc-unsigned-kmp-*.rpm

KV=$(ls /lib/modules | sort | tail -1)
mkdir -p /lib/modules/$KV/extra /lib/modules/$KV/weak-updates
# a module not owned by any package
cp /lib/modules/$KV/updates/sdc_unsigned.ko /lib/modules/$KV/extra/orphan.ko
# a broken weak-updates link, and a regular file where a link is expected
ln -s /lib/modules/$KV/extra/does-not-exist.ko /lib/modules/$KV/weak-updates/broken.ko
cp /lib/modules/$KV/updates/sdc_unsigned.ko /lib/modules/$KV/weak-updates/notalink.ko
```

In a container, `/proc/modules` belongs to the host kernel (on macOS, Docker's VM). So the `running` column means nothing there, and filters on `"running" = "True"` match nothing.

## Verifying a change

1. **Tests**: `tests/run_tests.sh` must pass. Add or change tests for the behaviour you changed.

2. **Syntax**: nothing must warn when compiled (Python turns some warnings into errors in later versions):

   ```sh
   for f in $(git ls-files 'src/*.py'); do python3 -W error::SyntaxWarning -m py_compile "$f"; done
   ```

3. **Every target you touched, in every format.**
   - Directory: `-f html` and `-f json`.
   - `system`: `-f html` and `-f json`.
   - Single `.rpm`: terminal output.

   Include the empty directory, and at least one `--filter`.

4. **Compare with the code before your change.** Check out `HEAD` next to your working tree and run both on the same data:

   ```sh
   git worktree add /tmp/sdc-head HEAD
   docker run -it --rm \
     --mount type=bind,source="$PWD",target=/root/source_codes,readonly \
     --mount type=bind,source=/tmp/sdc-head,target=/head,readonly \
     opensuse-leap-soliddriver-checks /bin/bash
   ```

   Inside the container, after `./build_install.sh` and preparing the test data:

   ```sh
   cd /tmp
   PYTHONPATH=/head/src              python3.13 -m soliddriver_checks.cli.cli /kmps -f json -o before.json
   PYTHONPATH=/root/source_codes/src python3.13 -m soliddriver_checks.cli.cli /kmps -f json -o after.json
   ```

   If the old code fails with `ModuleNotFoundError`, it needs packages the current version dropped. Install them in the container with `python3.13 -m pip install <package>`. For example, versions up to 3.0.9 need `openpyxl rich requests bottle`.

   Remove the worktree afterwards with `git worktree remove /tmp/sdc-head`.

   Then diff the grades per row. The JSON report is easy to load with `json.load()`. Every difference should be one you intended.

5. **Open the HTML reports** in a browser if you touched a reporter or a template.

6. **Run the README examples** if you changed options, filter behaviour or output.

Things to know when scripting runs:

- If the output file already exists, the CLI asks before overwriting it. In a non-interactive run there's no answer, so the run stops with `Not overwriting ...`. Use fresh output names, or delete old reports first.
- Progress and log messages go to stderr, and the single-KMP table goes to stdout.
- Invalid targets and filters exit with code 2 before anything is scanned.

## Adding or changing a check

A check runs through every layer, so a new column touches several files. Use an existing column of the same subject as a template, and grep for its name.

| Step | KMP check | Kernel module check |
| --- | --- | --- |
| Collect the raw value | `KMPReader` in `api/kmp.py` (`collect_kmp_data`, `_get_km_all_info`) | `KMReader.get_all_modinfo` in `api/km.py` |
| Grade it, and add it to the row level | `KMPAnalysis.kmp_analysis` (module checks: `_kmp_km_analysis`) | `KMAnalysis.kms_analysis` |
| Add the column | `KMP_COLUMNS` and the row in `analysis_kmps_to_dataframe` | `KM_COLUMNS` and the row in `kms_analysis` |
| HTML report | `KMPReporter._detail_to_html` (header and cell), `_summary` / `_summary_to_html` if it counts per vendor | `KMReporter._format_columns` and `_row_style_in_html` (one entry per column, in column order) |
| JSON report | automatic | automatic |
| Filter | automatic (the key is the column name) | automatic |
| User docs | README: the check table, the key list under [Filtering results](../README.md#filtering-results---filter) | same |
| Tests | A scenario in `tests/data/build.sh`, the column in `COLUMNS` and `EXPECTED` in `tests/test_kmp.py`, the grading rules in `tests/test_analysis.py` | same, in `tests/test_km.py` |

Rules that apply to every change:

- Wrap every path in a shell command in `shlex.quote()`.
- Accept `.ko`, `.ko.xz` and `.ko.zst`. The extension pattern appears in `api/km.py`, `api/kmp.py` and `utils/scripts/check-links.sh`, and must stay in sync.
- Key results by file path or package name. Don't match the output of two commands line by line.
- Put lists that users may want to change (licenses, keys, colors) in `config/soliddriver-checks.conf`, not in code.
- Keep presentation in `cli/` and system access in `api/`.

## Documentation

| File | Audience | Update when |
| --- | --- | --- |
| `README.md` | Users | Options, targets, checks, filter keys or output change |
| `docs/architecture.md` | Maintainers | Components, data flow, data model or design decisions change |
| `docs/workflow.md` | Maintainers | The development, test or release process changes |
| `AGENTS.md` | AI coding agents | Layout, commands or conventions change |

The usage block in the README is a copy of `soliddriver-checks --help`. Regenerate it with `COLUMNS=80` when option help changes.

## Releasing

Releases are published by hand.

1. **Bump the version** in `src/soliddriver_checks/version.py` (the only place it's defined), in its own commit:

   ```sh
   git commit -m "increase version to 3.1.0" src/soliddriver_checks/version.py
   ```

   Bump the minor version when results change for existing users (new checks, different grades), and the patch version for fixes that only stop crashes.

2. **Open a pull request** to `SUSE/soliddriver-checks` and merge it.

3. **Build** from the merged `main`, in a clean checkout:

   ```sh
   python3 -m pip install --upgrade build twine
   rm -rf dist build src/*.egg-info
   python3 -m build                 # creates dist/*.tar.gz and dist/*.whl
   python3 -m twine check dist/*
   ```

   Install the wheel in the development container and run a directory and a `system` check before publishing. This catches files missing from the package (config, templates, `check-links.sh`; see `MANIFEST.in`).

4. **Publish to PyPI**:

   ```sh
   python3 -m twine upload dist/*
   ```

5. **Update the openSUSE Build Service package** [home:huizhizhao:soliddriver-checks](https://build.opensuse.org/package/show/home:huizhizhao:soliddriver-checks/soliddriver-checks) to the new version, so the RPMs for zypper follow.
