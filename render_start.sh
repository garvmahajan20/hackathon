#!/usr/bin/env bash
set -euo pipefail

# Render startup guard: remove the single legacy Python 3.11-incompatible
# cache-candidate f-string before importing the FastAPI application.
python - <<'PY'
from pathlib import Path

orchestrator_path = Path("backend/orchestration/orchestrator.py")
if orchestrator_path.exists():
    text = orchestrator_path.read_text(encoding="utf-8")
    marker = "str(verification_id).replace"
    if marker in text:
        lines = [line for line in text.splitlines() if marker not in line]
        orchestrator_path.write_text("\n".join(lines) + "\n", encoding="utf-8")

# UptimeRobot's free HTTP monitor checks with HEAD. FastAPI does not
# automatically expose HEAD for this explicit GET route, so make the
# existing health route accept HEAD in the deployed runtime only.
app_path = Path("backend/api/app.py")
if app_path.exists():
    text = app_path.read_text(encoding="utf-8")
    old = '@app.get("/health", response_model=HealthResponse)'
    new = '@app.api_route("/health", methods=["GET", "HEAD"], response_model=HealthResponse)'
    if old in text and new not in text:
        text = text.replace(old, new, 1)
        app_path.write_text(text, encoding="utf-8")
PY

exec python -m uvicorn backend.api.app:app --host 0.0.0.0 --port "${PORT}"
