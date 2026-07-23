#!/bin/bash
# Test script to show kernel module level errors in KMP packages

set -e

echo "========================================="
echo "Kernel Module Error Test"
echo "========================================="
echo ""
echo "Testing KMP packages with embedded kernel module errors:"
echo "  - real-kmp-gpl-unsupported: Has module with supported=no (ERROR)"
echo "  - real-kmp-license-mismatch: KMP license != KM license (WARNING/ERROR)"
echo "  - real-kmp-multi-issue: Multiple KM-level issues (ERROR)"
echo "  - real-kmp-proprietary-external: Proprietary + external (WARNING)"
echo "  - real-kmp-bsd-module: BSD license module (WARNING)"
echo "  - real-kmp-no-supported-flag: Missing supported flag (WARNING)"
echo "  - kmp-with-unsupported-module: Embedded unsupported module (ERROR)"
echo "  - kmp-license-mismatch: KMP/KM license mismatch (WARNING)"
echo "  - kmp-multiple-issues: Multiple problems (ERROR)"
echo ""

# Create focused test directory
mkdir -p test-data-km-errors
cp test-data/real-kmp-gpl-unsupported-kmp-default-1.0-1.x86_64.rpm test-data-km-errors/
cp test-data/real-kmp-license-mismatch-kmp-default-1.0-1.x86_64.rpm test-data-km-errors/
cp test-data/real-kmp-multi-issue-kmp-default-1.0-1.x86_64.rpm test-data-km-errors/
cp test-data/real-kmp-proprietary-external-kmp-default-1.0-1.x86_64.rpm test-data-km-errors/
cp test-data/real-kmp-bsd-module-kmp-default-1.0-1.x86_64.rpm test-data-km-errors/
cp test-data/real-kmp-no-supported-flag-kmp-default-1.0-1.x86_64.rpm test-data-km-errors/
cp test-data/kmp-with-unsupported-module-kmp-default-1.0.3-1.x86_64.rpm test-data-km-errors/
cp test-data/kmp-license-mismatch-kmp-default-1.0.4-1.x86_64.rpm test-data-km-errors/
cp test-data/kmp-multiple-issues-kmp-default-1.0.5-1.x86_64.rpm test-data-km-errors/

# Also add a perfect one for comparison
cp test-data/real-kmp-perfect-kmp-default-1.0-1.x86_64.rpm test-data-km-errors/

echo "Package count: $(ls -1 test-data-km-errors/*.rpm | wc -l)"
echo ""
echo "Running soliddriver-checks..."
echo ""

# Check if running in virtual environment
if [ -d "venv" ]; then
    source venv/bin/activate
    soliddriver-checks test-data-km-errors -f html -o test-output/km-errors-report.html
    echo ""
    echo "✅ Report generated: test-output/km-errors-report.html"
    echo ""
    echo "Opening report in browser..."
    open test-output/km-errors-report.html
else
    echo "⚠️  Virtual environment not found. Please run:"
    echo "   python3 -m venv venv"
    echo "   source venv/bin/activate"
    echo "   pip install -e ."
    echo "   ./run-km-error-test.sh"
fi
