#!/usr/bin/env python3
"""
Regenerate a deck's speaker-notes page (.html) and .txt from the deck's own
slides. Reads each <section class="slide"> block: its title (slide-title >
divider h2 > cover h1 > kicker) and its data-notes JSON array, then rewrites
the <div id="notes"> ... </div> block of the existing speaker-notes HTML
(keeping all chrome: KEY, download name, CSS, JS) and the matching .txt.

Usage:
  python gen_speaker_notes.py <deck.html> <speaker-notes-x.html> <speaker-notes-x.txt>

The speaker-notes HTML must already exist (used as the template / output).
"""
import sys, re, json, html, pathlib

def clean(s):
    s = re.sub(r'<[^>]+>', ' ', s)        # tags -> space
    s = html.unescape(s)                  # entities -> unicode
    s = re.sub(r'\s+', ' ', s).strip()
    return s

def slide_title(block):
    m = re.search(r'<h2 class="slide-title"[^>]*>(.*?)</h2>', block, re.S)
    if m: return clean(m.group(1))
    m = re.search(r'<h2>(.*?)</h2>', block, re.S)          # divider
    if m: return clean(m.group(1))
    m = re.search(r'<h1[^>]*>(.*?)</h1>', block, re.S)      # cover
    if m: return clean(m.group(1))
    m = re.search(r'<div class="kicker">(.*?)</div>', block, re.S)
    if m: return clean(m.group(1))
    return ''

def parse_deck(deck_html):
    # split on slide sections; keep only real slides
    parts = re.split(r'(?=<section class="slide)', deck_html)
    slides = []
    for p in parts:
        if not p.startswith('<section class="slide'):
            continue
        m = re.search(r"data-notes='(.+?)'>", p, re.S)
        notes = []
        if m:
            try:
                notes = json.loads(m.group(1))
            except Exception as e:
                raise SystemExit(f"data-notes JSON parse failed near: {p[:120]!r}\n{e}")
        slides.append((slide_title(p), notes))
    return slides

def build_articles(slides):
    out = ['<div id="notes">']
    for i, (title, notes) in enumerate(slides, 1):
        out.append('    <article class="s">')
        out.append(f'      <div class="n">Slide {i}</div>')
        out.append(f'      <h2>{html.escape(title)}</h2>')
        out.append('      <ul>')
        for n in notes:
            out.append(f'        <li>{html.escape(n)}</li>')
        out.append('      </ul>')
        out.append('    </article>')
    out.append('  </div>')
    return '\n'.join(out)

def main():
    deck_p, notes_p, txt_p = (pathlib.Path(a) for a in sys.argv[1:4])
    slides = parse_deck(deck_p.read_text(encoding='utf-8'))
    n = len(slides)
    notes_html = notes_p.read_text(encoding='utf-8')

    # replace the articles block
    articles = build_articles(slides)
    notes_html = re.sub(r'<div id="notes">.*?\n  </div>', articles, notes_html, count=1, flags=re.S)
    # update slide counts in chrome + intro
    notes_html = re.sub(r'· \d+ slides', f'· {n} slides', notes_html, count=1)
    notes_html = re.sub(r'deck\. \d+ slides,', f'deck. {n} slides,', notes_html, count=1)
    notes_p.write_text(notes_html, encoding='utf-8')

    # .txt — match the in-page buildTxt() format
    title_line = txt_p.read_text(encoding='utf-8').splitlines()[0] if txt_p.exists() else 'OCBC CRAYON 2026'
    L = [title_line, f'Speaker notes · {n} slides',
         '================================================', '']
    for i, (title, notes) in enumerate(slides, 1):
        L.append(f'Slide {i} — {title}')
        for nt in notes:
            L.append('  • ' + nt)
        L.append('')
    txt = '\n'.join(L).rstrip() + '\n'
    txt_p.write_text(txt, encoding='utf-8')
    print(f"  {deck_p.name}: {n} slides -> {notes_p.name} + {txt_p.name}")

if __name__ == '__main__':
    main()
