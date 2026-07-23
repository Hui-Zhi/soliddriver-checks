#!/bin/bash
set -e

echo "Building license-test-proprietary-kmp..."

cd "$(dirname "$0")/proprietary"

# Build kernel module
make clean || true
make

# Build RPM
rpmbuild -bb kmp.spec \
    --define "_sourcedir $PWD" \
    --define "_rpmdir ../../" \
    --define "_builddir $PWD/build"

# Move RPM to tests/data
mv ../../x86_64/license-test-proprietary-kmp-*.rpm ../../ 2>/dev/null || true
mv ../../*/license-test-proprietary-kmp-*.rpm ../../ 2>/dev/null || true

# Cleanup
make clean
rm -rf build

echo "✓ Built: $(ls ../../license-test-proprietary-kmp-*.rpm)"
