# soliddriver-checks

`soliddriver-checks` checks whether third-party **Kernel Module Packages (KMPs)** and the **kernel modules (KMs)** installed on a system are built according to SUSE's requirements. It writes a report in HTML or JSON. Every checked field is graded `PASS`, `WARNING` or `ERROR`, and each KMP or kernel module also gets an overall grade.

Use it to:

- vet KMP RPMs from a hardware vendor before installing them on SUSE Linux Enterprise or openSUSE
- audit the kernel modules on a running system for unsupported, unsigned or orphaned modules

> **Note:** The tool only checks that KMPs and kernel modules are *built and packaged* the way SUSE requires. It doesn't look at the code, so it can't find bugs or security issues inside a kernel module.

Terms:

- **KM**: kernel module (`.ko`, `.ko.xz`, `.ko.zst`)
- **KMP**: kernel module package, an RPM named `*-kmp-*.rpm`

## Contents

- [Requirements](#requirements)
- [Installation](#installation)
- [Usage](#usage)
- [What is checked](#what-is-checked)
- [Filtering results (`--filter`)](#filtering-results---filter)
- [How should you address the issues?](#how-should-you-address-the-issues)

## Requirements

- A SUSE Linux Enterprise or openSUSE system. Checks run the system tools below, so they don't work on macOS or Windows.
- Python 3.7 or later
- `rpm`, `rpm2cpio`, `cpio`, `find`, and `kmod` (`/usr/sbin/modinfo`, `/usr/sbin/modprobe`)

## Installation

- From PyPI:

  ```sh
  pip install soliddriver-checks
  ```

- With zypper: RPMs are available on [build.opensuse.org](https://build.opensuse.org/package/show/home:huizhizhao:soliddriver-checks/soliddriver-checks).

## Usage

```text
Usage: soliddriver-checks [OPTIONS] [CHECK_TARGET]

  Run checks against CHECK_TARGET.

  CHECK_TARGET can be:
    KMP file
    directory containing KMP files
    "system" to check locally installed kernel modules

Options:
  -f, --format [html|json]  Specify output format
  -i, --filter TEXT         Only report the KMPs or kernel modules that match
                            the filter expression, e.g. '"level.level" !=
                            "PASS"'. See README.md for the syntax.
  -o, --output TEXT         Output destination. If it is an existing
                            directory, or ends with '/', the report is written
                            there as check_result.<format>. Otherwise it is
                            used as the file name. The extension matching the
                            output format is added if it is missing.
  --version
  --help                    Show this message and exit.
```

### Check targets

| `CHECK_TARGET` | What is checked | Output |
| --- | --- | --- |
| `system` (default) | Kernel modules currently loaded (`/proc/modules`) plus all modules under `/lib/modules` | Report file |
| A directory | Every `*-kmp-*.rpm` found in the directory and its subdirectories | Report file |
| A single `.rpm` file | That KMP only | A table printed to the terminal, no report file. `--format`, `--output` and `--filter` are ignored. |

### Options

- **`-f, --format`**: `json` (default) or `html`.
- **`-o, --output`**: where to write the report. The default is the current directory.
  - If it's an existing directory, or ends with `/`, the report is written there as `check_result.<format>`.
  - Otherwise it's used as the file name. `.html` or `.json` is added if the name doesn't already end with it.
  - If the file already exists, you're asked before it's overwritten.
- **`-i, --filter`**: only include the KMPs or kernel modules that match an expression. See [Filtering results](#filtering-results---filter).
- **`--version`**: print the version and exit.

### Examples

Check every KMP in a directory and write an HTML report:

```sh
soliddriver-checks /path/to/kmps -f html -o kmp-report.html
```

Check the kernel modules on this system and write a JSON report to `./check_result.json`:

```sh
soliddriver-checks
```

Check one KMP and print the result to the terminal:

```sh
soliddriver-checks /path/to/foo-kmp-default-1.0-1.x86_64.rpm
```

Write an HTML report that contains only the kernel modules that didn't pass:

```sh
soliddriver-checks -f html -o km-issues -i '"level.level" != "PASS"'
```

## What is checked

The grade colors in the HTML report:

- **Yellow (`WARNING`)**: not required, but a potential problem. Examples: no signature, a license that isn't GPL-compatible.
- **Red (`ERROR`)**: likely to cause problems during installation, after a kernel update, or while the module is running.

The overall grade of a row (`level`) is the worst grade of its fields.

### Kernel module checks (`system` target)

| Key | Content | WARNING when | ERROR when |
| --- | --- | --- | --- |
| `modulename` | Module name | | |
| `filename` | Path of the module file | The file isn't under `/lib/modules` or `/usr/lib/modules` | A module in `weak-updates/` isn't a symlink, or the symlink is broken |
| `license` | License(s) from `modinfo` | A license isn't on the list of accepted open source licenses | |
| `signature` | `Yes` or `No` | The module isn't signed | |
| `supported` | Value(s) of the `supported` flag | The flag is set more than once (with valid values) | The flag is missing, or has a value other than `yes`, `no` or `external` |
| `running` | `True` or `False`: whether the module is loaded | | |
| `kmp` | Name of the package that installed the module. A `weak-updates/` link counts as owned by the package of the module it points to. | The module isn't owned by any package, or the package isn't signed | |

### KMP checks (directory or `.rpm` target)

| Key | Content | WARNING when | ERROR when |
| --- | --- | --- | --- |
| `name` | Package name | | |
| `path` | Path of the RPM file | | |
| `vendor` | RPM vendor | The vendor is empty | |
| `signature` | RPM signature | The RPM isn't signed | |
| `license` | RPM license | The license is empty, or a license in it isn't accepted. SPDX expressions such as `GPL-2.0-only AND MIT` are checked license by license. | |
| `wm2_invoked` | `True` or `False`: whether the RPM scripts run `weak-modules2`, directly or through the `kernel-scriptlets` | | The scripts don't run `weak-modules2` (not checked for `debuginfo` packages) |
| `km_licenses` | Licenses of the modules in the KMP | A module's license isn't accepted | |
| `km_signatures` | Whether the modules in the KMP are signed | A module isn't signed | |
| `supported_flag` | Problems with the modules' `supported` flag | | A module has no `supported` flag, or a value other than `external` |
| `symbols` | Kernel symbol check result | | A module uses a kernel symbol the KMP doesn't declare in its `ksym()` requirements, or the symbol checksum doesn't match |
| `modalias` | Device alias check result | | The KMP claims every device (`modalias(...:*)`), or the PCI aliases of the modules and the package don't match |

The HTML KMP report starts with a summary of failed checks per vendor, followed by the details of each KMP.

The accepted licenses and known signing keys are configured in `src/soliddriver_checks/config/soliddriver-checks.conf`.

## Filtering results (`--filter`)

`--filter` (short form `-i`) takes an expression and keeps only the rows that match it. A row is one kernel module for the `system` target, or one KMP for a directory target. The filter works with every output format. It's ignored when the target is a single `.rpm` file. The counts in the HTML report reflect the filtered rows.

### Syntax

An expression is one or more conditions:

| Condition | Matches when |
| --- | --- |
| `"key" = "value"` | The key's value is exactly `value` |
| `"key" != "value"` | The key's value isn't exactly `value` |
| `"key" match "regex"` | The key's value contains a match for the Python regular expression `regex` |
| `no "key"` | The key's value is empty |

Combine conditions with `and` and `or`, and group them with `( )`:

```text
"signature" = "No" and "running" = "True"
"modulename" = "e1000" or "modulename" = "igb"
("license.level" != "PASS" or "signature" = "No") and "running" = "True"
```

Rules:

- **Keys and values must be in double quotes** (`"..."`). The operators `=`, `!=`, `match`, `no`, `and` and `or` aren't quoted.
- **`and` binds more tightly than `or`.** `A or B and C` means `A or (B and C)`. Use parentheses for anything else.
- **Comparisons are exact and case-sensitive.** `=` and `!=` compare the whole value as text. Booleans are written `"True"` and `"False"`.
- **`match` uses [Python regular expressions](https://docs.python.org/3/library/re.html)** and matches anywhere in the value, like `re.search`. Use `^` and `$` to anchor the pattern, and `(?i)` to ignore case.
- The filter is checked before the scan starts. An unknown key, a syntax error (for example `==` instead of `=`) or an invalid regular expression stops the run with an error message; for an unknown key it lists the valid keys.

The full grammar (EBNF) is at the top of [`src/soliddriver_checks/api/filter.py`](src/soliddriver_checks/api/filter.py).

### Keys

Use the keys from the tables in [What is checked](#what-is-checked):

- Kernel modules (`system`): `modulename`, `filename`, `license`, `signature`, `supported`, `running`, `kmp`
- KMPs (directory): `name`, `path`, `vendor`, `signature`, `license`, `wm2_invoked`, `km_licenses`, `km_signatures`, `supported_flag`, `symbols`, `modalias`

A key on its own refers to the field's **content**: the text shown in the report, which is the `value` in the JSON output. To filter on how a field was **graded**, add `.level` to the key and compare it with `PASS`, `WARNING` or `ERROR`:

```text
"signature.level" = "WARNING"
"supported.level" != "PASS"
```

`level.level` is the **overall grade of the row**:

```text
"level.level" = "ERROR"
```

If you aren't sure what a field contains, run once with `-f json` and look at the `value` fields.

### Shell quoting

The expression contains double quotes, so put the whole expression in **single quotes** in the shell:

```sh
soliddriver-checks -i '"running" = "True"'
```

Use plain ASCII quotes (`'` and `"`). Typographic quotes such as `“` and `‘` cause a parse error.

### Filter examples

Kernel modules (`system` target):

```sh
# Only modules that didn't pass
soliddriver-checks -f html -o issues -i '"level.level" != "PASS"'

# Loaded modules that aren't signed
soliddriver-checks -f html -o unsigned -i '"running" = "True" and "signature" = "No"'

# Modules not installed by any package, or with a problem in the supported flag
soliddriver-checks -i '"kmp" = "Not owned by any package" or "supported.level" != "PASS"'

# Modules whose name starts with "nvidia" or "nv_", ignoring case
soliddriver-checks -i '"modulename" match "(?i)^(nvidia|nv_)"'

# Modules in weak-updates/ that have errors
soliddriver-checks -i '"filename" match "/weak-updates/" and "level.level" = "ERROR"'

# Modules with a non-accepted license that are loaded
soliddriver-checks -i '"license.level" = "WARNING" and "running" = "True"'
```

KMPs (directory target):

```sh
# KMPs with at least one error
soliddriver-checks /path/to/kmps -f html -o kmp-errors -i '"level.level" = "ERROR"'

# KMPs from one vendor
soliddriver-checks /path/to/kmps -i '"vendor" match "(?i)acme"'

# KMPs that don't run weak-modules2 or have symbol problems
soliddriver-checks /path/to/kmps -i '"wm2_invoked" = "False" or "symbols.level" = "ERROR"'

# Unsigned KMPs
soliddriver-checks /path/to/kmps -i '"signature.level" = "WARNING"'
```

## How should you address the issues?

Contact the vendor of the KMP and ask them to rebuild it to meet SUSE's requirements, following the [Kernel Module Packages Manual](https://drivers.suse.com/doc/kmpm/). If they don't know how, they can contact SUSE directly.

## License

GPL-2.0. See [LICENSE](LICENSE).
