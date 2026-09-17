"""Runtime compatibility guard for the Railway deployment.

Python imports sitecustomize automatically before application imports. The
legacy orchestrator contains a redundant filename candidate whose f-string is
invalid under Python 3.11 because the expression contains a backslash. The
canonical _get_cache_filename helper already provides this behavior, so this
startup guard removes only that redundant line when present.
"""
from pathlib import Path


def _sanitize_orchestrator() -> None:
    path = Path(__file__).resolve().parent / "backend" / "orchestration" / "orchestrator.py"
    if not path.exists():
        return
    try:
        text = path.read_text(encoding="utf-8")
    except OSError:
        return

    marker = "str(verification_id).replace"
    if marker not in text:
        return

    lines = [line for line in text.splitlines() if marker not in line]
    path.write_text("\n".join(lines) + "\n", encoding="utf-8")


_sanitize_orchestrator()
