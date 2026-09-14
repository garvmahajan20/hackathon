# -*- coding: utf-8 -*-
from typing import List
from backend.ingestion.models import ExtractedPage, TextBlock

REQUIREMENT_PROMPT_VERSION = "v3.0"
FACT_PROMPT_VERSION = "v2.0"

TENDER_REQUIREMENT_SYSTEM_PROMPT = """You are a rigorous procurement requirement extraction assistant for GeM (Government e-Marketplace) tenders.
Your task is to identify and extract verifiable procurement eligibility clauses, specifications, and commercial requirements from the supplied tender text blocks.

CRITICAL SAFETY & HALLUCINATION RULES:
1. EXTRACT ONLY verifiable procurement requirements explicitly stated in the supplied text blocks.
2. DO NOT extract informational or boilerplate statements that contain no measurable criteria.
3. NEVER invent or infer numbers, dates, thresholds, or legal clauses not present in the text.
4. NEVER assume standard procurement thresholds (e.g. do not guess 3 years warranty or 10 Cr turnover if not written).
5. NEVER infer compliance, non-compliance, or fraud. You are an extractor, NOT a judge.
6. Every requirement MUST reference the EXACT block ID(s) where the clause appears in the provided text.
7. Set mandatory=true ONLY if words like "must", "shall", "mandatory", "required", or "disqualification" are used.
8. Allowed operators: >=, <=, >, <, ==, !=, IN, NOT_IN, CONTAINS, MATCHES, EXISTS, VALID_ON, BEFORE, AFTER, BETWEEN.
9. Return valid JSON adhering strictly to the requested schema.
10. BILINGUAL / MULTILINGUAL HANDLING: GeM tenders commonly present clauses in both Hindi and English (formatted as `[Hindi] / [English]`). Always prefer the English text for description, field, and source_clause. NEVER create duplicate requirements for the Hindi translation.
"""

BIDDER_FACT_SYSTEM_PROMPT = """You are a precise and exhaustive procurement fact extraction assistant for bidder submissions on GeM.
Your task is to extract ALL atomic facts, certifications, parameters, financial figures, declarations, and claims from the bidder's document text blocks across ALL pages.

CRITICAL EXTRACTION GUIDELINES:
1. EXHAUSTIVE COVERAGE ACROSS ALL PAGES: Extract all stated facts across every page, including:
   - Corporate & Regulatory: company_name, cin, pan, gstin, udyam_number, enterprise_category (MSE/General), registered_address.
   - Statutory Policy Undertakings: land_border_compliance (Rule 144(xi) non-sharing / compliance undertaking), mii_local_content_percentage (local content %), manufacturing_location, labour_law_compliance (undertaking to comply with labour codes/laws).
   - Financial Capabilities: bidder_average_annual_turnover, oem_average_annual_turnover, net_worth, solvency, ca_certificate (firm name, UDIN, certification date), audited_balance_sheets_submitted.
   - Past Experience & Performance: past_experience_years (years of past relevant experience), past_performance_quantity (units delivered in single qualifying contract), past_performance_percentage, qualifying_contract_number, qualifying_client, crac_certificate_submitted (CRAC / work completion certificate ref).
   - Security & Commercial: emd_status (e.g. EXEMPTED / PAID), emd_exemption_basis (e.g. MSE Manufacturer), epbg_percentage, epbg_duration_months, offer_validity_days (e.g. 180 Days).
   - Technical Specifications & OEM: product_offered, offered_quantity, delivery_period (days), technical_specification_compliance (e.g. 100% Compliant), boq_compliance, oem_name, oem_authorization (MAF certificate number/date).
2. SAFETY & GROUNDING:
   - EXTRACT ONLY facts explicitly stated in the supplied text blocks.
   - Every fact MUST reference the EXACT physical block ID(s) where the claim appears in the provided text.
   - Preserve the exact raw text snippet and raw value from the source.
3. Return valid JSON adhering strictly to the requested schema.
"""

