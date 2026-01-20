#!/bin/bash
# View Latest Allure Report
# =========================
# Opens the most recent Allure HTML report with HTTP server

# Get the latest report directory
REPORTS_DIR="automation/reports"
LATEST_DIR=$(ls -dt $REPORTS_DIR/*/ 2>/dev/null | grep -v "allure-results" | head -1)

if [ -z "$LATEST_DIR" ]; then
    echo "❌ No reports found in $REPORTS_DIR"
    exit 1
fi

REPORT_PATH="${LATEST_DIR}allure-report"

if [ ! -d "$REPORT_PATH" ]; then
    echo "❌ No allure-report found in $LATEST_DIR"
    echo "💡 Run pytest first to generate reports"
    exit 1
fi

echo "📊 Opening latest Allure report..."
echo "📁 Location: $REPORT_PATH"
echo ""
echo "🌐 Server will start at: http://localhost:8000"
echo "🔴 Press Ctrl+C to stop the server"
echo ""

# Start HTTP server
python3 -m http.server 8000 --directory "$REPORT_PATH"
