#!/bin/bash
# Install NFC Manager on Linux

APP_DIR="$HOME/.local/lib/nfc-manager"
BIN_DIR="$HOME/.local/bin"
DESKTOP_DIR="$HOME/.local/share/applications"
ICON_DIR="$HOME/.local/share/icons/hicolor"

echo "🚀 Installing NFC Manager..."

# 1. Copy files
mkdir -p "$APP_DIR"
cp -r acr122u_app/* "$APP_DIR/"

# 2. Create virtual environment
python3 -m venv "$APP_DIR/venv"
"$APP_DIR/venv/bin/pip" install -r requirements.txt

# 3. Wrapper script
mkdir -p "$BIN_DIR"
cat > "$BIN_DIR/nfc-manager" << EOF
#!/bin/bash
cd "$APP_DIR"
source venv/bin/activate
python main.py "\$@"
EOF
chmod +x "$BIN_DIR/nfc-manager"

# 4. Icon
mkdir -p "$ICON_DIR/scalable/apps"
cp nfc-manager.svg "$ICON_DIR/scalable/apps/"

# 5. .desktop file
mkdir -p "$DESKTOP_DIR"
cat > "$DESKTOP_DIR/nfc-manager.desktop" << EOF
[Desktop Entry]
Version=1.0
Type=Application
Name=NFC Manager
Name[ar]=مدير NFC
GenericName=NFC Card Manager
GenericName[ar]=مدير بطاقات NFC
Comment=Read, write and manage NFC cards with ACR122U
Comment[ar]=قراءة وكتابة وإدارة بطاقات NFC عبر ACR122U
Exec=$BIN_DIR/nfc-manager
Icon=nfc-manager
Categories=Utility;Security;System;
Keywords=NFC;RFID;ACR122U;card;password;
StartupWMClass=nfc-manager
StartupNotify=true
Terminal=false
EOF

# 6. Update caches
update-icon-caches "$ICON_DIR" 2>/dev/null || true
gtk-update-icon-cache "$ICON_DIR" 2>/dev/null || true
update-desktop-database "$DESKTOP_DIR" 2>/dev/null || true

echo "✅ Installation successful!"
echo "Run it with: nfc-manager"
