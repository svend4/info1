#!/bin/bash
#
# AI Generator Toolkit - Benchmark Runner
#

set -e

echo "====================================================================="
echo "  AI Generator Toolkit - Performance Benchmarks"
echo "====================================================================="
echo ""

# Create reports directory
mkdir -p reports/benchmarks

# Run benchmarks
python benchmarks/run_all_benchmarks.py

echo ""
echo "====================================================================="
echo "  Reports Generated"
echo "====================================================================="
echo ""
echo "📄 JSON Report: reports/benchmarks/benchmark-report.json"
echo "📄 HTML Report: reports/benchmarks/benchmark-report.html"
echo ""
echo "To view HTML report:"
echo "  open reports/benchmarks/benchmark-report.html"
echo ""
