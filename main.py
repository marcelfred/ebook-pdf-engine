"""Generate a sample PDF using the ebook PDF engine."""

from __future__ import annotations

import base64
from pathlib import Path

from ebook_pdf_engine import Chapter, Ebook, ImageBlock, Paragraph, PDFRenderer

SAMPLE_IMAGE_BASE64 = (
    "iVBORw0KGgoAAAANSUhEUgAAAZAAAAGQCAIAAAAP3aGbAAAAGXRFWHRTb2Z0d2FyZQBBZG9iZSBJbWFnZVJlYWR5ccllPAAA"
    "AABJRU5ErkJggg=="
)


def ensure_sample_image(path: Path) -> None:
    if path.exists():
        return
    data = base64.b64decode(SAMPLE_IMAGE_BASE64)
    path.write_bytes(data)


def build_sample_ebook(image_path: Path) -> Ebook:
    chapter_one = Chapter(
        title="Getting Started",
        blocks=[
            Paragraph(
                "Welcome to the sample e-book. This chapter demonstrates basic paragraph layout and a simple image "
                "between text sections."
            ),
            ImageBlock(path=str(image_path), caption="A minimal placeholder image."),
            Paragraph(
                "The engine keeps a clear separation between content, layout, and rendering so you can swap out "
                "styles or rendering backends later."
            ),
        ],
    )

    chapter_two = Chapter(
        title="Full-Page Art",
        blocks=[
            Paragraph("The next page showcases a full-page image block."),
            ImageBlock(path=str(image_path), full_page=True, caption="Full-page image."),
            Paragraph("After the full-page image, content continues on a new page."),
        ],
    )

    return Ebook(title="Sample PDF E-Book", author="PDF Engine", chapters=[chapter_one, chapter_two])


def main() -> None:
    output_dir = Path("output")
    output_dir.mkdir(exist_ok=True)
    image_path = output_dir / "sample-image.png"
    ensure_sample_image(image_path)

    ebook = build_sample_ebook(image_path)
    renderer = PDFRenderer()
    renderer.render(ebook, output_dir / "sample-ebook.pdf")


if __name__ == "__main__":
    main()
