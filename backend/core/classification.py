# -*- coding: utf-8 -*-
"""
Deterministic Requirement Scope & Classification Engine.

Architectural Principles:
1. Actionable Bidder Obligation (BIDDER_COMPLIANCE):
   Demands affirmative action, documentary submission, certificate, undertaking,
   or quantitative capability threshold compliance from the bidder.
   Even if the clause contains phrases like 'SLA conditions', 'breach of contract',
   'pre-existing labour laws', 'consignee delivery', or 'prohibition on',
   if the bidder is required to submit/undertake/upload proof, it remains BIDDER_COMPLIANCE.

2. Administrative & Process Condition (PROCESS_CONDITION):
   Describes portal mechanisms, portal timelines, buyer purchase preferences/margins,
   or payment milestones WITHOUT demanding an affirmative bidder qualification submission.

3. Administrative Metadata (INFORMATIONAL):
   Buyer organisation details, ministry names, tender identification codes,
   total tender quantity, shipping addresses, or cross-reference pointers.

4. General Policy (GENERAL_POLICY):
   Statutory disclaimers, arbitration jurisdiction, standard GeM GTC prohibitions/restrictions,
   and statutory policy rules not tied to an actionable bidder document or threshold.
"""

import re
from typing import Any, Optional


def classify_requirement_scope(
    description: Optional[str],
    field: Optional[str] = None,
    mandatory: bool = False,
    operator: Optional[str] = None,
    expected_value: Any = None,
    source_clause: Optional[str] = None,
    declared_type: Optional[str] = None,
) -> str:
    """
    Deterministically classifies a tender requirement into one of:
    - 'BIDDER_COMPLIANCE': Actionable obligation on bidder to submit evidence or meet thresholds.
    - 'PROCESS_CONDITION': Procedural or portal conditions (dates, mechanisms, evaluation rules, payment milestones).
    - 'INFORMATIONAL': Buyer/portal administrative metadata or cross-references.
    - 'GENERAL_POLICY': General terms, legal disclaimers, or contractual clauses without submission.
    """
    desc_clean = (description or "").strip()
    fld_clean = (field or "").strip()
    sc_clean = (source_clause or "").strip()
    combined = f"{fld_clean} {desc_clean} {sc_clean}".lower()
    combined_norm = re.sub(r"[\s\-_]+", " ", combined)

    # 0. Umbrella document containers (parent tables decomposed into child requirements)
    if fld_clean in (
        "required_documents", "mandatory_documents", "seller_documents",
        "document_required_from_seller", "documents_required_from_seller",
        "document_required", "documents_required"
    ) or any(u in combined_norm for u in [
        "document required from seller", "documents required from seller",
        "document requested from seller", "documents requested from seller"
    ]):
        return "INFORMATIONAL"

    # 0B. Buyer-side evaluation procedures (actions performed by buyer, not bidder submissions)
    buyer_eval_markers = [
        "to be verified by the buyer", "verified by the buyer", "verified by buyer",
        "buyer at the time of technical evaluation", "evaluated by the buyer",
        "buyer evaluation", "verification by buyer"
    ]
    if any(m in combined_norm for m in buyer_eval_markers):
        return "PROCESS_CONDITION"

    # 1. Actionable bidder obligation markers (action verbs, submission nouns, compliance verbs)
    explicit_submission_markers = [
        "to be submitted", "must be submitted", "shall be submitted",
        "to be uploaded", "must be uploaded", "shall be uploaded",
        "undertaking required", "certificate required", "declaration required",
        "document required", "documents required", "proof required",
        "submit copy", "upload copy", "furnish", "provide copy", "submit official",
        "audited balance sheet", "ca certificate", "chartered accountant",
        "crac", "oem authorization", "boq compliance",
        "affidavit", "statutory declaration", "compliance undertaking",
        "certificate from oem", "undertaking for compliance", "declaration regarding",
        "undertaking certifying", "undertaking confirming", "certify compliance",
        "documentary evidence", "supporting document", "supporting documents"
    ]
    has_submission = any(m in combined_norm for m in explicit_submission_markers)

    general_actionable_markers = [
        "bidder must", "bidder shall", "seller must", "seller shall"
    ]
    has_actionable_marker = has_submission or any(m in combined_norm for m in general_actionable_markers)

    # 2. Informational Cross-reference pointer check (e.g. "As indicated in the bid document")
    if expected_value is not None:
        exp_str = str(expected_value).lower().strip()
        if any(p in exp_str for p in ["as indicated", "as per bid document", "refer to bid document", "refer to tender"]):
            if not has_submission:
                return "INFORMATIONAL"

    # 3. Administrative Metadata (buyer identifiers, tender codes, total quantity, delivery address)
    info_keywords = [
        "ministry", "department", "organisation", "organization", "office name",
        "grievance redressal", "item category", "bid number", "dated", "bid date",
        "bid document date", "estimated bid value", "beneficiary name", "total quantity",
        "consignee delivery details", "buyer uploaded atc", "required documents",
        "show documents to bidders"
    ]
    if any(k in combined_norm for k in info_keywords) and not has_submission:
        return "INFORMATIONAL"

    # 4. Portal Mechanics & Process Conditions (dates, evaluation methods, payment terms, buyer margins)
    process_keywords = [
        "bid end date", "bid opening date", "bid offer validity days", "bid offer validity",
        "bid validity", "offer validity", "reverse auction",
        "two packet", "auto extension", "clarification window", "technical clarifications",
        "evaluation method", "bid splitting", "option clause", "surety bond acceptance",
        "inspection required", "price margin", "purchase preference price margin",
        "purchase preference quantity", "purchase preference max percentage",
        "purchase preference enabled", "price match margin", "payment on delivery",
        "cost allocation percentage", "cost allocation for ict", "cost allocation",
        "completion days after site readiness", "site readiness communication", "site readiness",
        "days allowed for ict", "atc contravention rule", "tie breaking mechanism",
        "false declaration penalty", "bunch bid", "bunch bids", "mse purchase preference",
        "purchase preference"
    ]
    if any(k in combined_norm for k in process_keywords) and not has_submission:
        return "PROCESS_CONDITION"

    # 5. General Policy / Contractual Terms / Standard GTC Restrictions
    policy_keywords = [
        "mse relaxation", "startup relaxation", "traders are excluded",
        "traders and resellers are excluded", "traders excluded", "traders are not eligible",
        "trader eligibility", "arbitration", "mediation", "null and void", "null & void",
        "service level agreement", "sla conditions", "sla terms", "breach of contract",
        "pre existing labour laws", "pre-existing labour laws", "pre-existing labour enactments",
        "pre existing labour enactments", "applicable labour laws", "labour law compliance",
        "labour codes", "statutory labour codes", "precedence of terms",
        "custom boq bid restriction", "brand mandate restriction", "expired suspension",
        "physical document submission", "procurement of works", "cross procurement type",
        "sample trial policy", "experience restriction", "category selection",
        "external reference prohibition", "tender fee prohibition", "additional item addition",
        "bids less than 200 crore", "auditor certification threshold", "mii eligibility",
        "local supplier restriction", "class 2 local content threshold",
        "allow participation only", "allow participation", "participation only from",
        "less than 3 years", "date of constitution",
        "land border sharing registration"  # conditional statutory rule: only applies if from border country
    ]
    if any(k in combined_norm for k in policy_keywords) and not has_submission:
        return "GENERAL_POLICY"

    # 6. Check for substantive bidder capability thresholds
    op_upper = str(operator or "").upper()
    bidder_capability_terms = [
        "turnover", "revenue", "experience", "past performance",
        "warranty", "local content", "delivery period", "emd", "epbg"
    ]
    is_bidder_capability = any(t in combined_norm for t in bidder_capability_terms)

    has_substantive_operator = False
    if op_upper == "EXISTS" and not any(k in combined_norm for k in policy_keywords):
        has_substantive_operator = True
    elif op_upper in (">=", "<=", ">", "<", "==") and is_bidder_capability:
        exp_str = str(expected_value or "").lower()
        if any(c.isdigit() for c in exp_str) and not any(p in exp_str for p in ["as indicated", "as per bid", "refer to"]):
            has_substantive_operator = True

    # 7. Actionable bidder obligation if actionable marker or substantive capability operator
    if has_actionable_marker or has_substantive_operator:
        return "BIDDER_COMPLIANCE"

    # 8. Declared type fallback
    if declared_type and declared_type in ("BIDDER_COMPLIANCE", "PROCESS_CONDITION", "INFORMATIONAL", "GENERAL_POLICY"):
        return declared_type

    return "BIDDER_COMPLIANCE"
