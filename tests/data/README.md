# Test Data

This directory contains test KMP packages for validating soliddriver-checks.

## Test Packages

### Example Production Packages (Optional)

For comprehensive testing, you can use real SUSE SolidDriver certified KMP packages.
These are **not included** in the repository and must be obtained separately.

Examples of real-world packages (for reference only):
- Network driver KMPs from certified vendors
- Storage driver KMPs from certified vendors
- Other certified SolidDriver packages

The custom test packages below are sufficient for basic validation testing.

### Custom Test Packages (4 packages)

Built from `build-scripts/` to test specific scenarios:
- `acme-network-kmp-*.rpm` - Valid package (all checks PASS)
- `license-test-proprietary-kmp-*.rpm` - Tests proprietary license detection
- `license-test-unknown-kmp-*.rpm` - Tests unknown license detection
- `license-test-nosupported-kmp-*.rpm` - Tests missing supported flag

All packages use fake vendor names (ACME Corporation, Test Vendor Inc) to avoid trademark issues.

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
| acme-network | ✅ PASS | All checks pass |
| license-test-proprietary | ❌ ERROR | Non-GPL license |
| license-test-unknown | ❌ ERROR | Unknown license |
| license-test-nosupported | ❌ ERROR | Missing supported flag + no WM2 |

When testing with your own production packages, you'll see varied results based on the packages used.

## Notes

- Production KMP packages are **not** included in the repository
- Use your own KMP packages for comprehensive testing
- Custom test packages **must be built** on a Linux system with kernel headers
- Built RPMs are architecture-specific (x86_64, aarch64, etc.)
- The 4 custom test packages cover basic validation scenarios
- **Note:** The repository currently contains real vendor packages for testing purposes. To use only fake vendor packages, remove the real vendor RPMs and build the test packages from `build-scripts/`
