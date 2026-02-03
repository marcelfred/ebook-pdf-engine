"""Layout logic for translating content into PDF flowables."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Iterable, List

from reportlab.lib import pagesizes
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.lib.utils import ImageReader
from reportlab.platypus import Image, PageBreak, Paragraph, Spacer

from ebook_pdf_engine.content import Chapter, ContentBlock, Ebook, ImageBlock, Paragraph as TextBlock


@dataclass(frozen=True)
class PageLayout:
    page_size: tuple[float, float] = pagesizes.A4
    margin_left: float = 0.75 * inch
    margin_right: float = 0.75 * inch
    margin_top: float = 0.9 * inch
    margin_bottom: float = 0.9 * inch

    @property
    def frame_width(self) -> float:
        return self.page_size[0] - self.margin_left - self.margin_right

    @property
    def frame_height(self) -> float:
        return self.page_size[1] - self.margin_top - self.margin_bottom


class LayoutEngine:
    def __init__(self, layout: PageLayout | None = None) -> None:
        self.layout = layout or PageLayout()
        self.styles = getSampleStyleSheet()
        self.styles.add(
            ParagraphStyle(
                name="ChapterTitle",
                parent=self.styles["Heading1"],
                spaceAfter=0.3 * inch,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="BodyText",
                parent=self.styles["BodyText"],
                leading=15,
                spaceAfter=0.2 * inch,
            )
        )
        self.styles.add(
            ParagraphStyle(
                name="Caption",
                parent=self.styles["Italic"],
                fontSize=9,
                spaceAfter=0.2 * inch,
            )
        )

    def build_flowables(self, ebook: Ebook) -> List[object]:
        flowables: List[object] = []
        flowables.append(Paragraph(ebook.title, self.styles["Title"]))
        flowables.append(Paragraph(f"By {ebook.author}", self.styles["Italic"]))
        flowables.append(PageBreak())

        for index, chapter in enumerate(ebook.chapters, start=1):
            flowables.extend(self._chapter_flowables(chapter, index))
            flowables.append(PageBreak())

        if flowables:
            flowables.pop()
        return flowables

    def _chapter_flowables(self, chapter: Chapter, index: int) -> Iterable[object]:
        yield Paragraph(f"Chapter {index}: {chapter.title}", self.styles["ChapterTitle"])
        for block in chapter.blocks:
            yield from self._block_flowables(block)

    def _block_flowables(self, block: ContentBlock) -> Iterable[object]:
        if isinstance(block, TextBlock):
            yield Paragraph(block.text, self.styles["BodyText"])
            return

        if isinstance(block, ImageBlock):
            if block.full_page:
                yield from self._full_page_image(block)
            else:
                yield from self._inline_image(block)

    def _inline_image(self, block: ImageBlock) -> Iterable[object]:
        image, width, height = self._fit_image(block.path, self.layout.frame_width, self.layout.frame_height / 2)
        yield Spacer(1, 0.1 * inch)
        yield image
        if block.caption:
            yield Paragraph(block.caption, self.styles["Caption"])
        yield Spacer(1, 0.2 * inch)

    def _full_page_image(self, block: ImageBlock) -> Iterable[object]:
        image, _, _ = self._fit_image(block.path, self.layout.frame_width, self.layout.frame_height)
        yield PageBreak()
        yield image
        if block.caption:
            yield Paragraph(block.caption, self.styles["Caption"])
        yield PageBreak()

    @staticmethod
    def _fit_image(path: str, max_width: float, max_height: float) -> tuple[Image, float, float]:
        reader = ImageReader(path)
        width, height = reader.getSize()
        scale = min(max_width / width, max_height / height)
        scaled_width = width * scale
        scaled_height = height * scale
        image = Image(path, width=scaled_width, height=scaled_height)
        image.hAlign = "CENTER"
        return image, scaled_width, scaled_height
