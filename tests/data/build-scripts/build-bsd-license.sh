#!/bin/bash
set -e

echo "Building bsd-license-kmp (BSD license test)..."

cd "$(dirname "$0")/bsd-license"
make clean || true
make

# Build RPM
rpmbuild -bb kmp.spec \
    --define="_topdir $(pwd)/build/bsd-license-kmp-$version-build" \
    --define="_sourcedir $(pwd)" \
    --define="_rpmdir $(dirname $(pwd))" \
    --nodeps

echo "✓ bsd-license-kmp built successfully"
cd ..
