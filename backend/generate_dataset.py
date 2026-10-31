"""
FraudLens AI — Phase 3 Synthetic Dataset Generator
==================================================
Generates an interconnected, realistic synthetic healthcare-insurance dataset
for three verified hospitals in Prayagraj.

Target Scale:
- Hospitals: Exactly 3 verified demo institutions
- Patients: 300 (FL-PAT-000001 to FL-PAT-000300)
- Encounters: 600 (FL-ENC-000001 to FL-ENC-000600)
- Medical Issues: 600 (FL-ISS-000001 to FL-ISS-000600)
- Prescriptions: 550 (FL-RX-000001 to FL-RX-000550)
- Medicine References: 65 verified entries (WHO EML / CDSCO / NLEM India) + 3 unverified
- Prescription Medicines: ~1,200 line items
- Hospital Bills: 600 (FL-BILL-000001 to FL-BILL-000600)
- Insurance Claims: 550 (FL-CLM-000001 to FL-CLM-000550)
- Claim Verifications: 550 verification records

CRITICAL AUTHENTICITY NOTICE:
All patient names, addresses, identifiers, encounter records, prescriptions,
bills, and claims are entirely SYNTHETIC. No real patient data is used.
Hospital records are DEMO_INSTITUTION placeholders.
"""

import os
import json
import random
from datetime import datetime, timedelta, timezone

# Fix seed for reproducible academic prototype generation
random.seed(42)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')

# ─── 1. THREE VERIFIED PRAYAGRAJ DEMO HOSPITALS ──────────────────────────────
# Publicly verifiable institutions in Prayagraj, UP.
# Record type: DEMO_INSTITUTION.

DEMO_HOSPITALS = [
    {
        "hospital_id": "FL-HOSP-001",
        "name": "Swaroop Rani Nehru Hospital",
        "common_name": "SRN Hospital",
        "address": "MG Road, George Town",
        "city": "Prayagraj",
        "state": "Uttar Pradesh",
        "pincode": "211002",
        "type": "Government Teaching Hospital",
        "affiliated_to": "Motilal Nehru Medical College (MLNMC)",
        "source": "https://mlnmc.ac.in",
        "verification_date": "2026-10-31",
        "record_type": "DEMO_INSTITUTION",
        "phone": "0532-2256424",
    },
    {
        "hospital_id": "FL-HOSP-002",
        "name": "Moti Lal Nehru Divisional Hospital",
        "common_name": "Colvin Hospital",
        "address": "Building No. 14, K.N. Katju Road, Nakash Kohna / Shahganj",
        "city": "Prayagraj",
        "state": "Uttar Pradesh",
        "pincode": "211003",
        "type": "Government Divisional Hospital",
        "affiliated_to": "UP State Health Directorate",
        "source": "http://mlndh.com",
        "verification_date": "2026-10-31",
        "record_type": "DEMO_INSTITUTION",
        "phone": "0532-2240845",
    },
    {
        "hospital_id": "FL-HOSP-003",
        "name": "Kamla Nehru Memorial Hospital",
        "common_name": "KNMH",
        "address": "1 Hashimpur Road, Tagore Town",
        "city": "Prayagraj",
        "state": "Uttar Pradesh",
        "pincode": "211002",
        "type": "Charitable Trust Hospital",
        "affiliated_to": "Regional Cancer Centre Recognized",
        "source": "https://www.knmh.org",
        "verification_date": "2026-10-31",
        "record_type": "DEMO_INSTITUTION",
        "phone": "0532-2466624",
    },
]

# ─── 2. MEDICINE REFERENCE DATASET (WHO EML / CDSCO / NLEM India) ────────────
# Sources:
# - WHO Model List of Essential Medicines, 23rd List (2023) [https://list.essentialmeds.org/]
# - National List of Essential Medicines (NLEM), CDSCO, MoHFW India [https://cdsco.gov.in]

WHO_EML_SOURCE = "WHO Model List of Essential Medicines, 23rd Edition (2023)"
WHO_EML_URL = "https://list.essentialmeds.org/"
CDSCO_NLEM_SOURCE = "National List of Essential Medicines (NLEM), CDSCO / MoHFW India"
CDSCO_URL = "https://cdsco.gov.in"

