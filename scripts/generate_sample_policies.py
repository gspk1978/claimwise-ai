"""
generate_sample_policies.py
----------------------------
One-off utility script to generate two demo insurance policy PDFs
(auto + homeowners) with realistic section structure, so the app has
ready-to-use sample data for testing/demo purposes.

Run with: python scripts/generate_sample_policies.py
"""

from pathlib import Path

from reportlab.lib.pagesizes import letter
from reportlab.lib.styles import ParagraphStyle, getSampleStyleSheet
from reportlab.lib.units import inch
from reportlab.platypus import PageBreak, Paragraph, SimpleDocTemplate, Spacer

OUT_DIR = Path(__file__).resolve().parent.parent / "data" / "sample_policies"
OUT_DIR.mkdir(parents=True, exist_ok=True)

styles = getSampleStyleSheet()
title_style = ParagraphStyle("PolicyTitle", parent=styles["Title"], fontSize=18, spaceAfter=18)
h1_style = ParagraphStyle("H1", parent=styles["Heading1"], fontSize=13, spaceBefore=14, spaceAfter=6)
body_style = ParagraphStyle("Body", parent=styles["Normal"], fontSize=10.5, leading=15, spaceAfter=8)


def build_pdf(filename: str, title: str, sections: list):
    doc = SimpleDocTemplate(
        str(OUT_DIR / filename),
        pagesize=letter,
        topMargin=0.9 * inch,
        bottomMargin=0.9 * inch,
        leftMargin=0.9 * inch,
        rightMargin=0.9 * inch,
    )
    story = [Paragraph(title, title_style), Spacer(1, 6)]
    for heading, paragraphs in sections:
        story.append(Paragraph(heading, h1_style))
        for para in paragraphs:
            story.append(Paragraph(para, body_style))
    doc.build(story)
    print(f"Wrote {OUT_DIR / filename}")


# ---------------------------------------------------------------------------
# AUTO POLICY
# ---------------------------------------------------------------------------
auto_sections = [
    ("Section 1: Definitions", [
        "\"Insured Vehicle\" means the vehicle identified on the Declarations Page of this policy.",
        "\"Comprehensive Coverage\" means coverage for loss to the Insured Vehicle caused by "
        "something other than collision, including but not limited to fire, theft, vandalism, "
        "falling objects, hail, windstorm, flood, and contact with an animal.",
        "\"Collision Coverage\" means coverage for loss to the Insured Vehicle caused by "
        "collision with another object or vehicle, or by upset of the Insured Vehicle.",
        "\"Named Driver\" means any individual specifically listed as a driver on the "
        "Declarations Page of this policy.",
    ]),
    ("Section 2: Covered Perils - Comprehensive", [
        "Subject to the terms of this policy, we will pay for direct and accidental loss to the "
        "Insured Vehicle caused by: fire; theft or larceny; windstorm, hail, or earthquake; "
        "flood; vandalism or malicious mischief; falling objects; contact with a bird or animal; "
        "and glass breakage not resulting from collision.",
        "Hail and windstorm damage, including denting of the hood, roof, trunk, or body panels, "
        "is covered under Comprehensive Coverage subject to the applicable deductible shown on "
        "the Declarations Page.",
    ]),
    ("Section 3: Covered Perils - Collision", [
        "Subject to the terms of this policy, we will pay for direct and accidental loss to the "
        "Insured Vehicle caused by collision with another vehicle or object, or by upset, "
        "regardless of fault, subject to the collision deductible.",
    ]),
    ("Section 4: Exclusions", [
        "This policy does NOT provide coverage for: (a) loss occurring while the Insured Vehicle "
        "is operated by any person who is not a Named Driver and does not hold a valid driver's "
        "license; (b) loss occurring while the vehicle is used to carry persons or property for "
        "a fee (e.g. ridesharing or delivery services) unless a Rideshare Endorsement is attached; "
        "(c) loss due to wear and tear, mechanical breakdown, or road damage to tires; "
        "(d) loss occurring while the vehicle is used in any organized racing or speed contest; "
        "(e) intentional damage caused by the policyholder or a resident of the policyholder's "
        "household; (f) loss or damage occurring outside the United States and Canada unless "
        "otherwise endorsed.",
        "4.1 Unlicensed or Unauthorized Driver Exclusion: Any claim arising from an accident "
        "where the vehicle was being operated by a person without a valid license, or without "
        "the express permission of the policyholder, is excluded from coverage under this policy.",
    ]),
    ("Section 5: Theft Claims", [
        "In the event of theft of the Insured Vehicle, the policyholder must file a police report "
        "within 24 hours of discovering the theft and provide the claim number and a copy of the "
        "report to us. Payment for a stolen and unrecovered vehicle will be based on the actual "
        "cash value of the vehicle at the time of loss, less the applicable deductible.",
    ]),
    ("Section 6: Required Documentation for Claims", [
        "To process a claim, the policyholder must submit: (1) a completed claim form; "
        "(2) photographs of the damage; (3) a copy of any applicable police report; "
        "(4) a repair estimate from a licensed body shop; and (5) proof of ownership "
        "(vehicle registration or title).",
    ]),
    ("Section 7: Claims Process", [
        "Upon receiving a completed claim submission, we will assign a claims adjuster who will "
        "review the submitted documentation, may request an in-person or virtual inspection of "
        "the damage, and will issue a coverage determination within 15 business days of receiving "
        "all required documentation. All coverage determinations are subject to review and final "
        "approval by a licensed claims adjuster.",
    ]),
    ("Section 8: Deductibles", [
        "The Comprehensive Coverage deductible and Collision Coverage deductible are shown "
        "separately on the Declarations Page and are subtracted from the covered loss amount "
        "prior to payment.",
    ]),
]

