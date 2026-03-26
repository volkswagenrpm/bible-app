#!/usr/bin/env bash
# ─────────────────────────────────────────────────────
#  Bible App — GitHub Setup Script
#  Run this ONCE to push your code to GitHub
# ─────────────────────────────────────────────────────
set -e

GOLD='\033[1;33m'
BLUE='\033[1;34m'
GREEN='\033[1;32m'
RESET='\033[0m'

echo ""
echo -e "${GOLD}  ✝  Pushing Bible App to GitHub...${RESET}"
echo ""

# Initialize git if not already done
if [ ! -d ".git" ]; then
    git init
    echo -e "${BLUE}  → Git repository initialized${RESET}"
fi

# Set remote (update if already exists)
git remote remove origin 2>/dev/null || true
git remote add origin https://github.com/volkswagenrpm/bible-app.git
echo -e "${BLUE}  → Remote set to GitHub${RESET}"

# Add all files
git add .
echo -e "${BLUE}  → Files staged${RESET}"

# Commit
git commit -m "✝ Initial commit — Bible app with terminal + GUI + multilanguage" 2>/dev/null || \
git commit --allow-empty -m "✝ Update Bible app"
echo -e "${BLUE}  → Committed${RESET}"

# Push
git branch -M main
git push -u origin main
echo ""
echo -e "${GREEN}  ✅ Pushed to GitHub!${RESET}"
echo -e "  🌐 https://github.com/volkswagenrpm/bible-app"
echo ""
