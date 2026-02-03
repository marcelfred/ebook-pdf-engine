# ebook-pdf-engine

Reusable PDF generator engine for e-books with text and image support.

## Proposed folder structure

```
ebook-pdf-engine/
├── ebook_pdf_engine/
│   ├── __init__.py
│   ├── content.py      # content structure (chapters, paragraphs, images)
│   ├── layout.py       # layout logic (flowables + page sizing)
│   └── rendering.py    # PDF rendering interface
├── main.py             # example entrypoint
├── output/             # generated sample artifacts
└── requirements.txt
```

## Quick start

```bash
python -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
python main.py
```

The command above generates `output/sample-ebook.pdf`.
