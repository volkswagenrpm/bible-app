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

BOOK_CHAPTERS = {
    "Genesis": 50, "Exodus": 40, "Leviticus": 27, "Numbers": 36, "Deuteronomy": 34,
    "Joshua": 24, "Judges": 21, "Ruth": 4, "1 Samuel": 31, "2 Samuel": 24,
    "1 Kings": 22, "2 Kings": 25, "1 Chronicles": 29, "2 Chronicles": 36, "Ezra": 10,
    "Nehemiah": 13, "Esther": 10, "Job": 42, "Psalms": 150, "Proverbs": 31,
    "Ecclesiastes": 12, "Song of Solomon": 8, "Isaiah": 66, "Jeremiah": 52, "Lamentations": 5,
    "Ezekiel": 48, "Daniel": 12, "Hosea": 14, "Joel": 3, "Amos": 9,
    "Obadiah": 1, "Jonah": 4, "Micah": 7, "Nahum": 3, "Habakkuk": 3,
    "Zephaniah": 3, "Haggai": 2, "Zechariah": 14, "Malachi": 4, "Matthew": 28,
    "Mark": 16, "Luke": 24, "John": 21, "Acts": 28, "Romans": 16,
    "1 Corinthians": 16, "2 Corinthians": 13, "Galatians": 6, "Ephesians": 6, "Philippians": 4,
    "Colossians": 4, "1 Thessalonians": 5, "2 Thessalonians": 3, "1 Timothy": 6, "2 Timothy": 4,
    "Titus": 3, "Philemon": 1, "Hebrews": 13, "James": 5, "1 Peter": 5,
    "2 Peter": 3, "1 John": 5, "2 John": 1, "3 John": 1, "Jude": 1, "Revelation": 22
}


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
        return {
            "reference": ref,
            "text": text,
            "translation": translation.upper(),
            "verses": verses,
        }
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
        self.current_book        = tk.StringVar(value="John")
        self.current_chapter     = tk.IntVar(value=3)
        self.verse_history       = []
        self.chapter_verses      = []

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

        # Browse controls (book -> chapter -> verses)
        browse_header = tk.Frame(self, bg="#0a2342", pady=6, padx=16)
        browse_header.pack(fill="x")
        tk.Label(browse_header, text="Browse:", bg="#0a2342", fg="#dce0ff",
                 font=self.small_font).pack(side="left", padx=(0, 6))
        self.book_combo = ttk.Combobox(
            browse_header,
            textvariable=self.current_book,
            values=list(BOOK_CHAPTERS.keys()),
            width=20,
            state="readonly",
            font=self.small_font
        )
        self.book_combo.pack(side="left", padx=(0, 6))
        self.book_combo.bind("<<ComboboxSelected>>", self._on_book_change)

        tk.Label(browse_header, text="Chapter:", bg="#0a2342", fg="#dce0ff",
                 font=self.small_font).pack(side="left", padx=(6, 4))
        self.chapter_spin = tk.Spinbox(
            browse_header, from_=1, to=150, textvariable=self.current_chapter,
            width=5, font=self.small_font, command=self.load_chapter
        )
        self.chapter_spin.pack(side="left", padx=(0, 6))
        self.chapter_spin.bind("<Return>", lambda e: self.load_chapter())
        self.chapter_spin.bind("<FocusOut>", lambda e: self.load_chapter())
        tk.Button(browse_header, text="Load Chapter", command=self.load_chapter, **btn_style).pack(side="left")

        # Main content split: verse list + verse display
        content_frame = tk.Frame(self, bg="#1a1a2e")
        content_frame.pack(fill="both", expand=True)

        list_frame = tk.Frame(content_frame, bg="#101a35", padx=10, pady=10)
        list_frame.pack(side="left", fill="y")
        tk.Label(list_frame, text="Verses", bg="#101a35", fg="#f0c040",
                 font=self.ref_font).pack(anchor="w", pady=(0, 6))
        self.verse_list = tk.Listbox(
            list_frame, width=36, height=18, bg="#0e1730", fg="#dce0ff",
            relief="flat", highlightthickness=1, highlightbackground="#274060",
            selectbackground="#f0c040", selectforeground="#1a1a2e",
            font=self.small_font
        )
        self.verse_list.pack(side="left", fill="y")
        self.verse_list.bind("<<ListboxSelect>>", self._on_verse_select)
        verse_scroll = tk.Scrollbar(list_frame, orient="vertical", command=self.verse_list.yview)
        verse_scroll.pack(side="left", fill="y")
        self.verse_list.config(yscrollcommand=verse_scroll.set)

        # Verse display area
        verse_frame = tk.Frame(content_frame, bg="#1a1a2e", padx=24, pady=24)
        verse_frame.pack(side="left", fill="both", expand=True)

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

        self._on_book_change()

    # ── Actions ─────────────────────────────────

    def _on_lang_change(self, _event=None):
        name = self.current_lang_name.get()
        if name == "العربية (Arabic)":
            self.current_translation.set("arabic")
        else:
            self.current_translation.set(LANGUAGES.get(name, {}).get("id", "kjv"))
        self.load_chapter()

    def _on_book_change(self, _event=None):
        book = self.current_book.get()
        max_ch = BOOK_CHAPTERS.get(book, 1)
        current = self.current_chapter.get()
        if current < 1:
            current = 1
        if current > max_ch:
            current = max_ch
        self.current_chapter.set(current)
        self.chapter_spin.config(to=max_ch)
        self.load_chapter()

    def load_chapter(self):
        book = self.current_book.get().strip()
        chapter = self.current_chapter.get()
        if not book:
            return

        self.verse_list.delete(0, "end")
        self.chapter_verses = []
        trans = self.current_translation.get()

        if trans == "arabic":
            self.status_var.set("Arabic browse mode is offline only (limited sample verses).")
            self.ref_label.config(text=f"{book} {chapter} [عربي]")
            self.verse_text.config(state="normal")
            self.verse_text.delete("1.0", "end")
            self.verse_text.insert("end", "Arabic browse mode is limited offline.\nUse search for included Arabic verses.")
            self.verse_text.config(state="disabled")
            return

        self.status_var.set(f"Loading {book} {chapter}...")
        self.update()
        data = fetch_verse(f"{book} {chapter}", trans)
        if "error" in data:
            self.status_var.set("Could not load chapter.")
            self.ref_label.config(text="⚠ Error")
            self.verse_text.config(state="normal")
            self.verse_text.delete("1.0", "end")
            self.verse_text.insert("end", data["error"])
            self.verse_text.config(state="disabled")
            return

        verses = data.get("verses", [])
        if not verses:
            self.status_var.set("No verses found for this chapter.")
            return

        self.chapter_verses = verses
        for verse in verses:
            number = verse.get("verse", "?")
            text = verse.get("text", "").strip().replace("\n", " ")
            preview = text[:72] + ("..." if len(text) > 72 else "")
            self.verse_list.insert("end", f"{number}. {preview}")

        self.status_var.set(f"Loaded {book} {chapter} ({len(verses)} verses)")
        self.verse_list.selection_set(0)
        self._on_verse_select()

    def _on_verse_select(self, _event=None):
        if not self.chapter_verses:
            return
        selected = self.verse_list.curselection()
        if not selected:
            return
        verse_data = self.chapter_verses[selected[0]]
        ref = f"{verse_data.get('book_name', self.current_book.get())} {verse_data.get('chapter', self.current_chapter.get())}:{verse_data.get('verse', '?')}"
        text = verse_data.get("text", "").strip()
        self._show_verse({
            "reference": ref,
            "text": text,
            "translation": self.current_translation.get().upper()
        })

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
