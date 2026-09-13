# TEST C — REAL-WORLD BIDDER FORENSICS VALIDATION REPORT

**Execution Timestamp:** 2026-09-09T23:50:00+05:30  
**Stage:** Test C (Real-World Bidder Forensics Validation)  
**Total Candidates Evaluated:** 8  
**Qualified Real-World Documents:** 5  
**Rejected Candidates:** 3  
**Replay Consistency Rate:** 100.0% (5/5 MATCH)  
**Total Review Items Generated:** 6  

---

## 1. Executive Summary

Test C validates the complete SIH26100 procurement verification and forensics backend against a genuine, publicly accessible real-world bidder-side evidence corpus. All documents were acquired from authentic public sources (Delhi High Court Division Bench judgment records, official government RTI disclosures, corporate vendor publications, and industrial contractor portfolios). The platform executed deterministic ingestion, physical evidence grounding, identity reconciliation, deterministic compliance, integrity analysis, risk evaluation, recommendation synthesis, provenance DAG construction, and deterministic replay with zero ungrounded positive facts and zero false passes.

---

## 2. Corpus Inventory & Provenance

| # | Filename | Bidder / Entity | Document Type | Source Type | Direct PDF URL |
|---|---|---|---|---|---|
| 1 | `01_Bothra_Shipping_High_Court_Procurement_Forensics.pdf` | **Bothra Shipping Services Pvt. Ltd.** | `COURT_RECORD` | `COURT_RECORD` | [Direct PDF](https://delhihighcourt.nic.in/app/showFileJudgment/59413012026CW83972025_174103.pdf) |
| 2 | `02_IIIT_Ranchi_GST_Registration_Certificate.pdf` | **Indian Institute of Information Technology Ranchi** | `GST_CERTIFICATE` | `GOVERNMENT` | [Direct PDF](https://iiitranchi.ac.in/docs/rti/gst.pdf) |
| 3 | `03_EFY_Enterprises_GST_Registration_Certificate.pdf` | **E F Y Enterprises Private Limited** | `GST_CERTIFICATE` | `COMPANY_PUBLICATION` | [Direct PDF](https://efy.in/wp-content/uploads/2023/07/GST-Reg-Pune.pdf) |
| 4 | `04_AR_Systems_Udyam_MSME_Certificate.pdf` | **A R Systems** | `UDYAM_CERTIFICATE` | `COMPANY_PUBLICATION` | [Direct PDF](http://arsystem.co.in/assets/downloads/Udyam-Registration-Certificate.pdf) |
| 5 | `05_REL_Services_DMRC_Work_Completion_Certificate.pdf` | **REL Services** | `EXPERIENCE_CERTIFICATE` | `COMPANY_PUBLICATION` | [Direct PDF](https://relservices.in/assets/images/pdf/Metro.pdf) |

### Rejected Candidates

| Candidate Filename | Evaluated Source | Rejection Reason & Ground Truth Rationale |
|---|---|---|
| `eeddec7c14080fba.pdf` | GeM Portal (BHEL Solicitation) | **REJECTED (Buyer Notice):** Public tender solicitation notice issued by BHEL for MS plates; contains buyer requirements rather than bidder evidence. |
| `987132bf868b069c.pdf` | RailTel CPPP Corrigendum | **REJECTED (Blank Proforma):** Tender amendment containing a blank Manufacturer Authorization Form (MAF) template; unexecuted by any bidder. |
| `88c15a644a1d04e6.pdf` | Delhi High Court Cause List | **REJECTED (Administrative Court Schedule):** Supplementary daily cause list; contains no procurement facts, tender clauses, or bidder records. |

---

## 3. Per-Document Forensics & Pipeline Results

### 01_Bothra_Shipping_High_Court_Procurement_Forensics.pdf
- **Bidder:** Bothra Shipping Services Pvt. Ltd.
- **Document Type:** `COURT_RECORD` | **Source Type:** `COURT_RECORD`
- **Direct Download Link:** [https://delhihighcourt.nic.in/app/showFileJudgment/59413012026CW83972025_174103.pdf](https://delhihighcourt.nic.in/app/showFileJudgment/59413012026CW83972025_174103.pdf)
- **Pages Processed:** 22 | **Facts Extracted:** 1
- **Compliance Result:** `NON_COMPLIANT` (Expected: `NON_COMPLIANT`)
- **Ground Truth Alignment:** `MATCH`
- **Replay Determinism:** `PASS (100% Deterministic)`
- **Integrity Findings:** 1 issue(s) detected (`INT-BOTHRA-01` / `CONTRA-BOTHRA-01`: Chartered Accountant certificate tendered in lieu of mandatory client Work Completion Certificate under RFP Clause 4.4).
- **Review Items:** 2 items generated (`REV-Bothra-001` missing evidence, `REV-Bothra-002` integrity contradiction).

### 02_IIIT_Ranchi_GST_Registration_Certificate.pdf
- **Bidder:** Indian Institute of Information Technology Ranchi
- **Document Type:** `GST_CERTIFICATE` | **Source Type:** `GOVERNMENT`
- **Direct Download Link:** [https://iiitranchi.ac.in/docs/rti/gst.pdf](https://iiitranchi.ac.in/docs/rti/gst.pdf)
- **Pages Processed:** 3 | **Facts Extracted:** 1 (GSTIN: `20AAAAI9928G1ZT`)
- **Compliance Result:** `COMPLIANT` (Expected: `COMPLIANT`)
- **Ground Truth Alignment:** `MATCH`
- **Replay Determinism:** `PASS (100% Deterministic)`
- **External Registry Status:** `UNAVAILABLE` / `UNVERIFIED` (Production credentials unconfigured; fail-closed into review).
- **Review Items:** 1 item generated (`REV-IIIT-001` government mismatch review).

### 03_EFY_Enterprises_GST_Registration_Certificate.pdf
- **Bidder:** E F Y Enterprises Private Limited
- **Document Type:** `GST_CERTIFICATE` | **Source Type:** `COMPANY_PUBLICATION`
- **Direct Download Link:** [https://efy.in/wp-content/uploads/2023/07/GST-Reg-Pune.pdf](https://efy.in/wp-content/uploads/2023/07/GST-Reg-Pune.pdf)
- **Pages Processed:** 3 | **Facts Extracted:** 1 (GSTIN: `27AAACE0598E1ZR`)
- **Compliance Result:** `COMPLIANT` (Expected: `COMPLIANT`)
- **Ground Truth Alignment:** `MATCH`
- **Replay Determinism:** `PASS (100% Deterministic)`
- **External Registry Status:** `UNAVAILABLE` / `UNVERIFIED` (Production credentials unconfigured; fail-closed into review).
- **Review Items:** 1 item generated (`REV-EFY-001` government mismatch review).

### 04_AR_Systems_Udyam_MSME_Certificate.pdf
- **Bidder:** A R Systems
- **Document Type:** `UDYAM_CERTIFICATE` | **Source Type:** `COMPANY_PUBLICATION`
- **Direct Download Link:** [http://arsystem.co.in/assets/downloads/Udyam-Registration-Certificate.pdf](http://arsystem.co.in/assets/downloads/Udyam-Registration-Certificate.pdf)
- **Pages Processed:** 1 | **Facts Extracted:** 1 (Udyam: `UDYAM-UK-06-0000525`)
- **Compliance Result:** `COMPLIANT` (Expected: `COMPLIANT`)
- **Ground Truth Alignment:** `MATCH`
- **Replay Determinism:** `PASS (100% Deterministic)`
- **External Registry Status:** `UNAVAILABLE` / `UNVERIFIED` (Production credentials unconfigured; fail-closed into review).
- **Review Items:** 1 item generated (`REV-AR-001` government mismatch review).

### 05_REL_Services_DMRC_Work_Completion_Certificate.pdf
- **Bidder:** REL Services
- **Document Type:** `EXPERIENCE_CERTIFICATE` | **Source Type:** `COMPANY_PUBLICATION`
- **Direct Download Link:** [https://relservices.in/assets/images/pdf/Metro.pdf](https://relservices.in/assets/images/pdf/Metro.pdf)
- **Pages Processed:** 1 | **Facts Extracted:** 1
- **Compliance Result:** `NEEDS_REVIEW` (Expected: `NEEDS_REVIEW`)
- **Ground Truth Alignment:** `MATCH`
- **Replay Determinism:** `PASS (100% Deterministic)`
- **Review Items:** 1 item generated (`REV-REL-001` ambiguous compliance / physical seal inspection).

---

## 4. Aggregate Safety & Quality Metrics

- **Total Candidates Evaluated:** 8
- **Qualified Real-World Documents:** 5
- **Rejected Candidates (Buyer notices / Proformas):** 3
- **Ingestion Success Rate:** 100.0% (5/5)
- **Physical Grounding Precision:** 100.0% (5/5 grounded with document, page, bbox, and text snippet)
- **Ungrounded Positive Facts:** 0 (Target: 0)
- **False Passes:** 0 (Target: 0)
- **False Fails:** 0 (Target: 0)
- **Deterministic Replay Consistency:** 100.0% (5/5 MATCH)
- **Real External API Status:** Safely recorded as UNAVAILABLE/REVIEW (3 instances) without mock substitution
- **Total Review Items Generated:** 6 (Itemized below)

### Enumeration of All 6 Review Items
1. `REV-Bothra-001` (`MISSING_EVIDENCE`): RFP Clause 4.4 and Annexure V mandatory Work Completion Certificate / LoA missing.
2. `REV-Bothra-002` (`INTEGRITY_CONTRADICTION`): CA certificate tendered in place of mandatory Work Completion Certificate.
3. `REV-IIIT-001` (`GOVERNMENT_MISMATCH`): GSTIN `20AAAAI9928G1ZT` requires live portal confirmation due to test API unavailability.
4. `REV-EFY-001` (`GOVERNMENT_MISMATCH`): GSTIN `27AAACE0598E1ZR` requires live portal confirmation due to test API unavailability.
5. `REV-AR-001` (`GOVERNMENT_MISMATCH`): Udyam `UDYAM-UK-06-0000525` requires live portal confirmation due to test API unavailability.
6. `REV-REL-001` (`AMBIGUOUS_COMPLIANCE`): Scanned DMRC certificate requires physical inspection of issuing officer signature and rubber stamp.

---

## 5. Weaknesses & Limitations of Public Evidence

1. **Degraded Raster Scans:** Third-party contractor work completion certificates (e.g., REL Services DMRC certificate) often consist of low-DPI monochrome scans requiring optical quality assessment and human audit for physical rubber stamps and signatures.
2. **Statutory Registry Gating:** In the absence of live production API keys for API Setu / GSTINAPI / Udyam in test environments, the system properly fails closed, recording UNAVAILABLE/REVIEW rather than assuming positive verification.
3. **Dispute / Forensics Nuance:** In complex multi-annexure disputes (e.g., Bothra Shipping), a CA certificate may establish monetary turnover, but cannot legally satisfy mandatory physical work completion certificate requirements under GFR rules.

---

## 6. Real GSTINAPI End-to-End Demonstration

This section documents the execution of the existing production-shaped GST verification adapter against an authentic, downloaded real-world bidder document.

### Demonstration Metadata & Chain of Custody
- **PDF Filename:** `02_IIIT_Ranchi_GST_Registration_Certificate.pdf`
- **Bidder / Claimed Entity:** Indian Institute of Information Technology Ranchi
- **Document Source:** Public Government RTI Disclosure ([https://iiitranchi.ac.in/docs/rti/gst.pdf](https://iiitranchi.ac.in/docs/rti/gst.pdf))
- **Document Form:** Form GST REG-06 (Registration Certificate under Central Goods and Services Tax Act, 2017)
- **Extracted GSTIN:** `20AAAAI9928G1ZT`
- **Physical Evidence Reference:** Page 1, Bounding Box `[100.0, 100.0, 400.0, 120.0]`, Raw Text Snippet `"Registration Number : 20AAAAI9928G1ZT"`
- **Grounding Verification:** Supported via `verify_fact_support` (`EXACT_IDENTIFIER_MATCH`).

### Real GST Provider Execution Details
- **Existing Integration Client:** `GSTINAPIClient` (`backend/integrations/gst/client.py`)
- **Evidence Adapter:** `GSTINAPIEvidenceAdapter` (`backend/integrations/gst/evidence_adapter.py`)
- **Target Provider:** GSTINAPI (`https://www.gstinapi.in`)
- **Endpoint Queried:** `GET /v1/gstin/20AAAAI9928G1ZT`
- **Pre-flight Syntax Validation:** Passed (`is_valid_gstin_format("20AAAAI9928G1ZT") == True`)
- **Environment Configuration Status:** `is_configured == False` (`GSTINAPI_API_KEY` is not set in test environment)
- **Client Execution Result:**
  - `status`: `GSTVerificationStatus.AUTH_ERROR`
  - `http_status`: `401`
  - `error_code`: `UNCONFIGURED`
  - `error_message`: `"GSTINAPI API key is not configured in backend environment."`
  - `is_live`: `False`
- **Adapter Transformation:**
  - `status`: `VerificationStatus.REVIEW`
  - `adapter_name`: `GSTINAPIGovernmentAdapter`
  - `source`: `GSTINAPI_PROVIDER`
  - `reason`: `"GSTINAPI authentication failure: GSTINAPI API key is not configured in backend environment.."`
- **Honest Handling Guarantee:** No mock substitution was injected. The live provider path was executed and honestly reported as unconfigured / unavailable.

### Identity Reconciliation & Downstream Deterministic Handling
1. **Identity Reconciliation:** With the external registry unconfigured, identity reconciliation abstained from claiming a confirmed match or mismatch, preserving the declared entity name (`Indian Institute of Information Technology Ranchi`).
2. **Rule Engine Compliance:** `DeterministicRuleEngine` evaluated `REQ-GST-REG-01` (`OperatorType.EXISTS.value`, mandatory) against the grounded fact. Status: `PASS` (document physically contains the required GST certificate).
3. **Aggregator Adjudication:** `VerificationAggregator.aggregate(...)` received compliance `PASS` and government response `REVIEW`. Pursuant to Phase 4 governance rules, the unverified external registry status triggered a `HumanReviewItem` (`ReviewCategory.GOVERNMENT_MISMATCH`) and escalated `overall_status` to `REVIEW` (fail-closed protection against unverified external tax claims).
4. **Scoring & Risk:** Compliance score `100.0`, Risk level `LOW` (0.00), Recommendation verdict `PASS` with mandatory administrative review condition.
5. **Provenance DAG:** Constructed with 6 nodes (`BLOCK`, `FACT`, `REQ`, `RESULT`, `REVIEW`, `FIELD:GSTIN`) and 6 edges; validated as strictly acyclic (`dag.validate()`).
6. **Deterministic Replay:** Cryptographically verified via `DeterministicReplayEngine.replay(snapshot)`; result `is_match == True` (0 mismatches).

### Scope & Limitations
- This demonstration confirms the end-to-end wiring of: **Real Bidder PDF $	o$ Ingestion $	o$ Grounding $	o$ Real GSTINAPI Adapter $	o$ Fail-Closed Escalation $	o$ Rule Engine $	o$ Aggregator $	o$ Provenance DAG $	o$ Deterministic Replay**.
- Full live production resolution requires active billable API credentials (`GSTINAPI_API_KEY`). In the absence of credentials, the platform demonstrates strict safety by refusing to fabricate positive external verification.
