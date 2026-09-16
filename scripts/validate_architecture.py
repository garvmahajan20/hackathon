"""
Comprehensive validation test for the Native PDF architecture.
Tests all components WITHOUT making live Gemini API calls.
"""
import os
import sys
import json
import hashlib

sys.path.insert(0, os.path.abspath("."))

from backend.config import load_dotenv
load_dotenv()

def test_imports():
    """Test A: All modules import correctly."""
    print("=" * 60)
    print("TEST A: Module imports")
    print("=" * 60)
    
    modules = [
        "backend.extraction.gemini_provider",
        "backend.extraction.provider",
        "backend.extraction.models",
        "backend.extraction.evidence_grounder",
        "backend.extraction.cache",
        "backend.extraction.mock_provider",
        "backend.extraction.fact_extractor",
        "backend.extraction.requirement_extractor",
        "backend.extraction.prompts",
        "backend.orchestration.orchestrator",
        "backend.api.app",
        "backend.ingestion.pipeline",
        "backend.ingestion.models",
        "backend.core.models",
        "backend.core.normalization",
        "backend.core.ontology",
    ]
    
    passed = 0
    failed = 0
    for mod in modules:
        try:
            __import__(mod)
            print(f"  [PASS] {mod}")
            passed += 1
        except Exception as e:
            print(f"  [FAIL] {mod}: {e}")
            failed += 1
    
    print(f"\n  Result: {passed}/{passed+failed} passed\n")
    return failed == 0


def test_native_pdf_provider():
    """Test B: GeminiProvider has generate_structured_from_pdf with correct payload."""
    print("=" * 60)
    print("TEST B: Native PDF provider method")
    print("=" * 60)
    
    from backend.extraction.gemini_provider import GeminiProvider
    from backend.extraction.provider import BaseLLMProvider
    import inspect
    
    # Check method exists on base
    assert hasattr(BaseLLMProvider, "generate_structured_from_pdf"), "BaseLLMProvider missing generate_structured_from_pdf"
    print("  [PASS] BaseLLMProvider has generate_structured_from_pdf")
    
    # Check method exists on GeminiProvider
    assert hasattr(GeminiProvider, "generate_structured_from_pdf"), "GeminiProvider missing generate_structured_from_pdf"
    print("  [PASS] GeminiProvider has generate_structured_from_pdf")
    
    # Verify the method constructs correct payload by inspecting the source
    source = inspect.getsource(GeminiProvider.generate_structured_from_pdf)
    assert "inlineData" in source, "generate_structured_from_pdf must use inlineData"
    assert "application/pdf" in source, "generate_structured_from_pdf must use application/pdf MIME type"
    assert "base64" in source, "generate_structured_from_pdf must base64-encode the PDF"
    print("  [PASS] Payload uses inlineData with application/pdf MIME type")
    
    # Verify fallback cascade exists
    assert "_fallback_models" in source or "fallback_m" in source, "Fallback cascade missing"
    print("  [PASS] Fallback cascade exists in generate_structured_from_pdf")
    
    print("\n  Result: All passed\n")
    return True


def test_mock_provider():
    """Test C: MockProvider implements generate_structured_from_pdf."""
    print("=" * 60)
    print("TEST C: Mock provider compatibility")
    print("=" * 60)
    
    from backend.extraction.mock_provider import MockLLMProvider
    
    mock = MockLLMProvider()
    assert hasattr(mock, "generate_structured_from_pdf"), "MockLLMProvider missing generate_structured_from_pdf"
    print("  [PASS] MockLLMProvider has generate_structured_from_pdf")
    
    # Test it with dummy bytes
    resp = mock.generate_structured_from_pdf(
        pdf_bytes=b"dummy",
        prompt="Test prompt",
        system_prompt="Test system"
    )
    assert resp is not None, "MockLLMProvider.generate_structured_from_pdf returned None"
    print("  [PASS] MockLLMProvider.generate_structured_from_pdf returns response")
    
    print("\n  Result: All passed\n")
    return True