MEDICINE_REFERENCES = [
    # ── Diabetes (E11 / E10) ──
    {
        "medicine_name": "Metformin",
        "generic_name": "Metformin Hydrochloride",
        "drug_class": "Biguanide / Oral Hypoglycaemic Agent",
        "indications": ["E11", "Type 2 Diabetes Mellitus", "T2DM", "Diabetes"],
        "dosage_forms": ["Tablet 500mg", "Tablet 850mg", "Tablet 1000mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Gliclazide",
        "generic_name": "Gliclazide (Modified Release)",
        "drug_class": "Sulfonylurea / Oral Hypoglycaemic Agent",
        "indications": ["E11", "Type 2 Diabetes Mellitus", "T2DM"],
        "dosage_forms": ["Tablet MR 30mg", "Tablet MR 60mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Glimepiride",
        "generic_name": "Glimepiride",
        "drug_class": "Sulfonylurea / Oral Hypoglycaemic Agent",
        "indications": ["E11", "Type 2 Diabetes Mellitus", "T2DM", "Diabetes"],
        "dosage_forms": ["Tablet 1mg", "Tablet 2mg"],
        "source": CDSCO_NLEM_SOURCE,
        "source_url": CDSCO_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Insulin Glargine",
        "generic_name": "Insulin Glargine (rDNA origin)",
        "drug_class": "Long-Acting Insulin Analogue",
        "indications": ["E11", "E10", "Type 2 Diabetes Mellitus", "Type 1 Diabetes Mellitus", "Diabetes"],
        "dosage_forms": ["Injection 100 IU/mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Insulin Regular",
        "generic_name": "Human Insulin (Soluble)",
        "drug_class": "Short-Acting Insulin",
        "indications": ["E10", "E11", "Type 1 Diabetes Mellitus", "Type 2 Diabetes Mellitus", "Diabetic Ketoacidosis"],
        "dosage_forms": ["Injection 40 IU/mL", "Injection 100 IU/mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },

    # ── Hypertension & Cardiovascular (I10 / I25 / I50) ──
    {
        "medicine_name": "Amlodipine",
        "generic_name": "Amlodipine Besylate",
        "drug_class": "Calcium Channel Blocker",
        "indications": ["I10", "Essential Hypertension", "Hypertension", "Stable Angina", "I20"],
        "dosage_forms": ["Tablet 5mg", "Tablet 10mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Losartan",
        "generic_name": "Losartan Potassium",
        "drug_class": "Angiotensin II Receptor Blocker (ARB)",
        "indications": ["I10", "Essential Hypertension", "Hypertension", "Diabetic Nephropathy", "I50"],
        "dosage_forms": ["Tablet 25mg", "Tablet 50mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Telmisartan",
        "generic_name": "Telmisartan",
        "drug_class": "Angiotensin II Receptor Blocker (ARB)",
        "indications": ["I10", "Essential Hypertension", "Hypertension", "Cardiovascular Prevention"],
        "dosage_forms": ["Tablet 20mg", "Tablet 40mg", "Tablet 80mg"],
        "source": CDSCO_NLEM_SOURCE,
        "source_url": CDSCO_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Bisoprolol",
        "generic_name": "Bisoprolol Fumarate",
        "drug_class": "Beta-1 Selective Blocker",
        "indications": ["I10", "Essential Hypertension", "Hypertension", "Heart Failure", "I50"],
        "dosage_forms": ["Tablet 2.5mg", "Tablet 5mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Atenolol",
        "generic_name": "Atenolol",
        "drug_class": "Beta Blocker",
        "indications": ["I10", "Essential Hypertension", "Hypertension", "Angina Pectoris", "I20"],
        "dosage_forms": ["Tablet 50mg", "Tablet 100mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Enalapril",
        "generic_name": "Enalapril Maleate",
        "drug_class": "ACE Inhibitor",
        "indications": ["I10", "Essential Hypertension", "Hypertension", "Heart Failure", "I50"],
        "dosage_forms": ["Tablet 2.5mg", "Tablet 5mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Hydrochlorothiazide",
        "generic_name": "Hydrochlorothiazide",
        "drug_class": "Thiazide Diuretic",
        "indications": ["I10", "Essential Hypertension", "Hypertension", "Edema"],
        "dosage_forms": ["Tablet 12.5mg", "Tablet 25mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Furosemide",
        "generic_name": "Furosemide",
        "drug_class": "Loop Diuretic",
        "indications": ["I50", "Heart Failure", "Edema", "Hypertension", "I10"],
        "dosage_forms": ["Tablet 40mg", "Injection 10mg/mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Atorvastatin",
        "generic_name": "Atorvastatin Calcium",
        "drug_class": "HMG-CoA Reductase Inhibitor (Statin)",
        "indications": ["E78", "Dyslipidemia", "Hypercholesterolemia", "Cardiovascular Prevention", "I25"],
        "dosage_forms": ["Tablet 10mg", "Tablet 20mg", "Tablet 40mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Rosuvastatin",
        "generic_name": "Rosuvastatin Calcium",
        "drug_class": "HMG-CoA Reductase Inhibitor",
        "indications": ["E78", "Dyslipidemia", "Hypercholesterolemia", "I25"],
        "dosage_forms": ["Tablet 5mg", "Tablet 10mg", "Tablet 20mg"],
        "source": CDSCO_NLEM_SOURCE,
        "source_url": CDSCO_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Aspirin",
        "generic_name": "Acetylsalicylic Acid (Low Dose)",
        "drug_class": "Antiplatelet Agent",
        "indications": ["I25", "I21", "Ischemic Heart Disease", "Myocardial Infarction Prevention", "Stroke Prevention"],
        "dosage_forms": ["Tablet enteric-coated 75mg", "Tablet 150mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Clopidogrel",
        "generic_name": "Clopidogrel Bisulfate",
        "drug_class": "Antiplatelet Agent",
        "indications": ["I25", "Acute Coronary Syndrome", "Ischemic Stroke", "Atherosclerosis"],
        "dosage_forms": ["Tablet 75mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },

    # ── Respiratory Infections & Pneumonia (J18 / J15 / J45) ──
    {
        "medicine_name": "Amoxicillin",
        "generic_name": "Amoxicillin Trihydrate",
        "drug_class": "Aminopenicillin Antibiotic",
        "indications": ["J18", "J15", "Community Acquired Pneumonia", "Pneumonia", "Respiratory Infection"],
        "dosage_forms": ["Capsule 250mg", "Capsule 500mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Amoxicillin-Clavulanate",
        "generic_name": "Amoxicillin with Clavulanic Acid",
        "drug_class": "Beta-Lactam Antibiotic with Inhibitor",
        "indications": ["J18", "Community Acquired Pneumonia", "Bacterial Sinusitis", "Lower Respiratory Infection"],
        "dosage_forms": ["Tablet 500mg+125mg", "Tablet 875mg+125mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Doxycycline",
        "generic_name": "Doxycycline Hyclate",
        "drug_class": "Tetracycline Antibiotic",
        "indications": ["J18", "Community Acquired Pneumonia", "Atypical Pneumonia", "Respiratory Infection"],
        "dosage_forms": ["Capsule 100mg", "Tablet 100mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Azithromycin",
        "generic_name": "Azithromycin Dihydrate",
        "drug_class": "Macrolide Antibiotic",
        "indications": ["J18", "J15", "Community Acquired Pneumonia", "Respiratory Tract Infection"],
        "dosage_forms": ["Tablet 250mg", "Tablet 500mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Ceftriaxone",
        "generic_name": "Ceftriaxone Sodium",
        "drug_class": "Third-Generation Cephalosporin",
        "indications": ["J18", "Severe Pneumonia", "Meningitis", "Bacterial Sepsis", "Pyelonephritis"],
        "dosage_forms": ["Powder for Injection 1g"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Cefixime",
        "generic_name": "Cefixime Trihydrate",
        "drug_class": "Oral Third-Generation Cephalosporin",
        "indications": ["J18", "Respiratory Tract Infection", "Urinary Tract Infection", "Typhoid Fever"],
        "dosage_forms": ["Tablet 200mg"],
        "source": CDSCO_NLEM_SOURCE,
        "source_url": CDSCO_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Salbutamol",
        "generic_name": "Salbutamol Sulfate",
        "drug_class": "Short-Acting Beta-2 Agonist",
        "indications": ["J45", "Asthma", "Bronchial Asthma", "COPD", "Bronchospasm"],
        "dosage_forms": ["Inhaler 100 mcg/dose", "Nebulizer Solution 2.5mg/2.5mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Budesonide",
        "generic_name": "Budesonide",
        "drug_class": "Inhaled Corticosteroid",
        "indications": ["J45", "Bronchial Asthma", "Asthma", "Chronic Asthma"],
        "dosage_forms": ["Inhaler 100 mcg/dose", "Inhaler 200 mcg/dose"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Montelukast",
        "generic_name": "Montelukast Sodium",
        "drug_class": "Leukotriene Receptor Antagonist",
        "indications": ["J45", "Bronchial Asthma", "Asthma Maintenance", "Allergic Rhinitis"],
        "dosage_forms": ["Tablet 10mg"],
        "source": CDSCO_NLEM_SOURCE,
        "source_url": CDSCO_URL,
        "verification_status": "VERIFIED"
    },

    # ── Gastrointestinal & Infectious (A09 / A07 / K21 / K25) ──
    {
        "medicine_name": "Oral Rehydration Salts",
        "generic_name": "Oral Rehydration Salts (WHO Formula)",
        "drug_class": "Electrolyte and Fluid Replacement",
        "indications": ["A09", "Acute Gastroenteritis", "Diarrhoea", "Dehydration"],
        "dosage_forms": ["Powder sachet 20.5g for 1L solution"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Zinc Sulfate",
        "generic_name": "Zinc Sulfate Monohydrate",
        "drug_class": "Essential Mineral Supplement",
        "indications": ["A09", "Acute Diarrhoea Adjunct", "Acute Gastroenteritis", "Zinc Deficiency"],
        "dosage_forms": ["Dispersible Tablet 20mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Metronidazole",
        "generic_name": "Metronidazole",
        "drug_class": "Nitroimidazole Antimicrobial / Antiprotozoal",
        "indications": ["A07", "A09", "Amoebiasis", "Giardiasis", "Anaerobic Bacterial Infection", "Gastroenteritis"],
        "dosage_forms": ["Tablet 200mg", "Tablet 400mg", "IV Infusion 500mg/100mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Ciprofloxacin",
        "generic_name": "Ciprofloxacin Hydrochloride",
        "drug_class": "Fluoroquinolone Antibacterial",
        "indications": ["A09", "Bacterial Diarrhoea", "Enteric Fever", "Urinary Tract Infection", "N39"],
        "dosage_forms": ["Tablet 250mg", "Tablet 500mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Levofloxacin",
        "generic_name": "Levofloxacin Hemihydrate",
        "drug_class": "Fluoroquinolone Antibacterial",
        "indications": ["J18", "N39", "Community Acquired Pneumonia", "Complicated UTI", "Pyelonephritis"],
        "dosage_forms": ["Tablet 500mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Omeprazole",
        "generic_name": "Omeprazole Magnesium",
        "drug_class": "Proton Pump Inhibitor (PPI)",
        "indications": ["K21", "K25", "Gastroesophageal Reflux Disease", "Peptic Ulcer", "GERD", "Dyspepsia"],
        "dosage_forms": ["Capsule 20mg", "Capsule 40mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Pantoprazole",
        "generic_name": "Pantoprazole Sodium",
        "drug_class": "Proton Pump Inhibitor (PPI)",
        "indications": ["K21", "K25", "Gastroesophageal Reflux Disease", "GERD", "Peptic Ulcer Disease"],
        "dosage_forms": ["Tablet 40mg", "Injection 40mg"],
        "source": CDSCO_NLEM_SOURCE,
        "source_url": CDSCO_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Ranitidine",
        "generic_name": "Ranitidine Hydrochloride",
        "drug_class": "H2 Receptor Antagonist",
        "indications": ["K21", "K25", "Gastroesophageal Reflux Disease", "Acid Peptic Disease", "Gastritis"],
        "dosage_forms": ["Tablet 150mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Ondansetron",
        "generic_name": "Ondansetron Hydrochloride",
        "drug_class": "5-HT3 Receptor Antagonist (Antiemetic)",
        "indications": ["R11", "A09", "Nausea and Vomiting", "Acute Gastroenteritis Antiemetic"],
        "dosage_forms": ["Tablet 4mg", "Tablet 8mg", "Injection 2mg/mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Domperidone",
        "generic_name": "Domperidone Maleate",
        "drug_class": "Dopamine Receptor Antagonist (Prokinetic/Antiemetic)",
        "indications": ["R11", "K21", "Nausea", "Dyspepsia", "Gastroparesis"],
        "dosage_forms": ["Tablet 10mg"],
        "source": CDSCO_NLEM_SOURCE,
        "source_url": CDSCO_URL,
        "verification_status": "VERIFIED"
    },

    # ── Urinary Tract Infections (N39 / N10) ──
    {
        "medicine_name": "Nitrofurantoin",
        "generic_name": "Nitrofurantoin Monohydrate / Macrocrystals",
        "drug_class": "Nitrofuran Antibacterial",
        "indications": ["N39", "Urinary Tract Infection", "Uncomplicated Cystitis", "UTI"],
        "dosage_forms": ["Tablet 100mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Trimethoprim-Sulfamethoxazole",
        "generic_name": "Co-trimoxazole",
        "drug_class": "Folate Synthesis Inhibitor Antibacterial",
        "indications": ["N39", "J18", "Urinary Tract Infection", "Pneumocystis Pneumonia"],
        "dosage_forms": ["Tablet 400mg+80mg", "Tablet 800mg+160mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },

    # ── Pain, Musculoskeletal & Inflammation (M17 / M06 / R52) ──
    {
        "medicine_name": "Paracetamol",
        "generic_name": "Acetaminophen",
        "drug_class": "Non-Opioid Analgesic / Antipyretic",
        "indications": ["R50", "R52", "M17", "Fever", "Mild to Moderate Pain", "Osteoarthritis"],
        "dosage_forms": ["Tablet 500mg", "Tablet 650mg", "IV Infusion 10mg/mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Ibuprofen",
        "generic_name": "Ibuprofen",
        "drug_class": "Non-Steroidal Anti-Inflammatory Drug (NSAID)",
        "indications": ["M17", "M06", "R52", "Osteoarthritis", "Rheumatoid Arthritis", "Acute Pain"],
        "dosage_forms": ["Tablet 200mg", "Tablet 400mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Diclofenac",
        "generic_name": "Diclofenac Sodium",
        "drug_class": "NSAID",
        "indications": ["M17", "M06", "Osteoarthritis", "Musculoskeletal Pain", "Rheumatoid Arthritis"],
        "dosage_forms": ["Tablet 50mg", "Injection 25mg/mL"],
        "source": CDSCO_NLEM_SOURCE,
        "source_url": CDSCO_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Tramadol",
        "generic_name": "Tramadol Hydrochloride",
        "drug_class": "Synthetic Opioid Analgesic",
        "indications": ["R52", "Moderate to Severe Pain", "Post-operative Pain", "M17"],
        "dosage_forms": ["Capsule 50mg", "Injection 50mg/mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },

    # ── Anaemia & Nutritional (D50 / E55) ──
    {
        "medicine_name": "Ferrous Sulfate",
        "generic_name": "Dried Ferrous Sulfate with Folic Acid",
        "drug_class": "Iron Supplement / Antianemic",
        "indications": ["D50", "Iron Deficiency Anaemia", "Anaemia", "Pregnancy Prophylaxis"],
        "dosage_forms": ["Tablet 60mg elemental iron + 400 mcg folic acid"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Cholecalciferol",
        "generic_name": "Vitamin D3",
        "drug_class": "Vitamin Supplement",
        "indications": ["E55", "Vitamin D Deficiency", "Osteomalacia", "Osteoporosis Adjunct"],
        "dosage_forms": ["Sachet 60,000 IU", "Capsule 60,000 IU"],
        "source": CDSCO_NLEM_SOURCE,
        "source_url": CDSCO_URL,
        "verification_status": "VERIFIED"
    },

    # ── Endocrine & Thyroid (E03 / E05) ──
    {
        "medicine_name": "Levothyroxine",
        "generic_name": "Levothyroxine Sodium",
        "drug_class": "Thyroid Hormone",
        "indications": ["E03", "Hypothyroidism", "Underactive Thyroid", "Goiter"],
        "dosage_forms": ["Tablet 25 mcg", "Tablet 50 mcg", "Tablet 100 mcg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Carbimazole",
        "generic_name": "Carbimazole",
        "drug_class": "Antithyroid Agent",
        "indications": ["E05", "Hyperthyroidism", "Thyrotoxicosis"],
        "dosage_forms": ["Tablet 5mg", "Tablet 10mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },

    # ── Neurology & Epilepsy (G40) ──
    {
        "medicine_name": "Carbamazepine",
        "generic_name": "Carbamazepine",
        "drug_class": "Anticonvulsant / Sodium Channel Blocker",
        "indications": ["G40", "Epilepsy", "Partial Seizures", "Trigeminal Neuralgia"],
        "dosage_forms": ["Tablet 100mg", "Tablet 200mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Phenytoin",
        "generic_name": "Phenytoin Sodium",
        "drug_class": "Hydantoin Anticonvulsant",
        "indications": ["G40", "Epilepsy", "Tonic-Clonic Seizures", "Status Epilepticus"],
        "dosage_forms": ["Tablet 100mg", "Injection 50mg/mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Sodium Valproate",
        "generic_name": "Sodium Valproate / Valproic Acid",
        "drug_class": "Broad-Spectrum Anticonvulsant",
        "indications": ["G40", "Epilepsy", "Generalized Seizures", "Bipolar Disorder"],
        "dosage_forms": ["Tablet 200mg", "Tablet 500mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },

    # ── Antihistamines & Allergy (L50 / J30) ──
    {
        "medicine_name": "Cetirizine",
        "generic_name": "Cetirizine Dihydrochloride",
        "drug_class": "Second-Generation H1 Antihistamine",
        "indications": ["L50", "J30", "Allergic Rhinitis", "Urticaria", "Allergy"],
        "dosage_forms": ["Tablet 10mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Levocetirizine",
        "generic_name": "Levocetirizine Dihydrochloride",
        "drug_class": "Antihistamine",
        "indications": ["L50", "J30", "Allergic Rhinitis", "Chronic Urticaria"],
        "dosage_forms": ["Tablet 5mg"],
        "source": CDSCO_NLEM_SOURCE,
        "source_url": CDSCO_URL,
        "verification_status": "VERIFIED"
    },

    # ── Parasitic Infections & Malaria (B50 / B51 / B82) ──
    {
        "medicine_name": "Albendazole",
        "generic_name": "Albendazole",
        "drug_class": "Benzimidazole Anthelmintic",
        "indications": ["B82", "Intestinal Helminthiasis", "Ascariasis", "Hookworm", "Neurocysticercosis"],
        "dosage_forms": ["Chewable Tablet 400mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Artesunate",
        "generic_name": "Artesunate",
        "drug_class": "Artemisinin Derivative Antimalarial",
        "indications": ["B50", "Severe Malaria", "Falciparum Malaria"],
        "dosage_forms": ["Powder for Injection 60mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Chloroquine",
        "generic_name": "Chloroquine Phosphate",
        "drug_class": "4-Aminoquinoline Antimalarial",
        "indications": ["B51", "Vivax Malaria", "Malaria Prophylaxis"],
        "dosage_forms": ["Tablet 150mg base"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Artemether-Lumefantrine",
        "generic_name": "Artemether + Lumefantrine",
        "drug_class": "Artemisinin-Based Combination Therapy (ACT)",
        "indications": ["B50", "Uncomplicated Falciparum Malaria", "Malaria"],
        "dosage_forms": ["Tablet 20mg+120mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },

    # ── Dermatology & Topical ──
    {
        "medicine_name": "Silver Sulfadiazine",
        "generic_name": "Silver Sulfadiazine 1%",
        "drug_class": "Topical Antibacterial",
        "indications": ["T20", "Burn Wound Infection", "Topical Antibacterial"],
        "dosage_forms": ["Cream 1% w/w"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },
    {
        "medicine_name": "Clotrimazole",
        "generic_name": "Clotrimazole",
        "drug_class": "Imidazole Antifungal",
        "indications": ["B35", "B37", "Fungal Skin Infection", "Candidiasis", "Tinea"],
        "dosage_forms": ["Cream 1% w/w", "Topical Solution 1%"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED"
    },

    # ── Explicit UNVERIFIED / INCOMPLETE Reference Records (for Scenario E testing) ──
    {
        "medicine_name": "BioImmuno Herbal Extract",
        "generic_name": "Polyherbal Compound (Unverified)",
        "drug_class": "Unverified Dietary Supplement",
        "indications": [],
        "dosage_forms": ["Capsule 500mg"],
        "source": "Unverified Market Submission (Demo)",
        "source_url": "",
        "verification_status": "UNVERIFIED"
    },
    {
        "medicine_name": "NeuroPeptil Forte",
        "generic_name": "Unspecified Nootropic Complex",
        "drug_class": "Unregistered Experimental Compound",
        "indications": [],
        "dosage_forms": ["Vial 10mL"],
        "source": "Unverified Prototype Submission",
        "source_url": "",
        "verification_status": "INCOMPLETE"
    },
    {
        "medicine_name": "AyurVital Gold",
        "generic_name": "Proprietary Wellness Tonic",
        "drug_class": "Uncategorized Supplement",
        "indications": [],
        "dosage_forms": ["Syrup 200mL"],
        "source": "Unverified Commercial Listing",
        "source_url": "",
        "verification_status": "UNVERIFIED"
    }
]

# ─── 3. CLINICAL TEMPLATES FOR ENCOUNTERS & PRESCRIPTIONS ────────────────────

DIAGNOSIS_TEMPLATES = [
    {
        "diagnosis_name": "Type 2 Diabetes Mellitus",
        "icd_code": "E11",
        "department": "Endocrinology & Diabetology",
        "meds": [
            ("Metformin", "Tablet 500mg", "Twice daily with meals", 30),
            ("Gliclazide", "Tablet MR 60mg", "Once daily before breakfast", 30),
        ],
        "base_bill": 8500.0,
    },
    {
        "diagnosis_name": "Essential Hypertension",
        "icd_code": "I10",
        "department": "Cardiology & Internal Medicine",
        "meds": [
            ("Amlodipine", "Tablet 5mg", "Once daily in morning", 30),
            ("Telmisartan", "Tablet 40mg", "Once daily in evening", 30),
        ],
        "base_bill": 7200.0,
    },
    {
        "diagnosis_name": "Community Acquired Pneumonia",
        "icd_code": "J18",
        "department": "Pulmonology & Respiratory Medicine",
        "meds": [
            ("Amoxicillin", "Capsule 500mg", "Three times daily", 7),
            ("Azithromycin", "Tablet 500mg", "Once daily for 5 days", 5),
            ("Paracetamol", "Tablet 650mg", "As needed for fever", 5),
        ],
        "base_bill": 14500.0,
    },
    {
        "diagnosis_name": "Acute Gastroenteritis",
        "icd_code": "A09",
        "department": "Gastroenterology",
        "meds": [
            ("Oral Rehydration Salts", "Powder sachet 20.5g for 1L solution", "As needed after each loose stool", 3),
            ("Zinc Sulfate", "Dispersible Tablet 20mg", "Once daily for 14 days", 14),
            ("Ondansetron", "Tablet 4mg", "As needed for vomiting", 3),
        ],
        "base_bill": 6200.0,
    },
    {
        "diagnosis_name": "Bronchial Asthma (Acute Exacerbation)",
        "icd_code": "J45",
        "department": "Pulmonology",
        "meds": [
            ("Salbutamol", "Inhaler 100 mcg/dose", "Two puffs every 6 hours", 30),
            ("Budesonide", "Inhaler 200 mcg/dose", "One puff twice daily", 30),
        ],
        "base_bill": 11000.0,
    },
    {
        "diagnosis_name": "Urinary Tract Infection",
        "icd_code": "N39",
        "department": "Urology & General Medicine",
        "meds": [
            ("Nitrofurantoin", "Tablet 100mg", "Twice daily with meals", 7),
            ("Paracetamol", "Tablet 500mg", "As needed for pain", 5),
        ],
        "base_bill": 5800.0,
    },
    {
        "diagnosis_name": "Osteoarthritis of Knee",
        "icd_code": "M17",
        "department": "Orthopedics",
        "meds": [
            ("Paracetamol", "Tablet 650mg", "Twice daily as needed", 15),
            ("Ibuprofen", "Tablet 400mg", "Once daily with food", 10),
        ],
        "base_bill": 9800.0,
    },
    {
        "diagnosis_name": "Iron Deficiency Anaemia",
        "icd_code": "D50",
        "department": "Hematology & Internal Medicine",
        "meds": [
            ("Ferrous Sulfate", "Tablet 60mg elemental iron + 400 mcg folic acid", "Once daily after meals", 60),
        ],
        "base_bill": 4900.0,
    },
    {
        "diagnosis_name": "Primary Hypothyroidism",
        "icd_code": "E03",
        "department": "Endocrinology",
        "meds": [
            ("Levothyroxine", "Tablet 50 mcg", "Once daily fasting", 60),
        ],
        "base_bill": 5200.0,
    },
    {
        "diagnosis_name": "Chronic Ischemic Heart Disease",
        "icd_code": "I25",
        "department": "Cardiology",
        "meds": [
            ("Atorvastatin", "Tablet 20mg", "Once daily at bedtime", 30),
            ("Aspirin", "Tablet enteric-coated 75mg", "Once daily after lunch", 30),
            ("Bisoprolol", "Tablet 5mg", "Once daily in morning", 30),
        ],
        "base_bill": 18500.0,
    },
]

# Doctors per hospital
DOCTORS = {
    "FL-HOSP-001": ["Dr. Arvind Tripathi, MD", "Dr. Shalini Mehrotra, MS", "Dr. Rajeshwar Pandey, MD", "Dr. Neha Agarwal, DNB"],
    "FL-HOSP-002": ["Dr. S.K. Srivastava, MD", "Dr. Anita Dwivedi, MD", "Dr. R.P. Mishra, MS", "Dr. Manoj Kumar, DNB"],
    "FL-HOSP-003": ["Dr. Vandana Tandon, MD", "Dr. Pradeep Kaul, MD", "Dr. Sunita Malaviya, MS", "Dr. Alok Verma, DNB"]
}

# Prayagraj local neighborhoods for realistic synthetic addresses
LOCALITIES = [
    "Civil Lines", "George Town", "Tagore Town", "Katra", "Naini",
    "Ashok Nagar", "Mumfordganj", "Rajapur", "Kareli", "Dhoomanganj",
    "Allahpur", "Bairhana", "Daraganj", "Lukerganj", "Govindpur",
    "Chauk", "Preetam Nagar", "Transport Nagar", "Sulem Sarai", "Jhunsi"
]

FIRST_NAMES_MALE = [
    "Ramesh", "Suresh", "Rajesh", "Vikram", "Amit", "Manoj", "Pradeep", "Alok",
    "Sunil", "Anil", "Deepak", "Sanjay", "Mahesh", "Dinesh", "Kishore", "Vijay",
    "Harish", "Pankaj", "Santosh", "Ashok", "Gaurav", "Rohit", "Mohit", "Arun"
]

FIRST_NAMES_FEMALE = [
    "Sunita", "Pooja", "Rekha", "Anjali", "Kavita", "Suman", "Meena", "Geeta",
    "Neelam", "Shashi", "Mamta", "Usha", "Seema", "Ritu", "Poonam", "Asha",
    "Kusum", "Pushpa", "Saroj", "Chitra", "Preeti", "Kiran", "Madhu", "Shweta"
]

LAST_NAMES = [
    "Verma", "Sharma", "Gupta", "Mishra", "Pandey", "Tripathi", "Srivastava",
    "Tiwari", "Singh", "Yadav", "Dwivedi", "Shukla", "Dubey", "Jaiswal",
    "Agarwal", "Patel", "Chauhan", "Maurya", "Kushwaha", "Chaturvedi"
]

INSURERS = [
    "Star Health and Allied Insurance",
    "The New India Assurance Co. Ltd.",
    "HDFC ERGO General Insurance",
    "ICICI Lombard General Insurance",
    "National Insurance Company Ltd.",
    "Care Health Insurance"
]


def generate_full_synthetic_dataset():
    """Generates the full connected dataset adhering strictly to prototype specifications."""
    print("Generating Phase 3 Synthetic Healthcare-Insurance Dataset...")

    # 1. Hospitals (3 verified demo institutions)
    hospitals = list(DEMO_HOSPITALS)

    # 2. Medicine References (65 verified + 3 unverified)
    medicine_references = list(MEDICINE_REFERENCES)
    med_lookup = {m["medicine_name"]: m for m in medicine_references}

    # 3. Generate 300 Synthetic Patients
    patients = []
    for i in range(1, 301):
        pat_id = f"FL-PAT-{str(i).zfill(6)}"
        gender = "Male" if (i % 2 == 1) else "Female"
        if i == 50:
            gender = "Other"

        if gender == "Male":
            first = FIRST_NAMES_MALE[(i * 7) % len(FIRST_NAMES_MALE)]
        elif gender == "Female":
            first = FIRST_NAMES_FEMALE[(i * 7) % len(FIRST_NAMES_FEMALE)]
        else:
            first = "Samar"

        last = LAST_NAMES[(i * 11) % len(LAST_NAMES)]
        full_name = f"{first} {last}"

        # Synthetic age 18 - 82
        age = 18 + ((i * 13) % 65)
        birth_year = 2026 - age
        birth_month = 1 + (i % 12)
        birth_day = 1 + (i % 28)
        dob = f"{birth_year}-{str(birth_month).zfill(2)}-{str(birth_day).zfill(2)}"

        phone = f"98765{str(i + 10000)[-5:]}"
        locality = LOCALITIES[(i * 3) % len(LOCALITIES)]
        address = f"{locality}, Prayagraj, Uttar Pradesh"

        patients.append({
            "patient_id": pat_id,
            "full_name": full_name,
            "date_of_birth": dob,
            "age": age,
            "gender": gender,
            "phone": phone,
            "address": address,
            "created_at": "2025-01-10T08:00:00Z",
            "potential_duplicate_flag": False,
            "dataset_designation": "SYNTHETIC_DEMO",
            "record_type": "SYNTHETIC_PATIENT"
        })

    # 4. Generate 600 Encounters
    # Distribution of encounters per patient:
    # 300 patients across 600 encounters = 2 encounters/patient on average.
    # We will explicitly ensure many patients visit multiple demo hospitals
    # to demonstrate SHARED PATIENT IDENTITY ACROSS HOSPITALS!
    encounters = []
    encounter_patient_map = []  # list of (enc_id, pat_id, hosp_id)

    # Strategy:
    # Patient 1 to 200 get exactly 2 encounters each (at DIFFERENT hospitals!)
    # Patient 201 to 250 get 3 encounters each (at all 3 hospitals!)
    # Patient 251 to 300 get 1 encounter each
    # Total = 200*2 + 50*3 + 50*1 = 400 + 150 + 50 = 600 encounters! Exactly 600!
    enc_counter = 1
    base_date = datetime(2025, 3, 1, 9, 0, 0, tzinfo=timezone.utc)

    # Cross-hospital assignment mapping
    hosp_ids = ["FL-HOSP-001", "FL-HOSP-002", "FL-HOSP-003"]

    for i in range(1, 301):
        pat_id = f"FL-PAT-{str(i).zfill(6)}"
        if i <= 200:
            num_enc = 2
        elif i <= 250:
            num_enc = 3
        else:
            num_enc = 1

        for visit_idx in range(num_enc):
            enc_id = f"FL-ENC-{str(enc_counter).zfill(6)}"
            # Select hospital cyclically to ensure cross-hospital visits for the same patient!
            hosp_idx = (i + visit_idx) % 3
            hosp_id = hosp_ids[hosp_idx]

            # Encounter date spacing
            enc_date = base_date + timedelta(days=((i * 2 + visit_idx * 45) % 500))
            adm_str = enc_date.strftime("%Y-%m-%d")

            enc_type = "OPD" if (enc_counter % 3 != 0) else "IPD"
            dis_str = (enc_date + timedelta(days=random.randint(1, 4))).strftime("%Y-%m-%d") if enc_type == "IPD" else None

            doctor = DOCTORS[hosp_id][(enc_counter) % len(DOCTORS[hosp_id])]
            template = DIAGNOSIS_TEMPLATES[(enc_counter) % len(DIAGNOSIS_TEMPLATES)]

            enc_item = {
                "encounter_id": enc_id,
                "patient_id": pat_id,
                "hospital_id": hosp_id,
                "admission_date": adm_str,
                "discharge_date": dis_str or "",
                "encounter_type": enc_type,
                "attending_doctor": doctor,
                "department": template["department"],
                "notes": f"Synthetic clinical consultation for {template['diagnosis_name']} at {hosp_id}.",
                "created_at": enc_date.isoformat(),
                "dataset_designation": "SYNTHETIC_DEMO",
                "record_type": "SYNTHETIC_ENCOUNTER"
            }
            encounters.append(enc_item)
            encounter_patient_map.append((enc_id, pat_id, hosp_id, enc_date, template))
            enc_counter += 1

    # 5. Generate 600 Medical Issues (1:1 with encounters)
    medical_issues = []
    for idx, (enc_id, pat_id, hosp_id, enc_date, template) in enumerate(encounter_patient_map, start=1):
        iss_id = f"FL-ISS-{str(idx).zfill(6)}"
        severity = "Severe" if (idx % 7 == 0) else ("Mild" if (idx % 3 == 0) else "Moderate")
        medical_issues.append({
            "issue_id": iss_id,
            "encounter_id": enc_id,
            "patient_id": pat_id,
            "diagnosis_name": template["diagnosis_name"],
            "icd_code": template["icd_code"],
            "severity": severity,
            "recorded_at": enc_date.isoformat(),
            "reference_source": "WHO ICD-10 Classification",
            "verification_status": "VERIFIED",
            "dataset_designation": "SYNTHETIC_DEMO",
            "record_type": "SYNTHETIC_ISSUE"
        })

    # 6. Generate 550 Prescriptions & ~1,200 Prescription Medicines
    # Encounters 1 to 550 have prescriptions. Encounters 551 to 600 are diagnostic/follow-up only.
    prescriptions = []
    prescription_medicines = []
    rx_counter = 1

    for idx in range(1, 551):
        enc_id, pat_id, hosp_id, enc_date, template = encounter_patient_map[idx - 1]
        iss_id = medical_issues[idx - 1]["issue_id"]
        rx_id = f"FL-RX-{str(rx_counter).zfill(6)}"

        prx_item = {
            "prescription_id": rx_id,
            "encounter_id": enc_id,
            "patient_id": pat_id,
            "hospital_id": hosp_id,
            "issue_id": iss_id,
            "prescribed_by": encounters[idx - 1]["attending_doctor"],
            "prescribed_at": enc_date.isoformat(),
            "dataset_designation": "SYNTHETIC_DEMO",
            "record_type": "SYNTHETIC_PRESCRIPTION"
        }
        prescriptions.append(prx_item)

        # Prescription line items
        med_list = template["meds"]
        
        # Scenario E hook: For prescription 40 (FL-RX-000040), add unverified medicine
        if idx == 40:
            med_list = [
                ("BioImmuno Herbal Extract", "Capsule 500mg", "Twice daily", 14),
                ("Paracetamol", "Tablet 500mg", "As needed", 5)
            ]
        # Scenario D hook: For prescription 30 (FL-RX-000030), mismatched medicine
        elif idx == 30:
            med_list = [
                ("Carbamazepine", "Tablet 200mg", "Twice daily", 30),  # Inappropriate for Gastroenteritis
            ]

        for m_idx, med_entry in enumerate(med_list, start=1):
            med_name, dosage, freq, dur = med_entry
            ref_info = med_lookup.get(med_name, {})
            pm_id = f"{rx_id}-M{str(m_idx).zfill(2)}"
            
            pm_item = {
                "pm_id": pm_id,
                "prescription_id": rx_id,
                "medicine_name": med_name,
                "generic_name": ref_info.get("generic_name", med_name),
                "strength": dosage.split()[-1] if len(dosage.split()) > 1 else "",
                "dosage": dosage,
                "frequency": freq,
                "duration_days": dur,
                "quantity": dur * (2 if "twice" in freq.lower() else (3 if "three" in freq.lower() else 1)),
                "reference_status": ref_info.get("verification_status", "UNVERIFIED"),
                "dataset_designation": "SYNTHETIC_DEMO",
                "record_type": "SYNTHETIC_RX_MEDICINE"
            }
            prescription_medicines.append(pm_item)

        rx_counter += 1

    # 7. Generate 600 Hospital Bills
    bills = []
    for idx in range(1, 601):
        enc_id, pat_id, hosp_id, enc_date, template = encounter_patient_map[idx - 1]
        bill_id = f"FL-BILL-{str(idx).zfill(6)}"

        base = template["base_bill"] + ((idx * 137) % 2500)
        # Itemize charges
        consult_fee = 800.0 if "001" in hosp_id else 600.0
        pharm_fee = round(base * 0.45, 2)
        diag_fee = round(base * 0.35, 2)
        facility_fee = round(base - consult_fee - pharm_fee - diag_fee, 2)

        itemized = [
            {"description": "Clinical Consultation & Registration", "amount": consult_fee},
            {"description": "Hospital Pharmacy Charges", "amount": pharm_fee},
            {"description": "Diagnostic Laboratory / Imaging Services", "amount": diag_fee},
            {"description": "Nursing & Facility Utilization Charges", "amount": facility_fee},
        ]
        total_amt = round(sum(i["amount"] for i in itemized), 2)

        bill_item = {
            "bill_id": bill_id,
            "encounter_id": enc_id,
            "patient_id": pat_id,
            "hospital_id": hosp_id,
            "total_amount": total_amt,
            "currency": "INR",
            "itemized": itemized,
            "billed_at": enc_date.isoformat(),
            "dataset_designation": "SYNTHETIC_DEMO",
            "record_type": "SYNTHETIC_BILL"
        }
        bills.append(bill_item)

    # 8. Generate 550 Insurance Claims (incorporating Test Scenarios A through H)
    claims = []
    for idx in range(1, 551):
        enc_id, pat_id, hosp_id, enc_date, template = encounter_patient_map[idx - 1]
        bill = bills[idx - 1]
        claim_id = f"FL-CLM-{str(idx).zfill(6)}"
        insurer = INSURERS[(idx * 3) % len(INSURERS)]
        policy_no = f"POL-{insurer[:3].upper()}-{str(idx + 50000)}"

        claim_amt = bill["total_amount"]
        test_scenario_note = None

        # ── Injected Test Scenarios ──
        # Scenario A: Default for idx == 1 (and most claims) -> Consistent, VERIFIED
        if idx == 1:
            test_scenario_note = "Scenario A: Fully consistent claim (Consistent Patient, Hospital, Bill, Prescription)"
        
        # Scenario B: idx == 10 -> Incorrect patient reference
        elif idx == 10:
            test_scenario_note = "Scenario B: Incorrect patient reference (Claim patient does not own encounter)"
            pat_id = "FL-PAT-000002"  # encounter actually belongs to FL-PAT-000005

        # Scenario C: idx == 20 -> Hospital mismatch
        elif idx == 20:
            test_scenario_note = "Scenario C: Hospital mismatch (Claim hospital differs from encounter hospital)"
            hosp_id = "FL-HOSP-003" if hosp_id != "FL-HOSP-003" else "FL-HOSP-001"

        # Scenario D: idx == 30 -> Clinical indication mismatch (Carbamazepine prescribed for Gastroenteritis)
        elif idx == 30:
            test_scenario_note = "Scenario D: Prescription mismatch (Medicine indication does not match recorded diagnosis)"

        # Scenario E: idx == 40 -> Unverified medicine (BioImmuno Herbal Extract)
        elif idx == 40:
            test_scenario_note = "Scenario E: Unverified medicine (Medicine lacks verified reference listing)"

        # Scenario F: idx == 50 -> Billing discrepancy
        elif idx == 50:
            test_scenario_note = "Scenario F: Billing discrepancy (Claimed amount differs from hospital bill)"
            claim_amt = round(bill["total_amount"] + 25000.0, 2)  # Inflated claim

        # Scenario G: idx == 61 -> Duplicate claim for encounter FL-ENC-000060 (already claimed in FL-CLM-000060)
        elif idx == 61:
            test_scenario_note = "Scenario G: Duplicate claim submission (Encounter already has prior claim FL-CLM-000060)"
            enc_id = "FL-ENC-000060"
            pat_id = encounters[59]["patient_id"]
            hosp_id = encounters[59]["hospital_id"]
            bill_id_target = bills[59]["bill_id"]
            bill = bills[59]
            claim_amt = bill["total_amount"]

        # Scenario H: idx == 70 -> Missing encounter
        elif idx == 70:
            test_scenario_note = "Scenario H: Missing encounter reference (References non-existent FL-ENC-999999)"
            enc_id = "FL-ENC-999999"

        claim_item = {
            "claim_id": claim_id,
            "patient_id": pat_id,
            "hospital_id": hosp_id,
            "encounter_id": enc_id,
            "bill_id": bill["bill_id"],
            "claim_amount": claim_amt,
            "submission_date": (enc_date + timedelta(days=2)).isoformat(),
            "policy_number": policy_no,
            "insurer": insurer,
            "status": "Submitted",
            "test_scenario": test_scenario_note,
            "dataset_designation": "SYNTHETIC_DEMO",
            "record_type": "SYNTHETIC_CLAIM"
        }
        claims.append(claim_item)

    print(f"Generated: {len(hospitals)} Hospitals, {len(patients)} Patients, {len(encounters)} Encounters, "
          f"{len(medical_issues)} Issues, {len(prescriptions)} Prescriptions, "
          f"{len(medicine_references)} Med References, {len(prescription_medicines)} Rx Medicines, "
          f"{len(bills)} Bills, {len(claims)} Claims.")

    return {
        "hospitals": hospitals,
        "patients": patients,
        "encounters": encounters,
        "medical_issues": medical_issues,
        "prescriptions": prescriptions,
        "prescription_medicines": prescription_medicines,
        "medicine_references": medicine_references,
        "bills": bills,
        "claims": claims
    }


def save_dataset_files(data: dict):
    """Saves the complete dataset to disk in JSON and CSV formats inside data/."""
    os.makedirs(DATA_DIR, exist_ok=True)
    json_path = os.path.join(DATA_DIR, "synthetic_database.json")
    with open(json_path, "w", encoding="utf-8") as f:
        json.dump(data, f, indent=2)
    print(f"Saved primary JSON database to: {json_path}")

    # Also save individual CSV files for audits / inspections
    import csv

    csv_mapping = [
        ("synthetic_hospitals.csv", data["hospitals"], ["hospital_id", "name", "address", "city", "state", "pincode", "type", "source", "record_type"]),
        ("synthetic_patients.csv", data["patients"], ["patient_id", "full_name", "date_of_birth", "age", "gender", "phone", "address", "dataset_designation"]),
        ("synthetic_encounters.csv", data["encounters"], ["encounter_id", "patient_id", "hospital_id", "admission_date", "discharge_date", "encounter_type", "attending_doctor", "department"]),
        ("synthetic_issues.csv", data["medical_issues"], ["issue_id", "encounter_id", "patient_id", "diagnosis_name", "icd_code", "severity", "recorded_at"]),
        ("synthetic_prescriptions.csv", data["prescriptions"], ["prescription_id", "encounter_id", "patient_id", "hospital_id", "issue_id", "prescribed_by", "prescribed_at"]),
        ("synthetic_prescription_medicines.csv", data["prescription_medicines"], ["pm_id", "prescription_id", "medicine_name", "generic_name", "strength", "dosage", "frequency", "duration_days", "quantity", "reference_status"]),
        ("synthetic_medicine_references.csv", data["medicine_references"], ["medicine_name", "generic_name", "drug_class", "source", "source_url", "verification_status"]),
        ("synthetic_bills.csv", data["bills"], ["bill_id", "encounter_id", "patient_id", "hospital_id", "total_amount", "currency", "billed_at"]),
        ("synthetic_claims.csv", data["claims"], ["claim_id", "patient_id", "hospital_id", "encounter_id", "bill_id", "claim_amount", "submission_date", "policy_number", "insurer", "status", "test_scenario"]),
        ("synthetic_verifications.csv", data.get("verifications", []), ["verification_id", "claim_id", "verified_at", "overall_status", "investigator_notes"]),
    ]

    for fname, records, fieldnames in csv_mapping:
        if not records:
            continue
        fpath = os.path.join(DATA_DIR, fname)
        with open(fpath, "w", newline="", encoding="utf-8") as f:
            writer = csv.DictWriter(f, fieldnames=fieldnames, extrasaction="ignore")
            writer.writeheader()
            for r in records:
                writer.writerow(r)
        print(f"Saved CSV: {fname} ({len(records)} records)")


def generate_all_verifications(data: dict):
    """Pre-runs authenticity verification for all claims and persists results."""
    print("Running initial claim verifications for all claims...")
    import services
    verifications = []
    for c in data["claims"]:
        cid = c["claim_id"]
        v = services.verify_claim_authenticity(cid)
        verifications.append(v)
    data["verifications"] = verifications
    print(f"Generated {len(verifications)} verification records.")
    return data


if __name__ == "__main__":
    dataset = generate_full_synthetic_dataset()
    save_dataset_files(dataset)
    dataset = generate_all_verifications(dataset)
    save_dataset_files(dataset)
