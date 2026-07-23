#!/bin/bash
# Comprehensive Kernel Module Test - Matches the reference screenshot

set -e

echo "========================================="
echo "Comprehensive Kernel Module Test Suite"
echo "========================================="
echo ""
echo "This test includes ALL KMP packages with kernel module checks:"
echo "  - All real-kmp-* packages (8 packages)"
echo "  - All kmp-with-* packages (3 packages)"
echo "  - All kmp-*-issues packages (2 packages)"
echo ""

# Create comprehensive test directory
rm -rf test-data-comprehensive
mkdir -p test-data-comprehensive

echo "Copying test packages..."

# Real KMP packages (actual kernel modules embedded)
cp test-data/real-kmp-bsd-module-kmp-default-1.0-1.x86_64.rpm test-data-comprehensive/
cp test-data/real-kmp-gpl-supported-kmp-default-1.0-1.x86_64.rpm test-data-comprehensive/
cp test-data/real-kmp-gpl-unsupported-kmp-default-1.0-1.x86_64.rpm test-data-comprehensive/
cp test-data/real-kmp-license-mismatch-kmp-default-1.0-1.x86_64.rpm test-data-comprehensive/
cp test-data/real-kmp-multi-issue-kmp-default-1.0-1.x86_64.rpm test-data-comprehensive/
cp test-data/real-kmp-no-supported-flag-kmp-default-1.0-1.x86_64.rpm test-data-comprehensive/
cp test-data/real-kmp-perfect-kmp-default-1.0-1.x86_64.rpm test-data-comprehensive/
cp test-data/real-kmp-proprietary-external-kmp-default-1.0-1.x86_64.rpm test-data-comprehensive/

# KMP with embedded modules
cp test-data/kmp-with-gpl-module-kmp-default-1.0.1-1.x86_64.rpm test-data-comprehensive/
cp test-data/kmp-with-proprietary-module-kmp-default-1.0.2-1.x86_64.rpm test-data-comprehensive/
cp test-data/kmp-with-unsupported-module-kmp-default-1.0.3-1.x86_64.rpm test-data-comprehensive/

# Issue packages
cp test-data/kmp-license-mismatch-kmp-default-1.0.4-1.x86_64.rpm test-data-comprehensive/
cp test-data/kmp-multiple-issues-kmp-default-1.0.5-1.x86_64.rpm test-data-comprehensive/

PACKAGE_COUNT=$(ls -1 test-data-comprehensive/*.rpm | wc -l | tr -d ' ')
echo "Package count: $PACKAGE_COUNT"
echo ""
echo "Running soliddriver-checks..."
echo ""

# Check if running in virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
else
    echo "Creating virtual environment..."
    python3 -m venv venv
    source venv/bin/activate
    echo "Installing soliddriver-checks..."
    pip install -q -e .
fi

# Run the check
soliddriver-checks test-data-comprehensive -f html -o test-output/comprehensive-km-test.html

echo ""
echo "✅ Report generated: test-output/comprehensive-km-test.html"
echo ""
echo "Expected coverage:"
echo "  ✅ Proprietary license warnings (KM Licenses column)"
echo "  ✅ Vendor validation errors (Vendor column)"
echo "  ✅ Supported flag errors (Supported Flag column)"
echo "  ✅ License mismatch warnings (KM Licenses column)"
echo "  ✅ Multi-issue packages (multiple columns)"
echo "  ✅ Perfect baseline (all green)"
echo ""
echo "Opening report in browser..."
open test-output/comprehensive-km-test.html
