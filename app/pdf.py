from pathlib import Path
from typing import Iterator
import pymupdf

def discover_pdfs(input_dir: Path) -> list[Path]:
    return sorted(input_dir.glob('*.pdf'))

def render_pages(pdf_path: Path, dpi: int) -> Iterator[tuple[int, object]]:
    document = pymupdf.open(pdf_path)
    try:
        scale = dpi / 72.0
        matrix = pymupdf.Matrix(scale, scale)
        for page_index, page in enumerate(document):
            pixmap = page.get_pixmap(matrix=matrix, alpha=False)
            yield page_index + 1, pixmap.pil_image()
    finally:
        document.close()
