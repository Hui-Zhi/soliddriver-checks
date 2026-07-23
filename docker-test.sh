#!/bin/bash
set -e

echo "================================================"
echo "Soliddriver-Checks Refactoring Test Script"
echo "================================================"
echo ""

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

PROJECT_DIR="/Users/hzzhao/projects/github.com/SUSE/soliddriver-checks"
cd "$PROJECT_DIR"

echo -e "${BLUE}Step 1: Building Docker image...${NC}"
docker build -f test-refactoring.Dockerfile -t soliddriver-checks-refactored:test .

echo ""
echo -e "${BLUE}Step 2: Running unit tests in container...${NC}"
docker run --rm \
    -v "$PROJECT_DIR/test-output:/output" \
    -v "$PROJECT_DIR/test-data:/test-data" \
    soliddriver-checks-refactored:test

echo ""
echo -e "${BLUE}Step 3: Testing system kernel module check...${NC}"
docker run --rm \
    -v "$PROJECT_DIR/test-output:/output" \
    -v "$PROJECT_DIR/test-data:/test-data" \
    soliddriver-checks-refactored:test \
    sh -c "soliddriver-checks system -f json -o /output/system-check.json && \
           echo 'System check JSON output created' && \
           soliddriver-checks system -f html -o /output/system-check.html && \
           echo 'System check HTML output created'"

echo ""
echo -e "${BLUE}Step 4: Testing filter functionality...${NC}"
docker run --rm \
    -v "$PROJECT_DIR/test-output:/output" \
    -v "$PROJECT_DIR/test-data:/test-data" \
    soliddriver-checks-refactored:test \
    sh -c "soliddriver-checks system -f json -o /output/filtered-check.json -i '\"license\" != \"\"' && \
           echo 'Filtered check completed'"

echo ""
echo -e "${BLUE}Step 5: Testing Python imports and API...${NC}"
docker run --rm \
    -v "$PROJECT_DIR/test-output:/output" \
    -v "$PROJECT_DIR/test-data:/test-data" \
    soliddriver-checks-refactored:test \
    python3.9 -c "
from soliddriver_checks.api.common import Evaluation
from soliddriver_checks.api.kmp import KMPReader, KMPAnalysis
from soliddriver_checks.api.km import KMReader as KMR, KMAnalysis as KMA
from soliddriver_checks.api.analysis import kms_to_dataframe, kms_to_json

print('✓ All imports successful')
print('✓ Evaluation enum:', Evaluation.PASS, Evaluation.WARNING, Evaluation.ERROR)
print('✓ Evaluation.PASS.to_json():', Evaluation.PASS.to_json())

# Test that the consolidated enum works
assert Evaluation.PASS.value == 1
assert Evaluation.WARNING.value == 2
assert Evaluation.ERROR.value == 3
print('✓ Enum values correct')
"

echo ""
echo -e "${GREEN}================================================${NC}"
echo -e "${GREEN}All tests completed successfully!${NC}"
echo -e "${GREEN}================================================${NC}"
echo ""
echo -e "${YELLOW}Test outputs saved to:${NC}"
echo "  $PROJECT_DIR/test-output/"
echo ""
echo "Generated files:"
ls -lh "$PROJECT_DIR/test-output/" 2>/dev/null || echo "  (No files generated yet)"
