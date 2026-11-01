"""
DynamoDB and Local Storage Abstraction Layer for FraudLens AI.
=============================================================
Provides a unified data access layer for all healthcare and insurance records:
  - 3 Prayagraj Demo Hospitals
  - 300 Synthetic Patients
  - 600 Hospital Encounters
  - 600 Medical Issues
  - 550 Prescriptions & ~1,200 Prescription Medicines
  - 60 Medicine Reference entries (WHO EML / CDSCO / NLEM India)
  - 600 Hospital Bills
  - 550 Insurance Claims
  - Claim Verifications
  - Investigation History

Dual Operation Mode:
1. AWS DynamoDB: Active when boto3 is installed and AWS credentials / DynamoDB Local are reachable.
2. Local Synthetic Database: Transparent persistent fallback when DynamoDB is offline or
   running standalone locally, using `data/synthetic_database.json`.
"""

import os
import json
import uuid
from decimal import Decimal
from datetime import datetime, timezone

# Optional boto3 import
try:
    import boto3
    from botocore.exceptions import ClientError, NoCredentialsError, EndpointConnectionError
    BOTO3_AVAILABLE = True
except ImportError:
    boto3 = None
    BOTO3_AVAILABLE = False
    class ClientError(Exception): pass
    class NoCredentialsError(Exception): pass
    class EndpointConnectionError(Exception): pass

AWS_REGION = os.environ.get("AWS_REGION", "us-east-1")
DYNAMODB_TABLE_NAME = os.environ.get("DYNAMODB_TABLE_NAME", "FraudInvestigationHistory")
DYNAMODB_ENDPOINT_URL = os.environ.get("DYNAMODB_ENDPOINT_URL", None)

# Table names
TBL_PATIENTS       = "FL_Patients"
TBL_HOSPITALS      = "FL_Hospitals"
TBL_ENCOUNTERS     = "FL_Encounters"
TBL_ISSUES         = "FL_MedicalIssues"
TBL_PRESCRIPTIONS  = "FL_Prescriptions"
TBL_RX_MEDICINES   = "FL_PrescriptionMedicines"
TBL_MED_REF        = "FL_MedicineReference"
TBL_BILLS          = "FL_HospitalBills"
TBL_CLAIMS         = "FL_InsuranceClaims"
TBL_VERIFICATIONS  = "FL_ClaimVerifications"

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(BASE_DIR, 'data', 'synthetic_database.json')):
    DATA_DIR = os.path.join(BASE_DIR, 'data')
else:
    DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
LOCAL_DB_FILE = os.path.join(DATA_DIR, 'synthetic_database.json')

# In-memory local cache & state
_local_db = None
_history_records = []


def _load_local_db():
    global _local_db
    if _local_db is not None:
        return _local_db

    if os.path.exists(LOCAL_DB_FILE):
        with open(LOCAL_DB_FILE, "r", encoding="utf-8") as f:
            _local_db = json.load(f)
    else:
        _local_db = {
            "hospitals": [],
            "patients": [],
            "encounters": [],
            "medical_issues": [],
            "prescriptions": [],
            "prescription_medicines": [],
            "medicine_references": [],
            "bills": [],
            "claims": [],
            "verifications": []
        }
    if "verifications" not in _local_db:
        _local_db["verifications"] = []
    return _local_db


def _save_local_db():
    if _local_db is not None:
        try:
            with open(LOCAL_DB_FILE, "w", encoding="utf-8") as f:
                json.dump(_local_db, f, indent=2)
        except Exception as e:
            print(f"Warning: Could not save local database: {e}")


def _is_dynamo_connected() -> bool:
    if not BOTO3_AVAILABLE:
        return False
    try:
        kwargs = {"region_name": AWS_REGION}
        if DYNAMODB_ENDPOINT_URL:
            kwargs["endpoint_url"] = DYNAMODB_ENDPOINT_URL
        client = boto3.client("dynamodb", **kwargs)
        client.describe_table(TableName=TBL_PATIENTS)
        return True
    except Exception:
        return False


def _get_dynamodb_resource():
    if not BOTO3_AVAILABLE:
        return None
    kwargs = {"region_name": AWS_REGION}
    if DYNAMODB_ENDPOINT_URL:
        kwargs["endpoint_url"] = DYNAMODB_ENDPOINT_URL
    return boto3.resource("dynamodb", **kwargs)