def test_data_models():
    """Test D: CandidateRequirement and CandidateFact have source_page/evidence_snippet."""
    print("=" * 60)
    print("TEST D: Data model fields")
    print("=" * 60)
    
    from backend.extraction.models import CandidateRequirement, CandidateFact
    
    # CandidateRequirement
    cr = CandidateRequirement(
        description="test",
        category="OTHER",
        source_page=5,
        evidence_snippet="some evidence"
    )
    assert cr.source_page == 5, f"source_page wrong: {cr.source_page}"
    assert cr.evidence_snippet == "some evidence", f"evidence_snippet wrong: {cr.evidence_snippet}"
    assert hasattr(cr, "evidence_block_ids"), "evidence_block_ids removed (should still exist for backward compat)"
    print("  [PASS] CandidateRequirement has source_page, evidence_snippet, evidence_block_ids")
    
    # CandidateFact
    cf = CandidateFact(
        field="gstin",
        raw_value="12ABCDE3456F7GH",
        source_page=2,
        evidence_snippet="GSTIN: 12ABCDE3456F7GH"
    )
    assert cf.source_page == 2, f"source_page wrong: {cf.source_page}"
    assert cf.evidence_snippet == "GSTIN: 12ABCDE3456F7GH"
    print("  [PASS] CandidateFact has source_page, evidence_snippet, evidence_block_ids")
    
    print("\n  Result: All passed\n")
    return True


def test_prompts_no_text_blocks():
    """Test E: Prompts do NOT inject page text blocks as semantic source."""
    print("=" * 60)
    print("TEST E: Prompts reference PDF, not text blocks")
    print("=" * 60)
    
    from backend.extraction.prompts import (
        format_tender_requirement_prompt,
        format_tender_bidder_obligation_prompt,
        format_bidder_fact_prompt,
        format_page_condition_prompt,
        BIDDER_FACT_SYSTEM_PROMPT,
        TENDER_EXHAUSTIVE_CONDITION_SYSTEM_PROMPT,
        TENDER_BIDDER_OBLIGATION_SYSTEM_PROMPT,
        FACT_PROMPT_VERSION,
        REQUIREMENT_PROMPT_VERSION,
    )
    from backend.ingestion.models import ExtractedPage, TextBlock
    
    pages = [
        ExtractedPage(
            page_number=1,
            width=595.0,
            height=842.0,
            text="Some secret text",
            raw_text="Some secret text",
            blocks=[TextBlock(block_id="B1", page_number=1, text="Some secret text", raw_text="Some secret text", bbox=[0,0,100,100])],
        )
    ]
    
    # Test that formatter outputs do NOT contain block text
    p1 = format_tender_requirement_prompt("T-001", pages)
    assert "Some secret text" not in p1, f"format_tender_requirement_prompt leaks block text: {p1}"
    assert "B1" not in p1 or "BLOCK" not in p1.upper(), f"format_tender_requirement_prompt references block IDs"
    print("  [PASS] format_tender_requirement_prompt does not inject block text")
    
    p2 = format_tender_bidder_obligation_prompt("T-001", pages)
    assert "Some secret text" not in p2, f"format_tender_bidder_obligation_prompt leaks block text"
    print("  [PASS] format_tender_bidder_obligation_prompt does not inject block text")
    
    p3 = format_bidder_fact_prompt("BID-001", pages)
    assert "Some secret text" not in p3, f"format_bidder_fact_prompt leaks block text"
    print("  [PASS] format_bidder_fact_prompt does not inject block text")
    
    p4 = format_page_condition_prompt("T-001", pages[0])
    assert "Some secret text" not in p4, f"format_page_condition_prompt leaks block text"
    print("  [PASS] format_page_condition_prompt does not inject block text")
    
    # Verify JSON schemas exist in system prompts
    assert '"facts"' in BIDDER_FACT_SYSTEM_PROMPT, "BIDDER_FACT_SYSTEM_PROMPT missing facts schema"
    assert '"requirements"' in TENDER_EXHAUSTIVE_CONDITION_SYSTEM_PROMPT, "Missing requirements schema"
    assert '"requirements"' in TENDER_BIDDER_OBLIGATION_SYSTEM_PROMPT, "Missing requirements schema"
    print("  [PASS] System prompts contain JSON schemas")
    
    # Verify source_page/evidence_snippet in schemas
    assert "source_page" in BIDDER_FACT_SYSTEM_PROMPT, "Missing source_page in fact schema"
    assert "evidence_snippet" in BIDDER_FACT_SYSTEM_PROMPT, "Missing evidence_snippet in fact schema"
    assert "source_page" in TENDER_EXHAUSTIVE_CONDITION_SYSTEM_PROMPT, "Missing source_page in req schema"
    assert "evidence_snippet" in TENDER_EXHAUSTIVE_CONDITION_SYSTEM_PROMPT, "Missing evidence_snippet in req schema"
    print("  [PASS] Schemas include source_page and evidence_snippet fields")
    
    # Verify prompt versions exist
    assert isinstance(FACT_PROMPT_VERSION, int), f"FACT_PROMPT_VERSION not int: {type(FACT_PROMPT_VERSION)}"
    assert isinstance(REQUIREMENT_PROMPT_VERSION, int), f"REQUIREMENT_PROMPT_VERSION not int: {type(REQUIREMENT_PROMPT_VERSION)}"
    print("  [PASS] FACT_PROMPT_VERSION and REQUIREMENT_PROMPT_VERSION exist")
    
    # Verify "text blocks" no longer in system prompts as semantic source
    assert "text blocks" not in BIDDER_FACT_SYSTEM_PROMPT.lower().replace("attached", ""), \
        "BIDDER_FACT_SYSTEM_PROMPT still references text blocks as semantic source"
    print("  [PASS] System prompts reference PDF document, not text blocks")
    
    print("\n  Result: All passed\n")
    return True


