# -*- coding: utf-8 -*-
"""
Generator script for the three J.A.R.V.I.S final demo bidder packets:
1. JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf
2. JARVIS_DEMO_FAIL_BIDDER_GEM_2026_B_7959150.pdf
3. JARVIS_DEMO_FORENSIC_BIDDER_GEM_2026_B_7959150.pdf

All three are strictly tailored against the real-world Department of Posts tender:
GEM/2026/B/7959150 (data/external/blind_test/REAL_WORLD_HOLDOUT_03.pdf)
"""

import os
import fitz  # PyMuPDF

DISCLAIMER_TEXT = (
    "SYNTHETIC CONTROLLED DEMONSTRATION BIDDER DOCUMENT\n"
    "This document is not a real procurement submission and is used only to demonstrate "
    "J.A.R.V.I.S extraction, compliance and forensic analysis."
)

def add_header_footer(page, page_num, total_pages, title, company_name):
    rect = page.rect
    # Top Disclaimer Box (Amber / Light Grey background)
    disclaimer_rect = fitz.Rect(36, 20, rect.width - 36, 52)
    page.draw_rect(disclaimer_rect, color=(0.7, 0.4, 0.1), fill=(0.98, 0.96, 0.90), width=0.8)
    page.insert_textbox(
        disclaimer_rect + fitz.Rect(5, 3, -5, -3),
        DISCLAIMER_TEXT,
        fontsize=7,
        fontname="helv",
        align=fitz.TEXT_ALIGN_CENTER,
        color=(0.5, 0.2, 0.0)
    )

    # Document Header Title
    page.insert_text((36, 70), company_name.upper(), fontsize=12, fontname="helv", color=(0.1, 0.2, 0.4))
    page.insert_text((36, 84), title, fontsize=9, fontname="helv", color=(0.3, 0.3, 0.3))
    page.draw_line(fitz.Point(36, 90), fitz.Point(rect.width - 36, 90), color=(0.7, 0.7, 0.7), width=0.8)

    # Footer
    page.draw_line(fitz.Point(36, rect.height - 35), fitz.Point(rect.width - 36, rect.height - 35), color=(0.7, 0.7, 0.7), width=0.8)
    footer_text = f"Tender Ref: GEM/2026/B/7959150 | Document: {company_name} | Page {page_num} of {total_pages}"
    page.insert_text((36, rect.height - 22), footer_text, fontsize=7.5, fontname="helv", color=(0.4, 0.4, 0.4))


def draw_section_box(page, rect, title, text_lines, fill_color=(0.98, 0.98, 0.99), border_color=(0.2, 0.3, 0.5)):
    # Draw border
    page.draw_rect(rect, color=border_color, fill=fill_color, width=0.8)
    # Header bar
    header_rect = fitz.Rect(rect.x0, rect.y0, rect.x1, rect.y0 + 20)
    page.draw_rect(header_rect, color=border_color, fill=border_color, width=0.8)
    page.insert_text((header_rect.x0 + 8, header_rect.y0 + 14), title.upper(), fontsize=9, fontname="helv", color=(1, 1, 1))

    # Content
    y = rect.y0 + 34
    for line in text_lines:
        page.insert_text((rect.x0 + 10, y), line, fontsize=8.5, fontname="helv", color=(0.1, 0.1, 0.1))
        y += 14


