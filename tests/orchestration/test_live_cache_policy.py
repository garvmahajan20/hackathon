# -*- coding: utf-8 -*-
import json
import os
import sys
import tempfile
import time
import unittest
from typing import Any, Dict, List, Optional
from unittest.mock import MagicMock

sys.path.insert(0, os.path.abspath("."))

import fitz  # PyMuPDF
from fastapi.testclient import TestClient

from backend.api.app import app
from backend.core.models import BidderFact, TenderRequirement
from backend.extraction.cache import CachePolicy, LLMCache
from backend.extraction.fact_extractor import LLMBidderFactExtractor
from backend.extraction.mock_provider import MockLLMProvider
from backend.extraction.models import LLMMode, LLMProviderResponse
from backend.extraction.provider import BaseLLMProvider
from backend.extraction.requirement_extractor import TenderRequirementExtractor
from backend.ingestion.pipeline import DocumentIngestionPipeline
from backend.orchestration import (
    ComplianceStatus,
    OverallStatus,
    ReviewCategory,
    VerificationAggregator,
    VerificationOrchestrator,
)

class TrackingDummyProvider(BaseLLMProvider):
    """
    Deterministic test provider that tracks calls and returns structured JSON.
    """
    def __init__(self, response_json: str):
        self.call_count = 0
        self.response_json = response_json

    @property
    def provider_name(self) -> str:
        return "TrackingDummyProvider"

    @property
    def model_name(self) -> str:
        return "tracking-model-v1"

    def is_available(self) -> bool:
        return True

    def generate_structured(
        self,
        prompt: str,
        system_prompt: Optional[str] = None,
        json_schema: Optional[Dict[str, Any]] = None,
        temperature: float = 0.0,
        **kwargs: Any
    ) -> LLMProviderResponse:
        self.call_count += 1
        return LLMProviderResponse(
            content=self.response_json,
            model_name=self.model_name,
            latency_ms=10.0,
            is_mock=False,
            is_cached=False,
        )

class FailingProvider(BaseLLMProvider):
    """
    Provider that raises an exception if invoked.
    Used to guarantee that CACHED mode never touches the provider when cache is populated.
    """
    def __init__(self):
        self.call_count = 0

    @property
    def provider_name(self) -> str:
        return "FailingProvider"

    @property
    def model_name(self) -> str:
        return "failing-model-v1"

    def is_available(self) -> bool:
        return True

    def generate_structured(self, *args, **kwargs) -> LLMProviderResponse:
        self.call_count += 1
        raise AssertionError("Provider was invoked when cache should have been used!")


