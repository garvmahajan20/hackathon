#!/usr/bin/env bash
set -euo pipefail

python - <<'PY'
from pathlib import Path

path = Path('backend/orchestration/orchestrator.py')
if path.exists():
    text = path.read_text(encoding='utf-8')
    marker = 'str(verification_id).replace'
    if marker in text:
        lines = [line for line in text.splitlines() if marker not in line]
        path.write_text('\n'.join(lines) + '\n', encoding='utf-8')
PY

exec python -m uvicorn backend.api.app:app --host 0.0.0.0 --port "${PORT}"
