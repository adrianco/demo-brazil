#!/bin/bash

# Brazilian Soccer MCP Knowledge Graph - Test Runner Script
#
# This script runs the complete test suite with various options for
# unit tests, integration tests, and BDD scenarios.
#
# Context Block:
# - Purpose: Automated test execution with comprehensive reporting
# - Usage: Run from project root directory
# - Features: Coverage reporting, parallel execution, test categorization
# - Output: HTML coverage reports and test results

set -e  # Exit on any error

# Colors for output
RED='\033[0;31m'
GREEN='\033[0;32m'
YELLOW='\033[1;33m'
BLUE='\033[0;34m'
NC='\033[0m' # No Color

# Project root directory
PROJECT_ROOT="$(cd "$(dirname "${BASH_SOURCE[0]}")/.." && pwd)"
cd "$PROJECT_ROOT"

# Default values
RUN_UNIT=true
RUN_INTEGRATION=true
RUN_BDD=true
RUN_COVERAGE=true
PARALLEL=false
VERBOSE=false
HTML_REPORT=true
CLEAN_CACHE=false

# Function to print colored output
print_info() {
    echo -e "${BLUE}[INFO]${NC} $1"
}

print_success() {
    echo -e "${GREEN}[SUCCESS]${NC} $1"
}

print_warning() {
    echo -e "${YELLOW}[WARNING]${NC} $1"
}

print_error() {
    echo -e "${RED}[ERROR]${NC} $1"
}

# Function to show usage
show_usage() {
    cat << EOF
Brazilian Soccer MCP Knowledge Graph - Test Runner

Usage: $0 [OPTIONS]

Options:
    -u, --unit-only          Run only unit tests
    -i, --integration-only   Run only integration tests
    -b, --bdd-only          Run only BDD tests
    -c, --no-coverage       Skip coverage reporting
    -p, --parallel          Run tests in parallel
    -v, --verbose           Verbose output
    -n, --no-html           Skip HTML coverage report
    -x, --clean-cache       Clean pytest cache before running
    -h, --help              Show this help message

Examples:
    $0                      # Run all tests with coverage
    $0 -u                   # Run only unit tests
    $0 -b -v                # Run BDD tests with verbose output
    $0 -p -c                # Run all tests in parallel without coverage
    $0 -x                   # Clean cache and run all tests

EOF
}

# Parse command line arguments
while [[ $# -gt 0 ]]; do
    case $1 in
        -u|--unit-only)
            RUN_INTEGRATION=false
            RUN_BDD=false
            shift
            ;;
        -i|--integration-only)
            RUN_UNIT=false
            RUN_BDD=false
            shift
            ;;
        -b|--bdd-only)
            RUN_UNIT=false
            RUN_INTEGRATION=false
            shift
            ;;
        -c|--no-coverage)
            RUN_COVERAGE=false
            shift
            ;;
        -p|--parallel)
            PARALLEL=true
            shift
            ;;
        -v|--verbose)
            VERBOSE=true
            shift
            ;;
        -n|--no-html)
            HTML_REPORT=false
            shift
            ;;
        -x|--clean-cache)
            CLEAN_CACHE=true
            shift
            ;;
        -h|--help)
            show_usage
            exit 0
            ;;
        *)
            print_error "Unknown option: $1"
            show_usage
            exit 1
            ;;
    esac
done

# Function to check prerequisites
check_prerequisites() {
    print_info "Checking prerequisites..."

    # Check if virtual environment is activated
    if [[ -z "$VIRTUAL_ENV" ]]; then
        print_warning "Virtual environment not detected. Consider activating it."
    fi

    # Check if required packages are installed
    if ! python -c "import pytest" 2>/dev/null; then
        print_error "pytest not found. Please install requirements: pip install -r requirements.txt"
        exit 1
    fi

    # Check Neo4j connection
    if ! python -c "
import sys
sys.path.insert(0, 'src')
from graph.connection import Neo4jConnection
from utils.config import load_config
try:
    config = load_config('config/config.yaml')
    conn = Neo4jConnection(config['database']['neo4j'])
    conn.execute_query('RETURN 1')
    conn.close()
    print('Neo4j connection successful')
except Exception as e:
    print(f'Neo4j connection failed: {e}')
    sys.exit(1)
" 2>/dev/null; then
        print_warning "Neo4j connection failed. Some tests may fail."
    fi

    print_success "Prerequisites check completed"
}

# Function to clean pytest cache
clean_cache() {
    if [[ "$CLEAN_CACHE" == true ]]; then
        print_info "Cleaning pytest cache..."
        rm -rf .pytest_cache/
        rm -rf __pycache__/
        find . -name "*.pyc" -delete
        find . -name "__pycache__" -type d -exec rm -rf {} + 2>/dev/null || true
        print_success "Cache cleaned"
    fi
}

# Function to setup test environment
setup_test_env() {
    print_info "Setting up test environment..."

    # Create logs directory if it doesn't exist
    mkdir -p logs

    # Create test reports directory
    mkdir -p test_reports

    # Set environment variables for testing
    export ENVIRONMENT=test
    export LOG_LEVEL=DEBUG
    export NEO4J_DATABASE=test_neo4j

    print_success "Test environment ready"
}