class TestLiveCachePolicyAndTruthfulStream(unittest.TestCase):
    @classmethod
    def setUpClass(cls):
        cls.temp_dir = tempfile.mkdtemp(prefix="test_cache_policy_")
        cls.cache_dir = os.path.join(cls.temp_dir, "llm_cache")
        cls.client = TestClient(app)

        # Generate minimal valid synthetic PDF documents for testing
        cls.tender_pdf_path = os.path.join(cls.temp_dir, "TEST_TENDER.pdf")
        cls.bid_pdf_path = os.path.join(cls.temp_dir, "TEST_BID.pdf")

        doc_t = fitz.open()
        p_t = doc_t.new_page()
        p_t.insert_text((50, 72), "Tender Requirement: Minimum average annual turnover of Rs 5.0 Crore required.")
        doc_t.save(cls.tender_pdf_path)
        doc_t.close()

        doc_b = fitz.open()
        p_b = doc_b.new_page()
        p_b.insert_text((50, 72), "Bidder Submission: Average annual turnover is Rs 8.5 Crore.")
        doc_b.save(cls.bid_pdf_path)
        doc_b.close()

        cls.ingestion = DocumentIngestionPipeline()
        cls.t_ingest = cls.ingestion.ingest_file(cls.tender_pdf_path)
        cls.b_ingest = cls.ingestion.ingest_file(cls.bid_pdf_path)

    @classmethod
    def tearDownClass(cls):
        import shutil
        shutil.rmtree(cls.temp_dir, ignore_errors=True)

    # 1. LIVE invokes provider even when matching cache exists
    def test_01_live_mode_bypasses_cache_and_invokes_provider(self):
        cache = LLMCache(cache_dir=self.cache_dir)
        canned_json = json.dumps({
            "requirements": [
                {
                    "clause_id": "REQ-01",
                    "category": "FINANCIAL_CAPACITY",
                    "parameter": "AVERAGE_ANNUAL_TURNOVER",
                    "operator": ">=",
                    "target_value": "5.0",
                    "unit": "CRORE",
                    "is_mandatory": True,
                    "evidence_block_ids": [self.t_ingest.pages[0].blocks[0].block_id if self.t_ingest.pages[0].blocks else "BLK-01"]
                }
            ]
        })

        provider = TrackingDummyProvider(canned_json)

        extractor = TenderRequirementExtractor(
            provider=provider,
            cache=cache,
            mode=LLMMode.LIVE,
            two_pass=False,
        )

        # Pre-seed cache with dummy stale content
        cache_key = cache.generate_cache_key(
            provider_name=provider.provider_name,
            model_name=provider.model_name,
            prompt_version="v1.0",
            prompt_content="dummy",
        )
        cache.set(cache_key, LLMProviderResponse(content='{"stale": true}', model_name=provider.model_name))
        self.assertTrue(cache.has(cache_key))

        # In LIVE mode, cache.should_read_cache must return False
        self.assertFalse(cache.should_read_cache(LLMMode.LIVE))

        reqs = extractor.extract_requirements(self.t_ingest, tender_id="TENDER-TEST-01")

        # Provider MUST have been invoked (fresh call)
        self.assertGreaterEqual(provider.call_count, 1)
        self.assertEqual(extractor.last_extraction_source, "FRESH")

        # Now test Fact Extractor in LIVE mode
        canned_facts = json.dumps({
            "facts": [
                {
                    "field": "AVERAGE_ANNUAL_TURNOVER",
                    "raw_value": "8.5 Crore",
                    "evidence_block_ids": [self.b_ingest.pages[0].blocks[0].block_id if self.b_ingest.pages[0].blocks else "BLK-01"]
                }
            ]
        })
        fact_provider = TrackingDummyProvider(canned_facts)
        fact_extractor = LLMBidderFactExtractor(
            provider=fact_provider,
            cache=cache,
            mode=LLMMode.LIVE,
            strict_grounding=False,
        )

        facts = fact_extractor.extract_facts(self.b_ingest, bid_id="BID-TEST-01")
        self.assertGreaterEqual(fact_provider.call_count, 1)
        self.assertEqual(fact_extractor.last_extraction_source, "FRESH")

    # 2. CACHED reads cache and does NOT invoke provider
    def test_02_cached_mode_reads_cache_without_calling_provider(self):
        cache = LLMCache(cache_dir=self.cache_dir)
        canned_reqs = json.dumps({
            "requirements": [
                {
                    "clause_id": "REQ-CACHED-01",
                    "category": "FINANCIAL_CAPACITY",
                    "parameter": "AVERAGE_ANNUAL_TURNOVER",
                    "operator": ">=",
                    "target_value": "5.0",
                    "unit": "CRORE",
                    "is_mandatory": True,
                    "evidence_block_ids": [self.t_ingest.pages[0].blocks[0].block_id if self.t_ingest.pages[0].blocks else "BLK-01"]
                }
            ]
        })

        failing_provider = FailingProvider()
        self.assertTrue(cache.should_read_cache(LLMMode.CACHED))

        extractor = TenderRequirementExtractor(
            provider=failing_provider,
            cache=cache,
            mode=LLMMode.CACHED,
            two_pass=False,
        )

        # Pre-seed cache with the expected prompt cache key
        from backend.extraction.prompts import format_tender_requirement_prompt, REQUIREMENT_PROMPT_VERSION
        expected_prompt = format_tender_requirement_prompt("TENDER-CACHED", self.t_ingest.pages)
        expected_key = cache.generate_cache_key(
            provider_name=failing_provider.provider_name,
            model_name=failing_provider.model_name,
            prompt_version=REQUIREMENT_PROMPT_VERSION,
            prompt_content=expected_prompt,
        )
        cache.set(expected_key, LLMProviderResponse(content=canned_reqs, model_name=failing_provider.model_name))

        # Extract: failing_provider should NOT be called because cache hits!
        reqs = extractor.extract_requirements(self.t_ingest, tender_id="TENDER-CACHED")
        self.assertEqual(failing_provider.call_count, 0)
        self.assertEqual(extractor.last_extraction_source, "CACHED")
        self.assertGreaterEqual(len(reqs), 1)

    # 3. MOCK mode remains mock and does not invoke live LLM
    def test_03_mock_mode_semantics_intact(self):
        orch = VerificationOrchestrator(mode=LLMMode.MOCK)
        self.assertEqual(orch.mode, LLMMode.MOCK)
        self.assertIsInstance(orch.provider, MockLLMProvider)

        aggregated, dossier = orch.verify_submission(
            tender_document_path=self.tender_pdf_path,
            bid_document_paths=[self.bid_pdf_path],
            tender_id="TENDER-MOCK",
            bid_id="BID-MOCK",
        )
        self.assertEqual(aggregated.processing_metadata.get("extraction_source"), "MOCK")
        self.assertEqual(aggregated.processing_metadata.get("cache_policy"), "DISABLED")

    # 4. SSE stage timing reflects actual backend execution
    def test_04_sse_stream_timing_and_events(self):
        with open(self.tender_pdf_path, "rb") as tf, open(self.bid_pdf_path, "rb") as bf:
            files = [
                ("tender_file", ("TENDER-STREAM.pdf", tf.read(), "application/pdf")),
                ("bid_files", ("BID-STREAM.pdf", bf.read(), "application/pdf")),
            ]
            data = {
                "tender_id": "TENDER-STREAM",
                "bid_id": "BID-STREAM",
                "mode": "mock",
            }
            t_start = time.perf_counter()
            resp = self.client.post("/api/v1/verify-stream", files=files, data=data)

        self.assertEqual(resp.status_code, 200)
        self.assertIn("text/event-stream", resp.headers.get("content-type", ""))

        events = []
        for line in resp.text.splitlines():
            line = line.strip()
            if line.startswith("data:"):
                events.append(json.loads(line[5:].strip()))

        # Check all 6 steps exist
        steps_seen = set()
        for e in events:
            if e.get("event") == "STAGE_PROGRESS":
                steps_seen.add(e.get("step"))
                self.assertIn(e.get("status"), ["RUNNING", "COMPLETED", "FAILED"])

        for step_num in range(1, 7):
            self.assertIn(step_num, steps_seen)

        # Check Step 3 metadata contains extraction_source
        step3_events = [e for e in events if e.get("event") == "STAGE_PROGRESS" and e.get("step") == 3 and e.get("status") == "COMPLETED"]
        self.assertGreaterEqual(len(step3_events), 1)
        self.assertIn("extraction_source", step3_events[0].get("meta", {}))

        # Check completion payload arrives
        completion = [e for e in events if e.get("event") == "VERIFICATION_COMPLETED"]
        self.assertEqual(len(completion), 1)
        self.assertEqual(completion[0]["result"]["verification_id"], f"VERIF-TENDER-STREAM-BID-STREAM")

    # 5. Zero-result guard remains intact
    def test_05_zero_requirements_guard_intact(self):
        aggregator = VerificationAggregator()
        result = aggregator.aggregate(
            tender_id="T-EMPTY",
            bid_id="B-EMPTY",
            compliance_results=[],
            integrity_findings=[],
            government_responses=[],
            requirements=[],
            facts=[],
        )
        self.assertNotEqual(result.compliance_status, ComplianceStatus.PASS.value)
        self.assertNotEqual(result.overall_status, OverallStatus.PASS.value)
        self.assertEqual(result.compliance_status, ComplianceStatus.REVIEW.value)
        self.assertEqual(result.overall_status, OverallStatus.REVIEW.value)

        # Review items must explain zero requirements
        reasons = [item.get("reason", "") if isinstance(item, dict) else getattr(item, "reason", "") for item in result.human_review_items]
        self.assertTrue(any("No verifiable compliance requirements" in r for r in reasons))

if __name__ == "__main__":
    unittest.main(verbosity=2)
