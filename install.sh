#!/bin/bash
set -e

echo "=== Autodarts Browser Installer ==="

# 0. Check for C Compiler (needed for some python packages like netifaces)
if ! command -v gcc &> /dev/null; then
    echo "Warning: gcc (C compiler) not found. Required for installing dependencies."
    read -p "Attempt to install build tools automatically? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v pacman &> /dev/null; then
            echo "Detected Arch/Manjaro. Installing base-devel..."
            sudo pacman -S --needed base-devel
        elif command -v apt-get &> /dev/null; then
            echo "Detected Debian/Ubuntu. Installing build-essential and python3-dev..."
            sudo apt-get update && sudo apt-get install -y build-essential python3-dev
        else
            echo "Error: Could not detect package manager. Please install 'gcc' / build tools manually."
            exit 1
        fi
    else
        echo "Aborting installation. Please install build tools manually."
        exit 1
    fi
fi

# 0b. Optional: Check for unclutter (hide mouse cursor)
if ! command -v unclutter &> /dev/null; then
    echo "Optional: 'unclutter' is not installed. It is recommended for hiding the mouse cursor."
    read -p "Install 'unclutter' now? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        if command -v pacman &> /dev/null; then
            echo "Installing unclutter..."
            sudo pacman -S --needed unclutter
        elif command -v apt-get &> /dev/null; then
            echo "Installing unclutter..."
            sudo apt-get update && sudo apt-get install -y unclutter
        else
            echo "Warning: Could not detect package manager. Skipping 'unclutter' installation."
        fi
    fi
fi

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
    fi
fi

# 6. Generate Desktop Entry
echo "Generating autodarts-browser.desktop..."
CURRENT_DIR=$(pwd)
START_SCRIPT="$CURRENT_DIR/start.sh"

cat > autodarts-browser.desktop <<EOF
[Desktop Entry]
Type=Application
Name=Autodarts-Browser
Comment=Der Autodarts-Browser
Exec=$START_SCRIPT
StartupNotify=false
Terminal=false
Hidden=false
EOF

chmod +x autodarts-browser.desktop
echo "Created 'autodarts-browser.desktop' in the current directory."

# 7. Optional: Install to Autostart
if [ -d "$HOME/.config/autostart" ]; then
    read -p "Do you want to install the autostart entry to ~/.config/autostart? (y/N) " -n 1 -r
    echo
    if [[ $REPLY =~ ^[Yy]$ ]]; then
        cp autodarts-browser.desktop "$HOME/.config/autostart/"
        echo "Autostart entry installed."
    fi
else
    echo "Autostart directory not found ($HOME/.config/autostart). You can copy the .desktop file manually if needed."
fi

echo ""
echo "=== Installation Complete! ==="
echo "You can now start the application with:"
echo "./start.sh"
echo ""
echo "Or manually:"
echo "source .venv/bin/activate"
echo "python darts-browser.py"
