#!/bin/bash
set -e

echo "============================================"
echo "Building ALL comprehensive test KMP packages"
echo "============================================"

SCRIPT_DIR="$(dirname "$0")"

# Perfect package (all PASS)
echo ""
echo "[1/6] Building perfect-kmp..."
"$SCRIPT_DIR/build-perfect.sh"

# BSD license (PASS)
echo ""
echo "[2/6] Building bsd-license-kmp..."
"$SCRIPT_DIR/build-bsd-license.sh"

# No weak-modules2 (ERROR)
echo ""
echo "[3/6] Building no-wm2-kmp..."
"$SCRIPT_DIR/build-no-wm2.sh"

# Proprietary module license (WARNING)
echo ""
echo "[4/6] Building proprietary module test..."
"$SCRIPT_DIR/build-proprietary.sh"

# Unknown module license (WARNING/ERROR)
echo ""
echo "[5/6] Building unknown license test..."
"$SCRIPT_DIR/build-unknown.sh"

# No supported flag (ERROR)
echo ""
echo "[6/6] Building no-supported-flag test..."
"$SCRIPT_DIR/build-nosupported.sh"

echo ""
echo "============================================"
echo "✓ All test packages built successfully"
echo "============================================"
echo ""
echo "Test packages generated:"
ls -lh "$SCRIPT_DIR/../"*.rpm 2>/dev/null | grep -v "debuginfo" || echo "Check build directory for RPMs"
echo ""
echo "Expected packages:"
echo "  1. perfect-kmp           - All PASS (golden reference)"
echo "  2. bsd-license-kmp       - BSD license (PASS)"
echo "  3. no-wm2-kmp            - Missing weak-modules2 (ERROR)"
echo "  4. proprietary-kmp       - Proprietary module (WARNING)"
echo "  5. unknown-license-kmp   - Unknown module license (WARNING/ERROR)"
echo "  6. nosupported-kmp       - Missing supported flag (ERROR)"