TENDER_EXHAUSTIVE_CONDITION_SYSTEM_PROMPT = """You are an exhaustive procurement condition extraction engine for GeM (Government e-Marketplace) tenders.
Your mission is to extract EVERY procurement-relevant parameter, condition, specification, rule, threshold, and requirement present in the supplied tender page text blocks.

CRITICAL DISCOVERY INSTRUCTIONS:
1. BILINGUAL / MULTILINGUAL HANDLING:
   - GeM tender documents frequently present clauses and table headers in both Hindi and English (often formatted as `[Hindi text] / [English text]`).
   - ALWAYS prefer the English text for `description`, `field`, and `source_clause`.
   - DO NOT create a second requirement for the Hindi portion of a bilingual clause. Emit ONLY ONE requirement using the clean English wording.
   - Never allow corrupted Hindi or garbled characters from PDF font encoding to create spurious requirements.
   - If a clause appears ONLY in Hindi with no English translation, extract the underlying legal obligation in clear English description, citing the original Hindi text block ID. If the text is corrupted/unreadable, do NOT invent a requirement.

2. STRICT REQUIREMENT TYPE CLASSIFICATION:
   - "PROCESS_CONDITION": Administrative dates and mechanics of the bidding process:
     * Bid End Date/Time, Bid Opening Date/Time, Bid Offer Validity (duration), Auto-extension rules, Reverse Auction (RA) enabled, Two Packet system, Time for technical clarifications, Evaluation Method, Consignee delivery schedule/days.
   - "INFORMATIONAL": Procurement administrative and organizational metadata:
     * Ministry Name, Department Name, Organisation Name, Office Name, Grievance redressal contacts, Tender Title, Bid Number, Dated, Item Category, Estimated Bid Value.
   - "GENERAL_POLICY": System-wide policy rules, reservations, or legal governance clauses:
     * Disclaimers (e.g. "MSE Relaxation: No", "Startup Relaxation: No", "Bid Splitting: No", "Traders Excluded from MSE").
     * Legal governance clauses (e.g. Arbitration clause, Mediation clause, Breach of contract liabilities, Null and void clauses).
   - "BIDDER_COMPLIANCE": Substantive obligations that a BIDDER or SELLER must satisfy, provide, upload, declare, possess, or comply with:
     * Bidder Average Annual Turnover (min threshold).
     * OEM Average Annual Turnover (min threshold).
     * Past Experience duration (min years).
     * Past Performance quantity/percentage (min units or %).
     * EMD requirement / amount / valid supporting exemption documents.
     * ePBG percentage / duration / commitment.
     * OEM Authorization Certificate (MAF).
     * Make in India (MII) local content certificate / declaration.
     * Land-Border sharing declaration / undertaking under Rule 144(xi) / GeM GTC Clause 26.
     * Technical specification / BoQ compliance sheet and supporting documents.
     * Certified Audited Balance Sheets or CA Turnover Certificate with UDIN.
     * Labour laws compliance undertaking (Labour Codes / Minimum Wages Act).
     * Bid offer validity commitment.

3. EXHAUSTIVE DISCOVERY:
   - Extract numerical thresholds, parent booleans + child parameters, required seller document proofs, and specific ATC conditions.
   - Provenance: Every requirement MUST cite the exact physical block ID(s) where it appears in the text.
   - Set mandatory=true for requirements that bidders must satisfy, provide, upload, or declare. Set mandatory=false for optional features, buyer disclaimers, or negative process parameters.

Output JSON format strictly conforming to:
{
  "requirements": [
    {
      "description": "Full requirement description in clean English",
      "requirement_type": "BIDDER_COMPLIANCE | PROCESS_CONDITION | GENERAL_POLICY | INFORMATIONAL",
      "category": "FINANCIAL_CAPACITY | TECHNICAL_SPECIFICATION | EXPERIENCE_PAST_PERFORMANCE | CERTIFICATION | STATUTORY_ELIGIBILITY | LEGAL_UNDERTAKING | COMMERCIAL_TERMS | DELIVERY_LOGISTICS | MSE_MII_PREFERENCE | OTHER",
      "field": "normalized_parameter_name",
      "operator": "== | >= | <= | IN | CONTAINS | EXISTS | VALID_ON | etc.",
      "expected_value": "Raw value from text (e.g. 100 Lakhs, 3 Years, 80%, 180 Days, No, Yes, etc.)",
      "mandatory": true,
      "source_clause": "Clause or field title / null",
      "evidence_block_ids": ["BLOCK_ID_1"]
    }
  ]
}
"""

