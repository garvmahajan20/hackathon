import hashlib
import json
import logging
import os
import re
import time
from typing import Any, Callable, Dict, List, Optional, Tuple, Union

logger = logging.getLogger(__name__)

def _get_cache_filename(verification_id: str) -> str:
    """
    Deterministic, filesystem-safe filename for verification persistence.
    Replaces illegal Windows characters (including '/') with '_' and appends a sha256 hash.
    """
    safe_slug = re.sub(r'[^a-zA-Z0-9_\-]', '_', verification_id)[:64]
    h = hashlib.sha256(verification_id.encode('utf-8')).hexdigest()[:12]
    return f"{safe_slug}_{h}.json"

from backend.core.contradiction_engine import CrossDocumentContradictionEngine
from backend.core.models import BidderFact, TenderRequirement, VerificationResult
from backend.core.rule_engine import DeterministicRuleEngine
from backend.extraction.cache import LLMCache
from backend.extraction.fact_extractor import LLMBidderFactExtractor
from backend.extraction.gemini_provider import GeminiProvider
from backend.extraction.mock_provider import MockLLMProvider
from backend.extraction.models import LLMMode, LLMProviderError
from backend.extraction.provider import BaseLLMProvider
from backend.extraction.requirement_extractor import TenderRequirementExtractor
from backend.extraction.schema_validator import SchemaValidator
from backend.ingestion.pipeline import DocumentIngestionPipeline
from backend.verification.base import BaseGovernmentAdapter
from backend.verification.mock_debarment import MockDebarmentAdapter
from backend.verification.mock_gst import MockGSTAdapter
from backend.verification.mock_pan import MockPANAdapter
from backend.verification.mock_udyam import MockUdyamAdapter
from backend.verification.mock_itd import MockITDAdapter
from backend.verification.mock_mca21 import MockMCA21Adapter
from backend.verification.mock_nsic import MockNSICAdapter
from backend.verification.mock_oem import MockOEMAdapter
from backend.verification.mock_mii import MockMIIAdapter
from backend.verification.mock_evidence_adapter import MockRegistryEvidenceAdapter
from backend.verification.models import AdapterResponse, IntegrityFinding, VerificationStatus
from .aggregator import VerificationAggregator
from .models import AggregatedVerification, VerificationDossier