def build_pass_bidder(output_path):
    doc = fitz.open()
    total_pages = 4
    company = "Apex Secure Systems Private Limited"

    # --- PAGE 1: Bidder Profile, Regulatory Credentials & BoQ Compliance ---
    p1 = doc.new_page(width=595, height=842)
    add_header_footer(p1, 1, total_pages, "TECHNICAL & COMMERCIAL BID SUBMISSION (ANNEXURE-A)", company)

    # Section 1: Corporate & Statutory Profile
    draw_section_box(
        p1,
        fitz.Rect(36, 105, 559, 215),
        "1. Bidder Corporate Identity & Statutory Registrations",
        [
            "Company Legal Name: Apex Secure Systems Private Limited",
            "Corporate Identity Number (CIN): U72900DL2019PTC345678",
            "Permanent Account Number (PAN): AAPCA5678K",
            "Goods & Services Tax Identification Number (GSTIN): 07AAPCA5678K1Z3",
            "MSME / Udyam Registration Number: UDYAM-DL-01-0087654",
            "Enterprise Category: Micro & Small Enterprise (MSE) - Manufacturing Category",
            "Registered Address: Plot 42, Okhla Industrial Area Phase-III, New Delhi 110020",
        ],
        border_color=(0.15, 0.35, 0.55)
    )

    # Section 2: Statutory Policy Undertakings (Land Border & Make in India)
    draw_section_box(
        p1,
        fitz.Rect(36, 230, 559, 360),
        "2. Mandatory Statutory Compliance Declarations",
        [
            "Land Border Sharing Rule 144(xi) Declaration:",
            "We hereby solemnly declare and certify under Rule 144(xi) of General Financial Rules (GFR) 2017",
            "and GeM GTC Clause 26 that Apex Secure Systems Private Limited is NOT from a country sharing a land",
            "border with India. Land Border Rule Compliance: Fully Compliant.",
            "",
            "Make in India (MII) Local Content Declaration:",
            "We certify that the offered Mobile Handheld Rugged Devices have 65.0% Local Value Addition.",
            "Local Content Percentage: 65% (Qualifying as Class-I Local Supplier against 50% tender requirement).",
            "Manufacturing Location: S-14, Electronic City, Sector 63, Noida, Uttar Pradesh 201301.",
        ],
        border_color=(0.15, 0.35, 0.55)
    )

    # Section 3: Delivery Terms & BoQ Specification Compliance
    draw_section_box(
        p1,
        fitz.Rect(36, 375, 559, 525),
        "3. Scope of Supply, Delivery Schedule & Technical Compliance",
        [
            "Tender Reference: GEM/2026/B/7959150 (Department of Posts / Parcel Directorate)",
            "Product Offered: RuggedHandheld Pro-X500 Enterprise Mobile Terminal",
            "Offered Quantity: 500 Units (100% of bid requirement)",
            "Delivery Period: 45 Days from contract award (Requirement: within 60 Days -> SATISFIED)",
            "Consignee Location: Parcel Directorate, Malcha Marg Post Office Complex, Chanakyapuri, New Delhi-110021",
            "BoQ Specification Compliance:",
            "1. Operating System: Android 11 with Google GMS Enterprise Certification",
            "2. Barcode Engine: Integrated Ultra-Fast Zebra 2D Imager Barcode Scanner",
            "3. Rugged Ingress Protection: IP67 Certified (water-proof, dust-tight, 1.5m drop resistant)",
            "4. Memory & Processor: 4GB LPDDR4 RAM, 64GB Flash Storage, Octa-core 2.0 GHz Processor",
            "Technical Specification Compliance: 100% Compliant with Buyer Specification.",
        ],
        border_color=(0.15, 0.35, 0.55)
    )

    # Section 4: Authorized Signatory
    draw_section_box(
        p1,
        fitz.Rect(36, 540, 559, 630),
        "4. Authorized Signatory Seal",
        [
            "For Apex Secure Systems Private Limited",
            "Name: Vikramaditya Malhotra | Designation: Managing Director & CEO",
            "Date: 04-09-2026 | Place: New Delhi",
            "Digitally Signed and Sealed under Corporate Authority.",
        ],
        border_color=(0.15, 0.35, 0.55)
    )

    # --- PAGE 2: Audited Financial Statements & CA Turnover Certificate ---
    p2 = doc.new_page(width=595, height=842)
    add_header_footer(p2, 2, total_pages, "AUDITED FINANCIAL TURNOVER CERTIFICATE (ANNEXURE-B)", company)

    draw_section_box(
        p2,
        fitz.Rect(36, 105, 559, 210),
        "1. Chartered Accountant Certificate - Bidder Turnover",
        [
            "Issuing Audit Firm: R. K. Sharma & Associates, Chartered Accountants (ICAI Reg No: 012345N)",
            "UDIN: 26012345ABCDEF1234 | Date of Certification: 28-08-2026",
            "This is to certify that we have examined the audited financial records of M/s Apex Secure Systems Private",
            "Limited for the preceding three financial years. The annual financial turnovers are certified as follows:",
            "  * Financial Year 2022-23: INR 125.00 Lakhs",
            "  * Financial Year 2023-24: INR 145.00 Lakhs",
            "  * Financial Year 2024-25: INR 165.00 Lakhs",
            "Bidder Average Annual Turnover: INR 145.00 Lakhs",
            "Tender Requirement: Minimum INR 100 Lakhs (1 Crore) -> CRITERION EXCEEDED & SATISFIED (PASS)",
        ],
        border_color=(0.15, 0.35, 0.55)
    )

    draw_section_box(
        p2,
        fitz.Rect(36, 225, 559, 335),
        "2. Chartered Accountant Certificate - OEM Annual Turnover",
        [
            "Original Equipment Manufacturer (OEM): RuggedDevice Technologies India Pvt Ltd",
            "Issuing Audit Firm: S. N. Mehra & Co, Chartered Accountants (ICAI Reg No: 009876N)",
            "UDIN: 26009876XYZW9876 | Date of Certification: 20-08-2026",
            "Certified Financial Turnovers of the OEM during the preceding three financial years:",
            "  * Financial Year 2022-23: INR 920.00 Lakhs",
            "  * Financial Year 2023-24: INR 1,050.00 Lakhs",
            "  * Financial Year 2024-25: INR 1,180.00 Lakhs",
            "OEM Average Annual Turnover: INR 1,050.00 Lakhs",
            "Tender Requirement: Minimum INR 800 Lakhs (8 Crores) -> CRITERION EXCEEDED & SATISFIED (PASS)",
        ],
        border_color=(0.15, 0.35, 0.55)
    )

    draw_section_box(
        p2,
        fitz.Rect(36, 350, 559, 440),
        "3. Net Worth & Solvency Affirmation",
        [
            "Audited Net Worth as on March 31, 2025: Positive (+ INR 285.50 Lakhs)",
            "Solvency Status: The company possesses sound financial health, positive liquidity, and has never",
            "defaulted on any commercial, banking, or government procurement commitment.",
        ],
        border_color=(0.15, 0.35, 0.55)
    )

    # --- PAGE 3: Past Experience & Past Performance Statement ---
    p3 = doc.new_page(width=595, height=842)
    add_header_footer(p3, 3, total_pages, "PAST EXPERIENCE & PERFORMANCE CREDENTIALS (ANNEXURE-C)", company)

    draw_section_box(
        p3,
        fitz.Rect(36, 105, 559, 215),
        "1. Relevant Commercial Experience Criteria",
        [
            "Criterion: Supply of same or similar category products to Central/State Govt/PSU for >= 3 Years",
            "Years of Relevant Experience Claimed: 4.5 Years in rugged enterprise mobile terminals.",
            "Historical Execution Timeline:",
            "  * FY 2021-22: Supply of 200 Handheld Terminals to Delhi State Civil Supplies Corporation",
            "  * FY 2022-23: Supply of 350 Rugged Mobile Devices to Bharat Heavy Electricals Limited (BHEL)",
            "  * FY 2023-24: Supply of 450 Rugged Terminals to Northern Railway Logistics Hub",
            "  * FY 2024-25: Supply of 300 Mobile Handheld POS Terminals to Container Corporation of India (CONCOR)",
            "Years of Past Experience: 4.5 Years (Tender Requirement: >= 3 Years -> SATISFIED / PASS)",
        ],
        border_color=(0.15, 0.35, 0.55)
    )

    draw_section_box(
        p3,
        fitz.Rect(36, 230, 559, 360),
        "2. Past Performance Order Execution (80% Benchmark)",
        [
            "Tender Requirement: Supply of same or similar products for >= 80% of bid quantity in a single order",
            "(80% of 500 Units = 400 Units minimum required in a single order).",
            "Qualifying Contract Reference: Northern Railway Purchase Order No. NR/S&T/2024/MDT-450",
            "Client Organization: Northern Railway, Ministry of Railways, Government of India",
            "Contract Date: 12-04-2024 | Order Value: INR 1,80,00,000",
            "Contracted Quantity: 450 Units of Handheld Mobile Rugged Terminals",
            "Execution & Delivery Status: 450 Units fully delivered and accepted on 15-01-2025.",
            "Past Performance Quantity: 450 Units (90% of current bid quantity -> SATISFIED / PASS)",
            "Client CRAC / Work Completion Certificate Ref: NR-CRAC-2025-089 attached.",
        ],
        border_color=(0.15, 0.35, 0.55)
    )

    # --- PAGE 4: EMD Exemption, ePBG Commitment & OEM Authorization ---
    p4 = doc.new_page(width=595, height=842)
    add_header_footer(p4, 4, total_pages, "SECURITY DEPOSIT, PBG & OEM AUTHORIZATION (ANNEXURE-D)", company)

    draw_section_box(
        p4,
        fitz.Rect(36, 105, 559, 215),
        "1. Earnest Money Deposit (EMD) Exemption",
        [
            "Tender EMD Requirement: INR 6,00,000 (Six Lakhs)",
            "EMD Exemption Claim: Yes, claiming full exemption under GeM GTC Micro & Small Enterprise Policy.",
            "Attached Statutory Certificate: Valid UDYAM Registration Certificate UDYAM-DL-01-0087654",
            "Enterprise Category: Micro and Small Enterprise (MSE) - Manufacturer of Telecommunication Devices.",
            "Under GeM GTC and Public Procurement Policy for MSEs Order 2012, bidder is entitled to 100% EMD exemption.",
            "Earnest Money Deposit (EMD) Status: EXEMPTED (Valid MSE Manufacturer UDYAM Verified).",
        ],
        border_color=(0.15, 0.35, 0.55)
    )

    draw_section_box(
        p4,
        fitz.Rect(36, 230, 559, 320),
        "2. Performance Security (ePBG) Undertaking",
        [
            "Tender ePBG Requirement: 3.00% of total contract value for 36 months duration.",
            "Commitment: We unequivocally undertake to furnish an Electronic Performance Bank Guarantee (ePBG)",
            "of exactly 3.00% of the total awarded contract value from State Bank of India valid for 36 months",
            "within 15 days of contract award as stipulated by the Department of Posts.",
            "ePBG Commitment: 100% Compliant.",
        ],
        border_color=(0.15, 0.35, 0.55)
    )

    draw_section_box(
        p4,
        fitz.Rect(36, 335, 559, 455),
        "3. Manufacturer Authorization Form (MAF)",
        [
            "OEM Name: RuggedDevice Technologies India Pvt Ltd (Reg No: 08876543)",
            "MAF Reference: RDT-MAF-2026-DEL-089 | Date: 18-08-2026",
            "We, RuggedDevice Technologies India Pvt Ltd, who are official manufacturers of Mobile Handheld Rugged",
            "Devices having factory at Sector 63 Noida, do hereby authorize M/s Apex Secure Systems Private Limited",
            "to submit bid against GeM Bid No. GEM/2026/B/7959150 for supply of 500 units of our RuggedHandheld Pro-X500.",
            "We further guarantee comprehensive 3-Year Onsite OEM Warranty and spare parts support for the full life cycle.",
            "OEM Authorization: Valid and Verified Manufacturer Authorization Form (MAF).",
        ],
        border_color=(0.15, 0.35, 0.55)
    )

    doc.save(output_path)
    doc.close()
    print(f"Generated PASS Bidder: {output_path} ({total_pages} pages)")


