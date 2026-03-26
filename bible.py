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
import traceback
import urllib.request
import urllib.parse

try:
    import tkinter as tk
    from tkinter import ttk, messagebox, font as tkfont
    TK_AVAILABLE = True
    TK_IMPORT_ERROR = None
except Exception as e:
    tk = None
    ttk = None
    messagebox = None
    tkfont = None
    TK_AVAILABLE = False
    TK_IMPORT_ERROR = e

# ─────────────────────────────────────────────
#  SOURCES
#  - GUI: wldeh/bible-api JSON dataset via jsDelivr + GitHub contents API
#  - Terminal quick lookup: bible-api.com endpoint
# ─────────────────────────────────────────────

ORTHODOX_LANGUAGES = {
    "English (Orthodox - KJV with Deuterocanon)": {
        "provider": "wldeh",
        "version": "en-kjv",
        "flag": "🇬🇧",
        "notes": "Full 80-book canon available in this source (public data via wldeh/bible-api).",
    },
    "Português (João Ferreira de Almeida)": {
        "provider": "bible_api",
        "version": "almeida",
        "flag": "🇧🇷",
        "notes": "Public-domain Portuguese Almeida text.",
    },
    "العربية (Arabic - ONAV 2012)": {
        "provider": "wldeh",
        "version": "arb-kehm",
        "flag": "🇸🇦",
        "notes": "Arabic official text source available online.",
    },
}

DEFAULT_GUI_LANGUAGE = "English (Orthodox - KJV with Deuterocanon)"
GITHUB_CONTENTS_BASE = "https://api.github.com/repos/wldeh/bible-api/contents/bibles"
BIBLE_TEXT_BASE = "https://cdn.jsdelivr.net/gh/wldeh/bible-api/bibles"
BIBLE_API_DATA_BASE = "https://bible-api.com/data"

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

PRAYER_ORDER = [
    "coptic_sixth_hour_3pm",
    "lords_prayer",
    "jesus_prayer",
    "trisagion",
    "before_sleep",
    "morning_offering",
    "thanksgiving",
    "purity",
    "protection",
    "mercy",
]

