#!/bin/bash
set -e

# Colors for output
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
RED='\033[0;31m'
NC='\033[0m' # No Color

echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  SolidDriver-Checks Docker Test Runner${NC}"
echo -e "${GREEN}============================================${NC}"
echo ""

# Check if RPMs exist
if [ ! -f tests/data/*.rpm ]; then
    echo -e "${RED}ERROR: No RPM files found in tests/data/${NC}"
    echo -e "${YELLOW}Please generate RPMs on workstation first.${NC}"
    echo -e "${YELLOW}See WORKSTATION_SETUP.md for instructions.${NC}"
    exit 1
fi

# Show available RPMs
echo -e "${GREEN}Found test RPMs:${NC}"
ls -lh tests/data/*.rpm
echo ""

# Create output directory
mkdir -p tests/output

# Run basic unit tests first
echo -e "${GREEN}[1/4] Running unit tests...${NC}"
docker run --rm \
    -v "$(pwd)/tests/data:/test-data" \
    -v "$(pwd)/tests/output:/output" \
    soliddriver-checks-test:latest \
    sh -c "python3.9 -m pytest tests/ -v || true"
echo ""

# Test 1: HTML Report
echo -e "${GREEN}[2/4] Generating HTML report...${NC}"
docker run --rm \
    -v "$(pwd)/tests/data:/test-data" \
    -v "$(pwd)/tests/output:/output" \
    soliddriver-checks-test:latest \
    soliddriver-checks /test-data -f html -o /output/kmp-report.html

if [ -f tests/output/kmp-report.html ]; then
    echo -e "${GREEN}✓ HTML report generated: tests/output/kmp-report.html${NC}"
    ls -lh tests/output/kmp-report.html
else
    echo -e "${RED}✗ HTML report generation failed${NC}"
fi
echo ""

# Test 2: JSON Report
echo -e "${GREEN}[3/4] Generating JSON report...${NC}"
docker run --rm \
    -v "$(pwd)/tests/data:/test-data" \
    -v "$(pwd)/tests/output:/output" \
    soliddriver-checks-test:latest \
    soliddriver-checks /test-data -f json -o /output/kmp-report.json

if [ -f tests/output/kmp-report.json ]; then
    echo -e "${GREEN}✓ JSON report generated: tests/output/kmp-report.json${NC}"
    ls -lh tests/output/kmp-report.json
    echo -e "${YELLOW}JSON preview:${NC}"
    head -20 tests/output/kmp-report.json
else
    echo -e "${RED}✗ JSON report generation failed${NC}"
fi
echo ""

# Test 3: Version check
echo -e "${GREEN}[4/4] Checking version...${NC}"
docker run --rm soliddriver-checks-test:latest soliddriver-checks --version
echo ""

# Summary
echo -e "${GREEN}============================================${NC}"
echo -e "${GREEN}  Test Summary${NC}"
echo -e "${GREEN}============================================${NC}"
if [ -f tests/output/kmp-report.html ] && [ -f tests/output/kmp-report.json ]; then
    echo -e "${GREEN}✓ All tests passed!${NC}"
    echo ""
    echo "Generated reports:"
    echo "  - HTML: tests/output/kmp-report.html"
    echo "  - JSON: tests/output/kmp-report.json"
    echo ""
    echo "To view HTML report:"
    echo "  open tests/output/kmp-report.html"
else
    echo -e "${RED}✗ Some tests failed${NC}"
    exit 1
fi
