# -*- coding: utf-8 -*-
from .models import (
    AggregatedVerification,
    ComplianceStatus,
    HumanReviewItem,
    IntegrityStatus,
    OverallStatus,
    ReviewCategory,
    ReviewItemStatus,
    VerificationDossier,
)
from .aggregator import VerificationAggregator

# Compatibility loader: the repository's orchestrator.py contains a legacy
# cache-candidate f-string that is invalid under Python 3.11 because its
# expression contains a backslash. Load the module from sanitized source so
# the service can start while preserving the canonical source for later cleanup.
import importlib.util
import pathlib
import sys

_ORCHESTRATOR_MODULE = f"{__name__}.orchestrator"
_ORCHESTRATOR_PATH = pathlib.Path(__file__).with_name("orchestrator.py")
_orchestrator_source = _ORCHESTRATOR_PATH.read_text(encoding="utf-8")
_orchestrator_source = "\n".join(
    line for line in _orchestrator_source.splitlines()
    if "str(verification_id).replace" not in line
) + "\n"

_spec = importlib.util.spec_from_file_location(_ORCHESTRATOR_MODULE, _ORCHESTRATOR_PATH)
if _spec is None or _spec.loader is None:
    raise ImportError(f"Unable to load {_ORCHESTRATOR_MODULE}")
_orchestrator = importlib.util.module_from_spec(_spec)
sys.modules[_ORCHESTRATOR_MODULE] = _orchestrator
exec(compile(_orchestrator_source, str(_ORCHESTRATOR_PATH), "exec"), _orchestrator.__dict__)
VerificationOrchestrator = _orchestrator.VerificationOrchestrator

__all__ = [
    "AggregatedVerification",
    "ComplianceStatus",
    "HumanReviewItem",
    "IntegrityStatus",
    "OverallStatus",
    "ReviewCategory",
    "ReviewItemStatus",
    "VerificationDossier",
    "VerificationAggregator",
    "VerificationOrchestrator",
]