def test_cache_pdf_sha256():
    """Test F: Cache key includes pdf_sha256."""
    print("=" * 60)
    print("TEST F: Cache key includes PDF SHA256")
    print("=" * 60)
    
    from backend.extraction.cache import LLMCache
    
    cache = LLMCache()
    
    key1 = cache.generate_cache_key(
        provider_name="test",
        model_name="test-model",
        prompt_version="1",
        prompt_content="test prompt",
        pdf_sha256="abc123"
    )
    
    key2 = cache.generate_cache_key(
        provider_name="test",
        model_name="test-model",
        prompt_version="1",
        prompt_content="test prompt",
        pdf_sha256="def456"
    )
    
    key3 = cache.generate_cache_key(
        provider_name="test",
        model_name="test-model",
        prompt_version="1",
        prompt_content="test prompt",
    )
    
    assert key1 != key2, "Different PDF SHA256 should produce different cache keys"
    assert key1 != key3, "With vs without SHA256 should produce different cache keys"
    print("  [PASS] Different PDF SHA256 produces different cache keys")
    print("  [PASS] Cache key generation accepts pdf_sha256 parameter")
    
    print("\n  Result: All passed\n")
    return True


def test_evidence_grounder():
    """Test G: ground_by_semantic_pointer works correctly."""
    print("=" * 60)
    print("TEST G: Evidence grounder")
    print("=" * 60)
    
    from backend.extraction.evidence_grounder import EvidenceGrounder
    from backend.ingestion.models import ExtractionResult, DocumentMetadata, ExtractedPage, TextBlock, DocumentType
    
    metadata = DocumentMetadata(
        document_id="DOC-001",
        filename="test.pdf",
        file_path="/tmp/test.pdf",
        file_size_bytes=1000,
        sha256="abc123",
        page_count=2,
        document_type=DocumentType.BID,
    )
    
    pages = [
        ExtractedPage(
            page_number=1,
            width=595.0,
            height=842.0,
            text="The bidder's average annual turnover is Rs. 150 Lakhs Company Name: CyberLogix Pvt Ltd",
            raw_text="The bidder's average annual turnover is Rs. 150 Lakhs Company Name: CyberLogix Pvt Ltd",
            blocks=[
                TextBlock(block_id="B1P1", page_number=1, text="The bidder's average annual turnover is Rs. 150 Lakhs", raw_text="The bidder's average annual turnover is Rs. 150 Lakhs", bbox=[10, 20, 300, 40]),
                TextBlock(block_id="B2P1", page_number=1, text="Company Name: CyberLogix Pvt Ltd", raw_text="Company Name: CyberLogix Pvt Ltd", bbox=[10, 50, 300, 70]),
            ]
        ),
        ExtractedPage(
            page_number=2,
            width=595.0,
            height=842.0,
            text="PAN: AABCC1234D Delivery period: 45 days from date of order",
            raw_text="PAN: AABCC1234D Delivery period: 45 days from date of order",
            blocks=[
                TextBlock(block_id="B1P2", page_number=2, text="PAN: AABCC1234D", raw_text="PAN: AABCC1234D", bbox=[10, 20, 200, 40]),
                TextBlock(block_id="B2P2", page_number=2, text="Delivery period: 45 days from date of order", raw_text="Delivery period: 45 days from date of order", bbox=[10, 50, 300, 70]),
            ]
        ),
    ]
    
    extraction_result = ExtractionResult(
        document_id="DOC-001",
        metadata=metadata,
        pages=pages,
    )
    
    grounder = EvidenceGrounder(extraction_result)
    
    # Test 1: Good match on correct page
    res = grounder.ground_by_semantic_pointer(
        source_page=1,
        evidence_snippet="average annual turnover is Rs. 150 Lakhs",
    )
    assert res.is_valid, f"Expected valid grounding, got: {res.errors}"
    assert res.primary_page == 1, f"Expected page 1, got: {res.primary_page}"
    assert res.resolved_evidence, "Expected resolved evidence"
    assert res.resolved_evidence[0]["block_id"] == "B1P1", f"Expected B1P1, got: {res.resolved_evidence[0]['block_id']}"
    print("  [PASS] Good snippet grounded to correct block on correct page")
    
    # Test 2: Empty snippet
    res2 = grounder.ground_by_semantic_pointer(
        source_page=1,
        evidence_snippet="",
    )
    assert not res2.is_valid, "Empty snippet should fail grounding"
    print("  [PASS] Empty evidence_snippet correctly rejected")
    
    # Test 3: Snippet from wrong page should still find it
    res3 = grounder.ground_by_semantic_pointer(
        source_page=99,  # wrong page
        evidence_snippet="PAN: AABCC1234D",
    )
    assert res3.is_valid, "Should find block even when page is wrong (fallback to all pages)"
    assert res3.primary_page == 2, f"Expected page 2, got: {res3.primary_page}"
    print("  [PASS] Wrong page number falls back to search all pages")
    
    # Test 4: Completely unrelated snippet
    res4 = grounder.ground_by_semantic_pointer(
        source_page=1,
        evidence_snippet="This text does not exist anywhere in the document at all xyz123",
    )
    assert not res4.is_valid, "Completely unrelated snippet should fail grounding"
    print("  [PASS] Unrelated snippet correctly rejected")
    
    # Test 5: Method signature does NOT accept 'strict' parameter
    import inspect
    sig = inspect.signature(grounder.ground_by_semantic_pointer)
    param_names = list(sig.parameters.keys())
    assert "strict" not in param_names, f"ground_by_semantic_pointer should not accept 'strict' parameter, has: {param_names}"
    print("  [PASS] ground_by_semantic_pointer does not accept 'strict' parameter")
    
    print("\n  Result: All passed\n")
    return True


