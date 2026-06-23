# OCBC CRAYON — repo notes

GitHub-Pages site (`.nojekyll`) for the OCBC CRAYON 2026 intern training series.
`index.html` is the landing page; each topic is a self-contained animated 16:9
HTML deck under `web/`.

## Landing-page convention (IMPORTANT — keep in sync when adding a topic)

Every **available** topic gets its own row on `index.html`, mirroring Topic 1:
a `.topic` block with a `.t-head` (Topic N · title · "Available" badge) followed
by a 3-button `.actions` row, **in this order**:

1. **Open the deck** → `web/<topic>.standalone.html`
2. **Components** → `web/components-<topic>.standalone.html`
3. **Speaker notes** → `<topic>-speaker-notes page>.html` (opens in a new tab)

So when you add a new topic deck you must ALSO produce, and link, all three:

- `web/<topic>.html` + `web/<topic>.standalone.html` (the deck; build the
  standalone with `web/make_standalone.py`).
- `web/components-<topic>.html` + `.standalone.html` — a bento component
  gallery of that deck's animated widgets (mirror `web/components.html`).
- `speaker-notes-<topic>.html` + `speaker-notes-<topic>.txt` — an editable
  speaker-notes page (mirror `speaker-notes.html`: inline edit + localStorage +
  download .txt). Generate it from the deck's `data-notes` attributes.

New, not-yet-built topics stay as "Coming soon" cards in the `.next` section.

## Deck system

All decks share one scaffold (see `web/python-data-foundations.html`): a fixed
1280×720 `.deck` scaled to the viewport by `fit()` (uses `visualViewport`,
re-fits on `orientationchange`); reveal-on-active animations via `[data-r]`/
`data-d`; a notebook-playback demo player; speaker-notes drawer (`N`); and a
portrait "rotate your device" cue for mobile. Match this scaffold exactly so all
decks read as one series. Theme: OCBC red `#EC1B23` on light surfaces, dark
cover/dividers/close; fonts Manrope / Inter / JetBrains Mono. Every slide has a
visual; titles centered only, body left-aligned.

`?static` in the URL snaps animations to final (for PDF/QA screenshots).

## Build / regenerate

```bash
cd web
# 1. rebuild the deck's self-contained standalone (inlines fonts + images)
python make_standalone.py <source>.html <source>.standalone.html
# 2. regenerate the speaker-notes page/.txt FROM the deck's data-notes
#    (the deck is the single source of truth; this keeps both in sync)
python make_speaker_notes.py ../<source>.html ../speaker-notes-<topic>.html \
       ../speaker-notes-<topic>.txt "OCBC CRAYON 2026 — <Deck Title>"
```

`make_speaker_notes.py` rewrites only the `<div id="notes">` list, the two
slide-count strings, and the `.txt` mirror — all page chrome is preserved. Slide
headings are derived from each slide (cover h1 / "eyebrow — h2" for dividers /
`.slide-title` / kicker), so edit notes in the **deck's `data-notes`**, never the
notes page directly. Whenever deck content or slide order changes, rebuild the
deck standalone, its components gallery standalone, AND regenerate the
speaker-notes page/.txt.
