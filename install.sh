#!/bin/bash
set -e

echo "=== Autodarts Browser Installer ==="

# 1. Check for Python 3
if ! command -v python3 &> /dev/null; then
    echo "Error: python3 could not be found. Please install Python 3."
    exit 1
fi

# 2. Create Virtual Environment
echo "Creating virtual environment in .venv..."
python3 -m venv .venv

# 3. Activate Virtual Environment
echo "Activating virtual environment..."
source .venv/bin/activate

# 4. Install Dependencies
echo "Installing dependencies..."
pip install --upgrade pip
if [ -f "requirements.txt" ]; then
    pip install -r requirements.txt
else
    echo "Warning: requirements.txt not found. Skipping dependency installation."
fi

# 5. Config Setup (Optional)
if [ ! -f "config.ini" ]; then
    if [ -f "config_example.ini" ]; then
        echo "Creating config.ini from example..."
        cp config_example.ini config.ini
    else
        echo "No config.ini found. A default configuration will be created on first start."
    end
fi

echo ""
echo "=== Installation Complete! ==="
echo "You can now start the application with:"
echo "./start.sh"
echo ""
echo "Or manually:"
echo "source .venv/bin/activate"
echo "python darts-browser.py"
