#!/bin/bash
set -e

echo "Building license-test-unknown-kmp..."

cd "$(dirname "$0")/unknown"

# Build kernel module
make clean || true
make

# Build RPM
rpmbuild -bb kmp.spec \
    --define "_sourcedir $PWD" \
    --define "_rpmdir ../../" \
    --define "_builddir $PWD/build"

# Move RPM to tests/data
mv ../../x86_64/license-test-unknown-kmp-*.rpm ../../ 2>/dev/null || true
mv ../../*/license-test-unknown-kmp-*.rpm ../../ 2>/dev/null || true

# Cleanup
make clean
rm -rf build

echo "✓ Built: $(ls ../../license-test-unknown-kmp-*.rpm)"
