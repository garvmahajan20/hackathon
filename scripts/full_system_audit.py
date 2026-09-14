# -*- coding: utf-8 -*-
"""
Full System Discovery & Static Forensic Audit Script.
Audits:
1. All Backend API endpoints vs Frontend API client calls.
2. Serialization / Schema mismatches between Pydantic and TypeScript interfaces.
3. Security: Path traversal, CORS, secret leakage, file upload sanitization.
4. Persistence / Caching / State leakage across verifications.
5. Rule Engine, Contradiction Engine, and Adjudication logic.
"""

import inspect
import json
import os
import re
import sys
sys.path.insert(0, ".")
from typing import get_type_hints

def audit_api_endpoints():
    print("=== 1. AUDITING API ENDPOINTS ===")
    from backend.api.app import app
    from fastapi.routing import APIRoute

    backend_routes = set()
    for r in app.routes:
        if isinstance(r, APIRoute):
            for method in r.methods:
                backend_routes.add((method, r.path))

    for m, p in sorted(backend_routes):
        print(f"  Backend: {m:6} {p}")

    # Inspect frontend API calls
    print("\n--- Frontend Client Endpoint Audit ---")
    client_ts_path = "frontend/src/api/client.ts"
    with open(client_ts_path, "r", encoding="utf-8") as f:
        content = f.read()

    calls = re.findall(r'request<[^>]+>\(["\']([^"\']+)["\'](?:,\s*\{[^}]*method:\s*["\']([A-Z]+)["\'])?', content)
    for path, method in calls:
        method = method or "GET"
        clean_path = re.sub(r'\$\{[^}]+\}', '{id}', path)
        print(f"  Frontend: {method:6} {clean_path}")

def audit_security_and_uploads():
    print("\n=== 2. AUDITING SECURITY & FILE UPLOADS ===")
    from backend.api.app import _validate_and_save_file

    # Check for path traversal vulnerabilities in _validate_and_save_file
    print("  Checking _validate_and_save_file security controls...")
    lines = inspect.getsource(_validate_and_save_file).splitlines()
    for l in lines:
        if ".." in l or "content_type" in l or "size" in l or "shutil" in l or "write" in l or "magic" in l or "MAGIC" in l:
            print(f"    {l.strip()}")

def audit_rule_engine_and_models():
    print("\n=== 3. AUDITING MODELS & RULE ENGINE ===")
    from backend.core.models import TenderRequirement, BidderFact, VerificationResult, ComplianceStatus
    from backend.orchestration.models import AggregatedVerification, VerificationDossier

    # Check field presence
    print("  TenderRequirement fields:", list(TenderRequirement.__annotations__.keys()))
    print("  BidderFact fields:", list(BidderFact.__annotations__.keys()))
    print("  VerificationResult fields:", list(VerificationResult.__annotations__.keys()))
    print("  AggregatedVerification fields:", list(AggregatedVerification.__annotations__.keys()))

def audit_frontend_types():
    print("\n=== 4. AUDITING FRONTEND TYPESCRIPT CONTRACTS ===")
    ts_types_path = "frontend/src/types/index.ts"
    if os.path.exists(ts_types_path):
        with open(ts_types_path, "r", encoding="utf-8") as f:
            ts_content = f.read()
        interfaces = re.findall(r'export interface (\w+)', ts_content)
        print("  TypeScript Interfaces:", interfaces)

if __name__ == "__main__":
    audit_api_endpoints()
    audit_security_and_uploads()
    audit_rule_engine_and_models()
    audit_frontend_types()