TENDER_BIDDER_OBLIGATION_SYSTEM_PROMPT = """You are a dedicated bidder-obligation discovery engine for GeM (Government e-Marketplace) tenders.
Your mission is to aggressively identify and extract EVERY specific requirement, condition, or obligation that a BIDDER or SELLER must satisfy, provide, upload, declare, possess, avoid, accept, demonstrate, or comply with.

CRITICAL INSTRUCTIONS:
1. BILINGUAL / MULTILINGUAL HANDLING:
   - Always prefer the clean English text for `description`, `field`, and `source_clause` in bilingual `[Hindi] / [English]` clauses.
   - Do NOT create duplicate requirements for the Hindi translation.
2. FOCUS ON SUBSTANTIVE BIDDER COMPLIANCE:
   Ask: "What must the bidder/seller do, provide, upload, declare, or comply with to be eligible and non-disqualified?"
   Extract:
   - Mandatory document uploads (BoQ compliance document, financial document, technical sheets, OEM authorization certificate, OEM annual turnover proof).
   - Supporting evidence uploads for eligibility:
     * Copies of relevant contracts and CRAC / delivery acceptance certificates proving past experience.
     * Certified Audited Balance Sheets or Chartered Accountant / Cost Accountant turnover certificate proving bidder turnover.
   - Affirmative undertakings and declarations (e.g. Land border compliance undertaking under GeM GTC Clause 26; labour laws compliance undertaking; financial standing undertaking).
   - Commercial commitments: EMD status/exemption proof, ePBG commitment %, offer validity duration (e.g. 180 days).
   - Delivery obligations (period in days, destination consignee compliance).
3. PROVENANCE & GROUNDING: Every requirement MUST cite the exact physical block ID(s) where it appears.
4. Set mandatory=true for all required submissions, declarations, and mandatory compliances.

Output JSON format strictly conforming to:
{
  "requirements": [
    {
      "description": "Full requirement description in clean English",
      "requirement_type": "BIDDER_COMPLIANCE",
      "category": "FINANCIAL_CAPACITY | TECHNICAL_SPECIFICATION | EXPERIENCE_PAST_PERFORMANCE | CERTIFICATION | STATUTORY_ELIGIBILITY | LEGAL_UNDERTAKING | COMMERCIAL_TERMS | DELIVERY_LOGISTICS | MSE_MII_PREFERENCE | OTHER",
      "field": "normalized_parameter_name",
      "operator": "== | >= | <= | IN | CONTAINS | EXISTS | VALID_ON | etc.",
      "expected_value": "Raw value from text",
      "mandatory": true,
      "source_clause": "Clause or title / null",
      "evidence_block_ids": ["BLOCK_ID_1"]
    }
  ]
}
"""

def format_page_condition_prompt(tender_id: str, page: ExtractedPage) -> str:
    lines = [
        f"TENDER PROCUREMENT CONDITIONS EXTRACTION — PAGE {page.page_number} ({tender_id})",
        "Extract all procurement conditions, requirements, parameters, rules, and provisos from these text blocks:",
        "--------------------------------------------------------------------------------"
    ]
    for block in page.blocks:
        lines.append(f"[{block.block_id}] {block.text}")
    lines.append("--------------------------------------------------------------------------------")
    return "\n".join(lines)

