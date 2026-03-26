#!/usr/bin/env bash
# ─────────────────────────────────────────────────────
#  Bible App — One-Command Installer for Arch Linux
# ─────────────────────────────────────────────────────
set -e

BLUE='\033[1;34m'
GOLD='\033[1;33m'
GREEN='\033[1;32m'
RED='\033[1;31m'
RESET='\033[0m'

echo ""
echo -e "${GOLD}  ✝  Bible App Installer${RESET}"
echo -e "${BLUE}  ─────────────────────────────────${RESET}"

# 1. Install dependencies automatically
echo -e "${BLUE}  → Installing dependencies (python, tk, git)...${RESET}"
if command -v pacman &> /dev/null; then
    sudo pacman -S --noconfirm --needed python tk git
elif command -v apt &> /dev/null; then
    sudo apt install -y python3 python3-tk git
elif command -v dnf &> /dev/null; then
    sudo dnf install -y python3 python3-tkinter git
else
    echo -e "${RED}  ⚠ Could not detect your Linux type. Please install python3, tk, and git manually.${RESET}"
fi

# 2. Make the main script executable
echo -e "${BLUE}  → Making bible.py executable...${RESET}"
chmod +x bible.py

# 2. Copy to /usr/local/bin so 'bible' works as a command
echo -e "${BLUE}  → Installing 'bible' command...${RESET}"
sudo cp bible.py /usr/local/bin/bible
sudo chmod +x /usr/local/bin/bible

# 3. Set up the .desktop entry (adds to app menu)
echo -e "${BLUE}  → Adding to app menu...${RESET}"
mkdir -p ~/.local/share/applications
cp bible.desktop ~/.local/share/applications/bible.desktop

# 3b. Install icon
echo -e "${BLUE}  → Installing app icon...${RESET}"
mkdir -p ~/.local/share/icons/hicolor/scalable/apps
cp assets/bible-app.svg ~/.local/share/icons/hicolor/scalable/apps/bible-app.svg

# Update the Exec path to point to /usr/local/bin/bible
sed -i 's|Exec=.*|Exec=bible --gui|' ~/.local/share/applications/bible.desktop
sed -i "s|Icon=.*|Icon=${HOME}/.local/share/icons/hicolor/scalable/apps/bible-app.svg|" ~/.local/share/applications/bible.desktop

# 4. Try to update icon cache
if command -v gtk-update-icon-cache &> /dev/null; then
    gtk-update-icon-cache -f -t ~/.local/share/icons/hicolor 2>/dev/null || true
fi

# 5. Refresh desktop database
if command -v update-desktop-database &> /dev/null; then
    update-desktop-database ~/.local/share/applications/ 2>/dev/null || true
fi

echo ""
echo -e "${GREEN}  ✅ Done! Bible App is installed!${RESET}"
echo ""
echo -e "  ${GOLD}Commands you can now run:${RESET}"
echo -e "    ${BLUE}bible${RESET}              — random verse"
echo -e "    ${BLUE}bible John 3:16${RESET}    — look up a specific verse"
echo -e "    ${BLUE}bible --gui${RESET}        — open the windowed app"
echo -e "    ${BLUE}bible --languages${RESET}  — list all supported languages"
echo -e "    ${BLUE}bible --arabic${RESET}     — random Arabic verse"
echo ""
echo -e "  The app also appears in your ${GOLD}start menu${RESET} as '${GOLD}Bible${RESET}'."
echo ""