PRAYERS = {
    "coptic_sixth_hour_3pm": {
        "title": {
            "en": "Coptic Orthodox — Sixth Hour (3 PM)",
            "ar": "الأجبية القبطية الأرثوذكسية — الساعة السادسة (3 مساءً)",
            "pt": "Ortodoxa Copta — Sexta Hora (3 da tarde)",
        },
        "text": {
            "en": """O You who on the sixth hour were nailed to the Cross for us:
put to death our sinful passions, and purify our hearts.

Remember us, O Lord, when You come into Your Kingdom.
Remember us, O Holy One, when You come into Your Kingdom.
Remember us, O Master, when You come into Your Kingdom.

Lord Jesus Christ, Son of God, have mercy on me, a sinner.
Amen.""",
            "ar": """يا من في الساعة السادسة سُمّرت على الصليب من أجلنا:
أمت أهواءنا الجسدية، وطهّر قلوبنا.

اذكرنا يا رب متى جئت في ملكوتك.
اذكرنا يا قدوس متى جئت في ملكوتك.
اذكرنا يا سيد متى جئت في ملكوتك.

يا رب يسوع المسيح ابن الله ارحمني أنا الخاطئ.
آمين.""",
            "pt": """Ó Tu que na sexta hora foste pregado na Cruz por nós:
mata as nossas paixões pecaminosas e purifica os nossos corações.

Lembra-Te de nós, Senhor, quando vieres no Teu Reino.
Lembra-Te de nós, ó Santo, quando vieres no Teu Reino.
Lembra-Te de nós, ó Mestre, quando vieres no Teu Reino.

Senhor Jesus Cristo, Filho de Deus, tem misericórdia de mim, pecador.
Amém.""",
        },
    },
    "lords_prayer": {
        "title": {"en": "The Lord's Prayer", "ar": "الصلاة الربانية", "pt": "Pai Nosso"},
        "text": {
            "en": """Our Father, who art in heaven,
hallowed be Thy name.
Thy kingdom come,
Thy will be done, on earth as it is in heaven.
Give us this day our daily bread,
and forgive us our trespasses,
as we forgive those who trespass against us.
And lead us not into temptation,
but deliver us from evil. Amen.""",
            "ar": """أبانا الذي في السموات،
ليتقدس اسمك.
ليأت ملكوتك.
لتكن مشيئتك كما في السماء كذلك على الأرض.
خبزنا كفافنا أعطنا اليوم.
واغفر لنا ذنوبنا كما نغفر نحن أيضًا للمذنبين إلينا.
ولا تدخلنا في تجربة لكن نجنا من الشرير. آمين.""",
            "pt": """Pai nosso que estais no céu,
santificado seja o vosso nome.
Venha a nós o vosso reino.
Seja feita a vossa vontade, assim na terra como no céu.
O pão nosso de cada dia nos dai hoje.
Perdoai-nos as nossas ofensas, assim como nós perdoamos a quem nos tem ofendido.
E não nos deixeis cair em tentação, mas livrai-nos do mal. Amém.""",
        },
    },
    "jesus_prayer": {
        "title": {"en": "Jesus Prayer", "ar": "صلاة يسوع", "pt": "Oração de Jesus"},
        "text": {
            "en": "Lord Jesus Christ, Son of God, have mercy on me, a sinner.",
            "ar": "يا رب يسوع المسيح ابن الله، ارحمني أنا الخاطئ.",
            "pt": "Senhor Jesus Cristo, Filho de Deus, tem misericórdia de mim, pecador.",
        },
    },
    "trisagion": {
        "title": {"en": "Trisagion Prayer", "ar": "صلاة التقديس الثلاثي", "pt": "Oração do Triságio"},
        "text": {
            "en": "Holy God, Holy Mighty, Holy Immortal, have mercy on us.",
            "ar": "قدوس الله، قدوس القوي، قدوس الحي الذي لا يموت، ارحمنا.",
            "pt": "Deus Santo, Forte Santo, Imortal Santo, tem misericórdia de nós.",
        },
    },
    "before_sleep": {
        "title": {"en": "Prayer Before Sleep", "ar": "صلاة قبل النوم", "pt": "Oração Antes de Dormir"},
        "text": {
            "en": """Into Your hands, O Lord, I commend my spirit.
Guard me through the night and grant me peace.
Forgive my sins and renew my heart for another day.
Amen.""",
            "ar": """بين يديك يا رب أستودع روحي.
احفظني في هذه الليلة وامنحني سلامك.
اغفر خطاياي وجدد قلبي ليوم جديد.
آمين.""",
            "pt": """Em Tuas mãos, ó Senhor, entrego o meu espírito.
Guarda-me durante a noite e concede-me a Tua paz.
Perdoa os meus pecados e renova o meu coração para um novo dia.
Amém.""",
        },
    },
    "morning_offering": {
        "title": {"en": "Morning Offering", "ar": "تقدمة الصباح", "pt": "Oferecimento da Manhã"},
        "text": {
            "en": "Lord Jesus Christ, I offer You this day: my thoughts, words, works, and all I am. Guide me in purity, love, and truth. Amen.",
            "ar": "يا رب يسوع المسيح، أقدم لك هذا اليوم: أفكاري وكلماتي وأعمالي وكل كياني. قُدني في الطهارة والمحبة والحق. آمين.",
            "pt": "Senhor Jesus Cristo, eu Te ofereço este dia: meus pensamentos, palavras, obras e tudo o que sou. Guia-me na pureza, no amor e na verdade. Amém.",
        },
    },
    "thanksgiving": {
        "title": {"en": "Prayer of Thanksgiving", "ar": "صلاة الشكر", "pt": "Oração de Ação de Graças"},
        "text": {
            "en": "We thank You, our compassionate Father, for You have guarded us, helped us, and accepted us. Take us in Your holy fear and grant us Your peace. Amen.",
            "ar": "نشكرك أيها الآب المتحنن لأنك سترتنا وأعنتنا وقبلتنا. اجعلنا في مخافتك المقدسة وامنحنا سلامك. آمين.",
            "pt": "Nós Te agradecemos, nosso Pai compassivo, porque nos guardaste, nos ajudaste e nos aceitaste. Recebe-nos no Teu santo temor e concede-nos a Tua paz. Amém.",
        },
    },
    "purity": {
        "title": {"en": "Prayer for Purity", "ar": "صلاة من أجل الطهارة", "pt": "Oração pela Pureza"},
        "text": {
            "en": "Create in me a clean heart, O God, and renew a right spirit within me. Strengthen me to flee temptation and to walk in holiness before You. Amen.",
            "ar": "قلبًا نقيًا اخلق فيّ يا الله، وروحًا مستقيمًا جدده في داخلي. قوّني أن أهرب من التجربة وأسلك في القداسة أمامك. آمين.",
            "pt": "Cria em mim um coração puro, ó Deus, e renova em mim um espírito reto. Fortalece-me para fugir da tentação e andar em santidade diante de Ti. Amém.",
        },
    },
    "protection": {
        "title": {"en": "Prayer for Protection", "ar": "صلاة للحماية", "pt": "Oração de Proteção"},
        "text": {
            "en": "O Lord, be before me and behind me, above me and beneath me. Cover me with Your mercy, and keep me from every evil. Amen.",
            "ar": "يا رب، كن أمامي وخلفي وفوقي وتحتي. ظللني برحمتك واحفظني من كل شر. آمين.",
            "pt": "Ó Senhor, sê diante de mim e atrás de mim, acima e abaixo de mim. Cobre-me com a Tua misericórdia e guarda-me de todo mal. Amém.",
        },
    },
    "mercy": {
        "title": {"en": "Prayer for Mercy", "ar": "صلاة من أجل الرحمة", "pt": "Oração por Misericórdia"},
        "text": {
            "en": "Lord, have mercy. Christ, have mercy. Lord, have mercy.",
            "ar": "يا رب ارحم. يا مسيح ارحم. يا رب ارحم.",
            "pt": "Senhor, tem piedade. Cristo, tem piedade. Senhor, tem piedade.",
        },
    },
}