class VerificationOrchestrator:
    """
    Central End-to-End Verification Orchestrator.
    Coordinates document ingestion, requirement extraction, fact extraction,
    compliance verification, contradiction detection, government adapters,
    aggregation, human review routing, and dossier generation.
    """

    def __init__(
        self,
        mode: Union[LLMMode, str] = LLMMode.LIVE,
        provider: Optional[BaseLLMProvider] = None,
        cache_dir: str = "data/cache/verifications",
        llm_cache_dir: str = "data/cache/llm",
        gst_adapter: Optional[BaseGovernmentAdapter] = None,
        itd_adapter: Optional[BaseGovernmentAdapter] = None,
        mca_adapter: Optional[BaseGovernmentAdapter] = None,
        nsic_adapter: Optional[BaseGovernmentAdapter] = None,
        oem_adapter: Optional[BaseGovernmentAdapter] = None,
        mii_adapter: Optional[BaseGovernmentAdapter] = None,
    ):
        if isinstance(mode, str):
            mode = LLMMode(mode.upper())
        self.mode = mode
        self.cache_dir = cache_dir
        os.makedirs(self.cache_dir, exist_ok=True)

        self.llm_cache = LLMCache(cache_dir=llm_cache_dir)
        self.validator = SchemaValidator()

        # Provider initialization
        if provider:
            self.provider = provider
        elif self.mode == LLMMode.LIVE:
            self.provider = GeminiProvider()
        else:
            self.provider = MockLLMProvider()

        # Internal Pipelines & Engines
        self.ingestion = DocumentIngestionPipeline()
        self.requirement_extractor = TenderRequirementExtractor(
            provider=self.provider,
            cache=self.llm_cache,
            mode=self.mode,
            schema_validator=self.validator,
        )
        self.fact_extractor = LLMBidderFactExtractor(
            provider=self.provider,
            cache=self.llm_cache,
            mode=self.mode,
            schema_validator=self.validator,
        )
        self.rule_engine = DeterministicRuleEngine()
        self.contradiction_engine = CrossDocumentContradictionEngine()
        self.aggregator = VerificationAggregator()

        # Government Adapters (Mock by default, pluggable)
        self.gst_adapter = gst_adapter or MockGSTAdapter()
        self.pan_adapter = MockPANAdapter()
        self.udyam_adapter = MockUdyamAdapter()
        self.debarment_adapter = MockDebarmentAdapter()
        self.itd_adapter = itd_adapter or MockITDAdapter()
        self.mca_adapter = mca_adapter or MockMCA21Adapter()
        self.nsic_adapter = nsic_adapter or MockNSICAdapter()
        self.oem_adapter = oem_adapter or MockOEMAdapter()
        self.mii_adapter = mii_adapter or MockMIIAdapter()
        self.mock_evidence_adapter = MockRegistryEvidenceAdapter()

        # In-memory session store
        self._verifications: Dict[str, AggregatedVerification] = {}
        self._dossiers: Dict[str, VerificationDossier] = {}

    def verify_submission(
        self,
        tender_document_path: str,
        bid_document_paths: List[str],
        tender_id: Optional[str] = None,
        bid_id: Optional[str] = None,
        company_name_hint: Optional[str] = None,
        progress_callback: Optional[Callable[[int, str, str, Optional[Dict[str, Any]]], None]] = None,
    ) -> Tuple[AggregatedVerification, VerificationDossier]:
        """
        Executes complete verification pipeline for a tender document and bid documents.
        Emits truthful stage progress events (Steps 1 through 6) via progress_callback.
        """
        def notify_progress(step: int, status_str: str, message: str, meta: Optional[Dict[str, Any]] = None):
            if progress_callback:
                try:
                    progress_callback(step, status_str, message, meta)
                except Exception as cb_err:
                    logger.warning(f"Progress callback notification error: {cb_err}")

        current_step = 1
        try:
            if self.mode == LLMMode.LIVE and not self.provider.is_available():
                raise LLMProviderError(
                    "Live verification failed: GEMINI_API_KEY is not configured in environment.",
                    provider_name=self.provider.provider_name,
                    model_name=self.provider.model_name,
                )

            t0 = time.perf_counter()

            # 1. Infer Identifiers if not provided
            t_base = os.path.basename(tender_document_path)
            b_base = os.path.basename(bid_document_paths[0]) if bid_document_paths else "BID-UNKNOWN"
            tender_id = tender_id or (t_base.split(".")[0] if "TENDER" in t_base else "TENDER-0001")
            bid_id = bid_id or (b_base.split(".")[0] if "BID" in b_base else "BID-00001")

            # --- STEP 1: PDF Ingestion & Page Segmentation ---
            current_step = 1
            notify_progress(1, "RUNNING", "Ingesting tender and bidder PDF documents and segmenting pages...")

            t_ingest_res = self.ingestion.ingest_file(tender_document_path)
            if t_ingest_res.overall_method.value == "FAILED" or len(t_ingest_res.pages) == 0:
                raise ValueError(f"Invalid or unreadable tender document '{tender_document_path}': {t_ingest_res.errors}")

            bid_ingest_results: List[Tuple[str, Any]] = []
            for b_path in bid_document_paths:
                b_ingest_res = self.ingestion.ingest_file(b_path)
                if b_ingest_res.overall_method.value == "FAILED" or len(b_ingest_res.pages) == 0:
                    raise ValueError(f"Invalid or unreadable bidder document '{b_path}': {b_ingest_res.errors}")
                bid_ingest_results.append((b_path, b_ingest_res))

            tender_pages_count = len(t_ingest_res.pages)
            bid_pages_count = sum(len(res.pages) for _, res in bid_ingest_results)
            notify_progress(1, "COMPLETED", f"Ingested {tender_pages_count} tender page(s) and {bid_pages_count} bidder page(s).", {
                "tender_pages": tender_pages_count,
                "bid_pages": bid_pages_count,
            })

            # --- STEP 2: Text Extraction & BBox Grounding ---
            current_step = 2
            notify_progress(2, "RUNNING", "Grounding spatial bounding boxes and layout geometry...")

            tender_blocks_count = sum(len(p.blocks) for p in t_ingest_res.pages)
            bid_blocks_count = sum(sum(len(p.blocks) for p in res.pages) for _, res in bid_ingest_results)
            notify_progress(2, "COMPLETED", f"Spatial bounding boxes and layout geometry indexed ({tender_blocks_count + bid_blocks_count} layout blocks).", {
                "tender_blocks": tender_blocks_count,
                "bid_blocks": bid_blocks_count,
            })

            # --- STEP 3: Candidate Parameter Extraction ---
            current_step = 3
            notify_progress(3, "RUNNING", "Extracting compliance requirements and bidder claims...")

            requirements = self.requirement_extractor.extract_requirements(t_ingest_res, tender_id=tender_id)

            all_facts: List[BidderFact] = []
            grounding_warnings: List[str] = []
            for b_path, b_ingest_res in bid_ingest_results:
                facts = self.fact_extractor.extract_facts(b_ingest_res, bid_id=bid_id)
                all_facts.extend(facts)

            notify_progress(3, "COMPLETED", f"Extracted {len(requirements)} requirement(s) and {len(all_facts)} bidder fact parameter(s).", {
                "requirements_count": len(requirements),
                "facts_count": len(all_facts),
            })

            # --- STEP 4: Deterministic Compliance Evaluation ---
            current_step = 4
            notify_progress(4, "RUNNING", "Evaluating deterministic compliance rules against extracted facts...")

            compliance_results = self.rule_engine.verify_bid(requirements, all_facts)
            pass_eval_count = sum(1 for c in compliance_results if getattr(c.status, "value", str(c.status)) == "PASS")
            fail_eval_count = sum(1 for c in compliance_results if getattr(c.status, "value", str(c.status)) == "FAIL")

            notify_progress(4, "COMPLETED", f"Evaluated {len(compliance_results)} clauses ({pass_eval_count} PASS, {fail_eval_count} FAIL).", {
                "evaluated_count": len(compliance_results),
                "pass_count": pass_eval_count,
                "fail_count": fail_eval_count,
            })

            # --- STEP 5: Contradictions & Government Registries ---
            current_step = 5
            notify_progress(5, "RUNNING", "Detecting cross-document contradictions and querying government registries...")

            integrity_findings = self.contradiction_engine.detect_contradictions_in_bid(bid_id, all_facts)

            # Extract legal name, GSTIN, PAN, Udyam from facts or hints
            facts_by_field = {f.field.lower(): f.value for f in all_facts if f.field}
            facts_by_canonical = {f.canonical_field: f.value for f in all_facts if f.canonical_field}
            legal_name = company_name_hint or facts_by_field.get("company_name", facts_by_field.get("entity_name")) or facts_by_canonical.get("LEGAL_ENTITY_NAME")
            gstin_val = facts_by_field.get("gstin") or facts_by_canonical.get("GSTIN")
            pan_val = facts_by_field.get("pan") or facts_by_canonical.get("PAN")
            udyam_val = (
                facts_by_field.get("udyam")
                or facts_by_field.get("udyam_registration")
                or facts_by_canonical.get("UDYAM_REGISTRATION")
            )

            # Derive PAN from GSTIN if PAN not submitted directly (chars 3-12 of 15-char GSTIN)
            if not pan_val and gstin_val and len(str(gstin_val)) == 15:
                pan_val = str(gstin_val)[2:12]

            gov_responses: List[AdapterResponse] = []

            if gstin_val:
                gov_responses.append(self.gst_adapter.verify(str(gstin_val), expected_name=str(legal_name) if legal_name else None))

            if pan_val:
                gov_responses.append(self.pan_adapter.verify(str(pan_val), expected_name=str(legal_name) if legal_name else None))

            if udyam_val:
                gov_responses.append(self.udyam_adapter.verify(str(udyam_val), expected_name=str(legal_name) if legal_name else None))

            # Debarment Check (check PAN, GSTIN, and legal name)
            debar_val = pan_val or gstin_val or legal_name
            if debar_val:
                gov_responses.append(self.debarment_adapter.verify(str(debar_val)))

            # Government Registry Verifications (MCA21, NSIC, OEM, MII, ITD)
            cin_val = facts_by_field.get("cin") or facts_by_canonical.get("CIN") or facts_by_field.get("corporate_id")
            nsic_val = (
                facts_by_field.get("nsic")
                or facts_by_field.get("nsic_certificate")
                or facts_by_canonical.get("NSIC_REGISTRATION")
                or facts_by_field.get("nsic_registration")
            )
            oem_val = (
                facts_by_field.get("oem_authorization")
                or facts_by_field.get("maf")
                or facts_by_field.get("oem_auth")
                or facts_by_canonical.get("OEM_AUTHORIZATION")
                or facts_by_field.get("oem_authorization_number")
            )
            mii_val = (
                facts_by_field.get("mii")
                or facts_by_field.get("mii_declaration")
                or facts_by_field.get("local_content")
                or facts_by_canonical.get("MII_DECLARATION")
                or facts_by_field.get("mii_certificate")
            )
            itr_val = (
                facts_by_field.get("itr")
                or facts_by_field.get("itr_ack")
                or facts_by_field.get("income_tax_return")
                or facts_by_canonical.get("ITR_ACKNOWLEDGEMENT")
                or facts_by_field.get("itr_acknowledgement")
            )

            if cin_val:
                gov_responses.append(self.mca_adapter.verify(str(cin_val), expected_name=str(legal_name) if legal_name else None))

            if nsic_val:
                gov_responses.append(self.nsic_adapter.verify(str(nsic_val), expected_name=str(legal_name) if legal_name else None))

            if oem_val:
                oem_name_hint = facts_by_field.get("oem_name") or facts_by_canonical.get("OEM_NAME")
                gov_responses.append(self.oem_adapter.verify(str(oem_val), expected_name=str(legal_name) if legal_name else None, oem_name=str(oem_name_hint) if oem_name_hint else None))

            if mii_val:
                gov_responses.append(self.mii_adapter.verify(str(mii_val), expected_name=str(legal_name) if legal_name else None))

            has_itr_req = any(
                "ITR" in (getattr(r, "requirement_id", "") or "").upper()
                or "ITR" in (getattr(r, "field", "") or "").upper()
                or "ITR" in (getattr(r, "canonical_field", "") or "").upper()
                or "INCOME TAX" in (getattr(r, "description", "") or "").upper()
                for r in requirements
            )
            if itr_val:
                gov_responses.append(self.itd_adapter.verify(str(itr_val), expected_name=str(legal_name) if legal_name else None))
            elif has_itr_req and pan_val:
                gov_responses.append(self.itd_adapter.verify(str(pan_val), expected_name=str(legal_name) if legal_name else None))

            notify_progress(5, "COMPLETED", f"Integrity check complete: {len(integrity_findings)} contradiction(s), {len(gov_responses)} registry queries executed.", {
                "findings_count": len(integrity_findings),
                "registry_checks_count": len(gov_responses),
            })

            # --- STEP 6: Audit Dossier Compilation & Sealing ---
            current_step = 6
            notify_progress(6, "RUNNING", "Aggregating compliance scores and compiling cryptographically sealed audit dossier...")

            total_time_ms = (time.perf_counter() - t0) * 1000.0
            extraction_meta = {
                "mode": self.mode.value if hasattr(self.mode, 'value') else str(self.mode),
                "model": self.provider.model_name,
                "latency_ms": total_time_ms,
            }

            aggregated = self.aggregator.aggregate(
                tender_id=tender_id,
                bid_id=bid_id,
                compliance_results=compliance_results,
                integrity_findings=integrity_findings,
                government_responses=gov_responses,
                grounding_warnings=grounding_warnings,
                extraction_metadata=extraction_meta,
                requirements=requirements,
                facts=all_facts,
            )

            dossier = self._generate_dossier(
                tender_id=tender_id,
                bid_id=bid_id,
                legal_name=legal_name,
                requirements=requirements,
                facts=all_facts,
                compliance_results=compliance_results,
                integrity_findings=integrity_findings,
                aggregated=aggregated,
                total_time_ms=total_time_ms,
            )

            # Cache results
            self._verifications[aggregated.verification_id] = aggregated
            self._dossiers[aggregated.verification_id] = dossier

            # Save to disk cache
            self._save_to_disk(aggregated, dossier)

            notify_progress(6, "COMPLETED", f"Audit dossier sealed (ID: {aggregated.verification_id}). Verification complete.", {
                "verification_id": aggregated.verification_id,
                "overall_status": aggregated.overall_status,
                "compliance_score": aggregated.compliance_score,
            })

            return aggregated, dossier

        except Exception as exc:
            notify_progress(current_step, "FAILED", f"Stage {current_step} failed: {str(exc)}")
            raise

    def get_verification(self, verification_id: str) -> Optional[AggregatedVerification]:
        if verification_id in self._verifications:
            return self._verifications[verification_id]
        return self._load_from_disk(verification_id)

    def get_dossier(self, verification_id: str) -> Optional[VerificationDossier]:
        if verification_id in self._dossiers:
            return self._dossiers[verification_id]
        verif = self.get_verification(verification_id)
        if verif and verification_id in self._dossiers:
            return self._dossiers[verification_id]
        return None

    def _generate_dossier(
        self,
        tender_id: str,
        bid_id: str,
        legal_name: Optional[Any],
        requirements: List[TenderRequirement],
        facts: List[BidderFact],
        compliance_results: List[VerificationResult],
        integrity_findings: List[IntegrityFinding],
        aggregated: AggregatedVerification,
        total_time_ms: float,
    ) -> VerificationDossier:
        evidence_list = []
        for f in facts:
            ev_item = {
                "fact_id": f.fact_id,
                "field": f.field,
                "value": f.value,
                "normalized_value": f.normalized_value,
                "unit": f.unit,
                "document": f.source_document,
                "page": f.page,
                "bbox": f.bbox,
                "snippet": f.raw_text_snippet,
                "confidence": f.extraction_confidence,
            }
            if getattr(f, "evidence", None):
                ev_item["evidence"] = f.evidence
                ev_item["bboxes"] = [e["bbox"] for e in f.evidence if e.get("bbox")]
            evidence_list.append(ev_item)

        # Construct deterministic provenance DAG
        from backend.core.provenance_dag import ProvenanceDAGBuilder
        dag = ProvenanceDAGBuilder.build(
            requirements=requirements,
            facts=facts,
            results=compliance_results,
            integrity_findings=integrity_findings,
            human_review_items=aggregated.human_review_items,
            adjudications=getattr(aggregated, "adjudications", None),
            bid_id=bid_id,
            tender_id=tender_id,
        )

        # Integrate verified mock government registry evidence into DAG
        for gov_item in getattr(aggregated, "government_checks", []):
            if isinstance(gov_item, dict):
                source = gov_item.get("source", "")
                status = gov_item.get("status", "")
                if source.startswith("MOCK_") and status == "VERIFIED":
                    mock_resp = AdapterResponse.from_dict(gov_item)
                    mock_facts = self.mock_evidence_adapter.to_bidder_facts(mock_resp, bid_id)
                    if mock_facts:
                        self.mock_evidence_adapter.integrate_with_dag(dag, mock_facts, mock_resp)

        return VerificationDossier(
            tender={
                "tender_id": tender_id,
                "requirements_count": len(requirements),
                "requirements": [r.to_dict() for r in requirements],
            },
            bidder={
                "bid_id": bid_id,
                "legal_name": str(legal_name) if legal_name else "UNKNOWN",
                "extracted_facts_count": len(facts),
                "facts": [f.to_dict() for f in facts],
            },
            compliance_summary={
                "compliance_status": aggregated.compliance_status,
                "overall_status": aggregated.overall_status,
                "critical_failures": aggregated.critical_failures,
                "major_failures": aggregated.major_failures,
                "total_requirements": len(requirements),
            },
            integrity_summary={
                "integrity_status": aggregated.integrity_status,
                "contradictions_count": len(aggregated.contradictions),
                "anomalies_count": aggregated.anomaly_count,
            },
            verification_results=aggregated.verification_results,
            government_checks=aggregated.government_checks,
            evidence=evidence_list,
            anomalies=aggregated.contradictions,
            human_review_items=aggregated.human_review_items,
            audit_metadata={
                "verification_id": aggregated.verification_id,
                "deterministic_run_id": aggregated.deterministic_run_id,
                "generated_at": aggregated.generated_at,
                "processing_time_ms": total_time_ms,
                "active_model": self.provider.model_name,
                "extraction_mode": self.mode.value if hasattr(self.mode, 'value') else str(self.mode),
            },
            provenance_graph=dag.to_dict(),
            compliance_score=aggregated.compliance_score_breakdown,
            risk_assessment=aggregated.risk_assessment,
            recommendation=aggregated.recommendation,
            pending_requirements=aggregated.pending_requirements,
            adjudications=getattr(aggregated, "adjudications", []),
        )

    def _save_to_disk(self, aggregated: AggregatedVerification, dossier: VerificationDossier) -> None:
        filename = _get_cache_filename(aggregated.verification_id)
        verif_file = os.path.join(self.cache_dir, filename)
        try:
            with open(verif_file, "w", encoding="utf-8") as f:
                json.dump({
                    "verification": aggregated.to_dict(),
                    "dossier": dossier.to_dict()
                }, f, indent=2)
        except Exception as e:
            logger.error(f"Failed to persist verification '{aggregated.verification_id}' to {verif_file}: {e}")
            raise IOError(f"Failed to persist verification to disk: {e}") from e

    def list_verifications(self) -> List[AggregatedVerification]:
        """
        Lists all cached verifications from in-memory store and disk cache.
        Scans cache_dir and loads any verification file not yet present in memory.
        Returns all verifications sorted by generated_at descending (newest first).
        """
        if os.path.exists(self.cache_dir):
            try:
                for fname in os.listdir(self.cache_dir):
                    if not fname.endswith(".json"):
                        continue
                    filepath = os.path.join(self.cache_dir, fname)
                    try:
                        with open(filepath, "r", encoding="utf-8") as f:
                            data = json.load(f)
                        if "verification" in data and "dossier" in data:
                            verif = AggregatedVerification.from_dict(data["verification"])
                            dossier = VerificationDossier.from_dict(data["dossier"])
                            vid = verif.verification_id
                            if vid not in self._verifications:
                                self._verifications[vid] = verif
                                self._dossiers[vid] = dossier
                    except Exception as e:
                        logger.debug(f"Skipping unparseable verification file '{fname}': {e}")
            except Exception as e:
                logger.error(f"Error scanning cache directory '{self.cache_dir}': {e}")

        verifs = list(self._verifications.values())
        verifs.sort(key=lambda v: getattr(v, "generated_at", "") or "", reverse=True)
        return verifs

    def get_all_review_items(self) -> List[Dict[str, Any]]:
        """
        Retrieves human review items across all persisted verifications.
        Enriches review items with verification identifiers and timestamps.
        Returns items sorted by created_at descending (newest first).
        """
        all_verifs = self.list_verifications()
        all_items: List[Dict[str, Any]] = []
        for v in all_verifs:
            for item in getattr(v, "human_review_items", []):
                item_dict = item.to_dict() if hasattr(item, "to_dict") else dict(item)
                if not item_dict.get("bid_id"):
                    item_dict["bid_id"] = v.bid_id
                if not item_dict.get("tender_id"):
                    item_dict["tender_id"] = v.tender_id
                if not item_dict.get("verification_id"):
                    item_dict["verification_id"] = v.verification_id
                if not item_dict.get("source_documents"):
                    item_dict["source_documents"] = [f"{v.bid_id}.pdf"]
                if not item_dict.get("created_at"):
                    item_dict["created_at"] = getattr(v, "generated_at", "")
                all_items.append(item_dict)

        all_items.sort(key=lambda x: x.get("created_at", "") or "", reverse=True)
        return all_items

    def _load_from_disk(self, verification_id: str) -> Optional[AggregatedVerification]:
        filename = _get_cache_filename(verification_id)
        verif_file = os.path.join(self.cache_dir, filename)
        if not os.path.exists(verif_file):
            # Legacy fallback: check if file was saved under raw verification_id
            legacy_file = os.path.join(self.cache_dir, f"{verification_id}.json")
            if os.path.exists(legacy_file):
                verif_file = legacy_file
            else:
                # Direct scan of cache_dir to locate file by internal verification_id
                if os.path.exists(self.cache_dir):
                    for fn in os.listdir(self.cache_dir):
                        if fn.endswith(".json"):
                            try:
                                fp = os.path.join(self.cache_dir, fn)
                                with open(fp, "r", encoding="utf-8") as f:
                                    data = json.load(f)
                                if data.get("verification", {}).get("verification_id") == verification_id:
                                    verif = AggregatedVerification.from_dict(data["verification"])
                                    dossier = VerificationDossier.from_dict(data["dossier"])
                                    self._verifications[verification_id] = verif
                                    self._dossiers[verification_id] = dossier
                                    return verif
                            except Exception:
                                pass
                return None

        try:
            with open(verif_file, "r", encoding="utf-8") as f:
                data = json.load(f)
            verif = AggregatedVerification.from_dict(data["verification"])
            dossier = VerificationDossier.from_dict(data["dossier"])
            self._verifications[verification_id] = verif
            self._dossiers[verification_id] = dossier
            return verif
        except Exception as e:
            logger.error(f"Failed to load verification '{verification_id}' from disk cache: {e}")
            return None

    def adjudicate(
        self,
        verification_id: str,
        request: Any,
    ) -> Tuple[AggregatedVerification, VerificationDossier, Any]:
        """
        Applies a procurement officer adjudication / override to an existing verification.
        Deterministically recalculates compliance score, risk assessment, and recommendation,
        updates provenance DAG, appends to immutable audit trail, and persists to cache.
        """
        from backend.core.adjudication import ProcurementOfficerAdjudicationEngine

        aggregated = self.get_verification(verification_id)
        if not aggregated:
            raise KeyError(f"Verification '{verification_id}' not found.")

        dossier = self.get_dossier(verification_id)
        if not dossier:
            raise KeyError(f"Dossier for verification '{verification_id}' not found.")

        updated_agg, updated_dos, record = ProcurementOfficerAdjudicationEngine.apply_adjudication(
            aggregated=aggregated,
            dossier=dossier,
            request=request,
        )

        # Update session store and disk cache
        self._verifications[verification_id] = updated_agg
        self._dossiers[verification_id] = updated_dos
        self._save_to_disk(updated_agg, updated_dos)

        return updated_agg, updated_dos, record

    def get_audit_trail(self, verification_id: str) -> Dict[str, Any]:
        """
        Retrieves the complete audit trail and adjudication records for a verification.
        """
        aggregated = self.get_verification(verification_id)
        if not aggregated:
            raise KeyError(f"Verification '{verification_id}' not found.")
        dossier = self.get_dossier(verification_id)

        adjudications = getattr(aggregated, "adjudications", [])
        return {
            "verification_id": verification_id,
            "deterministic_run_id": aggregated.deterministic_run_id,
            "tender_id": aggregated.tender_id,
            "bid_id": aggregated.bid_id,
            "generated_at": aggregated.generated_at,
            "adjudications_count": len(adjudications),
            "adjudications": adjudications,
            "human_review_items": aggregated.human_review_items,
            "provenance_node_count": len(dossier.provenance_graph.get("nodes", [])) if (dossier and dossier.provenance_graph) else 0,
            "provenance_edge_count": len(dossier.provenance_graph.get("edges", [])) if (dossier and dossier.provenance_graph) else 0,
        }

    def replay_verification(self, verification_id: str) -> Dict[str, Any]:
        """
        Performs an independent deterministic replay verification against the verification state
        using DeterministicReplayEngine, verifying zero-drift reproducibility.
        """
        from backend.core.replay_engine import DeterministicReplayEngine
        from backend.core.snapshot import SnapshotBuilder

        aggregated = self.get_verification(verification_id)
        if not aggregated:
            raise KeyError(f"Verification '{verification_id}' not found.")
        dossier = self.get_dossier(verification_id)
        if not dossier:
            raise KeyError(f"Dossier for verification '{verification_id}' not found.")

        # Reconstruct requirements and facts from dossier
        from backend.core.models import TenderRequirement, BidderFact, VerificationResult
        reqs = [TenderRequirement.from_dict(r) if isinstance(r, dict) else r for r in dossier.tender.get("requirements", [])]
        facts = [BidderFact.from_dict(f) if isinstance(f, dict) else f for f in dossier.bidder.get("facts", [])]
        results = [VerificationResult.from_dict(r) if isinstance(r, dict) else r for r in dossier.verification_results]

        snapshot = SnapshotBuilder.build(
            tender_id=aggregated.tender_id,
            bid_id=aggregated.bid_id,
            requirements=reqs,
            facts=facts,
            compliance_results=results,
            human_review_items=aggregated.human_review_items,
            aggregated_status={
                "compliance_status": aggregated.compliance_status,
                "integrity_status": aggregated.integrity_status,
                "overall_status": aggregated.overall_status,
                "critical_failures": aggregated.critical_failures,
                "major_failures": aggregated.major_failures,
                "anomaly_count": aggregated.anomaly_count,
                "review_required": aggregated.review_required,
            },
            provenance_graph=dossier.provenance_graph,
        )

        replay_engine = DeterministicReplayEngine()
        replay_result = replay_engine.replay(snapshot)
        return replay_result.to_dict(include_transient_metrics=True)

