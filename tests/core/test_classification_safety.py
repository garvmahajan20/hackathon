import unittest
from backend.core.classification import classify_requirement_scope
from backend.core.models import TenderRequirement, BidderFact, ComplianceStatus, Severity
from backend.core.rule_engine import DeterministicRuleEngine


class TestClassificationSafety(unittest.TestCase):
    """
    Forensic Adversarial Regression Suite for Requirement Scope Classification.
    Tests boundary conditions and adversarial phrasing:
    1. Genuine bidder obligations containing policy/process keywords MUST remain BIDDER_COMPLIANCE.
    2. Administrative/process metadata containing misleading bidder words MUST remain non-bidder scope.
    3. End-to-end evaluation via DeterministicRuleEngine preserves compliance vs N/A demarcation.
    """

    def test_01_genuine_bidder_obligations_with_process_policy_keywords(self):
        """
        Adversarial test: Genuine bidder obligations containing phrases like
        'SLA conditions', 'breach of contract', 'pre-existing labour laws',
        'consignee delivery', 'prohibition on', 'arbitration clause'.
        Must ALL classify as BIDDER_COMPLIANCE.
        """
        cases = [
            {
                "desc": "Bidder must furnish an undertaking agreeing to the SLA conditions of 99.9% uptime",
                "field": "sla_undertaking",
                "op": "EXISTS",
            },
            {
                "desc": "Bidder must submit declaration confirming no breach of contract or debarment in past 3 years",
                "field": "non_breach_declaration",
                "op": "EXISTS",
            },
            {
                "desc": "Bidder must submit proof of consignee delivery for past executed contracts",
                "field": "consignee_delivery_proof",
                "op": "EXISTS",
            },
            {
                "desc": "Bidder must certify compliance with all applicable and pre-existing labour laws",
                "field": "labour_law_undertaking",
                "op": "EXISTS",
            },
            {
                "desc": "Bidder must declare there is no prohibition on bidding imposed by any government ministry",
                "field": "no_prohibition_declaration",
                "op": "EXISTS",
            },
            {
                "desc": "Bidder must provide undertaking for compliance with GeM GTC Clause 26 regarding land border restrictions",
                "field": "land_border_undertaking",
                "op": "EXISTS",
            },
            {
                "desc": "Bidder shall submit an undertaking agreeing to the arbitration clause and dispute resolution mechanism",
                "field": "arbitration_undertaking",
                "op": "EXISTS",
            },
            {
                "desc": "Bidder must upload copy of valid MSE Udyam certificate for claiming MSE relaxation",
                "field": "mse_udyam_proof",
                "op": "EXISTS",
            },
            {
                "desc": "Supporting documents for exemption from Experience / Turnover Criteria must be uploaded",
                "field": "exemption_supporting_documents",
                "op": "EXISTS",
            },
        ]

        for case in cases:
            res = classify_requirement_scope(
                description=case["desc"],
                field=case["field"],
                mandatory=True,
                operator=case["op"],
            )
            self.assertEqual(
                res,
                "BIDDER_COMPLIANCE",
                f"Adversarial case falsely classified as non-bidder: {case['desc']} -> {res}",
            )

    def test_02_administrative_metadata_with_misleading_bidder_words(self):
        """
        Adversarial test: Administrative metadata and portal mechanics that contain
        misleading words like 'bidder', 'seller', 'quote'.
        Must ALL classify as PROCESS_CONDITION, INFORMATIONAL, or GENERAL_POLICY.
        """
        cases = [
            (
                "Bidder Clarification Window: Closes 5 days prior to Bid End Date",
                "bidder_clarification_window",
                "PROCESS_CONDITION",
            ),
            (
                "Bidder Auto-Extension: GeM portal shall automatically extend bid if fewer than 3 bids received",
                "auto_extension_rule",
                "PROCESS_CONDITION",
            ),
            (
                "Ministry / Department for Bidder Inquiries and Grievance Redressal: Parcel Directorate",
                "ministry_grievance_cell",
                "INFORMATIONAL",
            ),
            (
                "Estimated Bid Value for Bidder Information: INR 2.50 Crores",
                "estimated_bid_value",
                "INFORMATIONAL",
            ),
            (
                "Two Packet Bid System for Bidders: Technical and Financial Packets",
                "two_packet_system",
                "PROCESS_CONDITION",
            ),
            (
                "Bid Opening Date for Bidder Submissions: 16-09-2026 18:30:00",
                "bid_opening_date",
                "PROCESS_CONDITION",
            ),
            (
                "Bid Offer Validity for Seller Quotes: 180 Days",
                "bid_validity_days",
                "PROCESS_CONDITION",
            ),
            (
                "General Policy on Traders: Traders and resellers are excluded from MSE preferences",
                "trader_exclusion_policy",
                "GENERAL_POLICY",
            ),
            (
                "Arbitration Jurisdiction for Disputing Bidders: High Court of Delhi",
                "arbitration_jurisdiction",
                "GENERAL_POLICY",
            ),
        ]

        for desc, field, expected_type in cases:
            res = classify_requirement_scope(
                description=desc,
                field=field,
                mandatory=False,
                operator="==",
                expected_value=None,
            )
            self.assertEqual(
                res,
                expected_type,
                f"Administrative case failed classification: {desc} -> got {res}, expected {expected_type}",
            )

    def test_03_rule_engine_adversarial_integration(self):
        """
        Verifies that DeterministicRuleEngine respects the classification safety boundary:
        - Real obligation with 'breach of contract' evaluates to PASS when evidence provided.
        - Process condition with 'bidder' in title evaluates to N/A without review escalation.
        """
        engine = DeterministicRuleEngine()

        # Real bidder obligation with tricky wording
        req_obligation = TenderRequirement(
            requirement_id="REQ-ADV-001",
            tender_id="TENDER-ADV",
            description="Bidder must submit solemn declaration confirming no breach of contract has occurred",
            category="LEGAL_TERMS",
            field="non_breach_declaration",
            operator="EXISTS",
            expected_value="Solemn declaration of no breach",
            mandatory=True,
        )

        # Administrative process condition with tricky wording
        req_process = TenderRequirement(
            requirement_id="REQ-ADV-002",
            tender_id="TENDER-ADV",
            description="Bidder Clarification Window closes 5 days prior to Bid End Date",
            category="PORTAL_MECHANICS",
            field="bidder_clarification_window",
            operator="==",
            expected_value="5 Days",
            mandatory=False,
        )

        fact_affirmative = BidderFact(
            fact_id="FACT-ADV-001",
            bid_id="BID-ADV",
            field="non_breach_declaration",
            value="Affirmative declaration confirming no breach of contract or debarment",
            source_document="bidder_annexure.pdf",
            page=2,
            raw_text_snippet="Apex Computers certifies that no breach of contract has occurred.",
        )

        results = engine.verify_bid(
            requirements=[req_obligation, req_process],
            facts=[fact_affirmative],
        )

        self.assertEqual(len(results), 2)
        res_map = {r.requirement_id: r for r in results}

        # Obligation must PASS
        self.assertEqual(res_map["REQ-ADV-001"].status, ComplianceStatus.PASS.value)
        self.assertEqual(res_map["REQ-ADV-001"].requirement_type, "BIDDER_COMPLIANCE")
        self.assertFalse(res_map["REQ-ADV-001"].requires_human_review)

        # Process condition must be N/A
        self.assertEqual(res_map["REQ-ADV-002"].status, ComplianceStatus.N_A.value)
        self.assertEqual(res_map["REQ-ADV-002"].requirement_type, "PROCESS_CONDITION")
        self.assertEqual(res_map["REQ-ADV-002"].severity, Severity.INFO.value)
        self.assertFalse(res_map["REQ-ADV-002"].requires_human_review)


if __name__ == "__main__":
    unittest.main()
