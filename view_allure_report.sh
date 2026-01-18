#!/bin/bash

# ============================================================
# Allure Reports Generation and Viewing Script
# ============================================================

VENV_PATH="./venv"
PROJECT_ROOT="$(cd "$(dirname "$0")" && pwd)"

echo "============================================================"
echo "          ALLURE REPORTS - eBay LOGIN TEST"
echo "============================================================"
echo ""

# Check if allure-results exist
if [ -d "$PROJECT_ROOT/allure-results" ]; then
    echo "✅ Allure results directory found: $PROJECT_ROOT/allure-results/"
    echo ""
    
    # Count artifacts
    json_count=$(find "$PROJECT_ROOT/allure-results" -name "*.json" | wc -l)
    png_count=$(find "$PROJECT_ROOT/allure-results" -name "*.png" | wc -l)
    txt_count=$(find "$PROJECT_ROOT/allure-results" -name "*.txt" | wc -l)
    
    echo "📊 Allure Report Contents:"
    echo "   - JSON files (test results): $json_count"
    echo "   - PNG files (screenshots): $png_count"
    echo "   - TXT files (logs/metadata): $txt_count"
    echo "   - Total files: $(ls -1 $PROJECT_ROOT/allure-results | wc -l)"
    echo ""
    
    echo "📸 Screenshots Captured:"
    ls -1 $PROJECT_ROOT/allure-results/*-attachment.png 2>/dev/null | while read file; do
        filename=$(basename "$file")
        echo "   ✓ $filename"
    done
    echo ""
    
    echo "📝 Test Metadata:"
    ls -1 $PROJECT_ROOT/allure-results/*-result.json 2>/dev/null | while read file; do
        filename=$(basename "$file")
        echo "   ✓ $filename"
    done
    echo ""
    
else
    echo "❌ Allure results directory not found!"
    echo "   Run the test first: pytest tests/test_ebay_login_allure.py -v --alluredir=allure-results"
    exit 1
fi

# Check if allure is available
if command -v allure &> /dev/null; then
    echo "✅ Allure CLI is installed"
    echo ""
    echo "🚀 To view the HTML report, run:"
    echo "   allure serve allure-results/"
    echo ""
else
    echo "⚠️  Allure CLI not found in system PATH"
    echo "   Installing allure-commandline..."
    
    if [ -n "$VIRTUAL_ENV" ] || [ -d "$VENV_PATH" ]; then
        echo "   Attempting to activate venv and install allure..."
        if [ -d "$VENV_PATH" ]; then
            source "$VENV_PATH/bin/activate"
        fi
        
        pip install allure-commandline --quiet
        
        if command -v allure &> /dev/null; then
            echo "   ✅ Allure installed successfully!"
            echo ""
            echo "🚀 To view the HTML report, run:"
            echo "   allure serve allure-results/"
        fi
    fi
fi

echo ""
echo "============================================================"
echo "                    NEXT STEPS"
echo "============================================================"
echo ""
echo "1. Activate the virtual environment:"
echo "   source venv/bin/activate"
echo ""
echo "2. View the Allure report:"
echo "   allure serve allure-results/"
echo ""
echo "3. The report will open in your browser showing:"
echo "   ✓ Test results and status"
echo "   ✓ All test steps with timing"
echo "   ✓ Attached screenshots"
echo "   ✓ Error details (if any)"
echo "   ✓ Test history"
echo ""
echo "============================================================"
