import sys, os, pytest
from pathlib import Path

# Add repo root to sys.path so "import nano" works when running from tests/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

# only run if optional deps are installed
pytest.importorskip("reportlab.pdfgen.canvas")
pytest.importorskip("PyPDF2")

def test_pdf_multiline_ingest(tmp_path: Path):
    from reportlab.pdfgen import canvas
    from nano import InMemoryKV, ToolsRegistry, PerceptionEngine

    pdf = tmp_path / "multi.pdf"
    c = canvas.Canvas(str(pdf))
    c.drawString(72, 740, "ეს არის PDF test")
    c.drawString(72, 720, "Line two with number 123")
    c.save()

    mem = InMemoryKV()
    perceiver = PerceptionEngine(mem, ToolsRegistry())
    # First, raw extraction should contain our text
    text = perceiver._extract_pdf_text(str(pdf))
    assert text and "123" in text

    # Then, full ingest_file should succeed and produce tokens
    res = perceiver.ingest_file(str(pdf), title="pdf-test")
    assert res.get("ok") is True
    assert res.get("tokens", 0) > 0
