#!/usr/bin/env python3
"""
Bible App - Terminal & GUI Mode
A simple Bible app for reading and looking up verses.
Works as a terminal command and as a windowed application.
"""

import sys
import os
import random
import json
import urllib.request
import urllib.parse
import tkinter as tk
from tkinter import ttk, messagebox, font as tkfont

# ─────────────────────────────────────────────
#  BIBLE API — uses api.esv.org for English and
#  scripture.api.bible for other languages via
#  bible-api.com (free, no key needed)
# ─────────────────────────────────────────────

LANGUAGES = {
    "English (KJV)":        {"id": "kjv",          "flag": "🇺🇸"},
    "English (NIV)":        {"id": "web",           "flag": "🇺🇸"},
    "Português (ARC)":      {"id": "almeida",       "flag": "🇧🇷"},
    "Português (NVI-PT)":   {"id": "nvi",           "flag": "🇵🇹"},
    "Español":              {"id": "rvr1960",        "flag": "🇪🇸"},
    "Français":             {"id": "ls1910",         "flag": "🇫🇷"},
    "Deutsch":              {"id": "luther1912",     "flag": "🇩🇪"},
    "Italiano":             {"id": "giovanni",       "flag": "🇮🇹"},
    "Română":               {"id": "cornilescu",     "flag": "🇷🇴"},
    "Nederlands":           {"id": "statenvertaling","flag": "🇳🇱"},
    "Русский":              {"id": "sinodal",        "flag": "🇷🇺"},
    "中文 (Chinese CUV)":   {"id": "cunpss-shangdi", "flag": "🇨🇳"},
    "한국어 (Korean)":      {"id": "korean",         "flag": "🇰🇷"},
    "Tagalog":              {"id": "tagalog",        "flag": "🇵🇭"},
    "Swahili":              {"id": "swahili",        "flag": "🇹🇿"},
    "Bislama":              {"id": "bislama",        "flag": "🇻🇺"},
    "Tok Pisin":            {"id": "tok-pisin",      "flag": "🇵🇬"},
}

# Arabic uses a separate public domain source
ARABIC_VERSES = [
    ("يوحنا 3:16", "لأنه هكذا أحب الله العالم حتى بذل ابنه الوحيد، لكي لا يهلك كل من يؤمن به، بل تكون له الحياة الأبدية."),
    ("مزامير 23:1", "الرَّبُّ رَاعِيَّ فَلاَ يُعْوِزُنِي شَيْءٌ."),
    ("أمثال 3:5-6", "اتَّكِلْ عَلَى الرَّبِّ بِكُلِّ قَلْبِكَ، وَلاَ تَسْتَنِدْ إِلَى فَهْمِكَ الْخَاصِّ. فِي كُلِّ طُرُقِكَ اعْتَرِفْ بِهِ، وَهُوَ يُقَوِّمُ سُبُلَكَ."),
    ("فيلبي 4:13", "أَسْتَطِيعُ كُلَّ شَيْءٍ فِي الْمَسِيحِ الَّذِي يُقَوِّينِي."),
    ("إرميا 29:11", "لأَنِّي أَعْرِفُ الأَفْكَارَ الَّتِي أَنَا مُفَكِّرٌ بِهَا عَنْكُمْ، يَقُولُ الرَّبُّ، أَفْكَارَ سَلاَمٍ لاَ شَرٍّ، لأُعْطِيَكُمْ آخِرَةً وَرَجَاءً."),
]

RANDOM_VERSES = [
    "John 3:16", "Psalms 23:1", "Proverbs 3:5", "Romans 8:28",
    "Philippians 4:13", "Jeremiah 29:11", "Isaiah 40:31",
    "Matthew 5:3", "John 14:6", "Romans 6:23", "Ephesians 2:8",
    "Matthew 28:19", "1 Corinthians 13:4", "Galatians 5:22",
    "Hebrews 11:1", "James 1:2", "1 Peter 5:7", "Revelation 21:4",
    "Genesis 1:1", "Exodus 20:3", "Deuteronomy 6:5", "Joshua 1:9",
    "Psalms 119:105", "Proverbs 22:6", "Isaiah 53:5", "John 1:1",
    "Acts 2:38", "Romans 3:23", "Romans 5:8", "1 John 4:8",
]