def build_fail_bidder(output_path):
    doc = fitz.open()
    total_pages = 3
    company = "Vanguard Retail & Trade Solutions Private Limited"

    # --- PAGE 1: Corporate Profile & Submissions ---
    p1 = doc.new_page(width=595, height=842)
    add_header_footer(p1, 1, total_pages, "TECHNICAL & COMMERCIAL BID SUBMISSION (ANNEXURE-A)", company)

    draw_section_box(
        p1,
        fitz.Rect(36, 105, 559, 215),
        "1. Bidder Corporate Identity & Registrations",
        [
            "Company Legal Name: Vanguard Retail & Trade Solutions Private Limited",
            "Corporate Identity Number (CIN): U51909DL2023PTC412345",
            "Permanent Account Number (PAN): BBPVR1234B",
            "Goods & Services Tax Identification Number (GSTIN): 07BBPVR1234B1Z8",
            "MSME Registration Number: UDYAM-DL-01-0099999",
            "Enterprise Category: Micro Enterprise - RETAIL & WHOLESALE TRADING ONLY",
            "Registered Address: Shop 14, Commercial Complex, Karol Bagh, New Delhi 110005",
        ],
        border_color=(0.6, 0.15, 0.15)
    )

    draw_section_box(
        p1,
        fitz.Rect(36, 230, 559, 360),
        "2. Commercial Experience Shortfall",
        [
            "Experience in supplying Mobile Handheld Rugged Devices:",
            "The bidder was incorporated on 12-10-2023 and has been active in consumer mobile retail.",
            "Years of Relevant Experience: 1.5 Years total commercial operation.",
            "Tender Requirement: Minimum 3 Years in similar category products.",
            "Shortfall Notice: Bidder possesses only 1.5 Years of experience (< 3 Years required -> DETERMINISTIC FAIL).",
            "",
            "Make in India Local Content: 18.0% Local Value Addition (Requirement: Class-1 >= 50% -> NON-COMPLIANT).",
        ],
        border_color=(0.6, 0.15, 0.15)
    )

    draw_section_box(
        p1,
        fitz.Rect(36, 375, 559, 490),
        "3. Deficient Past Performance Execution",
        [
            "Tender Requirement: Supply of >= 80% of bid quantity (400 Units) in a single order to Govt/PSU.",
            "Single Largest Order Executed: Supply of 120 Units of entry-level barcode scanners to a private warehouse.",
            "Past Performance Quantity: 120 Units (Only 24% of current bid quantity).",
            "Shortfall Notice: 120 Units executed vs 400 Units required (< 80% required -> DETERMINISTIC FAIL).",
        ],
        border_color=(0.6, 0.15, 0.15)
    )

    # --- PAGE 2: Financial Turnover Deficit ---
    p2 = doc.new_page(width=595, height=842)
    add_header_footer(p2, 2, total_pages, "FINANCIAL STATEMENTS & CA CERTIFICATE (ANNEXURE-B)", company)

    draw_section_box(
        p2,
        fitz.Rect(36, 105, 559, 235),
        "1. Chartered Accountant Turnover Certificate (Deficient Turnover)",
        [
            "Issuing Audit Firm: Goyal & Goyal Associates, Chartered Accountants (ICAI Reg No: 023456N)",
            "UDIN: 26023456FAIL1234 | Date of Certification: 25-08-2026",
            "Certified annual financial turnover of Vanguard Retail & Trade Solutions Private Limited:",
            "  * Financial Year 2022-23: INR 35.00 Lakhs",
            "  * Financial Year 2023-24: INR 42.00 Lakhs",
            "  * Financial Year 2024-25: INR 48.00 Lakhs",
            "Bidder Average Annual Turnover: INR 41.67 Lakhs",
            "Tender Requirement: Minimum INR 100 Lakhs (1 Crore)",
            "Deficit Notice: Certified turnover of INR 41.67 Lakhs is far below INR 100 Lakhs -> DETERMINISTIC FAIL.",
        ],
        border_color=(0.6, 0.15, 0.15)
    )

    draw_section_box(
        p2,
        fitz.Rect(36, 250, 559, 360),
        "2. OEM Annual Turnover Deficit",
        [
            "Offered OEM: BasicScan Tech Ltd",
            "OEM Average Annual Turnover: INR 350.00 Lakhs (3.5 Crores)",
            "Tender Requirement: Minimum INR 800 Lakhs (8 Crores)",
            "Deficit Notice: OEM turnover of INR 350 Lakhs is below INR 800 Lakhs -> DETERMINISTIC FAIL.",
        ],
        border_color=(0.6, 0.15, 0.15)
    )

    # --- PAGE 3: Ineligible EMD Claim ---
    p3 = doc.new_page(width=595, height=842)
    add_header_footer(p3, 3, total_pages, "EMD SUBMISSION & STATUTORY DEFICIENCIES (ANNEXURE-C)", company)

    draw_section_box(
        p3,
        fitz.Rect(36, 105, 559, 245),
        "1. Ineligible EMD Exemption Claim (Trading Enterprise)",
        [
            "Tender EMD Requirement: INR 6,00,000 (Six Lakhs)",
            "Bidder Claim: Claiming EMD Exemption using UDYAM Certificate UDYAM-DL-01-0099999.",
            "Ineligibility Disqualification Notice:",
            "Under GeM GTC Page 3 Clause (a): 'Under MSE category, only manufacturers for goods and service",
            "providers for services are eligible for exemption from EMD. Traders are excluded from the purview",
            "of this Policy.'",
            "Vanguard Retail & Trade Solutions Private Limited is registered solely as a TRADING firm.",
            "No EMD payment challan, Bank Guarantee, or Surety Bond is enclosed.",
            "EMD Compliance Status: INVALID EXEMPTION / ZERO DEPOSIT SUBMITTED -> DETERMINISTIC FAIL.",
        ],
        border_color=(0.6, 0.15, 0.15)
    )

    doc.save(output_path)
    doc.close()
    print(f"Generated FAIL Bidder: {output_path} ({total_pages} pages)")


