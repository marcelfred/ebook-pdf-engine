"""PDF rendering layer."""

from __future__ import annotations

from dataclasses import dataclass
from pathlib import Path

from reportlab.platypus import SimpleDocTemplate

from ebook_pdf_engine.content import Ebook
from ebook_pdf_engine.layout import LayoutEngine, PageLayout


@dataclass(frozen=True)
class PDFRenderer:
    layout: PageLayout = PageLayout()

    def render(self, ebook: Ebook, output_path: str | Path) -> Path:
        output_path = Path(output_path)
        output_path.parent.mkdir(parents=True, exist_ok=True)
        layout_engine = LayoutEngine(self.layout)
        flowables = layout_engine.build_flowables(ebook)

        doc = SimpleDocTemplate(
            str(output_path),
            pagesize=self.layout.page_size,
            leftMargin=self.layout.margin_left,
            rightMargin=self.layout.margin_right,
            topMargin=self.layout.margin_top,
            bottomMargin=self.layout.margin_bottom,
        )
        doc.build(flowables)
        return output_path
