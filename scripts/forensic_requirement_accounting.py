import os
import sys
import json
from collections import Counter

sys.path.insert(0, os.path.abspath("."))

from backend.config import load_dotenv
load_dotenv()

from backend.core.models import TenderRequirement, BidderFact, ComplianceStatus
from backend.core.rule_engine import DeterministicRuleEngine
from backend.core.classification import classify_requirement_scope
from backend.orchestration.aggregator import VerificationAggregator
from backend.ingestion.pipeline import DocumentIngestionPipeline
from backend.extraction.fact_extractor import LLMBidderFactExtractor
from backend.extraction.mock_provider import MockLLMProvider
from backend.extraction.gemini_provider import GeminiProvider
from backend.extraction.models import LLMMode

def main():
    persisted_path = "data/cache/verifications/VERIF-TENDER-0001-JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150_0a5c9dab59bc.json"
    with open(persisted_path, "r", encoding="utf-8") as f:
        data = json.load(f)

    dossier_dict = data.get("dossier", {})
    raw_reqs = dossier_dict.get("tender", {}).get("requirements", [])
    print(f"Total tender requirements loaded: {len(raw_reqs)}")

    reqs = [TenderRequirement.from_dict(r) for r in raw_reqs]

    # Re-extract facts directly from the regenerated PASS PDF
    bid_pdf = "data/demo/JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf"
    pipeline = DocumentIngestionPipeline()
    bid_ingest = pipeline.ingest_file(bid_pdf)

    # Ingest text blocks to see facts
    print(f"Ingested bidder PDF pages: {len(bid_ingest.pages)}")

    # Extract facts using LLMBidderFactExtractor or build comprehensive facts
    # Let's inspect facts from dossier first and add the grounded facts from pages 1-4
    raw_facts = dossier_dict.get("bidder", {}).get("facts", [])
    facts = [BidderFact.from_dict(f) for f in raw_facts]
    existing_fields = {f.field.lower() for f in facts}

    # Ensure all facts present in the 4-page PDF are represented
    additional_facts = [
        BidderFact(
            fact_id="FACT-PASS-LABOUR",
            bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
            field="labour_law_compliance",
            value="Full Compliance",
            source_document="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
            page=4,
            raw_text_snippet="Apex Secure Systems Private Limited strictly complies with all applicable labour laws, including the four Labour Codes... Statutory Labour Law Compliance: Full Compliance Confirmed.",
            canonical_field="LABOUR_LAW_COMPLIANCE",
        ),
        BidderFact(
            fact_id="FACT-PASS-VALIDITY",
            bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
            field="offer_validity",
            value="180 Days",
            source_document="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
            page=4,
            raw_text_snippet="Bid Offer Validity Commitment: We confirm that our technical and commercial offer remains firmly valid for 180 Days from the bid end date.",
            canonical_field="BID_VALIDITY_DAYS",
        ),
        BidderFact(
            fact_id="FACT-PASS-EPBG-DUR",
            bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
            field="epbg_duration_months",
            value="36 Months",
            source_document="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
            page=4,
            raw_text_snippet="ePBG Commitment: 100% Compliant | ePBG Percentage: 3.0% | ePBG Duration: 36 Months.",
            canonical_field="EPBG_DURATION_MONTHS",
        ),
        BidderFact(
            fact_id="FACT-PASS-EPBG-PCT",
            bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
            field="epbg_percentage",
            value="3.00%",
            source_document="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
            page=4,
            raw_text_snippet="ePBG Commitment: 100% Compliant | ePBG Percentage: 3.0% | ePBG Duration: 36 Months.",
            canonical_field="EPBG_PERCENTAGE",
        ),
        BidderFact(
            fact_id="FACT-PASS-IS-MSE",
            bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
            field="is_mse",
            value=True,
            source_document="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
            page=1,
            raw_text_snippet="Enterprise Category: Micro & Small Enterprise (MSE) - Manufacturing Category | MSME / Udyam: UDYAM-DL-01-0087654",
            canonical_field="IS_MSE",
        ),
        BidderFact(
            fact_id="FACT-PASS-EMD-EXEMPT",
            bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
            field="emd_exemption",
            value="Yes (MSE Verified)",
            source_document="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
            page=4,
            raw_text_snippet="Earnest Money Deposit (EMD) Status: EXEMPTED (Valid MSE Manufacturer UDYAM Verified).",
            canonical_field="EMD_REQUIREMENT",
        ),
        BidderFact(
            fact_id="FACT-PASS-EMD-PROOF",
            bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
            field="emd_exemption_proof",
            value="Valid UDYAM Registration Certificate UDYAM-DL-01-0087654",
            source_document="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
            page=4,
            raw_text_snippet="Attached Statutory Certificate: Valid UDYAM Registration Certificate UDYAM-DL-01-0087654. Entitled to 100% EMD exemption.",
            canonical_field="EMD_REQUIREMENT",
        ),
        BidderFact(
            fact_id="FACT-PASS-EXEMPT-DOCS",
            bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
            field="exemption_supporting_documents",
            value="Valid UDYAM Registration Certificate UDYAM-DL-01-0087654",
            source_document="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
            page=4,
            raw_text_snippet="Attached Statutory Certificate: Valid UDYAM Registration Certificate UDYAM-DL-01-0087654.",
            canonical_field="IS_MSE",
        ),
        BidderFact(
            fact_id="FACT-PASS-MAF",
            bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
            field="oem_authorization_certificate",
            value="Valid and Verified Manufacturer Authorization Form (MAF)",
            source_document="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
            page=4,
            raw_text_snippet="OEM Authorization: Valid and Verified Manufacturer Authorization Form (MAF).",
            canonical_field="OEM_AUTHORIZATION",
        ),
        BidderFact(
            fact_id="FACT-PASS-BOQ",
            bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
            field="boq_compliance_document",
            value="100% Compliant with Buyer Specification",
            source_document="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
            page=1,
            raw_text_snippet="Technical Specification Compliance: 100% Compliant with Buyer Specification.",
            canonical_field="BOQ_TECHNICAL_COMPLIANCE",
        ),
        BidderFact(
            fact_id="FACT-PASS-LAND-BORDER",
            bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
            field="land_border_compliance_undertaking",
            value="Affirmative Undertaking certifying compliance with Clause 26",
            source_document="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
            page=1,
            raw_text_snippet="Apex Secure Systems Private Limited is NOT from a country sharing a land border with India. Land Border Rule Compliance: Fully Compliant.",
            canonical_field="LAND_BORDER_DECLARATION",
        ),
        BidderFact(
            fact_id="FACT-PASS-EXP-YRS",
            bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
            field="bidder_or_oem_experience_years",
            value="4.5 Years",
            source_document="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
            page=3,
            raw_text_snippet="Years of Past Experience: 4.5 Years (Tender Requirement: >= 3 Years -> SATISFIED / PASS)",
            canonical_field="PAST_EXPERIENCE_DURATION",
        ),
        BidderFact(
            fact_id="FACT-PASS-PAST-PERF",
            bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
            field="past_performance_threshold",
            value="90%",
            source_document="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
            page=3,
            raw_text_snippet="Past Performance Quantity: 450 Units (90% of current bid quantity -> SATISFIED / PASS)",
            canonical_field="PAST_PERFORMANCE_PERCENT",
        ),
    ]

    fact_dict = {f.field.lower(): f for f in facts}
    for af in additional_facts:
        fact_dict[af.field.lower()] = af
    facts = list(fact_dict.values())

    # Execute deterministic rule engine
    engine = DeterministicRuleEngine()
    results = engine.verify_bid(reqs, facts)

    aggregator = VerificationAggregator()
    agg = aggregator.aggregate(
        tender_id="GEM/2026/B/7959150",
        bid_id="JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150",
        compliance_results=results,
        integrity_findings=[],
        government_responses=[],
        requirements=reqs,
        facts=facts,
    )

    # 1. Mutually exclusive requirement_type accounting
    type_counts = Counter()
    status_counts = Counter()
    for r in results:
        type_counts[r.requirement_type] += 1
        status_counts[r.status] += 1

    total_reqs = len(results)
    scope_sum = (
        type_counts['BIDDER_COMPLIANCE']
        + type_counts['PROCESS_CONDITION']
        + type_counts['INFORMATIONAL']
        + type_counts['GENERAL_POLICY']
    )
    status_sum = (
        status_counts['N/A']
        + status_counts['PASS']
        + status_counts['FAIL']
        + status_counts['MISSING']
        + status_counts['REVIEW']
    )
    with open("scripts/accounting_report.txt", "w", encoding="utf-8") as out:
        out.write("=" * 120 + "\n")
        out.write(f"EXACT REQUIREMENT ACCOUNTING (TOTAL = {total_reqs})\n")
        out.write("=" * 120 + "\n\n")
        out.write("--- SCOPE BREAKDOWN (Sums to Total) ---\n")
        out.write(f"BIDDER_COMPLIANCE = {type_counts['BIDDER_COMPLIANCE']}\n")
        out.write(f"PROCESS_CONDITION = {type_counts['PROCESS_CONDITION']}\n")
        out.write(f"INFORMATIONAL     = {type_counts['INFORMATIONAL']}\n")
        out.write(f"GENERAL_POLICY    = {type_counts['GENERAL_POLICY']}\n")
        out.write(f"Sum of Scopes     = {scope_sum} (Matches Total: {scope_sum == total_reqs})\n\n")
        out.write("--- STATUS BREAKDOWN (Sums to Total) ---\n")
        out.write(f"N/A     = {status_counts['N/A']}\n")
        out.write(f"PASS    = {status_counts['PASS']}\n")
        out.write(f"FAIL    = {status_counts['FAIL']}\n")
        out.write(f"MISSING = {status_counts['MISSING']}\n")
        out.write(f"REVIEW  = {status_counts['REVIEW']}\n")
        out.write(f"Sum of Statuses = {status_sum} (Matches Total: {status_sum == total_reqs})\n\n")
        out.write("--- AGGREGATOR METRICS ---\n")
        out.write(f"Overall Status   : {agg.overall_status}\n")
        out.write(f"Compliance Status: {agg.compliance_status}\n")
        out.write(f"Compliance Score : {agg.compliance_score:.2f}%\n")
        out.write(f"Human Review Items: {len(agg.human_review_items)}\n\n")
        out.write("=" * 140 + "\n")
        out.write(f"{'ID':<20} | {'TYPE':<18} | {'STATUS':<8} | {'FIELD':<40} | {'DESCRIPTION'}\n")
        out.write("-" * 140 + "\n")
        for r in results:
            req_obj = next((q for q in reqs if q.requirement_id == r.requirement_id), None)
            desc_str = req_obj.description if req_obj else ""
            field_str = req_obj.field if req_obj else ""
            out.write(f"{r.requirement_id:<20} | {r.requirement_type:<18} | {r.status:<8} | {field_str:<40} | {desc_str}\n")
    print("Report written to scripts/accounting_report.txt")

if __name__ == "__main__":
    main()
