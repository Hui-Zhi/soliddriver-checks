#!/bin/bash
set -e

echo "Building perfect-kmp (ALL PASS test)..."

cd "$(dirname "$0")/perfect"
make clean || true
make

# Build RPM
rpmbuild -bb kmp.spec \
    --define="_topdir $(pwd)/build/perfect-kmp-$version-build" \
    --define="_sourcedir $(pwd)" \
    --define="_rpmdir $(dirname $(pwd))" \
    --nodeps

echo "✓ perfect-kmp built successfully"
cd ..