def build_forensic_bidder(output_path):
    doc = fitz.open()
    total_pages = 4
    company = "CyberLogix Automation Private Limited"

    # --- PAGE 1: Formal Bid Submission Declaration (Contains Claim A) ---
    p1 = doc.new_page(width=595, height=842)
    add_header_footer(p1, 1, total_pages, "FORMAL BID SUBMISSION DECLARATION (ANNEXURE-A)", company)

    draw_section_box(
        p1,
        fitz.Rect(36, 105, 559, 215),
        "1. Corporate Identity & Registration",
        [
            "Company Legal Name: CyberLogix Automation Private Limited",
            "Corporate Identity Number (CIN): U74999DL2020PTC367890",
            "Permanent Account Number (PAN): CCCC9999C",
            "Goods & Services Tax Identification Number (GSTIN): 07CCCC9999C1Z9",
            "MSME / Udyam Number: UDYAM-DL-01-0055443 (MSE Manufacturer)",
            "Registered Office: Cyber House, 12 Barakhamba Road, Connaught Place, New Delhi 110001",
        ],
        border_color=(0.5, 0.2, 0.6)
    )

    draw_section_box(
        p1,
        fitz.Rect(36, 230, 559, 365),
        "2. Solemn Declaration of Financial Standing (CONTRADICTION CLAIM-A)",
        [
            "Declaration under Tender Ref: GEM/2026/B/7959150:",
            "We hereby solemnly affirm, declare, and state that the Minimum Average Annual Turnover of the bidder",
            "for the preceding three financial years (FY 2022-23, FY 2023-24, FY 2024-25) is:",
            "Bidder Average Annual Turnover: INR 145.00 Lakhs",
            "The bidder confirms that its turnover comfortably exceeds the mandatory threshold of INR 100 Lakhs.",
            "",
            "Land Border Sharing Rule 144(xi): Certified Compliant (Not from land border sharing country).",
            "Make in India (MII) Local Content: 62% Local Content Certified (Class-I Supplier).",
            "Delivery Commitment: 45 Days to Parcel Directorate, New Delhi.",
        ],
        border_color=(0.5, 0.2, 0.6)
    )

    draw_section_box(
        p1,
        fitz.Rect(36, 380, 559, 480),
        "3. Undertaking on Authenticity of Records",
        [
            "The undersigned confirms that all statements, financial declarations, and contract quantities",
            "contained in this dossier are true, correct, and un-tampered.",
            "Authorized Signatory: Rajiv Nambiar, Director | Date: 02-09-2026",
        ],
        border_color=(0.5, 0.2, 0.6)
    )

    # --- PAGE 2: Financial Schedule / CA Certificate (Contains Conflicting Fact B) ---
    p2 = doc.new_page(width=595, height=842)
    add_header_footer(p2, 2, total_pages, "CHARTERED ACCOUNTANT CERTIFICATE (ANNEXURE-B)", company)

    draw_section_box(
        p2,
        fitz.Rect(36, 105, 559, 255),
        "1. Audited Financial Statements & Turnover Breakdown (CONTRADICTION FACT-B)",
        [
            "Issuing Audit Firm: M. K. Aggarwal & Co., Chartered Accountants (ICAI Reg No: 014567N)",
            "UDIN: 26014567FORENSIC99 | Date of Certification: 29-08-2026",
            "We have audited the books of accounts of M/s CyberLogix Automation Private Limited.",
            "The authentic audited financial turnovers extracted from official ledger accounts are:",
            "  * Financial Year 2022-23: INR 35.00 Lakhs",
            "  * Financial Year 2023-24: INR 42.00 Lakhs",
            "  * Financial Year 2024-25: INR 48.00 Lakhs",
            "Actual Audited Average Annual Turnover: INR 41.67 Lakhs",
            "",
            "[FORENSIC NOTE]: This audited value of INR 41.67 Lakhs directly contradicts the claim on Page 1",
            "where Bidder Average Annual Turnover was declared as INR 145.00 Lakhs.",
        ],
        border_color=(0.5, 0.2, 0.6)
    )

    draw_section_box(
        p2,
        fitz.Rect(36, 270, 559, 380),
        "2. OEM Financial Standing",
        [
            "OEM Name: RuggedDevice Technologies India Pvt Ltd",
            "OEM Average Annual Turnover: INR 1,050.00 Lakhs (Audited and Verified).",
            "Tender Requirement: Minimum INR 800 Lakhs (SATISFIED).",
        ],
        border_color=(0.5, 0.2, 0.6)
    )

    # --- PAGE 3: Past Performance Contract Claim (Contains Claim C) ---
    p3 = doc.new_page(width=595, height=842)
    add_header_footer(p3, 3, total_pages, "PAST PERFORMANCE CONTRACT DETAILS (ANNEXURE-C)", company)

    draw_section_box(
        p3,
        fitz.Rect(36, 105, 559, 245),
        "1. Major Qualifying Contract Claim (CONTRADICTION CLAIM-C)",
        [
            "Qualifying Past Contract Ref: Northern Railway Contract No. NR/S&T/2024/MDT-450",
            "Client: Northern Railway, Ministry of Railways, Government of India",
            "Awarded Contract Quantity: 450 Units of Handheld Mobile Rugged Terminals",
            "Contract Claim Summary:",
            "The bidder asserts in this statement that it successfully manufactured, supplied, and delivered",
            "Past Performance Quantity: 450 Units of handheld rugged terminals to Northern Railway.",
            "Tender Requirement: >= 80% of bid quantity (400 Units) -> Claimed as SATISFIED.",
        ],
        border_color=(0.5, 0.2, 0.6)
    )

    draw_section_box(
        p3,
        fitz.Rect(36, 260, 559, 360),
        "2. General Experience",
        [
            "Years of Relevant Experience: 4.0 Years in industrial rugged automation.",
            "Tender Requirement: Minimum 3 Years -> SATISFIED.",
        ],
        border_color=(0.5, 0.2, 0.6)
    )

    # --- PAGE 4: Client Completion Certificate (Contains Conflicting Fact D) ---
    p4 = doc.new_page(width=595, height=842)
    add_header_footer(p4, 4, total_pages, "CLIENT WORK COMPLETION CERTIFICATE (ANNEXURE-D)", company)

    draw_section_box(
        p4,
        fitz.Rect(36, 105, 559, 255),
        "1. Northern Railway Work Completion Certificate (CONTRADICTION FACT-D)",
        [
            "Issuing Authority: Office of Senior Divisional Signal & Telecomm Engineer (Sr DSTE), Northern Railway",
            "Certificate No: NR/DSTE/COMPLETION/2025/112 | Dated: 10-02-2025",
            "TO WHOMSOEVER IT MAY CONCERN:",
            "This is to certify that M/s CyberLogix Automation Private Limited was awarded contract",
            "NR/S&T/2024/MDT-450 for supply of 450 units. However, due to severe supply chain delays, the vendor",
            "completed delivery of only 120 Units. The remaining order was cancelled on mutual grounds.",
            "Actual Delivered and Completed Quantity: 120 Units",
            "",
            "[FORENSIC NOTE]: This certified quantity of 120 Units directly contradicts the claim on Page 3",
            "where Past Performance Quantity was asserted as 450 Units.",
        ],
        border_color=(0.5, 0.2, 0.6)
    )

    draw_section_box(
        p4,
        fitz.Rect(36, 270, 559, 375),
        "2. EMD Exemption Enclosure",
        [
            "UDYAM Certificate UDYAM-DL-01-0055443 (MSE Manufacturer).",
            "Earnest Money Deposit (EMD): Claimed Exempted under GeM GTC Policy.",
        ],
        border_color=(0.5, 0.2, 0.6)
    )

    doc.save(output_path)
    doc.close()
    print(f"Generated FORENSIC Bidder: {output_path} ({total_pages} pages)")


if __name__ == "__main__":
    out_dir = "data/demo"
    os.makedirs(out_dir, exist_ok=True)
    pass_pdf = os.path.join(out_dir, "JARVIS_DEMO_PASS_BIDDER_GEM_2026_B_7959150.pdf")
    fail_pdf = os.path.join(out_dir, "JARVIS_DEMO_FAIL_BIDDER_GEM_2026_B_7959150.pdf")
    forensic_pdf = os.path.join(out_dir, "JARVIS_DEMO_FORENSIC_BIDDER_GEM_2026_B_7959150.pdf")

    build_pass_bidder(pass_pdf)
    build_fail_bidder(fail_pdf)
    build_forensic_bidder(forensic_pdf)
