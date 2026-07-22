#!/bin/bash
set -e

echo "Building license-test-nosupported-kmp..."

cd "$(dirname "$0")/nosupported"

# Build kernel module
make clean || true
make

# Build RPM
rpmbuild -bb kmp.spec \
    --define "_sourcedir $PWD" \
    --define "_rpmdir ../../" \
    --define "_builddir $PWD/build"

# Move RPM to tests/data
mv ../../x86_64/license-test-nosupported-kmp-*.rpm ../../ 2>/dev/null || true
mv ../../*/license-test-nosupported-kmp-*.rpm ../../ 2>/dev/null || true

# Cleanup
make clean
rm -rf build

echo "✓ Built: $(ls ../../license-test-nosupported-kmp-*.rpm)"
