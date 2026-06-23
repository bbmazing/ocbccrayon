#!/usr/bin/env python3
"""
Regenerate a speaker-notes page from a deck's data-notes attributes so the
deck stays the single source of truth.

It rewrites, in place:
  - the <div id="notes"> ... </div> article list in <speaker-notes-x.html>
  - the two slide-count strings in that page (header + intro)
  - the matching <speaker-notes-x.txt> plain-text mirror

All page chrome (head, styles, edit/download JS) is preserved untouched.

Heading per slide is derived from the deck the same way the hand-made pages did:
  cover   -> the <h1> text
  divider -> "<eyebrow> — <h2>"   (e.g. "Part 1 — Large Language Models")
  content -> the .slide-title text
  quote   -> the .kicker text      (slides with no .slide-title)

Usage:
  python make_speaker_notes.py <deck.html> <notes.html> <notes.txt> "<TXT title>"
"""
import sys, re, json, html, pathlib

TXT_RULE = "================================================"


def strip_tags(s):
    """Inner text of an HTML fragment: drop tags, decode entities, collapse ws."""
    s = re.sub(r"<[^>]+>", " ", s)
    s = html.unescape(s)
    return re.sub(r"\s+", " ", s).strip()


def esc_html(s):
    """Escape only the structural characters; keep Unicode (— · ’ “ ”) literal."""
    return s.replace("&", "&amp;").replace("<", "&lt;").replace(">", "&gt;")


def slide_heading(classes, body):
    if "cover" in classes:
        m = re.search(r"<h1[^>]*>(.*?)</h1>", body, re.S)
        return strip_tags(m.group(1)) if m else ""
    if "divider" in classes:
        eb = re.search(r'<div class="eyebrow">(.*?)</div>', body, re.S)
        h2 = re.search(r"<h2[^>]*>(.*?)</h2>", body, re.S)
        eb_t = strip_tags(eb.group(1)) if eb else ""
        h2_t = strip_tags(h2.group(1)) if h2 else ""
        return f"{eb_t} — {h2_t}".strip(" —")
    m = re.search(r'<h2 class="slide-title"[^>]*>(.*?)</h2>', body, re.S)
    if m:
        return strip_tags(m.group(1))
    m = re.search(r'<div class="kicker">(.*?)</div>', body, re.S)
    return strip_tags(m.group(1)) if m else ""


def parse_deck(deck):
    """-> list of (heading, [note, ...]) in slide order."""
    starts = [m.start() for m in re.finditer(r'<section class="slide', deck)]
    if not starts:
        sys.exit("no slides found in deck")
    starts.append(deck.index("</main>"))
    slides = []
    for i in range(len(starts) - 1):
        body = deck[starts[i]:starts[i + 1]]
        classes = re.match(r'<section class="slide([^"]*)"', body).group(1)
        dn = re.search(r"data-notes='([^']*)'", body)
        notes = [html.unescape(x) for x in json.loads(dn.group(1))] if dn else []
        slides.append((slide_heading(classes, body), notes))
    return slides


def build_articles(slides):
    out = []
    for i, (head, notes) in enumerate(slides, 1):
        lis = "\n".join(f"        <li>{esc_html(n)}</li>" for n in notes)
        out.append(
            f'    <article class="s">\n'
            f'      <div class="n">Slide {i}</div>\n'
            f"      <h2>{esc_html(head)}</h2>\n"
            f"      <ul>\n{lis}\n      </ul>\n"
            f"    </article>"
        )
    return "\n".join(out)


def build_txt(title, slides):
    L = [title, f"Speaker notes · {len(slides)} slides", TXT_RULE, ""]
    for i, (head, notes) in enumerate(slides, 1):
        L.append(f"Slide {i} — {head}")
        for n in notes:
            L.append(f"  • {n}")
        L.append("")
    return "\n".join(L).rstrip() + "\n"


def main():
    deck_p, html_p, txt_p, txt_title = (pathlib.Path(sys.argv[1]),
                                        pathlib.Path(sys.argv[2]),
                                        pathlib.Path(sys.argv[3]), sys.argv[4])
    slides = parse_deck(deck_p.read_text(encoding="utf-8"))
    n = len(slides)

    page = html_p.read_text(encoding="utf-8")
    new_body = "<div id=\"notes\">\n" + build_articles(slides) + "\n  </div>"
    page, k = re.subn(r'<div id="notes">.*</div>(\s*</main>)',
                      lambda m: new_body + m.group(1), page, flags=re.S)
    if k != 1:
        sys.exit(f"could not locate #notes block in {html_p}")
    page = re.sub(r"· \d+ slides", f"· {n} slides", page)
    page = re.sub(r"\d+ slides, in order", f"{n} slides, in order", page)
    html_p.write_text(page, encoding="utf-8")

    txt_p.write_text(build_txt(txt_title, slides), encoding="utf-8")
    print(f"  {html_p.name}: {n} slides  |  {txt_p.name} rewritten")


if __name__ == "__main__":
    main()