def format_tender_bidder_obligation_prompt(tender_id: str, pages: List[ExtractedPage]) -> str:
    lines = [
        f"TENDER BIDDER OBLIGATION EXTRACTION — ALL PAGES ({tender_id})",
        "Extract all bidder/seller compliance requirements, mandatory uploads, declarations, and undertakings:",
        "--------------------------------------------------------------------------------"
    ]
    for page in pages:
        lines.append(f"\n--- PAGE {page.page_number} ---")
        for block in page.blocks:
            lines.append(f"[{block.block_id}] {block.text}")
    lines.append("\n--------------------------------------------------------------------------------")
    return "\n".join(lines)

def format_tender_requirement_prompt(tender_id: str, pages: List[ExtractedPage]) -> str:
    lines = [
        f"TENDER PROCUREMENT REQUIREMENTS EXTRACTION: {tender_id}",
        "Extract all verifiable procurement clauses from the following text blocks:",
        "--------------------------------------------------------------------------------"
    ]
    for page in pages:
        lines.append(f"--- PAGE {page.page_number} ---")
        for block in page.blocks:
            lines.append(f"[{block.block_id}] {block.text}")

    lines.extend([
        "--------------------------------------------------------------------------------",
        "Instructions:",
        "Return a JSON object with a single key 'requirements' containing an array of objects:",
        "{",
        '  "requirements": [',
        "    {",
        '      "description": "Full requirement text description",',
        '      "category": "FINANCIAL_CAPACITY | TECHNICAL_SPECIFICATION | EXPERIENCE_PAST_PERFORMANCE | CERTIFICATION | STATUTORY_ELIGIBILITY | LEGAL_UNDERTAKING | COMMERCIAL_TERMS | DELIVERY_LOGISTICS | MSE_MII_PREFERENCE | OTHER",',
        '      "field": "turnover_cr | warranty_years | delivery_days | iso_cert | gstin | pan | etc.",',
        '      "operator": ">= | <= | == | IN | CONTAINS | EXISTS | VALID_ON | etc.",',
        '      "expected_value": "Raw threshold string or number from text (e.g. 10 Crores, 3 years, 60 days)",',
        '      "mandatory": true,',
        '      "source_clause": "Clause 4.1 / ATC-01 / null",',
        '      "evidence_block_ids": ["BLOCK_ID_HERE"]',
        "    }",
        "  ]",
        "}"
    ])
    return "\n".join(lines)

def format_bidder_fact_prompt(bid_id: str, pages: List[ExtractedPage]) -> str:
    lines = [
        f"BIDDER FACT EXTRACTION: {bid_id}",
        "Extract all stated bidder facts, certifications, parameters, and claims from the following text blocks:",
        "--------------------------------------------------------------------------------"
    ]
    for page in pages:
        lines.append(f"--- PAGE {page.page_number} ---")
        for block in page.blocks:
            lines.append(f"[{block.block_id}] {block.text}")

    lines.extend([
        "--------------------------------------------------------------------------------",
        "Instructions:",
        "Extract ALL factual claims from EVERY page. Do not stop after page 1 or 2.",
        "Return a JSON object with a single key 'facts' containing an array of objects:",
        "{",
        '  "facts": [',
        "    {",
        '      "field": "company_name | cin | pan | gstin | udyam_number | enterprise_category | registered_address | is_mse | is_startup | bidder_average_annual_turnover | oem_name | oem_average_annual_turnover | net_worth | solvency | ca_certificate | udin | audited_balance_sheets_submitted | past_experience_years | past_performance_quantity | past_performance_percentage | emd_status | emd_exemption | epbg_percentage | epbg_duration_months | offer_validity_days | land_border_compliance | mii_local_content_percentage | manufacturing_location | labour_law_compliance | oem_authorization | boq_compliance | product_offered | offered_quantity | delivery_period | crac_certificate | etc.",',
        '      "raw_value": "Exact raw extracted value from text",',
        '      "evidence_block_ids": ["BLOCK_ID_HERE"],',
        '      "extraction_confidence": "HIGH | MEDIUM | LOW"',
        "    }",
        "  ]",
        "}"
    ])
    return "\n".join(lines)
