#!/usr/bin/env python3
"""
Bundle a deck HTML into a single fully self-contained file:
  - inlines every assets/*.png as a base64 data URI
  - downloads the Google Fonts (latin subset, woff2) and embeds them as @font-face
Result works 100% offline with no assets folder and no internet.

Usage:  python make_standalone.py <in.html> <out.html>
"""
import sys, re, base64, urllib.request, pathlib

UA = ("Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 "
      "(KHTML, like Gecko) Chrome/120.0 Safari/537.36")

def fetch(url, binary=False):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    with urllib.request.urlopen(req, timeout=60) as r:
        return r.read() if binary else r.read().decode("utf-8")

def embed_fonts(gf_url):
    """Fetch Google Fonts CSS, keep latin @font-face blocks, inline woff2 as base64."""
    css = fetch(gf_url)
    # split into '/* subset */ @font-face {...}' chunks
    chunks = re.split(r'(?=/\*[^*]*\*/)', css)
    out = []
    for c in chunks:
        if "@font-face" not in c:
            continue
        if not re.search(r'/\*\s*latin\s*\*/', c):
            continue  # latin subset only -> smaller file; symbols fall back gracefully
        m = re.search(r"url\((https://[^)]+\.woff2)\)", c)
        if not m:
            continue
        data = fetch(m.group(1), binary=True)
        b64 = base64.b64encode(data).decode()
        c = c.replace(m.group(1), f"data:font/woff2;base64,{b64}")
        out.append(c.strip())
    return "<style>\n" + "\n".join(out) + "\n</style>"

def inline_images(html, base_dir):
    paths = set(re.findall(r"assets/[A-Za-z0-9_./-]+\.png", html))
    for p in sorted(paths):
        fp = base_dir / p
        b64 = base64.b64encode(fp.read_bytes()).decode()
        uri = f"data:image/png;base64,{b64}"
        html = html.replace(p, uri)
        print(f"  inlined {p}  ({len(b64)//1024} KB b64)")
    return html

def main():
    src, dst = pathlib.Path(sys.argv[1]), pathlib.Path(sys.argv[2])
    base_dir = src.parent
    html = src.read_text(encoding="utf-8")

    gf = re.search(r'href="(https://fonts\.googleapis\.com/css2[^"]+)"', html)
    print("Embedding fonts...")
    font_style = embed_fonts(gf.group(1)) if gf else ""
    # drop preconnect + the google fonts <link>, inject embedded @font-face
    html = re.sub(r'<link rel="preconnect"[^>]*>\s*', "", html)
    html = re.sub(r'<link href="https://fonts\.googleapis\.com/css2[^"]+"[^>]*>',
                  font_style, html)

    print("Inlining images...")
    html = inline_images(html, base_dir)

    dst.write_text(html, encoding="utf-8")
    kb = len(html.encode("utf-8")) // 1024
    leftover = re.findall(r'(assets/|fonts\.googleapis)', html)
    print(f"Wrote {dst}  ({kb} KB)  | leftover external refs: {len(leftover)}")

if __name__ == "__main__":
    main()
