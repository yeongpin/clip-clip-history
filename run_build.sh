#!/bin/bash

echo "Building ClipClip History..."

# Detect OS
OS="unknown"
case "$(uname -s)" in
    Darwin*)    OS="mac";;
    Linux*)     OS="linux";;
    *)          echo "Unsupported OS"; exit 1;;
esac

# Check if Python is installed
if ! command -v python3 &> /dev/null; then
    echo "Error: Python 3 is not installed"
    exit 1
fi

# Create and activate virtual environment
python3 -m venv venv
source venv/bin/activate

# Install requirements
echo "Installing requirements..."
pip install -r requirements.txt
pip install pyinstaller python-dotenv

# Clean previous builds
echo "Cleaning previous builds..."
rm -rf build dist

# Build executable
echo "Building executable..."
pyinstaller ClipClip.spec

if [ "$OS" = "mac" ]; then
    # Create DMG for macOS
    echo "Creating DMG..."
    
    # Get version from .env
    VERSION=$(grep "version" .env | cut -d'=' -f2 | tr -d ' ')
    DMG_NAME="ClipClip-${VERSION}-mac.dmg"
    
    # Create temporary directory for DMG
    TEMP_DMG="./dist/dmg_temp"
    mkdir -p "$TEMP_DMG"
    
    # Copy application bundle
    cp -r "dist/ClipClip-${VERSION}-mac" "$TEMP_DMG/ClipClip.app"
    
    # Create symbolic link to Applications folder
    ln -s /Applications "$TEMP_DMG/Applications"
    
    # Create DMG
    hdiutil create -volname "ClipClip" -srcfolder "$TEMP_DMG" -ov -format UDZO "dist/$DMG_NAME"
    
    # Clean up
    rm -rf "$TEMP_DMG"
    
elif [ "$OS" = "linux" ]; then
    # Create Debian package for Linux
    echo "Creating DEB package..."
    
    # Get version from .env
    VERSION=$(grep "version" .env | cut -d'=' -f2 | tr -d ' ')
    
    # Create package structure
    PKG_ROOT="./dist/linux_pkg"
    mkdir -p "$PKG_ROOT/DEBIAN"
    mkdir -p "$PKG_ROOT/usr/local/bin"
    mkdir -p "$PKG_ROOT/usr/share/applications"
    mkdir -p "$PKG_ROOT/usr/share/icons/hicolor/scalable/apps"
    
    # Copy executable
    cp "dist/ClipClip-${VERSION}-linux" "$PKG_ROOT/usr/local/bin/clipclip"
    chmod +x "$PKG_ROOT/usr/local/bin/clipclip"
    
    # Copy icon
    cp "src/resources/clip_clip_icon.svg" "$PKG_ROOT/usr/share/icons/hicolor/scalable/apps/clipclip.svg"
    
    # Create desktop entry
    cat > "$PKG_ROOT/usr/share/applications/clipclip.desktop" << EOF
[Desktop Entry]
Name=ClipClip
Exec=/usr/local/bin/clipclip
Icon=clipclip
Type=Application
Categories=Utility;
EOF
    
    # Create control file
    cat > "$PKG_ROOT/DEBIAN/control" << EOF
Package: clipclip
Version: $VERSION
Section: utils
Priority: optional
Architecture: amd64
Maintainer: $(grep "author" .env | cut -d'=' -f2 | tr -d ' ')
Description: Clipboard History Manager
 A lightweight clipboard history tool that supports
 text, images, videos, and files.
EOF
    
    # Build package
    dpkg-deb --build "$PKG_ROOT" "dist/clipclip-${VERSION}-amd64.deb"
    
    # Clean up
    rm -rf "$PKG_ROOT"
fi

echo "Build complete!"
if [ "$OS" = "mac" ]; then
    echo "DMG installer can be found in the dist folder"
elif [ "$OS" = "linux" ]; then
    echo "DEB package can be found in the dist folder"
fi

# Deactivate virtual environment
deactivate 