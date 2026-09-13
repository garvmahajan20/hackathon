# -*- coding: utf-8 -*-
import unittest
from backend.core.models import (
    BidderFact,
    ComplianceStatus,
    OperatorType,
    Severity,
    TenderRequirement,
)
from backend.core.rule_engine import DeterministicRuleEngine
from backend.orchestration.aggregator import VerificationAggregator
from backend.orchestration.models import HumanReviewItem, ReviewCategory


class TestRequirementTypesAndReviewRouting(unittest.TestCase):
    """
    Validates:
    1. Requirement type preservation & serialization
    2. Non-bidder requirements (PROCESS_CONDITION, INFORMATIONAL, GENERAL_POLICY) evaluated as N_A without review flags
    3. Expanded canonical ontology matching for turnover, OEM turnover, past performance, local content, delivery
    4. Aggregator propagation of parent verification_id to all HumanReviewItem records
    5. Compliance status determination considering effective (non-N/A) compliance checks
    """

    def test_requirement_type_preservation(self):
        req1 = TenderRequirement(
            requirement_id="REQ-001",
            tender_id="TND-1",
            category="PROCESS",
            description="Bid opening date",
            operator="==",
            applicability={"requirement_type": "PROCESS_CONDITION"},
        )
        self.assertEqual(req1.requirement_type, "PROCESS_CONDITION")
        d = req1.to_dict()
        self.assertEqual(d["requirement_type"], "PROCESS_CONDITION")

        req1_restored = TenderRequirement.from_dict(d)
        self.assertEqual(req1_restored.requirement_type, "PROCESS_CONDITION")

    def test_non_bidder_requirements_evaluated_as_na(self):
        reqs = [
            TenderRequirement(
                requirement_id="REQ-001",
                tender_id="TND-1",
                category="PROCESS",
                description="Bid end date",
                operator="==",
                expected_value="2026-10-01",
                requirement_type="PROCESS_CONDITION",
            ),
            TenderRequirement(
                requirement_id="REQ-002",
                tender_id="TND-1",
                category="METADATA",
                description="Department name",
                operator="==",
                expected_value="Dept of Posts",
                requirement_type="INFORMATIONAL",
            ),
            TenderRequirement(
                requirement_id="REQ-003",
                tender_id="TND-1",
                category="POLICY",
                description="No physical documents allowed",
                operator="==",
                expected_value="No",
                requirement_type="GENERAL_POLICY",
            ),
            TenderRequirement(
                requirement_id="REQ-004",
                tender_id="TND-1",
                category="FINANCIAL_CAPACITY",
                description="Minimum turnover",
                operator=">=",
                field="bidder_minimum_average_annual_turnover",
                expected_value="100 Lakh (s)",
                requirement_type="BIDDER_COMPLIANCE",
            ),
        ]

        facts = [
            BidderFact(
                fact_id="FACT-001",
                bid_id="BID-1",
                field="bidder_average_annual_turnover",
                value="INR 420 lakh",
                source_document="bid.pdf",
                page=1,
            )
        ]

        engine = DeterministicRuleEngine()
        results = engine.verify_bid(reqs, facts)

        results_by_id = {r.requirement_id: r for r in results}
        self.assertEqual(results_by_id["REQ-001"].status, ComplianceStatus.N_A.value)
        self.assertFalse(results_by_id["REQ-001"].requires_human_review)

        self.assertEqual(results_by_id["REQ-002"].status, ComplianceStatus.N_A.value)
        self.assertFalse(results_by_id["REQ-002"].requires_human_review)

        self.assertEqual(results_by_id["REQ-003"].status, ComplianceStatus.N_A.value)
        self.assertFalse(results_by_id["REQ-003"].requires_human_review)

        # REQ-004 should pass through canonical alias matching
        self.assertEqual(results_by_id["REQ-004"].status, ComplianceStatus.PASS.value)

    def test_canonical_aliases_matching(self):
        reqs = [
            TenderRequirement(
                requirement_id="REQ-TURNOVER",
                tender_id="TND-1",
                category="FINANCIAL",
                description="Bidder Turnover",
                operator=">=",
                field="bidder_minimum_average_annual_turnover",
                expected_value="100 Lakh (s)",
                requirement_type="BIDDER_COMPLIANCE",
            ),
            TenderRequirement(
                requirement_id="REQ-OEM-TURNOVER",
                tender_id="TND-1",
                category="FINANCIAL",
                description="OEM Turnover",
                operator=">=",
                field="oem_average_turnover",
                expected_value="800 Lakh (s)",
                requirement_type="BIDDER_COMPLIANCE",
            ),
            TenderRequirement(
                requirement_id="REQ-PAST-PERF",
                tender_id="TND-1",
                category="EXPERIENCE",
                description="Past Performance",
                operator=">=",
                field="past_performance_threshold",
                expected_value="80% of bid quantity",
                requirement_type="BIDDER_COMPLIANCE",
            ),
            TenderRequirement(
                requirement_id="REQ-LOCAL-CONTENT",
                tender_id="TND-1",
                category="ELIGIBILITY",
                description="Local Content",
                operator=">=",
                field="class_1_local_content_threshold",
                expected_value="50%",
                requirement_type="BIDDER_COMPLIANCE",
            ),
            TenderRequirement(
                requirement_id="REQ-DELIVERY",
                tender_id="TND-1",
                category="OPERATIONAL",
                description="Delivery commitment",
                operator="==",
                field="consignee_delivery_schedule",
                expected_value="500 units in 45 days",
                requirement_type="BIDDER_COMPLIANCE",
            ),
        ]

        facts = [
            BidderFact(
                fact_id="F-1",
                bid_id="BID-1",
                field="bidder_average_annual_turnover",
                value="INR 420 lakh",
                source_document="bid.pdf",
                page=1,
            ),
            BidderFact(
                fact_id="F-2",
                bid_id="BID-1",
                field="oem_average_annual_turnover",
                value="INR 1,250 lakh",
                source_document="bid.pdf",
                page=1,
            ),
            BidderFact(
                fact_id="F-3",
                bid_id="BID-1",
                field="past_performance_percentage",
                value="90%",
                source_document="bid.pdf",
                page=1,
            ),
            BidderFact(
                fact_id="F-4",
                bid_id="BID-1",
                field="local_content_percentage",
                value="65%",
                source_document="bid.pdf",
                page=1,
            ),
            BidderFact(
                fact_id="F-5",
                bid_id="BID-1",
                field="delivery_days",
                value="45 days",
                source_document="bid.pdf",
                page=1,
            ),
        ]

        engine = DeterministicRuleEngine()
        results = engine.verify_bid(reqs, facts)
        for r in results:
            self.assertEqual(r.status, ComplianceStatus.PASS.value, f"Failed for {r.requirement_id}: {r.reason}")

    def test_aggregator_review_item_parent_verification_id(self):
        reqs = [
            TenderRequirement(
                requirement_id="REQ-MISSING",
                tender_id="TND-1",
                category="FINANCIAL",
                description="Missing document",
                operator="EXISTS",
                field="non_existent_doc",
                expected_value="document",
                mandatory=True,
                requirement_type="BIDDER_COMPLIANCE",
            )
        ]

        dummy_fact = BidderFact(
            fact_id="F-1",
            bid_id="BID-99",
            field="dummy_field",
            value="sample",
            source_document="bid.pdf",
            page=1,
        )
        engine = DeterministicRuleEngine()
        results = engine.verify_bid(reqs, [dummy_fact])

        agg = VerificationAggregator().aggregate(
            tender_id="TND-1",
            bid_id="BID-99",
            compliance_results=results,
            integrity_findings=[],
            government_responses=[],
            grounding_warnings=[],
            facts=[dummy_fact],
            tender_metadata={},
        )

        expected_dossier_id = "VERIF-TND-1-BID-99"
        self.assertEqual(agg.verification_id, expected_dossier_id)
        self.assertGreater(len(agg.human_review_items), 0)
        review_item = agg.human_review_items[0]
        self.assertEqual(review_item["verification_id"], expected_dossier_id)
        self.assertEqual(review_item["related_verification_id"], "VERIF-BID-99-REQ-MISSING")


if __name__ == "__main__":
    unittest.main()