# Function to build pytest command
build_pytest_cmd() {
    local test_type="$1"
    local cmd="python -m pytest"

    # Add verbosity
    if [[ "$VERBOSE" == true ]]; then
        cmd="$cmd -v"
    else
        cmd="$cmd -q"
    fi

    # Add parallel execution
    if [[ "$PARALLEL" == true ]]; then
        cmd="$cmd -n auto"
    fi

    # Add coverage if enabled
    if [[ "$RUN_COVERAGE" == true ]]; then
        cmd="$cmd --cov=src --cov-branch"
        if [[ "$HTML_REPORT" == true ]]; then
            cmd="$cmd --cov-report=html:test_reports/coverage_${test_type}"
        fi
        cmd="$cmd --cov-report=term-missing"
        cmd="$cmd --cov-report=xml:test_reports/coverage_${test_type}.xml"
    fi

    # Add JUnit XML report
    cmd="$cmd --junit-xml=test_reports/junit_${test_type}.xml"

    echo "$cmd"
}

# Function to run unit tests
run_unit_tests() {
    if [[ "$RUN_UNIT" == true ]]; then
        print_info "Running unit tests..."

        local cmd
        cmd=$(build_pytest_cmd "unit")
        cmd="$cmd tests/unit/"

        if eval "$cmd"; then
            print_success "Unit tests passed"
        else
            print_error "Unit tests failed"
            return 1
        fi
    fi
}

# Function to run integration tests
run_integration_tests() {
    if [[ "$RUN_INTEGRATION" == true ]]; then
        print_info "Running integration tests..."

        local cmd
        cmd=$(build_pytest_cmd "integration")
        cmd="$cmd tests/integration/"

        if eval "$cmd"; then
            print_success "Integration tests passed"
        else
            print_error "Integration tests failed"
            return 1
        fi
    fi
}

# Function to run BDD tests
run_bdd_tests() {
    if [[ "$RUN_BDD" == true ]]; then
        print_info "Running BDD tests..."

        local cmd
        cmd=$(build_pytest_cmd "bdd")
        cmd="$cmd tests/features/"

        if eval "$cmd"; then
            print_success "BDD tests passed"
        else
            print_error "BDD tests failed"
            return 1
        fi
    fi
}

# Function to run all tests together (for combined coverage)
run_all_tests() {
    if [[ "$RUN_UNIT" == true && "$RUN_INTEGRATION" == true && "$RUN_BDD" == true ]]; then
        print_info "Running all tests with combined coverage..."

        local cmd
        cmd=$(build_pytest_cmd "all")
        cmd="$cmd tests/"

        if eval "$cmd"; then
            print_success "All tests passed"
        else
            print_error "Some tests failed"
            return 1
        fi
    fi
}

# Function to generate summary report
generate_summary() {
    print_info "Generating test summary..."

    local report_file="test_reports/summary.txt"
    {
        echo "Brazilian Soccer MCP Knowledge Graph - Test Summary"
        echo "=================================================="
        echo "Date: $(date)"
        echo "Environment: ${ENVIRONMENT:-development}"
        echo ""

        if [[ -f "test_reports/junit_unit.xml" ]]; then
            echo "Unit Tests: $(grep -o 'tests="[0-9]*"' test_reports/junit_unit.xml | cut -d'"' -f2) tests"
            echo "Unit Failures: $(grep -o 'failures="[0-9]*"' test_reports/junit_unit.xml | cut -d'"' -f2)"
        fi

        if [[ -f "test_reports/junit_integration.xml" ]]; then
            echo "Integration Tests: $(grep -o 'tests="[0-9]*"' test_reports/junit_integration.xml | cut -d'"' -f2) tests"
            echo "Integration Failures: $(grep -o 'failures="[0-9]*"' test_reports/junit_integration.xml | cut -d'"' -f2)"
        fi

        if [[ -f "test_reports/junit_bdd.xml" ]]; then
            echo "BDD Tests: $(grep -o 'tests="[0-9]*"' test_reports/junit_bdd.xml | cut -d'"' -f2) tests"
            echo "BDD Failures: $(grep -o 'failures="[0-9]*"' test_reports/junit_bdd.xml | cut -d'"' -f2)"
        fi

        echo ""
        if [[ "$HTML_REPORT" == true ]]; then
            echo "Coverage Reports:"
            find test_reports -name "index.html" | while read -r file; do
                echo "  - $(dirname "$file")/index.html"
            done
        fi

    } > "$report_file"

    cat "$report_file"
    print_success "Summary report generated: $report_file"
}

# Main execution
main() {
    print_info "Starting Brazilian Soccer MCP Knowledge Graph test suite"

    # Check prerequisites
    check_prerequisites

    # Clean cache if requested
    clean_cache

    # Setup test environment
    setup_test_env

    local exit_code=0

    # Run tests based on configuration
    if [[ "$RUN_UNIT" == true && "$RUN_INTEGRATION" == true && "$RUN_BDD" == true && "$RUN_COVERAGE" == true ]]; then
        # Run all tests together for combined coverage
        run_all_tests || exit_code=$?
    else
        # Run tests separately
        run_unit_tests || exit_code=$?
        run_integration_tests || exit_code=$?
        run_bdd_tests || exit_code=$?
    fi

    # Generate summary
    generate_summary

    if [[ $exit_code -eq 0 ]]; then
        print_success "🎉 All tests completed successfully!"
        if [[ "$HTML_REPORT" == true ]]; then
            print_info "📊 Coverage reports available in test_reports/ directory"
        fi
    else
        print_error "❌ Some tests failed. Check the reports for details."
    fi

    exit $exit_code
}

# Run main function
main "$@"