#!/bin/bash
set -e

echo "============================================"
echo "Building all test KMP packages"
echo "============================================"

SCRIPT_DIR="$(dirname "$0")"

# Build valid package (PASS)
"$SCRIPT_DIR/build-acme-network.sh"
echo ""

# Build license test packages (ERROR/WARNING)
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
ls -lh "$SCRIPT_DIR/../"*.rpm 2>/dev/null | grep -E "(acme|license-test)" || echo "No test RPMs found"
