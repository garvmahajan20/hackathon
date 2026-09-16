import os
import sys
import json
import asyncio

sys.path.insert(0, os.path.abspath("."))
from backend.config import load_dotenv
load_dotenv()

from backend.orchestration.orchestrator import VerificationOrchestrator
from backend.extraction.models import LLMMode

def run_case(case_name, tender_pdf, bidder_pdf, expected_status):
    print(f"\n{'='*50}\nRunning {case_name} Case...\n{'='*50}")
    
    mode_str = os.environ.get("VERIFICATION_MODE", "CACHED").upper()
    mode = LLMMode.LIVE if mode_str == "LIVE" else LLMMode.CACHED
    orchestrator = VerificationOrchestrator(mode=mode)
    
    tender_id = "GEM/2026/B/7959150"
    bid_id = f"JARVIS_DEMO_{case_name}_BIDDER"
    
    def log_callback(step_num, phase, msg, details):
        print(f"[{phase}] {msg}")
        
    try:
        result, dossier = orchestrator.verify_submission(
            tender_document_path=tender_pdf,
            bid_document_paths=[bidder_pdf],
            tender_id=tender_id,
            bid_id=bid_id,
            progress_callback=log_callback
        )
        
        print(f"\nOverall Status: {result.overall_status}")
        print(f"Compliance Score: {result.compliance_score}%")
        print(f"Critical Failures: {result.critical_failures}")
        print(f"Major Failures: {result.major_failures}")
        print(f"Human Review Items: {len(result.human_review_items)}")
        print(f"Contradictions/Integrity: {len(result.contradictions)}")
        for r in result.verification_results:
            st = r.get("status") if isinstance(r, dict) else getattr(r, "status", "")
            rid = r.get("requirement_id") if isinstance(r, dict) else getattr(r, "requirement_id", "")
            rtype = r.get("requirement_type") if isinstance(r, dict) else getattr(r, "requirement_type", "")
            reason = r.get("reason") if isinstance(r, dict) else getattr(r, "reason", "")
            if st in ("FAIL", "MISSING"):
                print(f"  [{st}] {rid} ({rtype}): {reason}")
        for c in result.contradictions:
            desc = c.get("description") if isinstance(c, dict) else getattr(c, "description", "")
            print(f"  [CONTRADICTION] {desc}")
        
        out_path = f"data/demo/result_{case_name.lower()}.json"
        with open(out_path, "w", encoding="utf-8") as f:
            json.dump(result.to_dict(), f, indent=2)
            
        dossier_path = f"data/demo/dossier_{case_name.lower()}.json"
        with open(dossier_path, "w", encoding="utf-8") as f:
            json.dump(dossier.to_dict(), f, indent=2)
            
        print(f"Saved result to {out_path} and {dossier_path}")
        
    except Exception as e:
        print(f"Error during {case_name} Case: {e}")
        import traceback
        traceback.print_exc()

def main():
    tender_pdf = "data/external/blind_test/REAL_WORLD_HOLDOUT_03.pdf"
    cases = [
        ("PASS", "data/demo/JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf", "PASS"),
        ("FAIL", "data/demo/JARVIS_DEMO_FAIL_BIDDER_GEM_2026_B_7959150.pdf", "FAIL"),
        ("FORENSIC", "data/demo/JARVIS_DEMO_FORENSIC_BIDDER_GEM_2026_B_7959150.pdf", "REVIEW_REQUIRED")
    ]
    
    selected_cases = [arg.upper() for arg in sys.argv[1:]] if len(sys.argv) > 1 else [c[0] for c in cases]
    for case_name, bidder_pdf, expected_status in cases:
        if case_name in selected_cases:
            run_case(case_name, tender_pdf, bidder_pdf, expected_status)

if __name__ == "__main__":
    main()
