# OCBC CRAYON — Python Data Foundations

An animated, self-contained HTML slide deck for the **OCBC CRAYON 2026** intern
training program (Topic 1: *Python Data Foundations*). Zero-dependency, fixed-16:9
web deck with live animated visuals and in-deck **notebook-playback** demos in
**Polars**.

## Present it

**Easiest — just open one file:**
[`web/python-data-foundations.standalone.html`](web/python-data-foundations.standalone.html)

It's a single file with every image and font embedded, so it works **fully offline
on any laptop with no setup** — copy it over and double-click. No `assets/` folder,
no internet needed.

**Controls**

| Key | Action |
|-----|--------|
| `→` / `←` / `Space` | next / previous slide |
| `N` | toggle speaker notes |
| `R` | replay the demo on a demo slide |
| `F` | fullscreen |
| `?static` (URL) | snap all animations to final — good for printing a PDF handout |

## Contents

36 slides across four pillars — **Basic Python → Data Science Concepts → Data
Wrangling → Analytics Principles** — bookended by a dark cover/quote and a closing,
with two recorded-style demos (load a CSV; clean a messy CSV → one summary) and a
sourced best-practices slide.

## Files

| File | Purpose |
|------|---------|
| `web/python-data-foundations.standalone.html` | **The deck — single self-contained file. Present this.** |
| `web/python-data-foundations.html` | Source deck (needs `web/assets/` + internet for fonts) |
| `web/components.standalone.html` | Animated component gallery — single self-contained file |
| `web/components.html` | Component gallery source |
| `web/assets/` | OCBC logo, icons, cover image, example charts |
| `web/make_standalone.py` | Bundles a source deck into a standalone file |
| `CRAYON_2026_Project_Brief_Suara_Pintar_v3.docx` | Project brief |

## Rebuild the standalone file

After editing the source deck, regenerate the self-contained version:

```bash
cd web
python make_standalone.py python-data-foundations.html python-data-foundations.standalone.html
python make_standalone.py components.html components.standalone.html
```

`make_standalone.py` base64-inlines every `assets/*.png` and downloads + embeds the
Google Fonts (latin subset, woff2) as `@font-face` rules.

---

Hand-written HTML/CSS/JS, no libraries. Type: Manrope · Inter · JetBrains Mono.
Theme: OCBC red `#EC1B23` on a light surface with dark section dividers.