def _api_get_json(url: str) -> dict:
    req = urllib.request.Request(url, headers={"User-Agent": "BibleApp/1.0"})
    with urllib.request.urlopen(req, timeout=12) as resp:
        return json.loads(resp.read().decode())


def _q(segment: str) -> str:
    return urllib.parse.quote(str(segment), safe="")


def fetch_version_books(version: str) -> dict:
    """List all books available in a specific translation/version."""
    try:
        url = f"{GITHUB_CONTENTS_BASE}/{_q(version)}/books"
        data = _api_get_json(url)
        if not isinstance(data, list):
            return {"error": "Unexpected response while loading books."}
        books = [item["name"] for item in data if item.get("type") == "dir" and item.get("name")]
        return {"books": books}
    except Exception as e:
        return {"error": f"Could not load books: {e}"}


def fetch_book_chapters(version: str, book_slug: str) -> dict:
    """List available chapter numbers for a given book."""
    try:
        url = f"{GITHUB_CONTENTS_BASE}/{_q(version)}/books/{_q(book_slug)}/chapters"
        data = _api_get_json(url)
        if not isinstance(data, list):
            return {"error": "Unexpected response while loading chapters."}
        chapters = []
        for item in data:
            name = item.get("name", "")
            if not name.endswith(".json"):
                continue
            stem = name[:-5]
            if stem.isdigit():
                chapters.append(int(stem))
        chapters.sort()
        return {"chapters": chapters}
    except Exception as e:
        return {"error": f"Could not load chapter list: {e}"}


def fetch_chapter_text(version: str, book_slug: str, chapter: int) -> dict:
    """Fetch chapter verses from the wldeh/bible-api JSON dataset."""
    try:
        url = f"{BIBLE_TEXT_BASE}/{_q(version)}/books/{_q(book_slug)}/chapters/{chapter}.json"
        data = _api_get_json(url)
        verse_rows = data.get("data", [])
        verses = []
        for i, row in enumerate(verse_rows, start=1):
            verses.append({
                "book_name": row.get("book", book_slug),
                "chapter": int(row.get("chapter", chapter)),
                "verse": int(row.get("verse", i)),
                "text": str(row.get("text", "")).strip(),
            })
        ref_book = verse_rows[0].get("book", book_slug) if verse_rows else book_slug
        joined_text = " ".join(v["text"] for v in verses).strip()
        return {
            "reference": f"{ref_book} {chapter}",
            "text": joined_text,
            "translation": version,
            "verses": verses,
        }
    except Exception as e:
        return {"error": f"Could not load chapter text: {e}"}


