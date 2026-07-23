#!/bin/bash
set -e

echo "Building acme-network-kmp (PASS test)..."

cd "$(dirname "$0")/acme-network"

# Build kernel module
make clean || true
make

# Build RPM
rpmbuild -bb kmp.spec \
    --define "_sourcedir $PWD" \
    --define "_rpmdir ../../" \
    --define "_builddir $PWD/build"

# Move RPM to tests/data
mv ../../x86_64/acme-network-kmp-*.rpm ../../ 2>/dev/null || true
mv ../../*/acme-network-kmp-*.rpm ../../ 2>/dev/null || true

# Cleanup
make clean
rm -rf build

echo "✓ Built: $(ls ../../acme-network-kmp-*.rpm)"
