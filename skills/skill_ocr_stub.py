# Auto-safe OCR stub (no forbidden imports/calls)
SKILL_META = {"description": "Stub OCR that echoes image path as text"}


def ocr(image_path=None, **kw):
    txt = f'OCR_STUB from: {image_path or ""}'
    return {"ok": True, "text": txt}


SKILLS = {"ocr": ocr}