def fetch_bible_api_books(translation: str) -> dict:
    try:
        url = f"{BIBLE_API_DATA_BASE}/{_q(translation)}"
        data = _api_get_json(url)
        books = data.get("books", [])
        out = []
        for row in books:
            book_id = row.get("id")
            name = row.get("name")
            if book_id and name:
                out.append({"id": book_id, "name": name})
        return {"books": out}
    except Exception as e:
        return {"error": f"Could not load books: {e}"}


def fetch_bible_api_book_chapters(translation: str, book_id: str) -> dict:
    try:
        url = f"{BIBLE_API_DATA_BASE}/{_q(translation)}/{_q(book_id)}"
        data = _api_get_json(url)
        chapters = []
        for row in data.get("chapters", []):
            chapter = row.get("chapter")
            if isinstance(chapter, int):
                chapters.append(chapter)
        chapters.sort()
        return {"chapters": chapters}
    except Exception as e:
        return {"error": f"Could not load chapter list: {e}"}


def fetch_bible_api_chapter_text(translation: str, book_id: str, chapter: int) -> dict:
    try:
        url = f"{BIBLE_API_DATA_BASE}/{_q(translation)}/{_q(book_id)}/{chapter}"
        data = _api_get_json(url)
        verse_rows = data.get("verses", [])
        verses = []
        for i, row in enumerate(verse_rows, start=1):
            verses.append({
                "book_name": row.get("book", book_id),
                "chapter": int(row.get("chapter", chapter)),
                "verse": int(row.get("verse", i)),
                "text": str(row.get("text", "")).strip(),
            })
        ref_book = verse_rows[0].get("book", book_id) if verse_rows else book_id
        joined_text = " ".join(v["text"] for v in verses).strip()
        return {
            "reference": f"{ref_book} {chapter}",
            "text": joined_text,
            "translation": translation,
            "verses": verses,
        }
    except Exception as e:
        return {"error": f"Could not load chapter text: {e}"}


def format_book_label(book_slug: str) -> str:
    """Convert ASCII slugs like '1maccabees' to readable labels for the UI."""
    if any(ord(ch) > 127 for ch in book_slug):
        return book_slug
    slug = book_slug.replace("_", " ").replace("-", " ").strip()
    if slug and slug[0].isdigit() and len(slug) > 1 and slug[1].isalpha():
        slug = f"{slug[0]} {slug[1:]}"
    return slug.title()


def normalize_book_key(text: str) -> str:
    return "".join(ch for ch in text.lower() if ch.isalnum())


def prayer_locale_from_version(version: str) -> str:
    if version == "arb-kehm":
        return "ar"
    if version == "almeida":
        return "pt"
    return "en"


def prayer_title(prayer_key: str, locale: str = "en") -> str:
    entry = PRAYERS.get(prayer_key, {})
    titles = entry.get("title", {})
    return titles.get(locale, titles.get("en", prayer_key))


def prayer_text(prayer_key: str, locale: str = "en") -> str:
    entry = PRAYERS.get(prayer_key, {})
    texts = entry.get("text", {})
    return texts.get(locale, texts.get("en", ""))


def resolve_prayer_key(query: str) -> str:
    normalized = query.strip().lower()
    if normalized in PRAYERS:
        return normalized
    for key in PRAYER_ORDER:
        for locale in ("en", "ar", "pt"):
            if prayer_title(key, locale).lower() == normalized:
                return key
    return ""


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


