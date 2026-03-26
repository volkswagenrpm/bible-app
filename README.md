# ✝ Bible App

A simple, beautiful Bible app for Linux with **Terminal Mode** and **GUI Mode**. Supports 17+ languages including English, Português, Arabic, Español, Français, and more.

---

## 🚀 Install — One Command

```bash
git clone https://github.com/volkswagenrpm/bible-app.git && cd bible-app && bash install.sh
```

> This installs everything automatically — Python, tkinter, the `bible` terminal command, and adds Bible to your app start menu.

---

## 📖 How to Use

### Terminal

```bash
# Random verse (English KJV)
bible

# Look up a specific verse
bible John 3:16

# Portuguese 🇧🇷
bible John 3:16 -l almeida

# Arabic 🇸🇦
bible --arabic

# See all languages
bible --languages

# Open the window app
bible --gui
```

### GUI

Click **Bible** in your start menu, or type `bible --gui` in terminal.

- Use the **dropdown** to pick your language
- Click **🎲 Random** for a surprise verse
- Type a reference like `John 3:16` and click **🔍 Look Up**

---

## 🌍 Supported Languages

| Flag | Language | Translation ID |
|------|----------|---------------|
| 🇺🇸 | English (KJV) | `kjv` |
| 🇺🇸 | English (WEB) | `web` |
| 🇧🇷 | Português - Brasil (ARC) | `almeida` |
| 🇵🇹 | Português - Portugal (NVI) | `nvi` |
| 🇸🇦 | العربية (Arabic) | `--arabic` |
| 🇪🇸 | Español | `rvr1960` |
| 🇫🇷 | Français | `ls1910` |
| 🇩🇪 | Deutsch | `luther1912` |
| 🇮🇹 | Italiano | `giovanni` |
| 🇷🇴 | Română | `cornilescu` |
| 🇳🇱 | Nederlands | `statenvertaling` |
| 🇷🇺 | Русский | `sinodal` |
| 🇨🇳 | 中文 | `cunpss-shangdi` |
| 🇰🇷 | 한국어 | `korean` |
| 🇵🇭 | Tagalog | `tagalog` |
| 🇹🇿 | Swahili | `swahili` |

---

## 📁 Files

| File | What it does |
|------|-------------|
| `bible.py` | The whole app — terminal + GUI in one file |
| `bible.desktop` | Makes the app appear in your start menu |
| `install.sh` | One-command installer |

---

> *"Thy word is a lamp unto my feet, and a light unto my path."* — Psalm 119:105