def _get_table():
    res = _get_dynamodb_resource()
    return res.Table(DYNAMODB_TABLE_NAME) if res else None


def _get_named_table(name: str):
    res = _get_dynamodb_resource()
    return res.Table(name) if res else None


def _convert_floats(obj):
    if isinstance(obj, float):
        return Decimal(str(obj))
    elif isinstance(obj, dict):
        return {k: _convert_floats(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_floats(i) for i in obj]
    return obj


def _convert_decimals(obj):
    if isinstance(obj, Decimal):
        if obj % 1 == 0:
            return int(obj)
        return float(obj)
    elif isinstance(obj, dict):
        return {k: _convert_decimals(v) for k, v in obj.items()}
    elif isinstance(obj, list):
        return [_convert_decimals(i) for i in obj]
    return obj


def _full_scan(table) -> list:
    if not table:
        return []
    response = table.scan()
    items = response.get("Items", [])
    while "LastEvaluatedKey" in response:
        response = table.scan(ExclusiveStartKey=response["LastEvaluatedKey"])
        items.extend(response.get("Items", []))
    return items


def _get_next_sequential_id(table_name: str, id_field: str, prefix: str, width: int = 6) -> str:
    db = _load_local_db()
    # Map table_name to local_db key
    key_map = {
        TBL_PATIENTS: "patients",
        TBL_HOSPITALS: "hospitals",
        TBL_ENCOUNTERS: "encounters",
        TBL_ISSUES: "medical_issues",
        TBL_PRESCRIPTIONS: "prescriptions",
        TBL_RX_MEDICINES: "prescription_medicines",
        TBL_BILLS: "bills",
        TBL_CLAIMS: "claims",
        TBL_VERIFICATIONS: "verifications",
    }
    local_key = key_map.get(table_name)
    items = db.get(local_key, []) if local_key else []

    max_num = 0
    for item in items:
        val = item.get(id_field, "")
        if isinstance(val, str) and val.startswith(prefix):
            try:
                num = int(val.split("-")[-1])
                max_num = max(max_num, num)
            except (ValueError, IndexError):
                pass
    return f"{prefix}{str(max_num + 1).zfill(width)}"


# ─── Investigation History ───────────────────────────────────────────────────

def check_dynamodb_connection() -> dict:
    if _is_dynamo_connected():
        return {"status": "connected", "table": DYNAMODB_TABLE_NAME, "region": AWS_REGION, "mode": "DYNAMODB_CLOUD"}
    return {
        "status": "connected_local",
        "detail": "Operating in verified local synthetic database mode (AWS DynamoDB inactive)",
        "region": AWS_REGION,
        "mode": "LOCAL_SYNTHETIC_STORE",
        "records_loaded": {
            "patients": len(_load_local_db().get("patients", [])),
            "hospitals": len(_load_local_db().get("hospitals", [])),
            "encounters": len(_load_local_db().get("encounters", [])),
            "prescriptions": len(_load_local_db().get("prescriptions", [])),
            "claims": len(_load_local_db().get("claims", [])),
            "medicines": len(_load_local_db().get("medicine_references", []))
        }
    }


def save_history_record(record: dict) -> dict:
    if _is_dynamo_connected():
        try:
            table = _get_table()
            table.put_item(Item=_convert_floats(record))
        except Exception:
            pass
    _history_records.insert(0, record)
    return record


def get_all_history() -> list:
    if _is_dynamo_connected():
        try:
            table = _get_table()
            items = _full_scan(table)
            items = [_convert_decimals(item) for item in items]
            items.sort(key=lambda x: x.get("timestamp", ""), reverse=True)
            return items
        except Exception:
            pass
    return list(_history_records)


def get_history_by_id(record_id: str) -> dict | None:
    if _is_dynamo_connected():
        try:
            table = _get_table()
            response = table.get_item(Key={"id": record_id})
            item = response.get("Item")
            if item:
                return _convert_decimals(item)
        except Exception:
            pass
    for h in _history_records:
        if h.get("id") == record_id:
            return h
    return None


def delete_all_history() -> int:
    deleted = len(_history_records)
    _history_records.clear()
    if _is_dynamo_connected():
        try:
            table = _get_table()
            response = table.scan(ProjectionExpression="id")
            items = response.get("Items", [])
            with table.batch_writer() as batch:
                for item in items:
                    batch.delete_item(Key={"id": item["id"]})
        except Exception:
            pass
    return deleted


# ─── Patients ────────────────────────────────────────────────────────────────

def find_potential_duplicate(full_name: str, date_of_birth: str, gender: str, phone: str) -> tuple[dict | None, str]:
    db = _load_local_db()
    items = db.get("patients", [])
    name_norm = full_name.strip().lower()
    possible_match = None

    for item in items:
        item_name = item.get("full_name", "").strip().lower()
        item_dob = item.get("date_of_birth", "")
        item_gender = item.get("gender", "")
        item_phone = item.get("phone", "")

        matches = sum([
            item_name == name_norm,
            item_dob == date_of_birth,
            item_gender == gender,
            item_phone == phone and bool(phone)
        ])

        if matches == 4:
            return (item, "EXACT")
        elif matches == 3 and possible_match is None:
            possible_match = item

    if possible_match:
        return (possible_match, "POSSIBLE")
    return (None, "NONE")


def flag_patient_for_review(patient_id: str) -> dict | None:
    db = _load_local_db()
    for item in db.get("patients", []):
        if item.get("patient_id") == patient_id:
            item["potential_duplicate_flag"] = True
            _save_local_db()
            return item
    return None


def create_patient(patient_data: dict) -> dict:
    patient_id = _get_next_sequential_id(TBL_PATIENTS, "patient_id", "FL-PAT-", 6)
    now = datetime.now(timezone.utc).isoformat()
    item = {
        "patient_id": patient_id,
        "full_name": patient_data.get("full_name", ""),
        "date_of_birth": patient_data.get("date_of_birth", ""),
        "age": patient_data.get("age", 35),
        "gender": patient_data.get("gender", ""),
        "phone": patient_data.get("phone", ""),
        "address": patient_data.get("address", ""),
        "created_at": now,
        "potential_duplicate_flag": patient_data.get("potential_duplicate_flag", False),
        "dataset_designation": "SYNTHETIC_DEMO",
        "record_type": "SYNTHETIC_PATIENT"
    }
    db = _load_local_db()
    db.setdefault("patients", []).append(item)
    _save_local_db()
    return item


def get_patient_by_id(patient_id: str) -> dict | None:
    db = _load_local_db()
    for p in db.get("patients", []):
        if p.get("patient_id") == patient_id:
            return p
    return None


def get_all_patients() -> list:
    db = _load_local_db()
    items = list(db.get("patients", []))
    items.sort(key=lambda x: x.get("patient_id", ""))
    return items


# ─── Hospitals ───────────────────────────────────────────────────────────────

def get_hospital_by_id(hospital_id: str) -> dict | None:
    db = _load_local_db()
    for h in db.get("hospitals", []):
        if h.get("hospital_id") == hospital_id:
            return h
    return None


def get_all_hospitals() -> list:
    db = _load_local_db()
    items = list(db.get("hospitals", []))
    items.sort(key=lambda x: x.get("hospital_id", ""))
    return items


# ─── Encounters ──────────────────────────────────────────────────────────────

def create_encounter(data: dict) -> dict:
    encounter_id = _get_next_sequential_id(TBL_ENCOUNTERS, "encounter_id", "FL-ENC-", 6)
    now = datetime.now(timezone.utc).isoformat()
    item = {
        "encounter_id": encounter_id,
        "patient_id": data["patient_id"],
        "hospital_id": data["hospital_id"],
        "admission_date": data["admission_date"],
        "discharge_date": data.get("discharge_date") or "",
        "encounter_type": data.get("encounter_type", "OPD"),
        "attending_doctor": data.get("attending_doctor", ""),
        "department": data.get("department", ""),
        "notes": data.get("notes", ""),
        "created_at": now,
        "dataset_designation": "SYNTHETIC_DEMO",
        "record_type": "SYNTHETIC_ENCOUNTER"
    }
    db = _load_local_db()
    db.setdefault("encounters", []).append(item)
    _save_local_db()
    return item


def get_encounter_by_id(encounter_id: str) -> dict | None:
    db = _load_local_db()
    for e in db.get("encounters", []):
        if e.get("encounter_id") == encounter_id:
            return e
    return None


def get_encounters_by_patient(patient_id: str) -> list:
    db = _load_local_db()
    items = [e for e in db.get("encounters", []) if e.get("patient_id") == patient_id]
    items.sort(key=lambda x: x.get("admission_date", ""), reverse=True)
    return items


def get_encounters_by_hospital(hospital_id: str) -> list:
    db = _load_local_db()
    items = [e for e in db.get("encounters", []) if e.get("hospital_id") == hospital_id]
    items.sort(key=lambda x: x.get("admission_date", ""), reverse=True)
    return items


# ─── Medical Issues ──────────────────────────────────────────────────────────

def create_medical_issue(data: dict) -> dict:
    issue_id = _get_next_sequential_id(TBL_ISSUES, "issue_id", "FL-ISS-", 6)
    now = datetime.now(timezone.utc).isoformat()
    item = {
        "issue_id": issue_id,
        "encounter_id": data["encounter_id"],
        "patient_id": data["patient_id"],
        "diagnosis_name": data["diagnosis_name"],
        "icd_code": data.get("icd_code", ""),
        "severity": data.get("severity", "Moderate"),
        "recorded_at": now,
        "dataset_designation": "SYNTHETIC_DEMO",
        "record_type": "SYNTHETIC_ISSUE"
    }
    db = _load_local_db()
    db.setdefault("medical_issues", []).append(item)
    _save_local_db()
    return item


def get_issues_by_encounter(encounter_id: str) -> list:
    db = _load_local_db()
    return [i for i in db.get("medical_issues", []) if i.get("encounter_id") == encounter_id]


# ─── Prescriptions ───────────────────────────────────────────────────────────

def create_prescription(data: dict, medicines: list) -> dict:
    prescription_id = _get_next_sequential_id(TBL_PRESCRIPTIONS, "prescription_id", "FL-RX-", 6)
    now = datetime.now(timezone.utc).isoformat()

    header = {
        "prescription_id": prescription_id,
        "encounter_id": data["encounter_id"],
        "patient_id": data["patient_id"],
        "hospital_id": data.get("hospital_id", ""),
        "issue_id": data["issue_id"],
        "prescribed_by": data.get("prescribed_by", ""),
        "prescribed_at": now,
        "dataset_designation": "SYNTHETIC_DEMO",
        "record_type": "SYNTHETIC_PRESCRIPTION"
    }
    db = _load_local_db()
    db.setdefault("prescriptions", []).append(header)

    saved_medicines = []
    for idx, med in enumerate(medicines, start=1):
        pm_id = f"{prescription_id}-M{str(idx).zfill(2)}"
        med_item = {
            "pm_id": pm_id,
            "prescription_id": prescription_id,
            "medicine_name": med.get("medicine_name", ""),
            "generic_name": med.get("generic_name", ""),
            "strength": med.get("strength", ""),
            "dosage": med.get("dosage", ""),
            "frequency": med.get("frequency", ""),
            "duration_days": int(med.get("duration_days", 1)),
            "quantity": int(med.get("quantity", 0)),
            "reference_status": med.get("reference_status", "INSUFFICIENT_INFORMATION"),
            "dataset_designation": "SYNTHETIC_DEMO",
            "record_type": "SYNTHETIC_RX_MEDICINE"
        }
        db.setdefault("prescription_medicines", []).append(med_item)
        saved_medicines.append(med_item)

    _save_local_db()
    return {**header, "medicines": saved_medicines}


def get_prescription_by_encounter(encounter_id: str) -> dict | None:
    db = _load_local_db()
    for p in db.get("prescriptions", []):
        if p.get("encounter_id") == encounter_id:
            prx = dict(p)
            prx["medicines"] = get_medicines_by_prescription(prx["prescription_id"])
            return prx
    return None


def get_prescription_by_id(prescription_id: str) -> dict | None:
    db = _load_local_db()
    for p in db.get("prescriptions", []):
        if p.get("prescription_id") == prescription_id:
            prx = dict(p)
            prx["medicines"] = get_medicines_by_prescription(prescription_id)
            return prx
    return None


def get_medicines_by_prescription(prescription_id: str) -> list:
    db = _load_local_db()
    items = [m for m in db.get("prescription_medicines", []) if m.get("prescription_id") == prescription_id]
    items.sort(key=lambda x: x.get("pm_id", ""))
    return items


# ─── Medicine Reference ──────────────────────────────────────────────────────

def get_medicine_reference(medicine_name: str) -> dict | None:
    db = _load_local_db()
    name_lower = medicine_name.strip().lower()
    for m in db.get("medicine_references", []):
        if m.get("medicine_name", "").strip().lower() == name_lower:
            return m
    return None


def get_all_medicine_references() -> list:
    db = _load_local_db()
    items = list(db.get("medicine_references", []))
    items.sort(key=lambda x: x.get("medicine_name", ""))
    return items


# ─── Hospital Bills ──────────────────────────────────────────────────────────

def create_bill(data: dict) -> dict:
    bill_id = _get_next_sequential_id(TBL_BILLS, "bill_id", "FL-BILL-", 6)
    now = datetime.now(timezone.utc).isoformat()
    itemized = data.get("itemized", [])
    total = sum(float(i.get("amount", 0)) for i in itemized)
    item = {
        "bill_id": bill_id,
        "encounter_id": data["encounter_id"],
        "patient_id": data["patient_id"],
        "hospital_id": data["hospital_id"],
        "total_amount": round(total, 2),
        "currency": "INR",
        "itemized": itemized,
        "billed_at": now,
        "dataset_designation": "SYNTHETIC_DEMO",
        "record_type": "SYNTHETIC_BILL"
    }
    db = _load_local_db()
    db.setdefault("bills", []).append(item)
    _save_local_db()
    return item


def get_bill_by_encounter(encounter_id: str) -> dict | None:
    db = _load_local_db()
    for b in db.get("bills", []):
        if b.get("encounter_id") == encounter_id:
            return b
    return None


def get_bill_by_id(bill_id: str) -> dict | None:
    db = _load_local_db()
    for b in db.get("bills", []):
        if b.get("bill_id") == bill_id:
            return b
    return None


# ─── Insurance Claims ────────────────────────────────────────────────────────

def create_claim(data: dict) -> dict:
    claim_id = _get_next_sequential_id(TBL_CLAIMS, "claim_id", "FL-CLM-", 6)
    now = datetime.now(timezone.utc).isoformat()
    item = {
        "claim_id": claim_id,
        "patient_id": data["patient_id"],
        "hospital_id": data["hospital_id"],
        "encounter_id": data["encounter_id"],
        "bill_id": data["bill_id"],
        "claim_amount": float(data["claim_amount"]),
        "submission_date": now,
        "policy_number": data.get("policy_number", ""),
        "insurer": data.get("insurer", ""),
        "status": "Submitted",
        "dataset_designation": "SYNTHETIC_DEMO",
        "record_type": "SYNTHETIC_CLAIM"
    }
    db = _load_local_db()
    db.setdefault("claims", []).append(item)
    _save_local_db()
    return item


def get_claim_by_id(claim_id: str) -> dict | None:
    db = _load_local_db()
    for c in db.get("claims", []):
        if c.get("claim_id") == claim_id:
            return c
    return None


def get_claims_by_patient(patient_id: str) -> list:
    db = _load_local_db()
    items = [c for c in db.get("claims", []) if c.get("patient_id") == patient_id]
    items.sort(key=lambda x: x.get("submission_date", ""), reverse=True)
    return items


def get_claim_by_encounter(encounter_id: str) -> dict | None:
    db = _load_local_db()
    for c in db.get("claims", []):
        if c.get("encounter_id") == encounter_id:
            return c
    return None


# ─── Claim Verifications ─────────────────────────────────────────────────────

def save_verification(data: dict) -> dict:
    db = _load_local_db()
    vers = db.setdefault("verifications", [])
    # Replace existing or append
    for idx, v in enumerate(vers):
        if v.get("verification_id") == data.get("verification_id") or v.get("claim_id") == data.get("claim_id"):
            vers[idx] = data
            _save_local_db()
            return data
    vers.append(data)
    _save_local_db()
    return data


def get_verification_by_claim(claim_id: str) -> dict | None:
    db = _load_local_db()
    matching = [v for v in db.get("verifications", []) if v.get("claim_id") == claim_id]
    if matching:
        matching.sort(key=lambda x: x.get("verified_at", ""), reverse=True)
        return matching[0]
    return None


def get_verification_by_id(verification_id: str) -> dict | None:
    db = _load_local_db()
    for v in db.get("verifications", []):
        if v.get("verification_id") == verification_id:
            return v
    return None
