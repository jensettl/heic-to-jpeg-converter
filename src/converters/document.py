"""Document file converter using pypdf and python-docx."""

from pathlib import Path

from .base import BaseConverter


class DocumentConverter(BaseConverter):
    """Converts document files between common formats."""

    def convert(self, source: Path, target_format: str) -> Path:
        """Convert a document file to the target format.

        Currently supported routes:
            pdf  → txt
            docx → txt

        Args:
            source: Path to the source document.
            target_format: Target extension without dot (e.g. "txt").

        Returns:
            Path to the converted document.

        Raises:
            ValueError: If the conversion route is unsupported.
        """
        source_fmt = source.suffix.lower().lstrip(".")
        target_fmt = target_format.lower()
        route = (source_fmt, target_fmt)

        converters = {
            ("pdf",  "txt"):  self._pdf_to_txt,
            ("docx", "txt"):  self._docx_to_txt,
        }

        if route not in converters:
            raise ValueError(
                f"Unsupported document conversion: {source_fmt} → {target_fmt}"
            )

        return converters[route](source)

    def _pdf_to_txt(self, source: Path) -> Path:
        """Extract text from a PDF and save as .txt.

        Args:
            source: Path to the PDF file.

        Returns:
            Path to the output .txt file.
        """
        from pypdf import PdfReader

        output_path = self.get_output_path(source, "txt")
        reader = PdfReader(str(source))

        text = "\n".join(
            page.extract_text() or "" for page in reader.pages
        )

        output_path.write_text(text, encoding="utf-8")
        return output_path

    def _docx_to_txt(self, source: Path) -> Path:
        """Extract text from a DOCX file and save as .txt.

        Args:
            source: Path to the DOCX file.

        Returns:
            Path to the output .txt file.
        """
        from docx import Document

        output_path = self.get_output_path(source, "txt")
        doc = Document(str(source))

        text = "\n".join(para.text for para in doc.paragraphs)
        output_path.write_text(text, encoding="utf-8")
        return output_path
