"""Content structure for e-books."""

from __future__ import annotations

from dataclasses import dataclass, field
from typing import List, Optional, Sequence


@dataclass(frozen=True)
class Paragraph:
    text: str


@dataclass(frozen=True)
class ImageBlock:
    path: str
    full_page: bool = False
    caption: Optional[str] = None


ContentBlock = Paragraph | ImageBlock


@dataclass(frozen=True)
class Chapter:
    title: str
    blocks: Sequence[ContentBlock] = field(default_factory=list)


@dataclass(frozen=True)
class Ebook:
    title: str
    author: str
    chapters: Sequence[Chapter] = field(default_factory=list)