def test_requirement_extractor_parse():
    """Test H: Requirement parser handles new schema."""
    print("=" * 60)
    print("TEST H: Requirement extractor parser")
    print("=" * 60)
    
    from backend.extraction.requirement_extractor import TenderRequirementExtractor
    from backend.extraction.mock_provider import MockLLMProvider
    from backend.extraction.models import LLMMode
    
    ext = TenderRequirementExtractor(
        provider=MockLLMProvider(),
        mode=LLMMode.MOCK,
    )
    
    # Test parsing of new schema response
    test_response = json.dumps({
        "requirements": [
            {
                "description": "Bidder must have average annual turnover >= 100 Lakhs",
                "category": "FINANCIAL_CAPACITY",
                "field": "bidder_average_annual_turnover",
                "operator": ">=",
                "expected_value": "100 Lakhs",
                "mandatory": True,
                "source_page": 3,
                "evidence_snippet": "The average Annual Turnover of the Bidder should be >= Rs. 100 Lakhs",
                "source_clause": "ATC Clause 1",
                "requirement_type": "BIDDER_COMPLIANCE",
            }
        ]
    })
    
    candidates = ext._parse_candidates(test_response, default_source_pass="PASS_1_EXHAUSTIVE")
    assert len(candidates) == 1, f"Expected 1 candidate, got {len(candidates)}"
    c = candidates[0]
    assert c.source_page == 3, f"Expected source_page 3, got {c.source_page}"
    assert "100 Lakhs" in c.evidence_snippet, f"Expected evidence_snippet with turnover text"
    assert c.category == "FINANCIAL_CAPACITY"
    assert c.field == "bidder_average_annual_turnover"
    assert c.operator == ">="
    assert c.mandatory is True
    assert c.source_pass == "PASS_1_EXHAUSTIVE"
    print("  [PASS] Parser handles new schema with source_page, evidence_snippet")
    
    # Test empty/bad JSON
    bad_candidates = ext._parse_candidates("not json at all")
    assert len(bad_candidates) == 0, f"Expected 0 from bad JSON, got {len(bad_candidates)}"
    print("  [PASS] Parser returns empty list on bad JSON")
    
    print("\n  Result: All passed\n")
    return True


