# Test RPM Build Scripts

This directory contains scripts to build test KMP packages for validating soliddriver-checks.

## Prerequisites

**Linux environment with:**
- Kernel headers (`kernel-devel` package)
- RPM build tools (`rpm-build`, `rpmbuild`)
- GCC compiler
- Make

**On SUSE/openSUSE:**
```bash
sudo zypper install kernel-default-devel rpm-build gcc make
```

**On Ubuntu/Debian:**
```bash
sudo apt-get install linux-headers-$(uname -r) rpm build-essential
```

## Building Test RPMs

### Quick Start

Build all test RPMs:
```bash
cd tests/data/build-scripts
./build-all.sh
```

Output: `tests/data/*.rpm`

### Individual Builds

**Valid Package (PASS):**
```bash
./build-acme-network.sh
```

**Proprietary License Test:**
```bash
./build-proprietary.sh
```

**Unknown License Test:**
```bash
./build-unknown.sh
```

**No Supported Flag Test:**
```bash
./build-nosupported.sh
```

## What Gets Built

| RPM | Purpose | Expected Result |
|-----|---------|-----------------|
| `acme-network-kmp-*.rpm` | Valid package with all checks passing | PASS: All validations pass |
| `license-test-proprietary-kmp-*.rpm` | MODULE_LICENSE("Proprietary") | ERROR: Non-GPL license |
| `license-test-unknown-kmp-*.rpm` | MODULE_LICENSE("Unknown") | ERROR: Unknown license |
| `license-test-nosupported-kmp-*.rpm` | GPL but no MODULE_INFO(supported) | WARNING: Missing supported flag |

## Directory Structure

```
build-scripts/
├── README.md                # This file
├── build-all.sh             # Build all test RPMs
├── build-acme-network.sh    # Build valid PASS test
├── build-proprietary.sh     # Build proprietary license test
├── build-unknown.sh         # Build unknown license test
├── build-nosupported.sh     # Build no-supported-flag test
├── acme-network/            # Source for valid PASS test
│   ├── module.c
│   ├── Makefile
│   └── kmp.spec
├── proprietary/             # Source for proprietary test
│   ├── module.c
│   ├── Makefile
│   └── kmp.spec
├── unknown/                 # Source for unknown license test
│   ├── module.c
│   ├── Makefile
│   └── kmp.spec
└── nosupported/             # Source for no-supported-flag test
    ├── module.c
    ├── Makefile
    └── kmp.spec
```

## How It Works

Each test package:
1. Compiles a kernel module (`.c` → `.ko`)
2. Packages it into an RPM using rpmbuild
3. Outputs to `tests/data/`

The kernel modules are minimal - just enough to test specific validation scenarios.

## Troubleshooting

**"No rule to make target":**
- Install kernel headers for your running kernel
- Check: `ls /lib/modules/$(uname -r)/build`

**"rpmbuild: command not found":**
- Install rpm-build: `zypper install rpm-build` or `apt-get install rpm`

**Permission denied:**
- Make scripts executable: `chmod +x *.sh`

## Notes

- Built RPMs are architecture-specific (`x86_64`, `aarch64`, etc.)
- Production KMP packages should be obtained separately for comprehensive testing
- These are **test packages only** - not for production use
- These test packages demonstrate specific validation scenarios for soliddriver-checks
