import os
import sys
import json

sys.path.insert(0, os.path.abspath("."))
from backend.config import load_dotenv
load_dotenv()

from backend.extraction.gemini_provider import GeminiProvider
from backend.extraction.prompts import BIDDER_FACT_SYSTEM_PROMPT, format_bidder_fact_prompt
from backend.extraction.evidence_grounder import EvidenceGrounder
from backend.ingestion.pipeline import DocumentIngestionPipeline

print("=== STEP 1: PHYSICAL INGESTION VIA PYMUPDF ===")
bidder_pdf = "data/demo/JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf"
pipeline = DocumentIngestionPipeline()
ingest_res = pipeline.ingest_file(bidder_pdf)
print(f"Ingested {len(ingest_res.pages)} pages, total blocks: {sum(len(p.blocks) for p in ingest_res.pages)}")

print("\n=== STEP 2: NATIVE PDF EXTRACTION VIA GEMINI ===")
provider = GeminiProvider()
print(f"Provider model: {provider.model_name}")

with open(bidder_pdf, "rb") as f:
    pdf_bytes = f.read()

prompt = format_bidder_fact_prompt("JARVIS_DEMO_PASS_BIDDER", ingest_res.pages)
print(f"Sending {len(pdf_bytes)} bytes of PDF with prompt...")

resp = provider.generate_structured_from_pdf(
    pdf_bytes=pdf_bytes,
    prompt=prompt,
    system_prompt=BIDDER_FACT_SYSTEM_PROMPT,
    temperature=0.0,
)

print(f"Gemini response error: {resp.error}")
print(f"Gemini response latency: {resp.latency_ms:.2f} ms")
print(f"Gemini model used: {resp.model_name}")

if not resp.error and resp.content:
    data = json.loads(resp.content)
    facts = data.get("facts", [])
    print(f"Extracted {len(facts)} raw facts from Gemini Native PDF!")
    for f in facts[:5]:
        print(f"  Field: {f.get('field')}, Page: {f.get('source_page')}, Snippet: {f.get('evidence_snippet')[:60]}...")

    print("\n=== STEP 3: DETERMINISTIC EVIDENCE GROUNDING ===")
    grounder = EvidenceGrounder(ingest_res)
    grounded_count = 0
    for f in facts:
        res = grounder.ground_by_semantic_pointer(
            source_page=f.get("source_page", 1),
            evidence_snippet=f.get("evidence_snippet", ""),
        )
        if res.is_valid:
            grounded_count += 1
            best_block = res.resolved_evidence[0] if res.resolved_evidence else {}
            print(f"  [GROUNDED] Field: {f.get('field')} -> Block: {best_block.get('block_id')} Page: {res.primary_page} BBox: {res.primary_bbox}")
        else:
            print(f"  [UNGROUNDED] Field: {f.get('field')} -> {res.errors}")

    print(f"\nGrounding summary: {grounded_count}/{len(facts)} facts successfully grounded to PyMuPDF physical blocks!")
