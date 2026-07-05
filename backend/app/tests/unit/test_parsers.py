import pytest
import fitz
from backend.app.parser.txt_parser import TXTParser
from backend.app.parser.pdf_parser import PDFParser

pytestmark = pytest.mark.unit


class TestTXTParser:
    def test_parses_plain_text(self, tmp_path):
        """UT-011"""
        f = tmp_path / "a.txt"
        f.write_text("hello world")
        assert TXTParser().parse(str(f)) == "hello world"

    def test_returns_none_for_missing_file(self, tmp_path):
        """UT-012 (R11)"""
        assert TXTParser().parse(str(tmp_path / "missing.txt")) is None

    def test_returns_none_for_empty_file(self, tmp_path):
        """UT-013"""
        f = tmp_path / "empty.txt"
        f.write_text("   \n  ")
        assert TXTParser().parse(str(f)) is None

    def test_recovers_from_bad_encoding(self, tmp_path):
        """UT-014 (R11)"""
        f = tmp_path / "bad.txt"
        f.write_bytes(b"\xff\xfe not valid utf-8 alone")
        assert TXTParser().parse(str(f)) is not None


def _make_pdf(path, text: str):
    doc = fitz.open()
    doc.new_page().insert_text((72, 72), text)
    doc.save(str(path))
    doc.close()


class TestPDFParser:
    def test_parses_text_pdf(self, tmp_path):
        """UT-021"""
        f = tmp_path / "doc.pdf"
        _make_pdf(f, "hello from pdf")
        text = PDFParser().parse(str(f))
        assert text is not None and "hello" in text.lower()

    def test_returns_none_for_corrupt_pdf(self, tmp_path):
        """UT-022 (R11)"""
        f = tmp_path / "corrupt.pdf"
        f.write_bytes(b"not actually a pdf")
        assert PDFParser().parse(str(f)) is None