def test_fact_extractor_parse():
    """Test I: Fact extractor parser handles new schema."""
    print("=" * 60)
    print("TEST I: Fact extractor parser")
    print("=" * 60)
    
    from backend.extraction.fact_extractor import LLMBidderFactExtractor
    from backend.extraction.mock_provider import MockLLMProvider
    from backend.extraction.models import LLMMode
    
    ext = LLMBidderFactExtractor(
        provider=MockLLMProvider(),
        mode=LLMMode.MOCK,
    )
    
    test_response = json.dumps({
        "facts": [
            {
                "field": "company_name",
                "raw_value": "CyberLogix Pvt Ltd",
                "source_page": 1,
                "evidence_snippet": "Company Name: CyberLogix Pvt Ltd",
                "extraction_confidence": "HIGH",
                "metadata": {"fact_category": "Corporate & Regulatory"}
            },
            {
                "field": "bidder_average_annual_turnover",
                "raw_value": "150 Lakhs",
                "source_page": 2,
                "evidence_snippet": "Average Annual Turnover: Rs. 150 Lakhs",
                "extraction_confidence": "HIGH",
            }
        ]
    })
    
    candidates = ext._parse_candidates(test_response)
    assert len(candidates) == 2, f"Expected 2 candidates, got {len(candidates)}"
    
    c1 = candidates[0]
    assert c1.field == "company_name"
    assert c1.source_page == 1
    assert "CyberLogix" in c1.evidence_snippet
    print("  [PASS] Fact parser handles new schema with source_page, evidence_snippet")
    
    c2 = candidates[1]
    assert c2.field == "bidder_average_annual_turnover"
    assert c2.source_page == 2
    print("  [PASS] Multiple facts parsed correctly")
    
    print("\n  Result: All passed\n")
    return True