def get_random_verse_from_wldeh(version: str) -> dict:
    books_info = fetch_version_books(version)
    if "error" in books_info:
        return books_info
    books = books_info.get("books", [])
    if not books:
        return {"error": f"No books available for {version}."}
    book_slug = random.choice(books)
    chapters_info = fetch_book_chapters(version, book_slug)
    if "error" in chapters_info:
        return chapters_info
    chapters = chapters_info.get("chapters", [])
    if not chapters:
        return {"error": f"No chapters available for {book_slug} ({version})."}
    chapter = random.choice(chapters)
    chapter_data = fetch_chapter_text(version, book_slug, chapter)
    if "error" in chapter_data:
        return chapter_data
    verses = chapter_data.get("verses", [])
    if not verses:
        return {"error": "No verses found in random chapter."}
    verse = random.choice(verses)
    return {
        "reference": f"{verse.get('book_name', book_slug)} {verse.get('chapter', chapter)}:{verse.get('verse', '?')}",
        "text": verse.get("text", "").strip(),
        "translation": version,
        "verses": [verse],
    }


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


def print_prayer(prayer_query: str, locale: str = "en"):
    key = resolve_prayer_key(prayer_query)
    if not key:
        print(c("gray", f"  ⚠  Prayer not found: {prayer_query}"))
        return
    title = prayer_title(key, locale)
    text = prayer_text(key, locale)
    print()
    print(c("gold", "  ✝  ") + c("bold", title))
    print(c("gray", "  " + "─" * 50))
    for raw_line in text.splitlines():
        print(c("blue", "  " + raw_line))
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
        print(c("gray",  "    bible --prayers              — list built-in Christian prayers"))
        print(c("gray",  "    bible --prayer \"<name>\"      — show a specific prayer"))
        print(c("gray",  "    bible --coptic-3pm           — Coptic Orthodox Sixth Hour prayer"))
        print()
        return

    if args[0] == "--gui":
        gui_mode()
        return

    if args[0] == "--languages":
        print(c("green", "  Available translations:"))
        for name, info in ORTHODOX_LANGUAGES.items():
            print(f"    {info['flag']}  {c('gold', info['version']):30s}  {c('gray', name)}")
        print()
        return

    if args[0] == "--arabic":
        print(c("gray", "  Fetching a random Arabic verse..."))
        print_verse(get_random_verse_from_wldeh("arb-kehm"))
        return

    if args[0] == "--prayers":
        print(c("green", "  Built-in prayers:"))
        for key in PRAYER_ORDER:
            print(c("gray", f"    - {prayer_title(key, 'en')}"))
        print()
        return

    if args[0] == "--coptic-3pm":
        print_prayer("coptic_sixth_hour_3pm", "en")
        return

    if args[0] == "--prayer":
        if len(args) < 2:
            print(c("gray", "  ⚠  Please pass a prayer name. Example: bible --prayer \"The Lord's Prayer\""))
            return
        prayer_name = " ".join(args[1:])
        print_prayer(prayer_name, "en")
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

        self.current_translation = tk.StringVar(value=ORTHODOX_LANGUAGES[DEFAULT_GUI_LANGUAGE]["version"])
        self.current_lang_name   = tk.StringVar(value=DEFAULT_GUI_LANGUAGE)
        self.search_var          = tk.StringVar()
        self.prayer_name_var     = tk.StringVar(value="")
        self.current_book        = tk.StringVar(value="")
        self.current_chapter     = tk.IntVar(value=1)
        self.verse_history       = []
        self.chapter_verses      = []
        self.books_cache         = {}
        self.chapters_cache      = {}
        self.book_display_to_slug = {}
        self.prayer_display_to_key = {}

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
        lang_names = list(ORTHODOX_LANGUAGES.keys())
        self.lang_combo = ttk.Combobox(lang_frame, textvariable=self.current_lang_name,
                                       values=lang_names, width=42, state="readonly",
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

        # Prayer bar
        prayer_frame = tk.Frame(self, bg="#112a4a", pady=6, padx=16)
        prayer_frame.pack(fill="x")
        tk.Label(prayer_frame, text="Prayer:", bg="#112a4a", fg="#dce0ff",
                 font=self.small_font).pack(side="left", padx=(0, 6))
        self.prayer_combo = ttk.Combobox(
            prayer_frame,
            textvariable=self.prayer_name_var,
            values=[],
            width=40,
            state="readonly",
            font=self.small_font
        )
        self.prayer_combo.pack(side="left", padx=(0, 6))
        tk.Button(prayer_frame, text="Read Prayer", command=self.show_selected_prayer, **btn_style).pack(side="left")

        # Browse controls (book -> chapter -> verses)
        browse_header = tk.Frame(self, bg="#0a2342", pady=6, padx=16)
        browse_header.pack(fill="x")
        tk.Label(browse_header, text="Browse:", bg="#0a2342", fg="#dce0ff",
                 font=self.small_font).pack(side="left", padx=(0, 6))
        self.book_combo = ttk.Combobox(
            browse_header,
            textvariable=self.current_book,
            values=[],
            width=20,
            state="readonly",
            font=self.small_font
        )
        self.book_combo.pack(side="left", padx=(0, 6))
        self.book_combo.bind("<<ComboboxSelected>>", self._on_book_change)

        tk.Label(browse_header, text="Chapter:", bg="#0a2342", fg="#dce0ff",
                 font=self.small_font).pack(side="left", padx=(6, 4))
        self.chapter_spin = tk.Spinbox(
            browse_header, from_=1, to=200, textvariable=self.current_chapter,
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

        self._refresh_prayers_for_current_language()
        self._load_books_for_current_language()

    # ── Actions ─────────────────────────────────

    def _on_lang_change(self, _event=None):
        name = self.current_lang_name.get()
        config = ORTHODOX_LANGUAGES.get(name, ORTHODOX_LANGUAGES[DEFAULT_GUI_LANGUAGE])
        self.current_translation.set(config["version"])
        self._refresh_prayers_for_current_language()
        self._load_books_for_current_language()

    def _current_language_config(self):
        name = self.current_lang_name.get()
        return ORTHODOX_LANGUAGES.get(name, ORTHODOX_LANGUAGES[DEFAULT_GUI_LANGUAGE])

    def _prayer_locale(self):
        return prayer_locale_from_version(self.current_translation.get())

    def _refresh_prayers_for_current_language(self):
        locale = self._prayer_locale()
        labels = [prayer_title(key, locale) for key in PRAYER_ORDER]
        self.prayer_display_to_key = {label: key for label, key in zip(labels, PRAYER_ORDER)}
        self.prayer_combo["values"] = labels
        current_key = resolve_prayer_key(self.prayer_name_var.get())
        if not current_key:
            current_key = "coptic_sixth_hour_3pm"
        self.prayer_name_var.set(prayer_title(current_key, locale))

    def _fetch_books_for_current_language(self, version: str):
        config = self._current_language_config()
        provider = config.get("provider", "wldeh")
        if provider == "bible_api":
            data = fetch_bible_api_books(version)
            if "error" in data:
                return data
            books = data.get("books", [])
            slugs = [b["id"] for b in books]
            labels = [b["name"] for b in books]
            return {"slugs": slugs, "labels": labels}
        data = fetch_version_books(version)
        if "error" in data:
            return data
        slugs = data.get("books", [])
        labels = [format_book_label(slug) for slug in slugs]
        return {"slugs": slugs, "labels": labels}

    def _fetch_chapters_for_current_language(self, version: str, book_slug: str):
        config = self._current_language_config()
        provider = config.get("provider", "wldeh")
        if provider == "bible_api":
            return fetch_bible_api_book_chapters(version, book_slug)
        return fetch_book_chapters(version, book_slug)

    def _fetch_chapter_text_for_current_language(self, version: str, book_slug: str, chapter: int):
        config = self._current_language_config()
        provider = config.get("provider", "wldeh")
        if provider == "bible_api":
            return fetch_bible_api_chapter_text(version, book_slug, chapter)
        return fetch_chapter_text(version, book_slug, chapter)

    def _on_book_change(self, _event=None):
        version = self.current_translation.get()
        book_display = self.current_book.get().strip()
        book_slug = self.book_display_to_slug.get(book_display, "")
        if not book_slug:
            return
        cache_key = (version, book_slug)
        chapter_info = self.chapters_cache.get(cache_key)
        if chapter_info is None:
            chapter_info = self._fetch_chapters_for_current_language(version, book_slug)
            self.chapters_cache[cache_key] = chapter_info

        if "error" in chapter_info:
            self.status_var.set(chapter_info["error"])
            self.chapter_spin.config(from_=1, to=200)
            self.current_chapter.set(1)
            return

        chapters = chapter_info.get("chapters", [])
        if not chapters:
            self.chapter_spin.config(from_=1, to=200)
            self.current_chapter.set(1)
            return

        min_ch, max_ch = chapters[0], chapters[-1]
        current = self.current_chapter.get()
        if current < min_ch:
            current = min_ch
        if current > max_ch:
            current = max_ch
        self.chapter_spin.config(from_=min_ch, to=max_ch)
        self.current_chapter.set(current)
        self.load_chapter()

    def load_chapter(self):
        version = self.current_translation.get()
        book_display = self.current_book.get().strip()
        book_slug = self.book_display_to_slug.get(book_display, "")
        chapter = self.current_chapter.get()
        if not book_slug:
            return

        self.verse_list.delete(0, "end")
        self.chapter_verses = []
        self.status_var.set(f"Loading {book_display} {chapter}...")
        self.update()
        data = self._fetch_chapter_text_for_current_language(version, book_slug, chapter)
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

        lang_note = ORTHODOX_LANGUAGES.get(self.current_lang_name.get(), {}).get("notes", "")
        self.status_var.set(f"Loaded {book_display} {chapter} ({len(verses)} verses) · {lang_note}")
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
            "translation": self.current_translation.get()
        })

    def _load_books_for_current_language(self):
        version = self.current_translation.get()
        books_info = self.books_cache.get(version)
        if books_info is None:
            self.status_var.set("Loading books...")
            self.update()
            books_info = self._fetch_books_for_current_language(version)
            self.books_cache[version] = books_info

        if "error" in books_info:
            self.status_var.set(books_info["error"])
            self.book_combo["values"] = []
            self.current_book.set("")
            return

        slugs = books_info.get("slugs", [])
        labels = books_info.get("labels", [])
        self.book_display_to_slug = {label: slug for label, slug in zip(labels, slugs)}
        self.book_combo["values"] = labels
        if not labels:
            self.current_book.set("")
            self.status_var.set("No books found for this language/source.")
            return

        preferred = "John" if "John" in labels else labels[0]
        self.current_book.set(preferred)
        self.current_chapter.set(1)
        self._on_book_change()

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

    def show_selected_prayer(self):
        label = self.prayer_name_var.get().strip()
        key = self.prayer_display_to_key.get(label) or resolve_prayer_key(label)
        if not key:
            self._show_verse({"error": f"Prayer not found: {label}"})
            return
        locale = self._prayer_locale()
        text = prayer_text(key, locale)
        title = prayer_title(key, locale)
        self._show_verse({
            "reference": title,
            "text": text,
            "translation": "Prayer",
        })

    def load_random(self):
        version = self.current_translation.get()
        books_info = self.books_cache.get(version)
        if not books_info or "error" in books_info or not books_info.get("slugs"):
            self._load_books_for_current_language()
            books_info = self.books_cache.get(version, {})
        slugs = books_info.get("slugs", [])
        if not slugs:
            self.status_var.set("Could not load books for random verse.")
            return

        book_slug = random.choice(slugs)
        cache_key = (version, book_slug)
        chapter_info = self.chapters_cache.get(cache_key)
        if chapter_info is None:
            chapter_info = self._fetch_chapters_for_current_language(version, book_slug)
            self.chapters_cache[cache_key] = chapter_info
        chapters = chapter_info.get("chapters", [])
        if not chapters:
            self.status_var.set("Could not load chapters for random verse.")
            return
        chapter = random.choice(chapters)

        selected_label = next((label for label, slug in self.book_display_to_slug.items() if slug == book_slug), None)
        if selected_label:
            self.current_book.set(selected_label)
        self.current_chapter.set(chapter)
        self.status_var.set("Fetching a random verse…")
        self.update()
        chapter_data = self._fetch_chapter_text_for_current_language(version, book_slug, chapter)
        if "error" in chapter_data:
            self._show_verse(chapter_data)
            return
        verses = chapter_data.get("verses", [])
        if not verses:
            self._show_verse({"error": "No verses found in this random chapter."})
            return
        self.chapter_verses = verses
        self.verse_list.delete(0, "end")
        for verse in verses:
            number = verse.get("verse", "?")
            text = verse.get("text", "").strip().replace("\n", " ")
            preview = text[:72] + ("..." if len(text) > 72 else "")
            self.verse_list.insert("end", f"{number}. {preview}")
        idx = random.randrange(len(verses))
        self.verse_list.selection_set(idx)
        self._on_verse_select()

    def search_verse(self):
        ref = self.search_var.get().strip()
        if not ref:
            messagebox.showinfo("Bible", "Please type a verse reference first!\nExample: John 3:16")
            return
        trans = self.current_translation.get()
        self.status_var.set(f"Looking up {ref}…")
        self.update()
        # Accept "Book 3:16" or "Book 3"
        parsed = self._parse_reference(ref)
        if not parsed:
            self._show_verse({"error": "Use format like John 3:16 or John 3"})
            return
        book_slug, chapter, verse_no = parsed
        chapter_data = self._fetch_chapter_text_for_current_language(trans, book_slug, chapter)
        if "error" in chapter_data:
            self._show_verse(chapter_data)
            return

        verses = chapter_data.get("verses", [])
        self.chapter_verses = verses
        self.verse_list.delete(0, "end")
        for verse in verses:
            number = verse.get("verse", "?")
            text = verse.get("text", "").strip().replace("\n", " ")
            preview = text[:72] + ("..." if len(text) > 72 else "")
            self.verse_list.insert("end", f"{number}. {preview}")

        selected_label = next((label for label, slug in self.book_display_to_slug.items() if slug == book_slug), None)
        if selected_label:
            self.current_book.set(selected_label)
        self.current_chapter.set(chapter)

        if verse_no is None:
            if verses:
                self.verse_list.selection_set(0)
                self._on_verse_select()
            return

        for idx, verse in enumerate(verses):
            if verse.get("verse") == verse_no:
                self.verse_list.selection_set(idx)
                self._on_verse_select()
                return
        self._show_verse({"error": f"Verse {verse_no} not found in {ref} for {trans}."})

    def _parse_reference(self, ref: str):
        parts = ref.rsplit(" ", 1)
        if len(parts) != 2:
            return None
        book_part = parts[0].strip()
        chapter_verse = parts[1].strip()
        if ":" in chapter_verse:
            ch_txt, vs_txt = chapter_verse.split(":", 1)
            if not ch_txt.isdigit() or not vs_txt.isdigit():
                return None
            chapter = int(ch_txt)
            verse = int(vs_txt)
        else:
            if not chapter_verse.isdigit():
                return None
            chapter = int(chapter_verse)
            verse = None

        book_slug = self._find_book_slug(book_part)
        if not book_slug:
            return None
        return book_slug, chapter, verse

    def _find_book_slug(self, raw_book: str) -> str:
        key = normalize_book_key(raw_book)
        if not key:
            return ""
        for label, slug in self.book_display_to_slug.items():
            if normalize_book_key(label) == key:
                return slug
            if normalize_book_key(slug) == key:
                return slug
        return ""


def gui_mode():
    if not TK_AVAILABLE:
        print("GUI could not start because tkinter is not available.")
        print(f"Details: {TK_IMPORT_ERROR}")
        print("On Arch Linux, install it with: sudo pacman -S --needed tk")
        return

    log_path = os.path.expanduser("~/.cache/bible-app.log")
    try:
        app = BibleApp()
        app.mainloop()
    except Exception:
        os.makedirs(os.path.dirname(log_path), exist_ok=True)
        with open(log_path, "a", encoding="utf-8") as f:
            f.write("\n=== Bible App Crash ===\n")
            f.write(traceback.format_exc())
        print("Bible GUI crashed. Error saved to:")
        print(log_path)


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
