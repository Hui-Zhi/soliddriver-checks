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

There is no CI. Every pull request is verified by hand, as described below.

## Development environment

The checks run Linux tools (`rpm`, `rpm2cpio`, `cpio`, `modinfo`, `modprobe`), so they only work on SUSE Linux Enterprise or openSUSE.

### On SUSE Linux or openSUSE

```sh
pip install -e .
soliddriver-checks --help
```

### On macOS (or any other OS): the development container

`tests/container_env/` builds an openSUSE Leap 15.6 image with Python 3.11 and the required tools:

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
PYTHONPATH=/root/source_codes/src python3.11 -m soliddriver_checks.cli.cli /path/to/kmps -f html -o report
```

## Test data

The development image has no kernel modules and no KMPs. Add what the change needs.

**Real KMPs** from the openSUSE repositories:

```sh
zypper se -t package -- -kmp-default                 # list available KMPs
zypper --non-interactive download vhba-kmp-default v4l2loopback-kmp-default xtables-addons-kmp-default
mkdir -p /kmps && find /var/cache/zypp/packages -name '*-kmp-*.rpm' -exec cp {} /kmps/ \;
```

**Special cases** worth covering:

```sh
# an unsigned KMP
cp /kmps/vhba-kmp-*.rpm /kmps/unsigned-kmp-default-1-1.rpm
rpmsign --delsign /kmps/unsigned-kmp-default-1-1.rpm

# a path with a space
mkdir -p "/kmps/with space" && cp /kmps/vhba-kmp-*.rpm "/kmps/with space/vhba copy-kmp-default.rpm"

# an empty directory
mkdir -p /kmps-empty
```

**A system to check** (`system` target):

```sh
zypper --non-interactive in --no-recommends kernel-default   # populates /lib/modules
rpm -i --nodeps /kmps/vhba-kmp-*.rpm /kmps/v4l2loopback-kmp-*.rpm   # third-party modules + weak-updates links

KV=$(ls /lib/modules | sort | tail -1)
mkdir -p /lib/modules/$KV/extra /lib/modules/$KV/weak-updates
# a module not owned by any package
cp "$(find /lib/modules/$KV/kernel -name '*.ko*' | head -1)" /lib/modules/$KV/extra/orphan.ko.zst
# a broken weak-updates link, and a regular file where a link is expected
ln -s /lib/modules/$KV/extra/does-not-exist.ko /lib/modules/$KV/weak-updates/broken.ko
cp "$(find /lib/modules/$KV/kernel -name '*.ko*' | sed -n 2p)" /lib/modules/$KV/weak-updates/notalink.ko.zst
```

In a container, `/proc/modules` belongs to the host kernel (on macOS, Docker's VM). So the `running` column means nothing there, and filters on `"running" = "True"` match nothing.

## Verifying a change

1. **Syntax**: nothing must warn when compiled (Python turns some warnings into errors in later versions):

   ```sh
   for f in $(git ls-files 'src/*.py'); do python3 -W error::SyntaxWarning -m py_compile "$f"; done
   ```

2. **Every target you touched, in every format.**
   - Directory: `-f html` and `-f json`.
   - `system`: `-f html` and `-f json`.
   - Single `.rpm`: terminal output.

   Include the empty directory, and at least one `--filter`.

3. **Compare with the code before your change.** Check out `HEAD` next to your working tree and run both on the same data:

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
   PYTHONPATH=/head/src              python3.11 -m soliddriver_checks.cli.cli /kmps -f json -o before.json
   PYTHONPATH=/root/source_codes/src python3.11 -m soliddriver_checks.cli.cli /kmps -f json -o after.json
   ```

   If the old code fails with `ModuleNotFoundError`, it needs packages the current version dropped. Install them in the container with `python3.11 -m pip install <package>`. For example, versions up to 3.0.9 need `openpyxl rich requests bottle`.

   Remove the worktree afterwards with `git worktree remove /tmp/sdc-head`.

   Then diff the grades per row. The JSON report is easy to load with `json.load()`. Every difference should be one you intended.

4. **Open the HTML reports** in a browser if you touched a reporter or a template.

5. **Run the README examples** if you changed options, filter behaviour or output.

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
