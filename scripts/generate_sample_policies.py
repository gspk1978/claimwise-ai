"""
generate_sample_policies.py
----------------------------
One-off utility script to generate demo insurance policy PDFs with
realistic section structure, so the app has ready-to-use sample data for
testing/demo purposes.

Generates 5 policies: Auto, Homeowners, Health, Renters, and Travel.

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
        "4.2 Rideshare and Commercial Use Exclusion: Loss occurring while the Insured Vehicle is "
        "being used to transport passengers or goods for compensation, including while a "
        "rideshare application is active and awaiting or en route to a passenger pickup, is "
        "excluded unless a Rideshare Endorsement has been purchased and is shown on the "
        "Declarations Page. Such claims should be directed to the applicable commercial or "
        "rideshare company policy in effect at the time of loss.",
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
        "3.3 Sewer and Drain Backup Exclusion: Loss caused by water or waterborne material which "
        "backs up through sewers or drains, or which overflows from a sump pump, is excluded "
        "unless a Water Backup Endorsement is shown on the Declarations Page.",
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


# ---------------------------------------------------------------------------
# HEALTH INSURANCE POLICY
# ---------------------------------------------------------------------------
health_sections = [
    ("Section 1: Definitions", [
        "\"Medically Necessary\" means a service or supply required to diagnose or treat an "
        "illness, injury, condition, or symptoms in accordance with generally accepted standards "
        "of medical practice.",
        "\"Prior Authorization\" means advance approval from us that a service, procedure, or "
        "prescription meets policy requirements for coverage before it is performed or filled.",
        "\"Pre-existing Condition\" means any illness, injury, or condition for which the "
        "policyholder received diagnosis, treatment, or medical advice prior to the policy's "
        "effective date.",
    ]),
    ("Section 2: Covered Services", [
        "This policy covers Medically Necessary services including: physician office visits; "
        "emergency room and urgent care visits; hospitalization; diagnostic imaging and "
        "laboratory testing; prescription medications listed on the covered formulary; "
        "outpatient surgery; and mental health and substance use treatment at parity with "
        "medical/surgical benefits.",
        "Emergency room visits are covered under the prudent layperson standard: coverage "
        "applies whenever a reasonable person could have believed that symptoms constituted an "
        "emergency, regardless of the final diagnosis.",
    ]),
    ("Section 3: Exclusions", [
        "This policy does NOT cover: (a) cosmetic or elective procedures not related to a "
        "Medically Necessary diagnosis, including elective cosmetic surgery such as rhinoplasty "
        "performed for appearance rather than functional/medical reasons; (b) experimental or "
        "investigational treatments not approved by the relevant regulatory body; (c) services "
        "received without required Prior Authorization, except in a documented emergency; "
        "(d) treatment for a Pre-existing Condition during the applicable waiting period defined "
        "in Section 4; (e) services rendered by an out-of-network provider without prior approval, "
        "except in an emergency.",
        "3.1 Cosmetic Procedure Exclusion: Procedures performed primarily to improve appearance "
        "rather than to restore bodily function or treat a diagnosed medical condition are "
        "excluded from coverage, regardless of provider recommendation.",
    ]),
    ("Section 4: Pre-existing Condition Waiting Period", [
        "Claims related to a Pre-existing Condition are excluded from coverage for the first 90 "
        "days following the policy's effective date. After the waiting period has elapsed, "
        "treatment for the condition becomes eligible for coverage subject to all other policy "
        "terms.",
    ]),
    ("Section 5: Prior Authorization Requirements", [
        "The following services require Prior Authorization before being performed: non-emergency "
        "diagnostic imaging (MRI, CT scan, PET scan); elective inpatient admissions; certain "
        "specialty prescription medications; and out-of-network referrals. Claims for these "
        "services submitted without a valid Prior Authorization on file may be denied, though "
        "policyholders may request retroactive authorization with supporting medical "
        "documentation.",
    ]),
    ("Section 6: Required Documentation for Claims", [
        "To process a claim, the policyholder must submit: (1) an itemized bill or superbill from "
        "the treating provider; (2) proof of payment if reimbursement is being requested; "
        "(3) applicable Prior Authorization confirmation number, if required; and (4) a physician's "
        "note or referral for specialist or diagnostic services.",
    ]),
    ("Section 7: Claims Process", [
        "Upon receiving a completed claim submission, a claims examiner will review the "
        "documentation against the covered services and exclusions listed in this policy and "
        "will issue a coverage determination within 30 calendar days. This determination is "
        "preliminary and subject to further review by a licensed claims adjuster or medical "
        "director before final payment or denial is issued.",
    ]),
    ("Section 8: Deductibles and Copays", [
        "The annual deductible, copay amounts per service type, and out-of-pocket maximum are "
        "shown on the Declarations Page and apply before or alongside coverage as indicated.",
    ]),
]

build_pdf("health_policy_sample.pdf", "Sample Health Insurance Policy - ClaimWise Demo", health_sections)


# ---------------------------------------------------------------------------
# RENTERS INSURANCE POLICY
# ---------------------------------------------------------------------------
renters_sections = [
    ("Section 1: Definitions", [
        "\"Personal Property\" means the policyholder's owned belongings located within the "
        "rented residence identified on the Declarations Page.",
        "\"Business Property\" means inventory, tools, equipment, or supplies used in connection "
        "with a trade, profession, or business, whether operated from the residence or elsewhere.",
        "\"Liability Coverage\" means coverage for the policyholder's legal responsibility for "
        "bodily injury or property damage to others.",
    ]),
    ("Section 2: Covered Perils - Personal Property", [
        "This policy covers direct physical loss to Personal Property caused by: fire or "
        "lightning; theft or attempted theft; vandalism; windstorm or hail; explosion; smoke; "
        "and sudden and accidental discharge or overflow of water from plumbing, heating, or "
        "household appliances within the residence.",
    ]),
    ("Section 3: Liability Coverage", [
        "This policy provides Liability Coverage for bodily injury or property damage "
        "unintentionally caused by the policyholder or a resident household member to a third "
        "party, up to the limit shown on the Declarations Page, including associated legal "
        "defense costs.",
    ]),
    ("Section 4: Exclusions", [
        "This policy does NOT cover: (a) Business Property or business-related inventory, "
        "equipment, or losses, regardless of where stored, unless a Business Property "
        "Endorsement is attached; (b) flood, surface water, or earth movement including "
        "earthquake; (c) theft or loss of property left unattended in a common or shared area "
        "without a filed police report; (d) bed bug, pest, or vermin infestation damage; "
        "(e) intentional acts by the policyholder or a resident household member; (f) damage to "
        "the physical structure of the building itself, which remains the landlord's "
        "responsibility and insurance obligation.",
        "4.1 Business Property Exclusion: Tools, inventory, or equipment used for a trade, side "
        "business, or profession are excluded from Personal Property coverage regardless of "
        "storage location, including storage units. A separate business property or inland "
        "marine policy is required for such items.",
        "4.2 Unattended/Unreported Theft: Theft claims involving property left in a shared, "
        "common, or otherwise unattended area require a police report identifying the "
        "circumstances of the loss before any payment will be considered, particularly where the "
        "responsible party is known or suspected.",
    ]),
    ("Section 5: Required Documentation for Claims", [
        "To process a claim, the policyholder must submit: (1) a completed claim form; "
        "(2) a police report for theft or vandalism claims; (3) an inventory of damaged or "
        "stolen items with estimated replacement values and, where available, receipts or "
        "photographs; and (4) a written statement describing how the loss occurred.",
    ]),
    ("Section 6: Claims Process", [
        "Upon receiving a completed claim submission, a claims adjuster will review the "
        "documentation and issue a coverage determination within 15 business days. All coverage "
        "determinations are preliminary until confirmed by a licensed human adjuster.",
    ]),
    ("Section 7: Deductibles", [
        "The Personal Property deductible is shown on the Declarations Page and is subtracted "
        "from the covered loss amount prior to payment. Liability Coverage is not subject to a "
        "deductible.",
    ]),
]

build_pdf("renters_policy_sample.pdf", "Sample Renters Insurance Policy - ClaimWise Demo", renters_sections)


# ---------------------------------------------------------------------------
# TRAVEL INSURANCE POLICY
# ---------------------------------------------------------------------------
travel_sections = [
    ("Section 1: Definitions", [
        "\"Trip\" means the covered travel itinerary identified on the Declarations Page, "
        "beginning on the scheduled departure date and ending on the scheduled return date.",
        "\"Covered Reason\" means an event specifically listed in Section 2 that permits Trip "
        "Cancellation or Trip Interruption benefits.",
        "\"Emergency Medical Treatment\" means treatment required for a sudden and unforeseen "
        "illness or injury occurring during the Trip.",
    ]),
    ("Section 2: Trip Cancellation and Interruption Coverage", [
        "This policy reimburses prepaid, non-refundable trip costs if the Trip is cancelled or "
        "interrupted for a Covered Reason, including: documented illness or injury of the "
        "traveler or a family member that a physician certifies makes travel inadvisable; death "
        "of the traveler or a family member; a natural disaster making the destination "
        "uninhabitable; and involuntary job loss of the traveler occurring after the policy was "
        "purchased.",
    ]),
    ("Section 3: Emergency Medical and Evacuation Coverage", [
        "This policy covers Emergency Medical Treatment received during the Trip, including "
        "hospital, physician, and prescription costs arising from a sudden illness or accidental "
        "injury, up to the limit shown on the Declarations Page. Emergency medical evacuation to "
        "the nearest adequate medical facility, or repatriation, is covered when certified as "
        "medically necessary by the treating physician.",
    ]),
    ("Section 4: Baggage and Personal Effects Coverage", [
        "This policy reimburses the policyholder for baggage or personal effects that are lost, "
        "stolen, or damaged by a common carrier during the Trip, subject to a per-item sub-limit "
        "shown on the Declarations Page. Any settlement received directly from the airline or "
        "common carrier for the same loss will be deducted from the amount payable under this "
        "policy to prevent duplicate recovery.",
    ]),
    ("Section 5: Exclusions", [
        "This policy does NOT cover: (a) treatment or complications arising from a Pre-existing "
        "Condition unless a Pre-existing Condition Waiver was purchased within the required "
        "timeframe after initial trip deposit; (b) injury or loss arising from participation in "
        "extreme or adventure sports, including but not limited to paragliding, skydiving, "
        "scuba diving beyond recreational certification limits, and mountaineering, unless an "
        "Adventure Sports Endorsement is attached; (c) cancellation due to a general fear of "
        "travel or a change of mind not tied to a Covered Reason (\"cancel for any reason\" "
        "coverage is only available if separately purchased and shown on the Declarations Page); "
        "(d) losses resulting from the policyholder's intoxication or illegal activity.",
        "5.1 Extreme Sports Exclusion: Injuries sustained while participating in extreme or "
        "adventure sports activities are excluded from Emergency Medical coverage unless the "
        "Adventure Sports Endorsement was purchased and is reflected on the Declarations Page.",
    ]),
    ("Section 6: Required Documentation for Claims", [
        "To process a claim, the policyholder must submit: (1) a completed claim form; "
        "(2) proof of the Trip cost and cancellation/interruption circumstances (e.g. physician's "
        "note, death certificate, airline documentation); (3) itemized medical bills and proof of "
        "payment for medical claims; and (4) a property irregularity report (PIR) from the "
        "airline and any settlement documentation for baggage claims.",
    ]),
    ("Section 7: Claims Process", [
        "Upon receiving a completed claim submission, a claims examiner will review the "
        "documentation and issue a coverage determination within 20 business days. All coverage "
        "determinations are preliminary and subject to confirmation by a licensed human claims "
        "adjuster before final payment.",
    ]),
]

build_pdf("travel_policy_sample.pdf", "Sample Travel Insurance Policy - ClaimWise Demo", travel_sections)

print("Sample policy PDFs generated successfully (5 policies: auto, home, health, renters, travel).")