def fetch_verse(reference: str, translation: str = "kjv") -> dict:
    """Fetch a Bible verse from bible-api.com (free, no API key needed)."""
    encoded_ref = urllib.parse.quote(reference)
    url = f"https://bible-api.com/{encoded_ref}?translation={translation}"
    try:
        req = urllib.request.Request(url, headers={"User-Agent": "BibleApp/1.0"})
        with urllib.request.urlopen(req, timeout=8) as resp:
            data = json.loads(resp.read().decode())
        if "error" in data:
            return {"error": data["error"]}
        verses = data.get("verses", [])
        text = " ".join(v["text"].strip() for v in verses)
        ref = data.get("reference", reference)
        return {"reference": ref, "text": text, "translation": translation.upper()}
    except Exception as e:
        return {"error": f"Could not connect: {e}"}


def get_random_verse(translation: str = "kjv") -> dict:
    ref = random.choice(RANDOM_VERSES)
    return fetch_verse(ref, translation)


# ─────────────────────────────────────────────
#  TERMINAL MODE
# ─────────────────────────────────────────────

COLORS = {
    "gold":  "\033[38;5;220m",
    "blue":  "\033[38;5;75m",
    "green": "\033[38;5;114m",
    "gray":  "\033[38;5;245m",
    "bold":  "\033[1m",
    "reset": "\033[0m",
    "dim":   "\033[2m",
}

def c(color, text):
    return f"{COLORS.get(color,'')}{text}{COLORS['reset']}"

def print_verse(verse_data: dict):
    if "error" in verse_data:
        print(c("gray", f"  ⚠  {verse_data['error']}"))
        return
    ref = verse_data.get("reference", "")
    text = verse_data.get("text", "")
    trans = verse_data.get("translation", "")
    print()
    print(c("gold", "  ✝  ") + c("bold", ref) + c("dim", f"  [{trans}]"))
    print(c("gray", "  " + "─" * 50))
    # Word-wrap at 60 chars
    words = text.split()
    line = "  "
    for word in words:
        if len(line) + len(word) + 1 > 64:
            print(c("blue", line))
            line = "  " + word + " "
        else:
            line += word + " "
    if line.strip():
        print(c("blue", line))
    print()

def terminal_mode(args):
    print()
    print(c("gold", "  ✝  ") + c("bold", "Bible — Word of God") + c("gray", "  (type 'bible --help' for help)"))
    print()

    if not args:
        # Random verse
        print(c("gray", "  Fetching a random verse..."))
        print_verse(get_random_verse())
        return

    if args[0] in ("--help", "-h", "help"):
        print(c("green", "  USAGE:"))
        print(c("gray",  "    bible                        — random verse (English KJV)"))
        print(c("gray",  "    bible <reference>             — specific verse, e.g: bible John 3:16"))
        print(c("gray",  "    bible <reference> -l <lang>  — with language, e.g: bible John 3:16 -l almeida"))
        print(c("gray",  "    bible --gui                  — open the windowed app"))
        print(c("gray",  "    bible --languages            — list all supported languages"))
        print()
        return

    if args[0] == "--gui":
        gui_mode()
        return

    if args[0] == "--languages":
        print(c("green", "  Available translations:"))
        for name, info in LANGUAGES.items():
            print(f"    {info['flag']}  {c('gold', info['id']):30s}  {c('gray', name)}")
        print(c("gray", "\n  Arabic is built-in (offline). Use: bible --arabic"))
        print()
        return

    if args[0] == "--arabic":
        ref, text = random.choice(ARABIC_VERSES)
        print()
        print(c("gold", "  ✝  ") + c("bold", ref) + c("dim", "  [عربي]"))
        print(c("gray", "  " + "─" * 50))
        print(c("blue", "  " + text))
        print()
        return

    # Check for -l / --language flag
    translation = "kjv"
    if "-l" in args:
        idx = args.index("-l")
        if idx + 1 < len(args):
            translation = args[idx + 1]
            args = args[:idx] + args[idx+2:]
    elif "--lang" in args:
        idx = args.index("--lang")
        if idx + 1 < len(args):
            translation = args[idx + 1]
            args = args[:idx] + args[idx+2:]

    reference = " ".join(args)
    print(c("gray", f"  Looking up: {reference}  [{translation}]..."))
    print_verse(fetch_verse(reference, translation))


