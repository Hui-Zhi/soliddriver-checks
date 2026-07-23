# soliddriver-checks Test Suite

Comprehensive test data using real SUSE SolidDriver KMP packages.

## Directory Structure

```
tests/
├── data/                    # Test input: Real + Custom KMP RPM packages
│   ├── intel-ice-kmp-*.rpm                  (✅ PASS)
│   ├── intel-ixgbe-kmp-*.rpm                (✅ PASS)
│   ├── intel-i40e-kmp-*.rpm                 (✅ PASS)
│   ├── elx-lpfc-kmp-*.rpm                   (⚠️ WARNING)
│   ├── broadcom-tg3-kmp-*.rpm               (❌ ERROR - modalias)
│   ├── broadcom-bnxt_en-kmp-*.rpm           (❌ ERROR - symbols)
│   ├── mlnx-en-kmp-*.rpm                    (❌ ERROR - symbols)
│   ├── suse-hello-kmp-*.rpm                 (❌ ERROR - multiple)
│   ├── license-test-proprietary-kmp-*.rpm   (❌ ERROR - KM license)  🧪
│   ├── license-test-unknown-kmp-*.rpm       (❌ ERROR - KM license)  🧪
│   └── license-test-nosupported-kmp-*.rpm   (❌ ERROR - no supported) 🧪
├── output/                  # Test output: Generated reports
│   ├── real-kmp-report.html
│   └── test-results.json
├── TEST_DATA_SUMMARY.md     # Detailed test data documentation
└── README.md                # This file
```

## Quick Start

### Run All Tests

```bash
# Build Docker image (required for isolated testing)
docker build -f test-refactoring.Dockerfile -t soliddriver-checks-fixed:latest .

# Run HTML report generation
docker run --rm \
  -v $(pwd)/tests/data:/test-data \
  -v $(pwd)/tests/output:/output \
  soliddriver-checks-fixed:latest \
  soliddriver-checks /test-data -f html -o /output/report.html

# View results
open tests/output/report.html
```

### Run JSON Output

```bash
docker run --rm \
  -v $(pwd)/tests/data:/test-data \
  -v $(pwd)/tests/output:/output \
  soliddriver-checks-fixed:latest \
  soliddriver-checks /test-data -f json -o /output/results.json
```

## Test Coverage

### ✅ PASS (3 packages)
All validation checks passed:
- **intel-ice-kmp-default** - Network driver
- **intel-ixgbe-kmp-default** - Network driver  
- **intel-i40e-kmp-default** - Network driver

### ⚠️ WARNING (1 package)
Minor issues, non-critical:
- **elx-lpfc-kmp-default** - Missing kernel module signature

### ❌ ERROR (9 packages)
Critical validation failures:
- **broadcom-tg3-kmp-default** (2 versions) - Modalias mismatch
- **broadcom-bnxt_en-kmp-default** (2 versions) - Symbol validation failure
- **mlnx-en-kmp-default** - Symbol validation failure
- **suse-hello-kmp-default** - Empty vendor, bad license, no wm2, no supported flag
- **license-test-proprietary-kmp** 🧪 - Proprietary module license
- **license-test-unknown-kmp** 🧪 - Unknown module license + no supported flag
- **license-test-nosupported-kmp** 🧪 - GPL but no supported flag

🧪 = Custom-built test package

## Test Data Source

**Origin:** Workstation 192.168.1.35  
**Path:** `/home/hui-zhi/codes/examples/rpm-samples/`  
**Type:** Real SUSE SolidDriver certified KMP packages  
**Kernel Version:** Built for 5.3.18-22 (SLES15 SP2)

## Validation Coverage

This test suite exercises **all soliddriver-checks features**:

### KMP Package Checks
- ✅ Vendor validation
- ✅ License detection (GPL-2.0, GPLv2, unknown)
- ✅ Package signature verification
- ✅ Weak-modules2 invocation

### Kernel Module Checks
- ✅ Module license detection
- ✅ Supported flag validation (yes/no/external/missing)
- ✅ Module signature verification
- ✅ Symbol availability checking
- ✅ Modalias validation

## Expected Results

| Package | Total | Vendor | License | Signature | WM2 | Supported | KM Sig | KM Lic | Symbols | Modalias |
|---------|-------|--------|---------|-----------|-----|-----------|--------|--------|---------|----------|
| intel-ice | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| intel-ixgbe | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| intel-i40e | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ |
| elx-lpfc | ⚠️ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️ | ✅ | ✅ | ✅ |
| broadcom-tg3 | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ⚠️/✅ | ✅ | ✅ | ❌ |
| broadcom-bnxt | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| mlnx-en | ❌ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ✅ | ❌ | ✅ |
| suse-hello | ❌ | ⚠️ | ⚠️ | ✅ | ❌ | ❌ | ⚠️ | ✅ | ✅ | ✅ |

## Test Scenarios Covered

1. **Perfect KMP** - All checks pass (Intel drivers)
2. **Missing Module Signature** - Package signed but module unsigned (elx-lpfc)
3. **Modalias Mismatch** - Package modalias doesn't match module (broadcom-tg3)
4. **Symbol Validation** - Missing kernel symbols due to version mismatch (broadcom-bnxt, mlnx-en)
5. **Multiple Failures** - Empty vendor, bad license, no wm2, no supported flag (suse-hello)

## Notes

- **Symbol errors are expected** - Test packages built for kernel 5.3.18 tested in different kernel version
- **Real kernel modules** - All .ko files are actual compiled ELF binaries
- **Production packages** - Real SUSE SolidDriver certified packages
- **Docker required** - Tests must run in Docker for proper RPM extraction (rpm2cpio, cpio, modinfo)

## Adding New Test Data

1. **On workstation (192.168.1.35):**
   ```bash
   # Place RPMs in
   /home/claude/soliddriver-checks/test-data/
   ```

2. **Copy to local:**
   ```bash
   scp claude@192.168.1.35:/path/to/*.rpm tests/data/
   ```

3. **Run tests:**
   ```bash
   docker run --rm \
     -v $(pwd)/tests/data:/test-data \
     -v $(pwd)/tests/output:/output \
     soliddriver-checks-fixed:latest \
     soliddriver-checks /test-data -f html -o /output/report.html
   ```

## Troubleshooting

### modinfo command not found
Use `/usr/sbin/modinfo` instead of `modinfo` to avoid sudo requirements.

### Permission denied in container
Ensure volume mounts have correct permissions:
```bash
chmod -R 755 tests/data tests/output
```

### No RPMs found
Verify RPMs are in `tests/data/`:
```bash
ls -lh tests/data/*.rpm
```

## Documentation

- **TEST_DATA_SUMMARY.md** - Detailed breakdown of each test package
- **.claude/CLAUDE.md** - Project overview and rules
- **.claude/rules/paths.md** - Path mappings workstation↔local↔Docker
- **.claude/rules/architecture.md** - Code structure and recent fixes

## Version

Test suite updated: 2026-07-21  
soliddriver-checks version: 3.0.9
