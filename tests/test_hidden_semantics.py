import ctypes
import json
import os
import subprocess
import sys
from pathlib import Path

# Add repo root to sys.path so "import nano" works when running from tests/
ROOT = Path(__file__).resolve().parents[1]
if str(ROOT) not in sys.path:
    sys.path.insert(0, str(ROOT))

NANO = (ROOT / "nano.py").resolve()


def _set_hidden_windows(p: Path, hidden=True, system=True):
    if os.name != "nt":
        return
    attrs = 0
    if hidden:
        attrs |= 0x2  # HIDDEN
    if system:
        attrs |= 0x4  # SYSTEM
    ctypes.windll.kernel32.SetFileAttributesW(str(p), attrs)


def _run_cli(args):
    """Run nano.py and parse the LAST JSON object from stdout (handles pretty-printed JSON)."""
    proc = subprocess.run(
        [sys.executable, str(NANO), *args], text=True, capture_output=True, check=False
    )
    out = (proc.stdout or "").strip()
    # grab the last {...} block from stdout
    first = out.find("{")
    last = out.rfind("}")
    payload = {}
    if first != -1 and last != -1 and last > first:
        blob = out[first : last + 1]
        payload = json.loads(blob)
    return proc.returncode, payload, out, (proc.stderr or "")


def test_ingest_dir_hidden_semantics(tmp_path: Path):
    root = tmp_path / "safe_root"
    data = tmp_path / "nano_test"
    data.mkdir()

    # files/dirs per your PS repro
    (data / "a.txt").write_text("hello one", encoding="utf-8")
    (data / "desktop.ini").write_text("hidden stuff", encoding="utf-8")
    (data / ".secret.txt").write_text("dot secret", encoding="utf-8")
    (data / "hidden_dir").mkdir()
    (data / "hidden_dir" / "b.txt").write_text("secret", encoding="utf-8")

    # mark Hidden/System on Windows
    if os.name == "nt":
        _set_hidden_windows(data / "desktop.ini")
        _set_hidden_windows(data / "hidden_dir")

    # 1) --ingest-skip-hidden
    rc1, res1, so1, se1 = _run_cli(
        [
            "--ingest-dir",
            str(data),
            "--ingest-skip-hidden",
            "--ingest-exts=",  # include all extensions
            "--root-dir",
            str(root),
        ]
    )
    assert "total_considered" in res1, f"stdout:\n{so1}\nstderr:\n{se1}"
    # Windows: desktop.ini + hidden_dir დამალულია; dot არ ითვლება დამალულად => 2
    # POSIX: dot-ფაილიც დამალულია => 1 (მხოლოდ a.txt)
    expected = 2 if os.name == "nt" else 1
    assert res1["total_considered"] == expected, res1
    assert rc1 == 0

    # 2) without skip -> 4
    rc2, res2, so2, se2 = _run_cli(
        [
            "--ingest-dir",
            str(data),
            "--ingest-exts=",
            "--root-dir",
            str(root),
        ]
    )
    assert "total_considered" in res2, f"stdout:\n{so2}\nstderr:\n{se2}"
    assert res2["total_considered"] == 4, res2
    assert rc2 == 0


def test_ingest_dir_not_found(tmp_path: Path):
    root = tmp_path / "safe_root"
    missing = tmp_path / "nope_does_not_exist"
    rc, res, so, se = _run_cli(
        [
            "--ingest-dir",
            str(missing),
            "--ingest-skip-hidden",
            "--root-dir",
            str(root),
        ]
    )
    # our CLI intentionally exits 2 on missing path and prints a JSON error
    assert rc == 2
    assert res.get("ok") is False
    assert res.get("error") == "ingest_dir_not_found"
    assert str(res.get("path", "")).endswith(str(missing))
