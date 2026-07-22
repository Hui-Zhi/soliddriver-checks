#!/bin/bash
set -e

echo "============================================"
echo "Building all test KMP packages"
echo "============================================"

SCRIPT_DIR="$(dirname "$0")"

# Build each test package
"$SCRIPT_DIR/build-proprietary.sh"
echo ""
"$SCRIPT_DIR/build-unknown.sh"
echo ""
"$SCRIPT_DIR/build-nosupported.sh"

echo ""
echo "============================================"
echo "✓ All test packages built successfully"
echo "============================================"
echo ""
ls -lh "$SCRIPT_DIR/../"*.rpm 2>/dev/null | grep license-test || echo "No RPMs found"