def test_orchestrator_construction():
    """Test J: Orchestrator constructs extractors correctly."""
    print("=" * 60)
    print("TEST J: Orchestrator construction")
    print("=" * 60)
    
    from backend.orchestration.orchestrator import VerificationOrchestrator
    from backend.extraction.models import LLMMode
    
    # Test MOCK mode
    orch = VerificationOrchestrator(mode=LLMMode.MOCK)
    assert orch.requirement_extractor is not None, "requirement_extractor not created"
    assert orch.fact_extractor is not None, "fact_extractor not created"
    assert hasattr(orch.requirement_extractor, '_read_pdf_bytes'), "requirement_extractor missing _read_pdf_bytes"
    assert hasattr(orch.fact_extractor, '_read_pdf_bytes'), "fact_extractor missing _read_pdf_bytes"
    print("  [PASS] Orchestrator creates extractors in MOCK mode")
    
    # Test LIVE mode (will use GeminiProvider)
    orch_live = VerificationOrchestrator(mode=LLMMode.LIVE)
    assert orch_live.requirement_extractor is not None
    assert orch_live.fact_extractor is not None
    provider = orch_live.provider
    assert hasattr(provider, 'generate_structured_from_pdf'), "LIVE provider missing generate_structured_from_pdf"
    print("  [PASS] Orchestrator creates extractors in LIVE mode with native PDF provider")
    
    print("\n  Result: All passed\n")
    return True


def test_uuid_in_app():
    """Test K: uuid is properly imported in app.py."""
    print("=" * 60)
    print("TEST K: uuid import in app.py")
    print("=" * 60)
    
    import sys
    import backend.api.app
    app_module = sys.modules["backend.api.app"]
    
    # Check that uuid is importable from the app module scope
    assert hasattr(app_module, 'uuid') or 'uuid' in dir(app_module), "uuid not in app module scope"
    print("  [PASS] uuid is available in backend.api.app module scope")
    
    # Check that the app object exists
    assert hasattr(app_module, 'app'), "FastAPI app object missing"
    print("  [PASS] FastAPI app object exists")
    
    print("\n  Result: All passed\n")
    return True


def test_demo_files_exist():
    """Test L: Demo files exist."""
    print("=" * 60)
    print("TEST L: Demo files exist")
    print("=" * 60)
    
    files = [
        "data/external/blind_test/REAL_WORLD_HOLDOUT_03.pdf",
        "data/demo/JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf",
        "data/demo/JARVIS_DEMO_FAIL_BIDDER_GEM_2026_B_7959150.pdf",
        "data/demo/JARVIS_DEMO_FORENSIC_BIDDER_GEM_2026_B_7959150.pdf",
    ]
    
    for f in files:
        exists = os.path.exists(f)
        size = os.path.getsize(f) if exists else 0
        status = "PASS" if exists else "FAIL"
        print(f"  [{status}] {f} ({size:,} bytes)")
    
    all_exist = all(os.path.exists(f) for f in files)
    print(f"\n  Result: {'All passed' if all_exist else 'SOME MISSING'}\n")
    return all_exist


def test_ingestion_pipeline():
    """Test M: Ingestion pipeline produces correct metadata including file_path and sha256."""
    print("=" * 60)
    print("TEST M: Ingestion pipeline metadata")
    print("=" * 60)
    
    from backend.ingestion.pipeline import DocumentIngestionPipeline
    
    pipeline = DocumentIngestionPipeline()
    
    # Use a real demo PDF
    pdf_path = "data/demo/JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf"
    if not os.path.exists(pdf_path):
        print("  [SKIP] Demo PDF not found")
        return True
    
    result = pipeline.ingest_file(
        file_path=pdf_path,
    )
    
    assert result.metadata.file_path == pdf_path, f"file_path mismatch: {result.metadata.file_path}"
    assert result.metadata.sha256, "sha256 is empty"
    assert len(result.metadata.sha256) == 64, f"sha256 wrong length: {len(result.metadata.sha256)}"
    assert result.metadata.page_count > 0, f"page_count is 0"
    assert len(result.pages) > 0, "No pages extracted"
    print(f"  [PASS] Metadata: file_path={pdf_path}, sha256={result.metadata.sha256[:16]}..., pages={result.metadata.page_count}")
    
    # Verify blocks exist for grounding
    total_blocks = sum(len(p.blocks) for p in result.pages)
    assert total_blocks > 0, "No text blocks extracted"
    print(f"  [PASS] Physical extraction: {total_blocks} text blocks across {len(result.pages)} pages")
    
    print("\n  Result: All passed\n")
    return True