# ─────────────────────────────────────────────
#  GUI MODE
# ─────────────────────────────────────────────

class BibleApp(tk.Tk):
    def __init__(self):
        super().__init__()
        self.title("✝ Bible")
        self.geometry("720x560")
        self.configure(bg="#1a1a2e")
        self.resizable(True, True)
        self.minsize(500, 400)

        # Fonts
        try:
            self.title_font  = tkfont.Font(family="Georgia",     size=18, weight="bold")
            self.verse_font  = tkfont.Font(family="Georgia",     size=14)
            self.ref_font    = tkfont.Font(family="Georgia",     size=11, slant="italic")
            self.btn_font    = tkfont.Font(family="Helvetica",   size=10, weight="bold")
            self.small_font  = tkfont.Font(family="Helvetica",   size=9)
        except Exception:
            self.title_font  = tkfont.Font(size=18, weight="bold")
            self.verse_font  = tkfont.Font(size=14)
            self.ref_font    = tkfont.Font(size=11, slant="italic")
            self.btn_font    = tkfont.Font(size=10, weight="bold")
            self.small_font  = tkfont.Font(size=9)

        self.current_translation = tk.StringVar(value="kjv")
        self.current_lang_name   = tk.StringVar(value="English (KJV)")
        self.search_var          = tk.StringVar()
        self.verse_history       = []

        self._build_ui()
        self.after(200, self.load_random)

    # ── UI Builder ──────────────────────────────

    def _build_ui(self):
        # Header
        hdr = tk.Frame(self, bg="#16213e", pady=10)
        hdr.pack(fill="x")
        tk.Label(hdr, text="✝  Holy Bible", font=self.title_font,
                 bg="#16213e", fg="#f0c040").pack(side="left", padx=20)

        # Language selector
        lang_frame = tk.Frame(hdr, bg="#16213e")
        lang_frame.pack(side="right", padx=20)
        tk.Label(lang_frame, text="Language:", bg="#16213e", fg="#aaaacc",
                 font=self.small_font).pack(side="left", padx=(0,4))
        lang_names = list(LANGUAGES.keys()) + ["العربية (Arabic)"]
        self.lang_combo = ttk.Combobox(lang_frame, textvariable=self.current_lang_name,
                                       values=lang_names, width=20, state="readonly",
                                       font=self.small_font)
        self.lang_combo.pack(side="left")
        self.lang_combo.bind("<<ComboboxSelected>>", self._on_lang_change)

        # Search bar
        search_frame = tk.Frame(self, bg="#0f3460", pady=8, padx=16)
        search_frame.pack(fill="x")
        self.search_entry = tk.Entry(search_frame, textvariable=self.search_var,
                                     bg="#1a1a2e", fg="#e0e0ff", insertbackground="#f0c040",
                                     relief="flat", font=self.verse_font, width=30)
        self.search_entry.pack(side="left", fill="x", expand=True, ipady=4)
        self.search_entry.bind("<Return>", lambda e: self.search_verse())
        tk.Label(search_frame, text="e.g.  John 3:16  or  Psalms 23:1",
                 bg="#0f3460", fg="#667799", font=self.small_font).pack(side="left", padx=8)

        btn_style = {"bg": "#f0c040", "fg": "#1a1a2e", "relief": "flat",
                     "font": self.btn_font, "cursor": "hand2", "padx": 10, "pady": 4}
        tk.Button(search_frame, text="🔍 Look Up",  command=self.search_verse, **btn_style).pack(side="left", padx=4)
        tk.Button(search_frame, text="🎲 Random",   command=self.load_random,  **btn_style).pack(side="left", padx=4)

        # Verse display area
        verse_frame = tk.Frame(self, bg="#1a1a2e", padx=30, pady=24)
        verse_frame.pack(fill="both", expand=True)

        self.ref_label = tk.Label(verse_frame, text="", font=self.ref_font,
                                  bg="#1a1a2e", fg="#f0c040", anchor="w")
        self.ref_label.pack(fill="x", pady=(0, 8))

        separator = tk.Frame(verse_frame, bg="#f0c040", height=1)
        separator.pack(fill="x", pady=(0, 16))

        self.verse_text = tk.Text(verse_frame, wrap="word", font=self.verse_font,
                                  bg="#1a1a2e", fg="#dce0ff", relief="flat",
                                  state="disabled", cursor="arrow",
                                  padx=0, pady=0, spacing3=4,
                                  selectbackground="#f0c040", selectforeground="#1a1a2e")
        self.verse_text.pack(fill="both", expand=True)

        # Status bar
        self.status_var = tk.StringVar(value="Welcome! Click 'Random' for a verse.")
        status_bar = tk.Label(self, textvariable=self.status_var,
                              bg="#0a0a1a", fg="#556677", font=self.small_font,
                              anchor="w", padx=12, pady=4)
        status_bar.pack(fill="x", side="bottom")

    # ── Actions ─────────────────────────────────

    def _on_lang_change(self, _event=None):
        name = self.current_lang_name.get()
        if name == "العربية (Arabic)":
            self.current_translation.set("arabic")
        else:
            self.current_translation.set(LANGUAGES.get(name, {}).get("id", "kjv"))

    def _show_verse(self, data: dict):
        self.verse_text.config(state="normal")
        self.verse_text.delete("1.0", "end")
        if "error" in data:
            self.ref_label.config(text="⚠ Error")
            self.verse_text.insert("end", data["error"])
            self.status_var.set("Could not load verse.")
        else:
            ref   = data.get("reference", "")
            text  = data.get("text", "")
            trans = data.get("translation", "")
            self.ref_label.config(text=f"{ref}   [{trans}]")
            self.verse_text.insert("end", text)
            self.status_var.set(f"Loaded: {ref}  ·  {trans}")
            self.verse_history.append(data)
        self.verse_text.config(state="disabled")

    def load_random(self):
        trans = self.current_translation.get()
        self.status_var.set("Fetching a random verse…")
        self.update()
        if trans == "arabic":
            ref, text = random.choice(ARABIC_VERSES)
            self._show_verse({"reference": ref, "text": text, "translation": "عربي"})
        else:
            self._show_verse(get_random_verse(trans))

    def search_verse(self):
        ref = self.search_var.get().strip()
        if not ref:
            messagebox.showinfo("Bible", "Please type a verse reference first!\nExample: John 3:16")
            return
        trans = self.current_translation.get()
        self.status_var.set(f"Looking up {ref}…")
        self.update()
        if trans == "arabic":
            # Try to find in built-in Arabic, else fall back to KJV
            for arabic_ref, arabic_text in ARABIC_VERSES:
                if ref.lower() in arabic_ref.lower():
                    self._show_verse({"reference": arabic_ref, "text": arabic_text, "translation": "عربي"})
                    return
            self._show_verse({"error": "Arabic verse not found offline. Try another reference."})
        else:
            self._show_verse(fetch_verse(ref, trans))


def gui_mode():
    app = BibleApp()
    app.mainloop()


# ─────────────────────────────────────────────
#  ENTRY POINT
# ─────────────────────────────────────────────

if __name__ == "__main__":
    args = sys.argv[1:]

    # If launched with --gui or no args but detected as GUI launch (from .desktop file)
    if "--gui" in args or os.environ.get("BIBLE_GUI") == "1":
        gui_mode()
    else:
        terminal_mode(args)
