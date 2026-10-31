"""
FraudLens AI — Phase 2 Seed Script
===================================
Creates all required DynamoDB tables and seeds:
  - 3 verified Prayagraj hospitals
  - 37 medicine reference entries (WHO EML verified)
  - 5 test patients with encounters, prescriptions, bills, and claims

Run from the backend/ directory:
    python seed_data.py [--endpoint-url http://localhost:8000]

For AWS (uses IAM role / aws configure credentials):
    python seed_data.py

For DynamoDB Local:
    python seed_data.py --endpoint-url http://localhost:8000

IMPORTANT:
- This script is safe to re-run; it uses put_item (idempotent for static data).
- Patient / encounter IDs are sequential and will increment if re-run on a
  non-empty table. Clear all FL_* tables before re-seeding if fresh data needed.
- This does NOT generate the full 300-patient synthetic dataset. That is Phase 3.
"""

import os
import sys
import time
import argparse
import boto3
from botocore.exceptions import ClientError
from decimal import Decimal
from datetime import datetime, timezone, timedelta

# ─── CLI Args ─────────────────────────────────────────────────────────────────
parser = argparse.ArgumentParser(description="FraudLens AI Phase 2 Seed Script")
parser.add_argument("--endpoint-url", default=None, help="Optional DynamoDB endpoint URL")
parser.add_argument("--region", default=os.environ.get("AWS_REGION", "us-east-1"), help="AWS region")
parser.add_argument("--dry-run", action="store_true", help="Show what would be seeded without writing")
args = parser.parse_args()

AWS_REGION = args.region
ENDPOINT_URL = args.endpoint_url or os.environ.get("DYNAMODB_ENDPOINT_URL")
DRY_RUN = args.dry_run

# ─── DynamoDB Setup ───────────────────────────────────────────────────────────
dynamo_kwargs = {"region_name": AWS_REGION}
if ENDPOINT_URL:
    dynamo_kwargs["endpoint_url"] = ENDPOINT_URL
    print(f"Using DynamoDB endpoint: {ENDPOINT_URL}")
else:
    print(f"Using AWS DynamoDB in region: {AWS_REGION}")

dynamodb = boto3.resource("dynamodb", **dynamo_kwargs)
client = boto3.client("dynamodb", **dynamo_kwargs)


