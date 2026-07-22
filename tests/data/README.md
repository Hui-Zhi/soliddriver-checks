# Test Data

This directory contains test KMP packages for validating soliddriver-checks.

## Test Packages

### Real SUSE SolidDriver Packages (10 packages)

These should be obtained from real SUSE SolidDriver certified vendors:
- `broadcom-bnxt_en-kmp-default-*.rpm` (2 versions)
- `broadcom-tg3-kmp-default-*.rpm` (2 versions)
- `elx-lpfc-kmp-default-*.rpm`
- `intel-i40e-kmp-default-*.rpm`
- `intel-ice-kmp-default-*.rpm`
- `intel-ixgbe-kmp-default-*.rpm`
- `mlnx-en-kmp-default-*.rpm`
- `suse-hello-kmp-default-*.rpm`

### Custom Test Packages (3 packages)

Built from `build-scripts/` to test specific scenarios:
- `license-test-proprietary-kmp-*.rpm` - Tests proprietary license detection
- `license-test-unknown-kmp-*.rpm` - Tests unknown license detection
- `license-test-nosupported-kmp-*.rpm` - Tests missing supported flag

## Building Test Packages

See [`build-scripts/README.md`](build-scripts/README.md) for instructions on building the custom test packages.

**Quick build:**
```bash
cd build-scripts
./build-all.sh
```

**Requirements:**
- Linux environment
- Kernel headers
- RPM build tools

## Running Tests

**With Docker (recommended):**
```bash
docker build -t soliddriver-checks -f test-refactoring.Dockerfile .
docker run --rm \
  -v $(pwd)/tests/data:/test-data \
  -v $(pwd)/tests/output:/output \
  soliddriver-checks \
  soliddriver-checks /test-data -f html -o /output/report.html
```

**Without Docker (Linux only):**
```bash
soliddriver-checks tests/data -f html -o tests/output/report.html
```

## Expected Test Results

| Package | Expected Status | Reason |
|---------|----------------|---------|
| Intel packages (3) | ✅ PASS | All checks pass |
| Broadcom lpfc | ⚠️ WARNING | Missing module signature |
| Other packages (9) | ❌ ERROR | Various validation failures |
| license-test-proprietary | ❌ ERROR | Non-GPL license |
| license-test-unknown | ❌ ERROR | Unknown license |
| license-test-nosupported | ⚠️ WARNING | Missing supported flag |

**Overall distribution:**
- PASS: 3 packages (23%)
- WARNING: 1-2 packages (8-15%)
- ERROR: 9-10 packages (69-77%)

## Notes

- Real SUSE packages are **not** included in the repository (too large)
- Obtain them from SUSE partners or SolidDriver certification samples
- Custom test packages **must be built** on a Linux system with kernel headers
- Built RPMs are architecture-specific (x86_64, aarch64, etc.)
