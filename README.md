# ✝ Bible App

A simple Bible app for Linux with **Terminal Mode** and **GUI Mode**.

The GUI now includes an **Orthodox-focused browsing mode** (book → chapter → verse list), including deuterocanonical books available in the selected source.

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

- Use the **language dropdown** (Orthodox-focused sources)
- Use **Browse** controls: pick book, chapter, then click a verse
- Click **🎲 Random** for a random verse in the current source
- Type `John 3:16` and click **🔍 Look Up**

---

## 🌍 GUI Sources

| Flag | Source | Version ID | Scope in source |
|------|--------|------------|-----------------|
| 🇬🇧 | English (Orthodox - KJV with Deuterocanon) | `en-kjv` | Full 80-book canon in this dataset |
| 🇧🇷 | Português (João Ferreira de Almeida) | `almeida` | Public-domain Portuguese Bible |
| 🇸🇦 | العربية (Arabic - ONAV 2012) | `arb-kehm` | Arabic Bible source |

---

## 📁 Files

| File | What it does |
|------|-------------|
| `bible.py` | The whole app — terminal + GUI in one file |
| `bible.desktop` | Makes the app appear in your start menu |
| `install.sh` | One-command installer |
| `assets/bible-app.svg` | App icon used in the desktop menu |
| `SOURCES.md` | Source and licensing notes for bundled providers |

---

> *"Thy word is a lamp unto my feet, and a light unto my path."* — Psalm 119:105
