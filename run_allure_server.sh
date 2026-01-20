#!/bin/bash

# Script to serve Allure reports via HTTP server
# Usage: ./run_allure_server.sh [PORT] [TIMESTAMP]
# Example: ./run_allure_server.sh 8000 20260119_225031

PORT=${1:-8000}
TIMESTAMP=${2:-$(ls -td automation/reports/20260119_* 2>/dev/null | head -1 | xargs basename)}

REPORT_DIR="automation/reports/$TIMESTAMP/allure-report"

if [ ! -d "$REPORT_DIR" ]; then
    echo "❌ Report directory not found: $REPORT_DIR"
    echo ""
    echo "Available reports:"
    ls -d automation/reports/20260119_* 2>/dev/null | while read dir; do
        echo "  - $(basename $dir)"
    done
    exit 1
fi

echo "🚀 Starting HTTP server for Allure report"
echo "📊 Report: $REPORT_DIR"
echo "🌐 URL: http://localhost:$PORT"
echo ""
echo "Press Ctrl+C to stop the server"
echo ""

cd "$REPORT_DIR"
python3 -m http.server $PORT
