import json
import glob
import os

print("=== INSPECTING CACHED RUNS ===")
for p in glob.glob("data/cache/verifications/*.json"):
    fn = os.path.basename(p)
    if "DEMO" not in fn:
        continue
    data = json.load(open(p, encoding="utf-8"))
    v = data.get("verification", {})
    vid = v.get("verification_id")
    bid = v.get("bid_id")
    score = v.get("compliance_score")
    overall = v.get("overall_status")
    comp = v.get("compliance_status")
    integ = v.get("integrity_status")
    results = v.get("verification_results", [])
    fails = [r for r in results if r.get("status") == "FAIL"]
    missing = [r for r in results if r.get("status") == "MISSING"]
    pass_cnt = len([r for r in results if r.get("status") == "PASS"])
    na_cnt = len([r for r in results if r.get("status") == "N/A"])
    print(f"\nFILE: {fn}")
    print(f"  VID: {vid}")
    print(f"  BID: {bid}")
    print(f"  SCORE: {score}% | OVERALL: {overall} | COMP: {comp} | INTEG: {integ}")
    print(f"  TOTAL: {len(results)} | PASS: {pass_cnt} | FAIL: {len(fails)} | MISSING: {len(missing)} | N/A: {na_cnt}")
    for f in fails:
        print(f"    FAIL -> {f.get('requirement_id')} | type: {f.get('requirement_type')} | exp: {f.get('expected')} | act: {f.get('actual')} | reason: {f.get('reason')}")
    for m in missing:
        print(f"    MISSING -> {m.get('requirement_id')} | type: {m.get('requirement_type')} | exp: {m.get('expected')} | act: {m.get('actual')} | reason: {m.get('reason')}")
    contras = v.get("contradictions", [])
    if contras:
        print(f"    CONTRADICTIONS ({len(contras)}):")
        for c in contras:
            print(f"      - {c.get('type')}: {c.get('description')}")
