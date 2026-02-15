from __future__ import annotations
"""PDF text extraction using pdfplumber and OCR."""

import pdfplumber
import fitz  # PyMuPDF
import pytesseract
from PIL import Image
from pathlib import Path
import io


class PDFExtractor:
    """Extract text from PDF files using text extraction and OCR."""

    def __init__(self, pdf_path: str | Path):
        """Initialize with path to PDF file."""
        self.pdf_path = Path(pdf_path)
        if not self.pdf_path.exists():
            raise FileNotFoundError(f"PDF file not found: {pdf_path}")

    def extract_text(self, use_ocr: bool = True, min_text_threshold: int = 200) -> str:
        """
        Extract all text from the PDF using text extraction and/or OCR.

        Args:
            use_ocr: Whether to use OCR if minimal text is found
            min_text_threshold: Minimum characters to consider adequate text extraction

        Returns:
            str: All text content from all pages concatenated
        """
        # First, try standard text extraction
        text_extracted = self._extract_text_standard()

        # If we got enough text, return it
        if len(text_extracted) >= min_text_threshold:
            return text_extracted

        # Otherwise, use OCR if enabled
        if use_ocr:
            print(f"Minimal text found ({len(text_extracted)} chars). Using OCR...")
            ocr_text = self._extract_text_ocr()
            # Combine both (in case some text was extractable)
            combined = text_extracted + "\n" + ocr_text
            return combined
        else:
            return text_extracted

    def _extract_text_standard(self) -> str:
        """Extract text using standard pdfplumber extraction."""
        all_text = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                if text:
                    all_text.append(text)

        return "\n".join(all_text)

    def _extract_text_ocr(self) -> str:
        """Extract text from PDF images using OCR."""
        all_text = []

        # Use PyMuPDF to extract images and render pages
        doc = fitz.open(self.pdf_path)

        for page_num in range(len(doc)):
            page = doc[page_num]

            # Render page to image at high resolution for better OCR
            # zoom=2.0 means 2x resolution (144 DPI instead of 72 DPI)
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)

            # Convert to PIL Image
            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            # Perform OCR with multiple configurations for better coverage
            # Try PSM 6 (uniform block) first - better for engineering diagrams
            custom_config = r'--oem 3 --psm 6'
            page_text = pytesseract.image_to_string(img, config=custom_config)

            # Also try PSM 11 (sparse text) to catch scattered tags
            custom_config_sparse = r'--oem 3 --psm 11'
            page_text_sparse = pytesseract.image_to_string(img, config=custom_config_sparse)

            # Combine both results
            page_text = page_text + "\n" + page_text_sparse

            if page_text:
                all_text.append(page_text)

        doc.close()

        return "\n".join(all_text)

    def extract_text_by_page(self, use_ocr: bool = True) -> list[str]:
        """
        Extract text from each page separately.

        Args:
            use_ocr: Whether to use OCR for extraction

        Returns:
            list[str]: List of text content, one per page
        """
        if use_ocr:
            return self._extract_text_by_page_ocr()
        else:
            return self._extract_text_by_page_standard()

    def _extract_text_by_page_standard(self) -> list[str]:
        """Extract text by page using standard extraction."""
        pages_text = []

        with pdfplumber.open(self.pdf_path) as pdf:
            for page in pdf.pages:
                text = page.extract_text()
                pages_text.append(text if text else "")

        return pages_text

    def _extract_text_by_page_ocr(self) -> list[str]:
        """Extract text by page using OCR."""
        pages_text = []
        doc = fitz.open(self.pdf_path)

        for page_num in range(len(doc)):
            page = doc[page_num]
            mat = fitz.Matrix(2.0, 2.0)
            pix = page.get_pixmap(matrix=mat)

            img_data = pix.tobytes("png")
            img = Image.open(io.BytesIO(img_data))

            custom_config = r'--oem 3 --psm 11'
            page_text = pytesseract.image_to_string(img, config=custom_config)
            pages_text.append(page_text if page_text else "")

        doc.close()
        return pages_text

    def get_page_count(self) -> int:
        """Get the number of pages in the PDF."""
        with pdfplumber.open(self.pdf_path) as pdf:
            return len(pdf.pages)