def test_two_pass_uses_native_pdf():
    """Test N: _extract_two_pass uses generate_structured_from_pdf not generate_structured."""
    print("=" * 60)
    print("TEST N: Two-pass extraction uses native PDF")
    print("=" * 60)
    
    import inspect
    from backend.extraction.requirement_extractor import TenderRequirementExtractor
    
    source = inspect.getsource(TenderRequirementExtractor._extract_two_pass)
    
    # Check that it calls generate_structured_from_pdf
    assert "generate_structured_from_pdf" in source, "_extract_two_pass does not call generate_structured_from_pdf"
    print("  [PASS] _extract_two_pass calls generate_structured_from_pdf")
    
    # Check that it does NOT loop per page
    assert "for page in extraction_result.pages" not in source, "_extract_two_pass still loops per page!"
    print("  [PASS] _extract_two_pass does NOT loop per page (sends whole PDF)")
    
    # Check it reads PDF bytes
    assert "_read_pdf_bytes" in source, "_extract_two_pass does not read PDF bytes"
    print("  [PASS] _extract_two_pass reads PDF bytes")
    
    # Check fact extractor too
    from backend.extraction.fact_extractor import LLMBidderFactExtractor
    fact_source = inspect.getsource(LLMBidderFactExtractor.extract_facts)
    assert "generate_structured_from_pdf" in fact_source, "extract_facts does not call generate_structured_from_pdf"
    print("  [PASS] Fact extractor calls generate_structured_from_pdf")
    
    assert "_read_pdf_bytes" in fact_source, "extract_facts does not read PDF bytes"
    print("  [PASS] Fact extractor reads PDF bytes")
    
    print("\n  Result: All passed\n")
    return True


def test_model_config():
    """Test O: Model configuration is sane."""
    print("=" * 60)
    print("TEST O: Model configuration")
    print("=" * 60)
    
    model = os.environ.get("GEMINI_MODEL", "unknown")
    fallback = os.environ.get("GEMINI_FALLBACK_MODEL", "unknown")
    api_key = os.environ.get("GEMINI_API_KEY", "")
    
    print(f"  Primary model: {model}")
    print(f"  Fallback model: {fallback}")
    print(f"  API key configured: {'Yes' if api_key else 'No'}")
    
    from backend.extraction.gemini_provider import GeminiProvider
    provider = GeminiProvider()
    print(f"  Provider model_name: {provider.model_name}")
    print(f"  Provider fallback_model: {provider.fallback_model}")
    print(f"  Provider timeout: {provider._timeout}s")
    
    assert provider._timeout >= 60, f"Timeout too low for native PDF: {provider._timeout}s"
    print(f"  [PASS] Timeout >= 60s for native PDF processing")
    
    print("\n  Result: Configuration reported\n")
    return True


# ======================== RUN ALL TESTS ========================

if __name__ == "__main__":
    tests = [
        test_imports,
        test_native_pdf_provider,
        test_mock_provider,
        test_data_models,
        test_prompts_no_text_blocks,
        test_cache_pdf_sha256,
        test_evidence_grounder,
        test_requirement_extractor_parse,
        test_fact_extractor_parse,
        test_orchestrator_construction,
        test_uuid_in_app,
        test_demo_files_exist,
        test_ingestion_pipeline,
        test_two_pass_uses_native_pdf,
        test_model_config,
    ]
    
    results = {}
    for test in tests:
        try:
            passed = test()
            results[test.__name__] = "PASS" if passed else "FAIL"
        except Exception as e:
            results[test.__name__] = f"ERROR: {e}"
            import traceback
            traceback.print_exc()
    
    print("\n" + "=" * 60)
    print("FINAL SUMMARY")
    print("=" * 60)
    
    total_pass = sum(1 for v in results.values() if v == "PASS")
    total_fail = sum(1 for v in results.values() if v != "PASS")
    
    for name, result in results.items():
        status = "PASS" if result == "PASS" else "FAIL"
        detail = "" if result == "PASS" else f" ({result})"
        print(f"  [{status}] {name}{detail}")
    
    print(f"\n  Total: {total_pass}/{len(results)} passed, {total_fail} failed")
    
    sys.exit(0 if total_fail == 0 else 1)
