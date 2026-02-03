 (cd "$(git rev-parse --show-toplevel)" && git apply --3way <<'EOF' 
diff --git a/README.md b/README.md
index 7b1f0229e9a96c273687b9c413b30d6a9c994fa7..b6752d6f4512bd6a27ed7af0f7dd1ceb9ac4aac4 100644
--- a/README.md
+++ b/README.md
@@ -1,2 +1,19 @@
 # ebook-pdf-engine
 Reusable PDF generator engine for e-books with text and image support.
+
+## Proposed structure
+```
+ebook_pdf_engine/
+  content/      # Content models (chapters, paragraphs, images)
+  layout/       # Layout logic (pagination, wrapping)
+  render/       # PDF rendering
+  assets/       # Example assets
+main.py         # Sample entry point
+```
+
+## Quick start
+```bash
+pip install -r requirements.txt
+python main.py
+```
+This generates `sample_ebook.pdf` in the repo root.
diff --git a/ebook_pdf_engine/__init__.py b/ebook_pdf_engine/__init__.py
new file mode 100644
index 0000000000000000000000000000000000000000..575619673a32f8848270b56c886b31e3666e0935
--- /dev/null
+++ b/ebook_pdf_engine/__init__.py
@@ -0,0 +1 @@
+"""Reusable PDF generator engine for e-books."""
diff --git a/ebook_pdf_engine/assets/sample_image.png b/ebook_pdf_engine/assets/sample_image.png
new file mode 100644
index 0000000000000000000000000000000000000000..90c31e082c8e0ce867944bdd53e9bcb6559d8cf1
GIT binary patch
literal 68
zcmeAS@N?(olHy`uVBq!ia0vp^j3CUx0wlM}@Gt=>Zci7-kcwN$fBwreFf%hTyi0%P
Q3lwJXboFyt=akR{0ETuBNdN!<

literal 0
HcmV?d00001

diff --git a/ebook_pdf_engine/content/__init__.py b/ebook_pdf_engine/content/__init__.py
new file mode 100644
index 0000000000000000000000000000000000000000..e69de29bb2d1d6434b8b29ae775ad8c2e48c5391
diff --git a/ebook_pdf_engine/content/models.py b/ebook_pdf_engine/content/models.py
new file mode 100644
index 0000000000000000000000000000000000000000..2e5e507320e4bad06ae04eef2b87662bbc5038d7
--- /dev/null
+++ b/ebook_pdf_engine/content/models.py
@@ -0,0 +1,31 @@
+from __future__ import annotations
+
+from dataclasses import dataclass, field
+from typing import List, Sequence, Union
+
+
+@dataclass(frozen=True)
+class Paragraph:
+    text: str
+
+
+@dataclass(frozen=True)
+class ImageBlock:
+    path: str
+    full_page: bool = False
+
+
+ContentBlock = Union[Paragraph, ImageBlock]
+
+
+@dataclass(frozen=True)
+class Chapter:
+    title: str
+    blocks: Sequence[ContentBlock] = field(default_factory=list)
+
+
+@dataclass(frozen=True)
+class Ebook:
+    title: str
+    author: str
+    chapters: Sequence[Chapter] = field(default_factory=list)
diff --git a/ebook_pdf_engine/layout/__init__.py b/ebook_pdf_engine/layout/__init__.py
new file mode 100644
index 0000000000000000000000000000000000000000..e69de29bb2d1d6434b8b29ae775ad8c2e48c5391
diff --git a/ebook_pdf_engine/layout/engine.py b/ebook_pdf_engine/layout/engine.py
new file mode 100644
index 0000000000000000000000000000000000000000..8787dc228dd125611a18df1e0d62208b94c2cd05
--- /dev/null
+++ b/ebook_pdf_engine/layout/engine.py
@@ -0,0 +1,230 @@
+from __future__ import annotations
+
+from dataclasses import dataclass, field
+from typing import List
+
+from reportlab.lib.pagesizes import A4
+from reportlab.pdfbase import pdfmetrics
+
+from ebook_pdf_engine.content.models import Chapter, Ebook, ImageBlock, Paragraph
+
+
+@dataclass(frozen=True)
+class LayoutConfig:
+    page_size: tuple[float, float] = A4
+    margin_left: float = 72
+    margin_right: float = 72
+    margin_top: float = 72
+    margin_bottom: float = 72
+    body_font: str = "Helvetica"
+    body_font_size: int = 12
+    title_font: str = "Helvetica-Bold"
+    title_font_size: int = 20
+    chapter_font: str = "Helvetica-Bold"
+    chapter_font_size: int = 16
+    line_spacing: float = 1.4
+
+
+@dataclass(frozen=True)
+class LayoutText:
+    x: float
+    y: float
+    text: str
+    font_name: str
+    font_size: int
+
+
+@dataclass(frozen=True)
+class LayoutImage:
+    x: float
+    y: float
+    width: float
+    height: float
+    path: str
+
+
+@dataclass
+class LayoutPage:
+    width: float
+    height: float
+    elements: List[LayoutText | LayoutImage] = field(default_factory=list)
+
+
+class LayoutEngine:
+    def __init__(self, config: LayoutConfig | None = None) -> None:
+        self.config = config or LayoutConfig()
+
+    def layout_ebook(self, ebook: Ebook) -> List[LayoutPage]:
+        pages: List[LayoutPage] = []
+        page = self._new_page()
+        pages.append(page)
+        y = page.height - self.config.margin_top
+
+        y, page = self._add_text_block(
+            pages,
+            page,
+            ebook.title,
+            self.config.title_font,
+            self.config.title_font_size,
+            y,
+            spacing_after=self.config.title_font_size * 1.5,
+        )
+        y, page = self._add_text_block(
+            pages,
+            page,
+            f"By {ebook.author}",
+            self.config.body_font,
+            self.config.body_font_size,
+            y,
+            spacing_after=self.config.body_font_size * 2,
+        )
+
+        for chapter in ebook.chapters:
+            y, page = self._add_chapter(pages, page, y, chapter)
+
+        return pages
+
+    def _new_page(self) -> LayoutPage:
+        width, height = self.config.page_size
+        return LayoutPage(width=width, height=height)
+
+    def _content_width(self, page: LayoutPage) -> float:
+        return page.width - self.config.margin_left - self.config.margin_right
+
+    def _add_chapter(
+        self, pages: List[LayoutPage], page: LayoutPage, y: float, chapter: Chapter
+    ) -> tuple[float, LayoutPage]:
+        y, page = self._ensure_space(
+            pages, page, y, self.config.chapter_font_size * 2
+        )
+        y, page = self._add_text_block(
+            pages,
+            page,
+            chapter.title,
+            self.config.chapter_font,
+            self.config.chapter_font_size,
+            y,
+            spacing_after=self.config.chapter_font_size,
+        )
+        for block in chapter.blocks:
+            if isinstance(block, Paragraph):
+                y, page = self._add_text_block(
+                    pages,
+                    page,
+                    block.text,
+                    self.config.body_font,
+                    self.config.body_font_size,
+                    y,
+                    spacing_after=self.config.body_font_size,
+                )
+            elif isinstance(block, ImageBlock):
+                y, page = self._add_image_block(pages, page, y, block)
+            page = pages[-1]
+        return y, page
+
+    def _add_text_block(
+        self,
+        pages: List[LayoutPage],
+        page: LayoutPage,
+        text: str,
+        font_name: str,
+        font_size: int,
+        y: float,
+        spacing_after: float,
+    ) -> tuple[float, LayoutPage]:
+        max_width = self._content_width(page)
+        lines = self._wrap_text(text, font_name, font_size, max_width)
+        line_height = font_size * self.config.line_spacing
+        for line in lines:
+            y, page = self._ensure_space(pages, page, y, line_height)
+            page.elements.append(
+                LayoutText(
+                    x=self.config.margin_left,
+                    y=y,
+                    text=line,
+                    font_name=font_name,
+                    font_size=font_size,
+                )
+            )
+            y -= line_height
+        y -= spacing_after
+        return y, page
+
+    def _wrap_text(
+        self, text: str, font_name: str, font_size: int, max_width: float
+    ) -> List[str]:
+        words = text.split()
+        if not words:
+            return [""]
+        lines: List[str] = []
+        current = words[0]
+        for word in words[1:]:
+            candidate = f"{current} {word}"
+            if pdfmetrics.stringWidth(candidate, font_name, font_size) <= max_width:
+                current = candidate
+            else:
+                lines.append(current)
+                current = word
+        lines.append(current)
+        return lines
+
+    def _add_image_block(
+        self,
+        pages: List[LayoutPage],
+        page: LayoutPage,
+        y: float,
+        block: ImageBlock,
+    ) -> tuple[float, LayoutPage]:
+        available_width = self._content_width(page)
+        if block.full_page:
+            page = self._new_page()
+            pages.append(page)
+            y = page.height - self.config.margin_top
+            image_width = page.width - self.config.margin_left - self.config.margin_right
+            image_height = page.height - self.config.margin_top - self.config.margin_bottom
+            x = self.config.margin_left
+            y_image = self.config.margin_bottom
+            page.elements.append(
+                LayoutImage(
+                    x=x,
+                    y=y_image,
+                    width=image_width,
+                    height=image_height,
+                    path=block.path,
+                )
+            )
+            page = self._new_page()
+            pages.append(page)
+            return page.height - self.config.margin_top, page
+
+        max_height = y - self.config.margin_bottom
+        image_height = min(max_height, available_width * 0.6)
+        if image_height <= 0:
+            page = self._new_page()
+            pages.append(page)
+            y = page.height - self.config.margin_top
+            max_height = y - self.config.margin_bottom
+            image_height = min(max_height, available_width * 0.6)
+        image_width = min(available_width, image_height * 1.5)
+        x = self.config.margin_left + (available_width - image_width) / 2
+        y_image = y - image_height
+        page.elements.append(
+            LayoutImage(
+                x=x,
+                y=y_image,
+                width=image_width,
+                height=image_height,
+                path=block.path,
+            )
+        )
+        y = y_image - self.config.body_font_size
+        return y, page
+
+    def _ensure_space(
+        self, pages: List[LayoutPage], page: LayoutPage, y: float, needed: float
+    ) -> tuple[float, LayoutPage]:
+        if y - needed < self.config.margin_bottom:
+            page = self._new_page()
+            pages.append(page)
+            return page.height - self.config.margin_top, page
+        return y, page
diff --git a/ebook_pdf_engine/render/__init__.py b/ebook_pdf_engine/render/__init__.py
new file mode 100644
index 0000000000000000000000000000000000000000..e69de29bb2d1d6434b8b29ae775ad8c2e48c5391
diff --git a/ebook_pdf_engine/render/pdf_renderer.py b/ebook_pdf_engine/render/pdf_renderer.py
new file mode 100644
index 0000000000000000000000000000000000000000..a69abd995429eda82150e71552cf3041858255c4
--- /dev/null
+++ b/ebook_pdf_engine/render/pdf_renderer.py
@@ -0,0 +1,39 @@
+from __future__ import annotations
+
+from pathlib import Path
+from typing import Iterable
+
+from reportlab.pdfgen import canvas
+
+from ebook_pdf_engine.layout.engine import LayoutImage, LayoutPage, LayoutText
+
+
+class PdfRenderer:
+    def __init__(self, output_path: str | Path) -> None:
+        self.output_path = Path(output_path)
+
+    def render(self, pages: Iterable[LayoutPage]) -> Path:
+        page_list = list(pages)
+        if not page_list:
+            raise ValueError("No pages to render")
+        first_page = page_list[0]
+        pdf = canvas.Canvas(str(self.output_path), pagesize=(first_page.width, first_page.height))
+        for page in page_list:
+            pdf.setPageSize((page.width, page.height))
+            for element in page.elements:
+                if isinstance(element, LayoutText):
+                    pdf.setFont(element.font_name, element.font_size)
+                    pdf.drawString(element.x, element.y, element.text)
+                elif isinstance(element, LayoutImage):
+                    pdf.drawImage(
+                        element.path,
+                        element.x,
+                        element.y,
+                        width=element.width,
+                        height=element.height,
+                        preserveAspectRatio=True,
+                        mask="auto",
+                    )
+            pdf.showPage()
+        pdf.save()
+        return self.output_path
diff --git a/main.py b/main.py
new file mode 100644
index 0000000000000000000000000000000000000000..95295b084226aa484c218d348d5f029dea192c2e
--- /dev/null
+++ b/main.py
@@ -0,0 +1,63 @@
+from __future__ import annotations
+
+from pathlib import Path
+
+from ebook_pdf_engine.content.models import Chapter, Ebook, ImageBlock, Paragraph
+from ebook_pdf_engine.layout.engine import LayoutEngine
+from ebook_pdf_engine.render.pdf_renderer import PdfRenderer
+
+
+def build_sample_ebook(asset_path: Path) -> Ebook:
+    return Ebook(
+        title="Sample E-Book",
+        author="PDF Engine",
+        chapters=[
+            Chapter(
+                title="Chapter 1: Getting Started",
+                blocks=[
+                    Paragraph(
+                        "This is a short example paragraph to demonstrate how text flows "
+                        "across the page. The layout engine wraps lines to keep content "
+                        "within margins."
+                    ),
+                    ImageBlock(path=str(asset_path), full_page=False),
+                    Paragraph(
+                        "Images can also be inserted between paragraphs. The renderer "
+                        "handles scaling and keeps them aligned within the layout."
+                    ),
+                ],
+            ),
+            Chapter(
+                title="Chapter 2: Full Page Image",
+                blocks=[
+                    Paragraph(
+                        "Sometimes a full-page illustration is needed to break up a "
+                        "chapter. The next page shows a full-page image."
+                    ),
+                    ImageBlock(path=str(asset_path), full_page=True),
+                    Paragraph(
+                        "After a full-page image, the layout resumes on a new page to "
+                        "keep content readable."
+                    ),
+                ],
+            ),
+        ],
+    )
+
+
+def main() -> None:
+    asset_path = Path(__file__).parent / "ebook_pdf_engine" / "assets" / "sample_image.png"
+    output_path = Path("sample_ebook.pdf")
+
+    ebook = build_sample_ebook(asset_path)
+    layout_engine = LayoutEngine()
+    pages = layout_engine.layout_ebook(ebook)
+
+    renderer = PdfRenderer(output_path)
+    renderer.render(pages)
+
+    print(f"Generated PDF at {output_path.resolve()}")
+
+
+if __name__ == "__main__":
+    main()
diff --git a/requirements.txt b/requirements.txt
new file mode 100644
index 0000000000000000000000000000000000000000..c17e5b8dd1e94866c09fd0b4cef698fccff94b5a
--- /dev/null
+++ b/requirements.txt
@@ -0,0 +1 @@
+reportlab>=3.6.12
 
EOF
)
