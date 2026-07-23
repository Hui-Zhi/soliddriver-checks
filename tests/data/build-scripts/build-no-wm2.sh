#!/bin/bash
set -e

echo "Building no-wm2-kmp (missing weak-modules2 test)..."

cd "$(dirname "$0")/no-wm2"
make clean || true
make

# Build RPM
rpmbuild -bb kmp.spec \
    --define="_topdir $(pwd)/build/no-wm2-kmp-$version-build" \
    --define="_sourcedir $(pwd)" \
    --define="_rpmdir $(dirname $(pwd))" \
    --nodeps

echo "✓ no-wm2-kmp built successfully"
cd ..