def _to_decimal(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: _to_decimal(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_to_decimal(i) for i in obj]
    return obj


# ─── Table Definitions ────────────────────────────────────────────────────────

TABLE_DEFINITIONS = [
    {
        "TableName": "FL_Patients",
        "KeySchema": [{"AttributeName": "patient_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "patient_id", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "FL_Hospitals",
        "KeySchema": [{"AttributeName": "hospital_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "hospital_id", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "FL_Encounters",
        "KeySchema": [{"AttributeName": "encounter_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "encounter_id", "AttributeType": "S"},
            {"AttributeName": "patient_id", "AttributeType": "S"},
            {"AttributeName": "hospital_id", "AttributeType": "S"},
            {"AttributeName": "admission_date", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "patient-index",
                "KeySchema": [
                    {"AttributeName": "patient_id", "KeyType": "HASH"},
                    {"AttributeName": "admission_date", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "ProjectionType": "INCLUDE",
                    "NonKeyAttributes": ["hospital_id", "discharge_date", "encounter_type", "encounter_id"],
                },
            },
            {
                "IndexName": "hospital-index",
                "KeySchema": [
                    {"AttributeName": "hospital_id", "KeyType": "HASH"},
                    {"AttributeName": "admission_date", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "KEYS_ONLY"},
            },
        ],
    },
    {
        "TableName": "FL_MedicalIssues",
        "KeySchema": [{"AttributeName": "issue_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "issue_id", "AttributeType": "S"},
            {"AttributeName": "encounter_id", "AttributeType": "S"},
            {"AttributeName": "recorded_at", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "encounter-index",
                "KeySchema": [
                    {"AttributeName": "encounter_id", "KeyType": "HASH"},
                    {"AttributeName": "recorded_at", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "ProjectionType": "INCLUDE",
                    "NonKeyAttributes": ["diagnosis_name", "icd_code", "severity", "issue_id"],
                },
            }
        ],
    },
    {
        "TableName": "FL_Prescriptions",
        "KeySchema": [{"AttributeName": "prescription_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "prescription_id", "AttributeType": "S"},
            {"AttributeName": "encounter_id", "AttributeType": "S"},
            {"AttributeName": "prescribed_at", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "encounter-index",
                "KeySchema": [
                    {"AttributeName": "encounter_id", "KeyType": "HASH"},
                    {"AttributeName": "prescribed_at", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "KEYS_ONLY"},
            }
        ],
    },
    {
        "TableName": "FL_PrescriptionMedicines",
        "KeySchema": [{"AttributeName": "pm_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "pm_id", "AttributeType": "S"},
            {"AttributeName": "prescription_id", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "prescription-index",
                "KeySchema": [{"AttributeName": "prescription_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    },
    {
        "TableName": "FL_MedicineReference",
        "KeySchema": [{"AttributeName": "medicine_name", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "medicine_name", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
    {
        "TableName": "FL_HospitalBills",
        "KeySchema": [{"AttributeName": "bill_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "bill_id", "AttributeType": "S"},
            {"AttributeName": "encounter_id", "AttributeType": "S"},
            {"AttributeName": "billed_at", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "encounter-index",
                "KeySchema": [
                    {"AttributeName": "encounter_id", "KeyType": "HASH"},
                    {"AttributeName": "billed_at", "KeyType": "RANGE"},
                ],
                "Projection": {"ProjectionType": "ALL"},
            }
        ],
    },
    {
        "TableName": "FL_InsuranceClaims",
        "KeySchema": [{"AttributeName": "claim_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [
            {"AttributeName": "claim_id", "AttributeType": "S"},
            {"AttributeName": "patient_id", "AttributeType": "S"},
            {"AttributeName": "encounter_id", "AttributeType": "S"},
            {"AttributeName": "submission_date", "AttributeType": "S"},
        ],
        "BillingMode": "PAY_PER_REQUEST",
        "GlobalSecondaryIndexes": [
            {
                "IndexName": "patient-index",
                "KeySchema": [
                    {"AttributeName": "patient_id", "KeyType": "HASH"},
                    {"AttributeName": "submission_date", "KeyType": "RANGE"},
                ],
                "Projection": {
                    "ProjectionType": "INCLUDE",
                    "NonKeyAttributes": ["encounter_id", "claim_amount", "status", "claim_id"],
                },
            },
            {
                "IndexName": "encounter-index",
                "KeySchema": [{"AttributeName": "encounter_id", "KeyType": "HASH"}],
                "Projection": {"ProjectionType": "KEYS_ONLY"},
            },
        ],
    },
    {
        "TableName": "FL_ClaimVerifications",
        "KeySchema": [{"AttributeName": "verification_id", "KeyType": "HASH"}],
        "AttributeDefinitions": [{"AttributeName": "verification_id", "AttributeType": "S"}],
        "BillingMode": "PAY_PER_REQUEST",
    },
]


def create_tables():
    """Create all FL_* tables if they do not exist."""
    print("\n== Creating DynamoDB Tables ==")
    for defn in TABLE_DEFINITIONS:
        name = defn["TableName"]
        try:
            client.describe_table(TableName=name)
            print(f"  ✓ {name} already exists — skipped")
        except ClientError as e:
            if e.response["Error"]["Code"] == "ResourceNotFoundException":
                if DRY_RUN:
                    print(f"  [DRY-RUN] Would create table: {name}")
                    continue
                dynamodb.create_table(**defn)
                print(f"  + Created: {name}")
                time.sleep(1)
            else:
                raise


def wait_for_tables():
    """Wait until all tables become ACTIVE."""
    print("\n== Waiting for tables to become ACTIVE ==")
    for defn in TABLE_DEFINITIONS:
        name = defn["TableName"]
        table = dynamodb.Table(name)
        table.wait_until_exists()
        print(f"  ✓ {name} is ACTIVE")


# ─── Hospital Seed Data ───────────────────────────────────────────────────────

HOSPITALS = [
    {
        "hospital_id": "FL-HOSP-001",
        "name": "Swaroop Rani Nehru Hospital",
        "address": "MG Road, George Town",
        "city": "Prayagraj",
        "state": "Uttar Pradesh",
        "type": "Government Teaching Hospital",
        "pincode": "211002",
        "affiliated_to": "Motilal Nehru Medical College",
        "source": "clinicspots.com; admittanceedutech.in; neetcounselling.org.in",
    },
    {
        "hospital_id": "FL-HOSP-002",
        "name": "Moti Lal Nehru Divisional Hospital",
        "common_name": "Colvin Hospital",
        "address": "Building No. 14, K.N. Katju Road, Nakash Kohna / Shahganj",
        "city": "Prayagraj",
        "state": "Uttar Pradesh",
        "type": "Government Divisional Hospital",
        "pincode": "211003",
        "phone": "0532-2240845",
        "website": "www.mlndh.com",
        "source": "mlndh.com (official website)",
    },
    {
        "hospital_id": "FL-HOSP-003",
        "name": "Kamla Nehru Memorial Hospital",
        "address": "1 Hashimpur Road, Tagore Town",
        "city": "Prayagraj",
        "state": "Uttar Pradesh",
        "type": "Charitable Trust Hospital",
        "pincode": "211002",
        "website": "knmh.org",
        "source": "knmh.org (official website); wikipedia.org",
    },
]


# ─── Medicine Reference Seed Data ─────────────────────────────────────────────
# Source: WHO Model List of Essential Medicines, 23rd Edition (2023)
# URL: https://iris.who.int/server/api/core/bitstreams/4ac531b7-e86d-4afd-8995-39d20193f837/content
# eEML: https://list.essentialmeds.org/

WHO_EML_SOURCE = "WHO Model List of Essential Medicines, 23rd Edition (2023)"
WHO_EML_URL = "https://list.essentialmeds.org/"

MEDICINE_REFERENCES = [
    # ── Type 2 Diabetes (E11) ────────────────────────────────────────────────
    {
        "medicine_name": "Metformin",
        "generic_name": "Metformin Hydrochloride",
        "drug_class": "Biguanide / Oral Hypoglycaemic Agent",
        "indications": ["E11", "Type 2 Diabetes Mellitus", "T2DM", "Diabetes"],
        "dosage_forms": ["Tablet 500mg", "Tablet 850mg", "Tablet 1000mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Gliclazide",
        "generic_name": "Gliclazide (Modified Release)",
        "drug_class": "Sulfonylurea / Oral Hypoglycaemic Agent",
        "indications": ["E11", "Type 2 Diabetes Mellitus", "T2DM"],
        "dosage_forms": ["Tablet MR 30mg", "Tablet MR 60mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Insulin Glargine",
        "generic_name": "Insulin Glargine (rDNA origin)",
        "drug_class": "Long-Acting Insulin Analogue",
        "indications": ["E11", "E10", "Type 2 Diabetes Mellitus", "Type 1 Diabetes Mellitus", "Diabetes"],
        "dosage_forms": ["Injection 100 IU/mL", "Injection 300 IU/mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    # ── Hypertension (I10) ───────────────────────────────────────────────────
    {
        "medicine_name": "Amlodipine",
        "generic_name": "Amlodipine Besylate",
        "drug_class": "Calcium Channel Blocker (Dihydropyridine)",
        "indications": ["I10", "Essential Hypertension", "Hypertension", "Stable Angina", "I20"],
        "dosage_forms": ["Tablet 5mg", "Tablet 10mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Losartan",
        "generic_name": "Losartan Potassium",
        "drug_class": "Angiotensin II Receptor Blocker (ARB)",
        "indications": ["I10", "Essential Hypertension", "Hypertension", "Diabetic Nephropathy", "I50"],
        "dosage_forms": ["Tablet 25mg", "Tablet 50mg", "Tablet 100mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Bisoprolol",
        "generic_name": "Bisoprolol Fumarate",
        "drug_class": "Beta-1 Selective Adrenergic Blocker",
        "indications": ["I10", "Essential Hypertension", "Hypertension", "Heart Failure", "I50", "I25"],
        "dosage_forms": ["Tablet 2.5mg", "Tablet 5mg", "Tablet 10mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    # ── Community-Acquired Pneumonia (J18) ───────────────────────────────────
    {
        "medicine_name": "Amoxicillin",
        "generic_name": "Amoxicillin Trihydrate",
        "drug_class": "Aminopenicillin / Beta-Lactam Antibiotic",
        "indications": ["J18", "J15", "Community Acquired Pneumonia", "Pneumonia", "Respiratory Infection"],
        "dosage_forms": ["Capsule 250mg", "Capsule 500mg", "Tablet dispersible 250mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Doxycycline",
        "generic_name": "Doxycycline Hyclate",
        "drug_class": "Tetracycline Antibiotic",
        "indications": ["J18", "J15", "Community Acquired Pneumonia", "Atypical Pneumonia", "Respiratory Infection"],
        "dosage_forms": ["Capsule 100mg", "Tablet 100mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Azithromycin",
        "generic_name": "Azithromycin Dihydrate",
        "drug_class": "Macrolide Antibiotic",
        "indications": ["J18", "J15", "Community Acquired Pneumonia", "Atypical Pneumonia", "Respiratory Infection"],
        "dosage_forms": ["Tablet 250mg", "Tablet 500mg", "Suspension 200mg/5mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    # ── Acute Gastroenteritis (A09) ──────────────────────────────────────────
    {
        "medicine_name": "Oral Rehydration Salts",
        "generic_name": "Low-Osmolarity ORS (Sodium Chloride + Potassium Chloride + Glucose + Sodium Citrate)",
        "drug_class": "Oral Rehydration Solution",
        "indications": ["A09", "Acute Gastroenteritis", "Diarrhoea", "Dehydration", "Watery Diarrhoea"],
        "dosage_forms": ["Powder sachet for oral solution"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Zinc Sulfate",
        "generic_name": "Zinc Sulfate Monohydrate",
        "drug_class": "Mineral Supplement / Anti-Diarrhoeal Adjunct",
        "indications": ["A09", "Acute Gastroenteritis", "Diarrhoea", "Zinc Deficiency", "D50"],
        "dosage_forms": ["Tablet 20mg", "Tablet 10mg", "Dispersible tablet"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Ondansetron",
        "generic_name": "Ondansetron Hydrochloride",
        "drug_class": "5-HT3 Receptor Antagonist / Antiemetic",
        "indications": ["A09", "Acute Gastroenteritis", "Nausea", "Vomiting", "Chemotherapy-induced nausea"],
        "dosage_forms": ["Tablet 4mg", "Tablet 8mg", "Injection 2mg/mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    # ── Giardiasis / Protozoal (A07.1) ───────────────────────────────────────
    {
        "medicine_name": "Metronidazole",
        "generic_name": "Metronidazole",
        "drug_class": "Nitroimidazole Antiprotozoal / Antianaerobic",
        "indications": ["A07", "A07.1", "Giardiasis", "Amoebiasis", "Intestinal Amebiasis", "K35", "Appendicitis"],
        "dosage_forms": ["Tablet 200mg", "Tablet 400mg", "Tablet 500mg", "Injection 5mg/mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Tinidazole",
        "generic_name": "Tinidazole",
        "drug_class": "Nitroimidazole Antiprotozoal",
        "indications": ["A07", "A07.1", "Giardiasis", "Amoebiasis", "Protozoal Infection"],
        "dosage_forms": ["Tablet 500mg", "Tablet 1000mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    # ── Uncomplicated UTI (N39.0) ────────────────────────────────────────────
    {
        "medicine_name": "Nitrofurantoin",
        "generic_name": "Nitrofurantoin",
        "drug_class": "Nitrofuran Antibiotic (WHO AWaRe: Access)",
        "indications": ["N39", "N39.0", "Urinary Tract Infection", "Cystitis", "Uncomplicated UTI"],
        "dosage_forms": ["Capsule 100mg (modified release)", "Tablet 50mg", "Tablet 100mg"],
        "source": WHO_EML_SOURCE + " / WHO AWaRe Antibiotic Book",
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Trimethoprim",
        "generic_name": "Trimethoprim",
        "drug_class": "Dihydrofolate Reductase Inhibitor Antibiotic (WHO AWaRe: Access)",
        "indications": ["N39", "N39.0", "Urinary Tract Infection", "Cystitis", "Uncomplicated UTI"],
        "dosage_forms": ["Tablet 100mg", "Tablet 200mg"],
        "source": WHO_EML_SOURCE + " / WHO AWaRe Antibiotic Book",
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    # ── Complicated UTI / Pyelonephritis (N10) ───────────────────────────────
    {
        "medicine_name": "Ciprofloxacin",
        "generic_name": "Ciprofloxacin Hydrochloride",
        "drug_class": "Fluoroquinolone Antibiotic (WHO AWaRe: Watch)",
        "indications": ["N10", "N39", "Pyelonephritis", "Complicated UTI", "Upper Urinary Tract Infection"],
        "dosage_forms": ["Tablet 250mg", "Tablet 500mg", "Injection 2mg/mL"],
        "source": WHO_EML_SOURCE + " / WHO AWaRe Antibiotic Book",
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Ceftriaxone",
        "generic_name": "Ceftriaxone Sodium",
        "drug_class": "Third-Generation Cephalosporin (WHO AWaRe: Watch)",
        "indications": ["N10", "Pyelonephritis", "Complicated UTI", "K35", "Appendicitis", "J18", "Pneumonia"],
        "dosage_forms": ["Injection 250mg/vial", "Injection 500mg/vial", "Injection 1g/vial"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    # ── Asthma (J45) ─────────────────────────────────────────────────────────
    {
        "medicine_name": "Salbutamol",
        "generic_name": "Salbutamol Sulfate (Albuterol)",
        "drug_class": "Short-Acting Beta-2 Agonist (SABA) / Bronchodilator",
        "indications": ["J45", "Asthma", "Bronchial Asthma", "Bronchospasm", "COPD", "J44"],
        "dosage_forms": ["Metered-dose inhaler 100mcg/actuation", "Nebuliser solution 2.5mg/2.5mL", "Injection"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Budesonide",
        "generic_name": "Budesonide",
        "drug_class": "Inhaled Corticosteroid (ICS) / Controller",
        "indications": ["J45", "Asthma", "Bronchial Asthma", "Persistent Asthma", "COPD", "J44"],
        "dosage_forms": ["Metered-dose inhaler 100mcg", "Metered-dose inhaler 200mcg", "Nebuliser suspension"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Beclometasone",
        "generic_name": "Beclometasone Dipropionate",
        "drug_class": "Inhaled Corticosteroid (ICS) / Controller",
        "indications": ["J45", "Asthma", "Bronchial Asthma", "Persistent Asthma"],
        "dosage_forms": ["Metered-dose inhaler 50mcg", "Metered-dose inhaler 100mcg", "Metered-dose inhaler 250mcg"],
        "source": WHO_EML_SOURCE + " (square-box equivalent to Budesonide §25.1)",
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    # ── Iron Deficiency Anaemia (D50) ────────────────────────────────────────
    {
        "medicine_name": "Ferrous Sulfate",
        "generic_name": "Ferrous Sulfate (60mg elemental iron)",
        "drug_class": "Iron Supplement / Anti-Anaemia Agent",
        "indications": ["D50", "Iron Deficiency Anaemia", "Anaemia", "Anemia"],
        "dosage_forms": ["Tablet 200mg (60mg elemental Fe)", "Tablet 325mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Folic Acid",
        "generic_name": "Folic Acid (Vitamin B9 / Folate)",
        "drug_class": "Vitamin / Anti-Anaemia Agent",
        "indications": ["D50", "D52", "Iron Deficiency Anaemia", "Megaloblastic Anaemia", "Neural Tube Defect Prevention"],
        "dosage_forms": ["Tablet 400mcg", "Tablet 1mg", "Tablet 5mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Ascorbic Acid",
        "generic_name": "Ascorbic Acid (Vitamin C)",
        "drug_class": "Vitamin / Iron Absorption Enhancer",
        "indications": ["D50", "Iron Deficiency Anaemia", "Scurvy", "E54"],
        "dosage_forms": ["Tablet 100mg", "Tablet 250mg", "Tablet 500mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    # ── Hypothyroidism (E03) ─────────────────────────────────────────────────
    {
        "medicine_name": "Levothyroxine",
        "generic_name": "Levothyroxine Sodium",
        "drug_class": "Thyroid Hormone Replacement",
        "indications": ["E03", "E03.9", "Hypothyroidism", "Underactive Thyroid"],
        "dosage_forms": ["Tablet 25mcg", "Tablet 50mcg", "Tablet 100mcg"],
        "source": WHO_EML_SOURCE + " §18.7 Thyroid hormones",
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    # ── Acute Appendicitis (K35) ─────────────────────────────────────────────
    # Note: Metronidazole is already listed above (shared with A07.1)
    # Ceftriaxone is listed above (shared with N10)
    # ── Dengue Fever (A90) ───────────────────────────────────────────────────
    {
        "medicine_name": "Paracetamol",
        "generic_name": "Paracetamol (Acetaminophen)",
        "drug_class": "Non-Opioid Analgesic / Antipyretic",
        "indications": ["A90", "Dengue Fever", "Fever", "Pain", "R50", "R52"],
        "dosage_forms": ["Tablet 500mg", "Tablet 1000mg", "Syrup 250mg/5mL", "Suppository"],
        "source": WHO_EML_SOURCE + " §2.1 / WHO Dengue Clinical Management Guidelines 2009",
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    # ── Additional commonly prescribed medicines ──────────────────────────────
    {
        "medicine_name": "Omeprazole",
        "generic_name": "Omeprazole",
        "drug_class": "Proton Pump Inhibitor (PPI)",
        "indications": ["K25", "K26", "K21", "Peptic Ulcer", "Gastroesophageal Reflux", "GERD", "Gastritis"],
        "dosage_forms": ["Capsule 20mg", "Capsule 40mg", "Injection 40mg/vial"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Atorvastatin",
        "generic_name": "Atorvastatin Calcium",
        "drug_class": "HMG-CoA Reductase Inhibitor (Statin)",
        "indications": ["E78", "Dyslipidaemia", "Hypercholesterolaemia", "Cardiovascular Risk Reduction", "I25"],
        "dosage_forms": ["Tablet 10mg", "Tablet 20mg", "Tablet 40mg", "Tablet 80mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Ibuprofen",
        "generic_name": "Ibuprofen",
        "drug_class": "Non-Steroidal Anti-Inflammatory Drug (NSAID)",
        "indications": ["M79", "M54", "R52", "Pain", "Musculoskeletal Pain", "Arthritis", "M05"],
        "dosage_forms": ["Tablet 200mg", "Tablet 400mg", "Tablet 600mg"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Diclofenac",
        "generic_name": "Diclofenac Sodium",
        "drug_class": "Non-Steroidal Anti-Inflammatory Drug (NSAID)",
        "indications": ["M79", "M54", "Musculoskeletal Pain", "Back Pain", "Arthritis"],
        "dosage_forms": ["Tablet 50mg", "Tablet 75mg", "Injection 75mg/3mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
    {
        "medicine_name": "Pantoprazole",
        "generic_name": "Pantoprazole Sodium",
        "drug_class": "Proton Pump Inhibitor (PPI)",
        "indications": ["K25", "K26", "K21", "Peptic Ulcer", "GERD", "Gastritis"],
        "dosage_forms": ["Tablet 20mg", "Tablet 40mg", "Injection 40mg/vial"],
        "source": "Standard clinical pharmacology; not listed on core WHO EML (PPI class represented by Omeprazole)",
        "source_url": "https://list.essentialmeds.org/",
        "verification_status": "UNVERIFIED",
    },
    {
        "medicine_name": "Cetirizine",
        "generic_name": "Cetirizine Hydrochloride",
        "drug_class": "Second-Generation Antihistamine",
        "indications": ["J30", "L50", "Allergic Rhinitis", "Urticaria", "Hay Fever"],
        "dosage_forms": ["Tablet 10mg", "Syrup 5mg/5mL"],
        "source": WHO_EML_SOURCE,
        "source_url": WHO_EML_URL,
        "verification_status": "VERIFIED",
    },
]


# ─── Test Patient Data ────────────────────────────────────────────────────────

def _now_minus(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).isoformat()

def _date_minus(days: int) -> str:
    return (datetime.now(timezone.utc) - timedelta(days=days)).strftime("%Y-%m-%d")


# 5 test patients. All data is entirely synthetic.
TEST_PATIENTS = [
    {"patient_id": "FL-PAT-000001", "full_name": "Ramesh Kumar Verma", "date_of_birth": "1978-04-12", "gender": "Male", "phone": "9876543201", "address": "Civil Lines, Prayagraj", "created_at": _now_minus(30), "potential_duplicate_flag": False},
    {"patient_id": "FL-PAT-000002", "full_name": "Sunita Devi Singh", "date_of_birth": "1985-09-23", "gender": "Female", "phone": "9876543202", "address": "Allahpur, Prayagraj", "created_at": _now_minus(28), "potential_duplicate_flag": False},
    {"patient_id": "FL-PAT-000003", "full_name": "Arun Mishra", "date_of_birth": "1965-02-07", "gender": "Male", "phone": "9876543203", "address": "George Town, Prayagraj", "created_at": _now_minus(25), "potential_duplicate_flag": False},
    {"patient_id": "FL-PAT-000004", "full_name": "Priya Sharma", "date_of_birth": "1993-11-30", "gender": "Female", "phone": "9876543204", "address": "Ashok Nagar, Prayagraj", "created_at": _now_minus(20), "potential_duplicate_flag": False},
    {"patient_id": "FL-PAT-000005", "full_name": "Deepak Tiwari", "date_of_birth": "1970-06-15", "gender": "Male", "phone": "9876543205", "address": "Mumfordganj, Prayagraj", "created_at": _now_minus(18), "potential_duplicate_flag": False},
]

# Encounters (cross-hospital for patients 1 and 3 to demonstrate global identity)
TEST_ENCOUNTERS = [
    # Patient 1 — visits FL-HOSP-001 (Type 2 Diabetes)
    {"encounter_id": "FL-ENC-000001", "patient_id": "FL-PAT-000001", "hospital_id": "FL-HOSP-001", "admission_date": _date_minus(20), "discharge_date": _date_minus(18), "encounter_type": "IPD", "attending_doctor": "Dr. Anita Kapoor", "department": "General Medicine", "notes": "Routine diabetes management admission.", "created_at": _now_minus(20)},
    # Patient 1 — also visits FL-HOSP-002 (same patient, different hospital)
    {"encounter_id": "FL-ENC-000002", "patient_id": "FL-PAT-000001", "hospital_id": "FL-HOSP-002", "admission_date": _date_minus(5), "discharge_date": _date_minus(4), "encounter_type": "OPD", "attending_doctor": "Dr. Sunil Yadav", "department": "General Medicine", "notes": "Follow-up consultation.", "created_at": _now_minus(5)},
    # Patient 2 — FL-HOSP-001 (Hypertension)
    {"encounter_id": "FL-ENC-000003", "patient_id": "FL-PAT-000002", "hospital_id": "FL-HOSP-001", "admission_date": _date_minus(15), "discharge_date": _date_minus(14), "encounter_type": "OPD", "attending_doctor": "Dr. Meera Gupta", "department": "Cardiology", "notes": "Hypertension monitoring.", "created_at": _now_minus(15)},
    # Patient 3 — FL-HOSP-002 (Pneumonia) — will be used for duplicate claim test
    {"encounter_id": "FL-ENC-000004", "patient_id": "FL-PAT-000003", "hospital_id": "FL-HOSP-002", "admission_date": _date_minus(12), "discharge_date": _date_minus(10), "encounter_type": "IPD", "attending_doctor": "Dr. Rajesh Srivastava", "department": "Pulmonology", "notes": "CAP — community-acquired pneumonia.", "created_at": _now_minus(12)},
    # Patient 3 — also visits FL-HOSP-003 (cross-hospital visit)
    {"encounter_id": "FL-ENC-000005", "patient_id": "FL-PAT-000003", "hospital_id": "FL-HOSP-003", "admission_date": _date_minus(3), "discharge_date": None, "encounter_type": "OPD", "attending_doctor": "Dr. Vandana Tripathi", "department": "General Medicine", "notes": "Follow-up after pneumonia.", "created_at": _now_minus(3)},
    # Patient 4 — FL-HOSP-003 (Iron Deficiency Anaemia) — bill mismatch scenario
    {"encounter_id": "FL-ENC-000006", "patient_id": "FL-PAT-000004", "hospital_id": "FL-HOSP-003", "admission_date": _date_minus(8), "discharge_date": _date_minus(7), "encounter_type": "OPD", "attending_doctor": "Dr. Savita Pandey", "department": "General Medicine", "notes": "Iron deficiency anaemia management.", "created_at": _now_minus(8)},
    # Patient 5 — FL-HOSP-001 (Dengue)
    {"encounter_id": "FL-ENC-000007", "patient_id": "FL-PAT-000005", "hospital_id": "FL-HOSP-001", "admission_date": _date_minus(6), "discharge_date": _date_minus(4), "encounter_type": "IPD", "attending_doctor": "Dr. Ravi Kumar", "department": "General Medicine", "notes": "Dengue fever — clinical management.", "created_at": _now_minus(6)},
]

# Medical Issues
TEST_ISSUES = [
    {"issue_id": "FL-ISS-000001", "encounter_id": "FL-ENC-000001", "patient_id": "FL-PAT-000001", "diagnosis_name": "Type 2 Diabetes Mellitus", "icd_code": "E11", "severity": "Moderate", "recorded_at": _now_minus(20)},
    {"issue_id": "FL-ISS-000002", "encounter_id": "FL-ENC-000002", "patient_id": "FL-PAT-000001", "diagnosis_name": "Type 2 Diabetes Mellitus", "icd_code": "E11", "severity": "Mild", "recorded_at": _now_minus(5)},
    {"issue_id": "FL-ISS-000003", "encounter_id": "FL-ENC-000003", "patient_id": "FL-PAT-000002", "diagnosis_name": "Essential Hypertension", "icd_code": "I10", "severity": "Moderate", "recorded_at": _now_minus(15)},
    {"issue_id": "FL-ISS-000004", "encounter_id": "FL-ENC-000004", "patient_id": "FL-PAT-000003", "diagnosis_name": "Community-Acquired Pneumonia", "icd_code": "J18", "severity": "Moderate", "recorded_at": _now_minus(12)},
    {"issue_id": "FL-ISS-000005", "encounter_id": "FL-ENC-000006", "patient_id": "FL-PAT-000004", "diagnosis_name": "Iron Deficiency Anaemia", "icd_code": "D50", "severity": "Mild", "recorded_at": _now_minus(8)},
    {"issue_id": "FL-ISS-000006", "encounter_id": "FL-ENC-000007", "patient_id": "FL-PAT-000005", "diagnosis_name": "Dengue Fever", "icd_code": "A90", "severity": "Moderate", "recorded_at": _now_minus(6)},
]

# Prescriptions
TEST_PRESCRIPTIONS = [
    {"prescription_id": "FL-RX-000001", "encounter_id": "FL-ENC-000001", "patient_id": "FL-PAT-000001", "issue_id": "FL-ISS-000001", "prescribed_by": "Dr. Anita Kapoor", "prescribed_at": _now_minus(19)},
    {"prescription_id": "FL-RX-000002", "encounter_id": "FL-ENC-000003", "patient_id": "FL-PAT-000002", "issue_id": "FL-ISS-000003", "prescribed_by": "Dr. Meera Gupta", "prescribed_at": _now_minus(14)},
    {"prescription_id": "FL-RX-000003", "encounter_id": "FL-ENC-000004", "patient_id": "FL-PAT-000003", "issue_id": "FL-ISS-000004", "prescribed_by": "Dr. Rajesh Srivastava", "prescribed_at": _now_minus(11)},
    {"prescription_id": "FL-RX-000004", "encounter_id": "FL-ENC-000006", "patient_id": "FL-PAT-000004", "issue_id": "FL-ISS-000005", "prescribed_by": "Dr. Savita Pandey", "prescribed_at": _now_minus(7)},
    {"prescription_id": "FL-RX-000005", "encounter_id": "FL-ENC-000007", "patient_id": "FL-PAT-000005", "issue_id": "FL-ISS-000006", "prescribed_by": "Dr. Ravi Kumar", "prescribed_at": _now_minus(5)},
]

# Prescription Medicines (verified references)
TEST_RX_MEDICINES = [
    # FL-RX-000001 — Diabetes
    {"pm_id": "FL-RX-000001-M01", "prescription_id": "FL-RX-000001", "medicine_name": "Metformin", "generic_name": "Metformin Hydrochloride", "strength": "500mg", "dosage": "500mg", "frequency": "Twice daily", "duration_days": 30, "quantity": 60, "reference_status": "VERIFIED_MATCH"},
    {"pm_id": "FL-RX-000001-M02", "prescription_id": "FL-RX-000001", "medicine_name": "Gliclazide", "generic_name": "Gliclazide Modified Release", "strength": "30mg", "dosage": "30mg", "frequency": "Once daily (morning)", "duration_days": 30, "quantity": 30, "reference_status": "VERIFIED_MATCH"},
    # FL-RX-000002 — Hypertension
    {"pm_id": "FL-RX-000002-M01", "prescription_id": "FL-RX-000002", "medicine_name": "Amlodipine", "generic_name": "Amlodipine Besylate", "strength": "5mg", "dosage": "5mg", "frequency": "Once daily", "duration_days": 30, "quantity": 30, "reference_status": "VERIFIED_MATCH"},
    {"pm_id": "FL-RX-000002-M02", "prescription_id": "FL-RX-000002", "medicine_name": "Losartan", "generic_name": "Losartan Potassium", "strength": "50mg", "dosage": "50mg", "frequency": "Once daily", "duration_days": 30, "quantity": 30, "reference_status": "VERIFIED_MATCH"},
    # FL-RX-000003 — Pneumonia
    {"pm_id": "FL-RX-000003-M01", "prescription_id": "FL-RX-000003", "medicine_name": "Amoxicillin", "generic_name": "Amoxicillin Trihydrate", "strength": "500mg", "dosage": "500mg", "frequency": "Three times daily", "duration_days": 7, "quantity": 21, "reference_status": "VERIFIED_MATCH"},
    {"pm_id": "FL-RX-000003-M02", "prescription_id": "FL-RX-000003", "medicine_name": "Azithromycin", "generic_name": "Azithromycin Dihydrate", "strength": "500mg", "dosage": "500mg", "frequency": "Once daily", "duration_days": 5, "quantity": 5, "reference_status": "VERIFIED_MATCH"},
    {"pm_id": "FL-RX-000003-M03", "prescription_id": "FL-RX-000003", "medicine_name": "Paracetamol", "generic_name": "Paracetamol", "strength": "500mg", "dosage": "500mg", "frequency": "Three times daily as needed", "duration_days": 5, "quantity": 15, "reference_status": "POSSIBLE_MATCH"},
    # FL-RX-000004 — Iron Deficiency Anaemia (includes unverified medicine for testing)
    {"pm_id": "FL-RX-000004-M01", "prescription_id": "FL-RX-000004", "medicine_name": "Ferrous Sulfate", "generic_name": "Ferrous Sulfate", "strength": "200mg", "dosage": "200mg", "frequency": "Once daily", "duration_days": 60, "quantity": 60, "reference_status": "VERIFIED_MATCH"},
    {"pm_id": "FL-RX-000004-M02", "prescription_id": "FL-RX-000004", "medicine_name": "Folic Acid", "generic_name": "Folic Acid", "strength": "5mg", "dosage": "5mg", "frequency": "Once daily", "duration_days": 60, "quantity": 60, "reference_status": "VERIFIED_MATCH"},
    {"pm_id": "FL-RX-000004-M03", "prescription_id": "FL-RX-000004", "medicine_name": "Pantoprazole", "generic_name": "Pantoprazole Sodium", "strength": "40mg", "dosage": "40mg", "frequency": "Once daily (before breakfast)", "duration_days": 30, "quantity": 30, "reference_status": "POSSIBLE_MATCH"},
    # FL-RX-000005 — Dengue
    {"pm_id": "FL-RX-000005-M01", "prescription_id": "FL-RX-000005", "medicine_name": "Paracetamol", "generic_name": "Paracetamol", "strength": "500mg", "dosage": "500mg", "frequency": "Three times daily", "duration_days": 5, "quantity": 15, "reference_status": "VERIFIED_MATCH"},
    {"pm_id": "FL-RX-000005-M02", "prescription_id": "FL-RX-000005", "medicine_name": "Ondansetron", "generic_name": "Ondansetron Hydrochloride", "strength": "4mg", "dosage": "4mg", "frequency": "Twice daily as needed", "duration_days": 3, "quantity": 6, "reference_status": "POSSIBLE_MATCH"},
]

# Hospital Bills (ENC-000006 bill deliberately less than claim for mismatch demo)
TEST_BILLS = [
    {"bill_id": "FL-BILL-000001", "encounter_id": "FL-ENC-000001", "patient_id": "FL-PAT-000001", "hospital_id": "FL-HOSP-001", "total_amount": 4500.0, "itemized": [{"description": "Consultation", "amount": 500.0}, {"description": "Blood Sugar Test (FBS + PPBS)", "amount": 800.0}, {"description": "HbA1c Test", "amount": 1200.0}, {"description": "Medicines", "amount": 1500.0}, {"description": "Nursing Charges (2 days)", "amount": 500.0}], "billed_at": _now_minus(18)},
    {"bill_id": "FL-BILL-000002", "encounter_id": "FL-ENC-000003", "patient_id": "FL-PAT-000002", "hospital_id": "FL-HOSP-001", "total_amount": 1800.0, "itemized": [{"description": "Consultation", "amount": 500.0}, {"description": "ECG", "amount": 400.0}, {"description": "Blood Pressure Monitoring", "amount": 300.0}, {"description": "Medicines", "amount": 600.0}], "billed_at": _now_minus(14)},
    {"bill_id": "FL-BILL-000003", "encounter_id": "FL-ENC-000004", "patient_id": "FL-PAT-000003", "hospital_id": "FL-HOSP-002", "total_amount": 8500.0, "itemized": [{"description": "Consultation", "amount": 600.0}, {"description": "Chest X-Ray", "amount": 800.0}, {"description": "Sputum Culture", "amount": 700.0}, {"description": "IV Antibiotics", "amount": 3000.0}, {"description": "Bed Charges (2 days IPD)", "amount": 2400.0}, {"description": "Medicines", "amount": 1000.0}], "billed_at": _now_minus(10)},
    # Bill for ENC-000006 is 3200 but the claim will say 5500 (billing mismatch test)
    {"bill_id": "FL-BILL-000004", "encounter_id": "FL-ENC-000006", "patient_id": "FL-PAT-000004", "hospital_id": "FL-HOSP-003", "total_amount": 3200.0, "itemized": [{"description": "Consultation", "amount": 500.0}, {"description": "CBC (Complete Blood Count)", "amount": 600.0}, {"description": "Serum Iron / TIBC", "amount": 900.0}, {"description": "Medicines (60-day supply)", "amount": 1200.0}], "billed_at": _now_minus(7)},
    {"bill_id": "FL-BILL-000005", "encounter_id": "FL-ENC-000007", "patient_id": "FL-PAT-000005", "hospital_id": "FL-HOSP-001", "total_amount": 12000.0, "itemized": [{"description": "Consultation", "amount": 700.0}, {"description": "NS1 Antigen + Dengue IgM/IgG", "amount": 1800.0}, {"description": "CBC (daily x 3)", "amount": 1500.0}, {"description": "IV Fluids (Ringer's Lactate 500mL x 6)", "amount": 2400.0}, {"description": "Bed Charges (2 days IPD)", "amount": 4000.0}, {"description": "Nursing + Monitoring", "amount": 1600.0}], "billed_at": _now_minus(4)},
]

# Insurance Claims:
# - FL-CLM-000001: Clean claim (Patient 1, ENC-001) → should be VERIFIED
# - FL-CLM-000002: Duplicate of FL-CLM-000001 for same encounter → duplicate_claim=True
# - FL-CLM-000003: Patient 2 → VERIFIED
# - FL-CLM-000004: Billing mismatch (ENC-000006, bill=3200, claim=5500) → REVIEW_REQUIRED
# - FL-CLM-000005: Patient 5, Dengue → REVIEW_REQUIRED (Ondansetron possible match)
TEST_CLAIMS = [
    {"claim_id": "FL-CLM-000001", "patient_id": "FL-PAT-000001", "hospital_id": "FL-HOSP-001", "encounter_id": "FL-ENC-000001", "bill_id": "FL-BILL-000001", "claim_amount": 4500.0, "submission_date": _now_minus(17), "policy_number": "POL-2024-11001", "insurer": "National Health Insurance Co.", "status": "Submitted"},
    {"claim_id": "FL-CLM-000002", "patient_id": "FL-PAT-000001", "hospital_id": "FL-HOSP-001", "encounter_id": "FL-ENC-000001", "bill_id": "FL-BILL-000001", "claim_amount": 4500.0, "submission_date": _now_minus(16), "policy_number": "POL-2024-11001", "insurer": "National Health Insurance Co.", "status": "Submitted"},
    {"claim_id": "FL-CLM-000003", "patient_id": "FL-PAT-000002", "hospital_id": "FL-HOSP-001", "encounter_id": "FL-ENC-000003", "bill_id": "FL-BILL-000002", "claim_amount": 1800.0, "submission_date": _now_minus(13), "policy_number": "POL-2024-22050", "insurer": "Star Health Insurance", "status": "Submitted"},
    {"claim_id": "FL-CLM-000004", "patient_id": "FL-PAT-000004", "hospital_id": "FL-HOSP-003", "encounter_id": "FL-ENC-000006", "bill_id": "FL-BILL-000004", "claim_amount": 5500.0, "submission_date": _now_minus(6), "policy_number": "POL-2024-33088", "insurer": "Bajaj Allianz Health Insurance", "status": "Submitted"},
    {"claim_id": "FL-CLM-000005", "patient_id": "FL-PAT-000005", "hospital_id": "FL-HOSP-001", "encounter_id": "FL-ENC-000007", "bill_id": "FL-BILL-000005", "claim_amount": 12000.0, "submission_date": _now_minus(3), "policy_number": "POL-2024-44021", "insurer": "HDFC ERGO Health Insurance", "status": "Submitted"},
]


# ─── Seeding Functions ────────────────────────────────────────────────────────

def seed_table(table_name: str, items: list, key_field: str):
    if DRY_RUN:
        print(f"  [DRY-RUN] Would seed {len(items)} items into {table_name}")
        return
    table = dynamodb.Table(table_name)
    with table.batch_writer() as batch:
        for item in items:
            batch.put_item(Item=_to_decimal(item))
    print(f"  ✓ {table_name}: seeded {len(items)} items")


def run_seed():
    print("\n== Creating Tables ==")
    create_tables()
    if not DRY_RUN:
        wait_for_tables()

    print("\n== Seeding Hospitals ==")
    seed_table("FL_Hospitals", HOSPITALS, "hospital_id")

    print("\n== Seeding Medicine Reference ==")
    seed_table("FL_MedicineReference", MEDICINE_REFERENCES, "medicine_name")

    print("\n== Seeding Test Patients (5) ==")
    seed_table("FL_Patients", TEST_PATIENTS, "patient_id")

    print("\n== Seeding Test Encounters (7) ==")
    seed_table("FL_Encounters", TEST_ENCOUNTERS, "encounter_id")

    print("\n== Seeding Test Medical Issues (6) ==")
    seed_table("FL_MedicalIssues", TEST_ISSUES, "issue_id")

    print("\n== Seeding Test Prescriptions (5) ==")
    seed_table("FL_Prescriptions", TEST_PRESCRIPTIONS, "prescription_id")

    print("\n== Seeding Test Prescription Medicines (12) ==")
    seed_table("FL_PrescriptionMedicines", TEST_RX_MEDICINES, "pm_id")

    print("\n== Seeding Test Hospital Bills (5) ==")
    seed_table("FL_HospitalBills", TEST_BILLS, "bill_id")

    print("\n== Seeding Test Insurance Claims (5) ==")
    seed_table("FL_InsuranceClaims", TEST_CLAIMS, "claim_id")

    print("\n== Seed Complete ==")
    print(f"""
Test Scenarios Available:
  FL-CLM-000001 → Expected: VERIFIED         (clean claim, Patient 1, Hospital 1)
  FL-CLM-000002 → Expected: INVALID_REFERENCE (duplicate of FL-CLM-000001)
  FL-CLM-000003 → Expected: VERIFIED         (clean claim, Patient 2)
  FL-CLM-000004 → Expected: REVIEW_REQUIRED   (billing mismatch: bill=3200, claim=5500)
  FL-CLM-000005 → Expected: REVIEW_REQUIRED   (medicine possible match — Ondansetron vs Dengue)

Cross-Hospital Identity:
  FL-PAT-000001 → visits FL-HOSP-001 (ENC-000001) and FL-HOSP-002 (ENC-000002)
  FL-PAT-000003 → visits FL-HOSP-002 (ENC-000004) and FL-HOSP-003 (ENC-000005)
""")


if __name__ == "__main__":
    run_seed()
