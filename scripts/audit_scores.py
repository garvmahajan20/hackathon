import json

def audit(file_path, label):
    data = json.load(open(file_path, encoding="utf-8"))
    v = data.get("verification", {})
    reqs = data.get("dossier", {}).get("requirements", [])
    req_map = {r.get("requirement_id"): r for r in reqs}
    
    print(f"\n==========================================")
    print(f"SCORE AUDIT FOR: {label}")
    print(f"File: {file_path}")
    print(f"VID: {v.get('verification_id')} | Score: {v.get('compliance_score')}% | Verdict: {v.get('overall_status')} | Comp: {v.get('compliance_status')} | Integ: {v.get('integrity_status')}")
    print(f"==========================================")
    
    results = v.get("verification_results", [])
    print(f"{'Req ID':<22} | {'Type':<17} | {'Mand':<5} | {'Status':<8} | {'Expected':<30} | {'Actual':<25} | {'Weight':<6} | {'Earned'}")
    print("-" * 130)
    
    tot_possible = 0.0
    tot_earned = 0.0
    
    for r in results:
        rid = r.get("requirement_id", "")
        rtype = r.get("requirement_type", "")
        status = r.get("status", "")
        exp = str(r.get("expected", ""))[:28]
        act = str(r.get("actual", ""))[:23]
        
        req_obj = req_map.get(rid, {})
        mandatory = req_obj.get("mandatory", True)
        
        # Calculate weight
        if rtype in ("PROCESS_CONDITION", "INFORMATIONAL", "GENERAL_POLICY") or status in ("N/A", "N_A"):
            weight = 0.0
            earned = 0.0
        else:
            base = 10.0 if mandatory else 5.0
            sev = r.get("severity", "INFO")
            mult = {"CRITICAL": 2.5, "HIGH": 1.5, "MEDIUM": 1.0, "LOW": 0.5, "INFO": 1.0}.get(sev, 1.0)
            weight = base * mult
            tot_possible += weight
            if status in ("PASS", "OVERRIDDEN_PASS"):
                earned = weight
            elif status == "PARTIAL":
                earned = weight * 0.5
            elif status == "REVIEW":
                earned = weight * 0.25
            else:
                earned = 0.0
            tot_earned += earned
            
        print(f"{rid:<22} | {rtype:<17} | {str(mandatory):<5} | {status:<8} | {exp:<30} | {act:<25} | {weight:<6.1f} | {earned:<6.1f}")
        
    print("-" * 130)
    calc_raw = (tot_earned / tot_possible * 100.0) if tot_possible > 0 else 0.0
    print(f"Total Possible: {tot_possible:.1f} | Total Earned: {tot_earned:.1f} | Calculated Raw: {calc_raw:.2f}%")
    print(f"Breakdown in JSON: {v.get('compliance_score_breakdown')}")
    
    print("\n--- BIDDER FACTS ---")
    facts = data.get("dossier", {}).get("bidder", {}).get("facts", [])
    for f in facts:
        print(f"  p{f.get('page')}: field={f.get('field')} | canon={f.get('canonical_field')} | val={f.get('value')}")

# audit("data/cache/verifications/VERIF-GEM_2026_B_7959150-JARVIS_DEMO_FAIL_BIDDER_83d19717d2bc.json", "OLD FAIL (4.26%)")
# audit("data/cache/verifications/VERIF-TENDER-0001-JARVIS_DEMO_FAIL_BIDDER_GEM_2026_B_7959150_64fba055ad6e.json", "NEW LIVE FAIL (0.0%)")
# audit("data/cache/verifications/VERIF-TENDER-0001-JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150_0a5c9dab59bc.json", "LIVE PASS")
audit("data/cache/verifications/VERIF-TENDER-0001-JARVIS_DEMO_FORENSIC_BIDDER_GEM_2026_B_7959150_a12f5423dfb8.json", "LIVE FORENSIC")