build_pdf("auto_policy_sample.pdf", "Sample Auto Insurance Policy - ClaimWise Demo", auto_sections)


# ---------------------------------------------------------------------------
# HOMEOWNERS POLICY
# ---------------------------------------------------------------------------
home_sections = [
    ("Section 1: Definitions", [
        "\"Dwelling\" means the residential structure identified on the Declarations Page, "
        "including attached structures.",
        "\"Personal Property\" means household and personal belongings owned by the "
        "policyholder or resident family members, located within the Dwelling.",
        "\"Water Damage\" means damage caused by the sudden and accidental discharge or "
        "overflow of water from a plumbing, heating, air conditioning, or household appliance "
        "system located within the Dwelling.",
    ]),
    ("Section 2: Covered Perils", [
        "This policy covers direct physical loss to the Dwelling and Personal Property caused by: "
        "fire or lightning; windstorm or hail; explosion; theft; vandalism or malicious mischief; "
        "falling objects; weight of ice, snow, or sleet; sudden and accidental discharge or "
        "overflow of water from plumbing, heating, or household appliances; and freezing of "
        "plumbing systems, provided reasonable care was taken to maintain heat in the Dwelling.",
    ]),
    ("Section 3: Exclusions", [
        "This policy does NOT cover loss caused by: (a) flood, surface water, waves, tidal water, "
        "or overflow of a body of water, regardless of cause; (b) earth movement, including "
        "earthquake, landslide, or sinkhole; (c) sewer or drain backup, unless a Water Backup "
        "Endorsement is attached; (d) neglect or failure to protect property from further damage "
        "after a loss occurs; (e) mold, fungus, or wet rot damage that results from a failure to "
        "promptly report and remediate a covered water loss; (f) gradual, ongoing seepage or "
        "leakage occurring over a period of weeks, months, or years; (g) war or nuclear hazard.",
        "3.1 Flood Exclusion: Damage caused by flooding, including overflow of rivers, streams, "
        "or other bodies of water, and damage from heavy rainfall causing surface water intrusion, "
        "is excluded under this policy. Flood coverage may be available under a separate flood "
        "insurance policy, such as through the National Flood Insurance Program (NFIP).",
        "3.2 Delayed Discovery / Mold Exclusion: If water damage is not discovered and reported "
        "within a reasonable time (generally within 7 days of the event or the policyholder's "
        "return to the property), resulting mold remediation costs may be excluded or limited.",
    ]),
    ("Section 4: Theft and High-Value Items", [
        "Coverage for theft of jewelry, watches, and furs is limited to $2,500 per occurrence "
        "unless the items are separately scheduled on a Personal Property Endorsement with proof "
        "of value (appraisal or receipt). Claims involving high-value items without proof of "
        "ownership or without a filed police report may require additional investigation before "
        "any payment is authorized.",
    ]),
    ("Section 5: Required Documentation for Claims", [
        "To process a claim, the policyholder must submit: (1) a completed claim form; "
        "(2) photographs or video of the damage; (3) a police report for theft, vandalism, or "
        "break-in claims; (4) a detailed inventory of damaged or stolen Personal Property with "
        "estimated values; and (5) contractor repair estimates for structural damage.",
    ]),
    ("Section 6: Claims Process", [
        "Upon receiving a completed claim submission, a licensed claims adjuster will review the "
        "documentation, may schedule a property inspection, and will issue a coverage "
        "determination within 15 business days of receiving all required documentation. This "
        "policy document alone does not constitute a final coverage decision; all claims are "
        "subject to human adjuster review before payment is authorized.",
    ]),
    ("Section 7: Deductibles", [
        "The standard all-perils deductible is shown on the Declarations Page. A separate, "
        "higher deductible may apply to windstorm or hail claims in certain geographic regions, "
        "as indicated on the Declarations Page.",
    ]),
]

build_pdf("home_policy_sample.pdf", "Sample Homeowners Insurance Policy - ClaimWise Demo", home_sections)

print("Sample policy PDFs generated successfully.")
