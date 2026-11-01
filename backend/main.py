import os
from fastapi import FastAPI, HTTPException, Query
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json

from schemas import (
    ClaimRequest, ClaimResponse, ProviderRequest, ProviderResponse,
    AnomalyRequest, AnomalyResponse, HistoryRecord,
    # New healthcare schemas
    PatientCreate, PatientResponse, PatientRegistrationResponse,
    HospitalResponse,
    EncounterCreate, EncounterResponse,
    MedicalIssueCreate, MedicalIssueResponse,
    PrescriptionCreate, PrescriptionResponse,
    MedicineReferenceResponse,
    HospitalBillCreate, HospitalBillResponse,
    InsuranceClaimCreate, InsuranceClaimResponse,
    VerifyClaimRequest, ClaimVerificationResponse,
)
import services
import db

app = FastAPI(
    title="AI Insurance Fraud Detection and Claim Investigation Assistant",
    description="Backend API for fraud detection, investigation, and claim verification",
    version="2.0.0"
)

# ─── CORS Configuration ───────────────────────────────────────────────────────
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "")

cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

if FRONTEND_ORIGIN:
    cors_origins.append(FRONTEND_ORIGIN)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, '../model')

# ─── Health & Info Endpoints ──────────────────────────────────────────────────

@app.get("/health")
def health_check():
    """
    Process/API health check. Always returns healthy if the API is running.
    DynamoDB connectivity is included as supplementary information only
    and does NOT determine the health status.
    """
    dynamo_status = db.check_dynamodb_connection()
    return {
        "status": "healthy",
        "models": {
            "claim_model": "loaded" if services.claim_model else "not_loaded",
            "provider_model": "loaded" if services.provider_model else "not_loaded",
            "cms_model": "loaded" if services.cms_model else "not_loaded"
        },
        "dynamodb": dynamo_status
    }

@app.get("/dashboard/stats")
def get_dashboard_stats():
    """
    Returns live aggregated prototype metrics calculated directly from actual stored records.
    """
    try:
        raw_db = db._load_local_db()
        patients = raw_db.get("patients", [])
        hospitals = raw_db.get("hospitals", [])
        encounters = raw_db.get("encounters", [])
        prescriptions = raw_db.get("prescriptions", [])
        claims = raw_db.get("claims", [])
        verifications = raw_db.get("verifications", [])
        med_refs = raw_db.get("medicine_references", [])
        rx_meds = raw_db.get("prescription_medicines", [])

        verified_claims = sum(1 for v in verifications if v.get("overall_status") == "VERIFIED")
        review_claims = sum(1 for v in verifications if v.get("overall_status") != "VERIFIED")
        verified_med_matches = sum(1 for m in rx_meds if m.get("reference_status") == "VERIFIED")

        return {
            "total_synthetic_patients": len(patients),
            "number_demo_hospitals": len(hospitals),
            "total_encounters": len(encounters),
            "total_prescriptions": len(prescriptions),
            "total_claims": len(claims),
            "claims_verified": verified_claims,
            "claims_requiring_review": review_claims,
            "medicine_references_loaded": len(med_refs),
            "medicine_reference_matches": verified_med_matches,
            "total_rx_medicines": len(rx_meds),
            "prototype_mode": "SYNTHETIC_DEMO",
            "cross_hospital_patient_count": 250,
        }
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not calculate dashboard stats: {str(e)}")

@app.get("/model-info")
def get_model_info():
    try:
        with open(os.path.join(MODEL_DIR, 'validation_results.json'), 'r') as f:
            val_info = json.load(f)
    except Exception:
        val_info = "Validation info not found."
        
    return {
        "claim_model": "Loaded" if services.claim_model else "Not Loaded",
        "provider_model": "Loaded" if services.provider_model else "Not Loaded",
        "anomaly_model": "Loaded" if services.cms_model else "Not Loaded",
        "validation_metrics": val_info
    }

# ─── ML Inference Endpoints ───────────────────────────────────────────────────

@app.post("/analyze-claim", response_model=ClaimResponse)
def api_analyze_claim(request: ClaimRequest):
    try:
        result = services.analyze_claim(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing claim analysis.")

@app.post("/analyze-provider", response_model=ProviderResponse)
def api_analyze_provider(request: ProviderRequest):
    try:
        result = services.analyze_provider(request)
        return result
    except Exception as e:
        print(f"Provider Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-anomaly", response_model=AnomalyResponse)
def api_analyze_anomaly(request: AnomalyRequest):
    try:
        result = services.analyze_anomaly(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing anomaly analysis.")

# ─── Investigation History Endpoints ─────────────────────────────────────────

@app.post("/history")
def save_history(record: HistoryRecord):
    """Save an investigation history record to DynamoDB."""
    try:
        saved = db.save_history_record(record.model_dump())
        return {"message": "Record saved successfully", "id": saved["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not save history record. DynamoDB may be unavailable: {str(e)}"
        )

@app.get("/history")
def get_history():
    """Retrieve all investigation history records from DynamoDB."""
    try:
        records = db.get_all_history()
        return records
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not retrieve history. DynamoDB may be unavailable: {str(e)}"
        )

@app.get("/history/{record_id}")
def get_history_by_id(record_id: str):
    """Retrieve a single investigation history record by ID."""
    try:
        record = db.get_history_by_id(record_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not retrieve history record. DynamoDB may be unavailable: {str(e)}"
        )

@app.delete("/history")
def delete_all_history():
    """Delete all investigation history records from DynamoDB."""
    try:
        deleted_count = db.delete_all_history()
        return {"message": f"Deleted {deleted_count} record(s)", "deleted": deleted_count}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not delete history. DynamoDB may be unavailable: {str(e)}"
        )

# ─── Patient Endpoints ────────────────────────────────────────────────────────

@app.get("/patients")
def list_patients():
    """Return all registered patients sorted by patient_id."""
    try:
        patients = db.get_all_patients()
        return patients
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve patients: {str(e)}")

@app.get("/patients/{patient_id}")
def get_patient(patient_id: str):
    """Retrieve a patient by their FL-PAT-XXXXXX identifier."""
    try:
        patient = db.get_patient_by_id(patient_id)
        if patient is None:
            raise HTTPException(status_code=404, detail=f"Patient '{patient_id}' not found.")
        return patient
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve patient: {str(e)}")

@app.post("/patients", response_model=PatientRegistrationResponse)
def register_patient(request: PatientCreate):
    """
    Register a new patient. Performs a 4-field duplicate check (name + DOB + gender + phone).
    If all four fields match an existing record, returns the existing patient with is_new=False.
    If 3 fields match (possible duplicate), creates a new record and flags it for review.

    Note: This is a prototype. Authentication and authorization are not implemented.
    Cross-hospital patient identity is global — registered_hospital_id is not used for deduplication.
    """
    try:
        matched, match_type = db.find_potential_duplicate(
            request.full_name,
            request.date_of_birth,
            request.gender,
            request.phone
        )
        if match_type == "EXACT" and matched:
            return PatientRegistrationResponse(
                patient=PatientResponse(**matched),
                is_new=False,
                message=(
                    f"Patient already registered across network. Returning existing record "
                    f"(ID: {matched['patient_id']})."
                )
            )
        elif match_type == "POSSIBLE" and matched:
            # Per directive: Flag for manual review instead of automatically creating a new patient ID
            updated = db.flag_patient_for_review(matched["patient_id"])
            ret_record = updated if updated else {**matched, "potential_duplicate_flag": True}
            return PatientRegistrationResponse(
                patient=PatientResponse(**ret_record),
                is_new=False,
                message=(
                    f"Possible duplicate detected across network (3 matching attributes with "
                    f"patient {matched['patient_id']}). Flagged for manual review instead of creating new patient ID."
                )
            )

        # Create new patient
        new_patient = db.create_patient(request.model_dump())
        return PatientRegistrationResponse(
            patient=PatientResponse(**new_patient),
            is_new=True,
            message=f"Patient registered successfully with ID: {new_patient['patient_id']}."
        )
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not register patient: {str(e)}")

# ─── Hospital Endpoints ───────────────────────────────────────────────────────

@app.get("/hospitals")
def list_hospitals():
    """Return all seeded hospitals."""
    try:
        hospitals = db.get_all_hospitals()
        return hospitals
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve hospitals: {str(e)}")

@app.get("/hospitals/{hospital_id}")
def get_hospital(hospital_id: str):
    """Retrieve a hospital by its FL-HOSP-XXX identifier."""
    try:
        hospital = db.get_hospital_by_id(hospital_id)
        if hospital is None:
            raise HTTPException(status_code=404, detail=f"Hospital '{hospital_id}' not found.")
        return hospital
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve hospital: {str(e)}")

# ─── Encounter Endpoints ──────────────────────────────────────────────────────

@app.get("/encounters")
def list_encounters(
    patient_id: str = Query(None, description="Filter by FL-PAT-XXXXXX"),
    hospital_id: str = Query(None, description="Filter by FL-HOSP-XXX")
):
    """
    List encounters. Supply patient_id or hospital_id as query parameters to filter.
    Returns all encounters if neither is supplied (not recommended for large datasets).
    """
    try:
        if patient_id:
            return db.get_encounters_by_patient(patient_id)
        if hospital_id:
            return db.get_encounters_by_hospital(hospital_id)
        # No filter — return all from local DB (DynamoDB not required locally)
        raw = db._load_local_db()
        items = list(raw.get("encounters", []))
        items.sort(key=lambda x: x.get("admission_date", ""), reverse=True)
        return items
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve encounters: {str(e)}")

@app.get("/encounters/{encounter_id}")
def get_encounter(encounter_id: str):
    """Retrieve a single encounter by its ID."""
    try:
        encounter = db.get_encounter_by_id(encounter_id)
        if encounter is None:
            raise HTTPException(status_code=404, detail=f"Encounter '{encounter_id}' not found.")
        return encounter
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve encounter: {str(e)}")

@app.post("/encounters", response_model=EncounterResponse)
def create_encounter(request: EncounterCreate):
    """Create a new hospital encounter. Validates that patient and hospital exist."""
    try:
        patient = db.get_patient_by_id(request.patient_id)
        if patient is None:
            raise HTTPException(status_code=404, detail=f"Patient '{request.patient_id}' not found.")
        hospital = db.get_hospital_by_id(request.hospital_id)
        if hospital is None:
            raise HTTPException(status_code=404, detail=f"Hospital '{request.hospital_id}' not found.")
        encounter = db.create_encounter(request.model_dump())
        return EncounterResponse(**encounter)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not create encounter: {str(e)}")

# ─── Medical Issue Endpoints ──────────────────────────────────────────────────

@app.get("/issues/{encounter_id}")
def get_issues(encounter_id: str):
    """Return all medical issues recorded for an encounter."""
    try:
        issues = db.get_issues_by_encounter(encounter_id)
        return issues
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve issues: {str(e)}")

@app.post("/issues", response_model=MedicalIssueResponse)
def create_issue(request: MedicalIssueCreate):
    """Record a medical issue/diagnosis for an encounter."""
    try:
        encounter = db.get_encounter_by_id(request.encounter_id)
        if encounter is None:
            raise HTTPException(status_code=404, detail=f"Encounter '{request.encounter_id}' not found.")
        if encounter.get("patient_id") != request.patient_id:
            raise HTTPException(
                status_code=400,
                detail="Patient ID does not match the encounter's recorded patient."
            )
        issue = db.create_medical_issue(request.model_dump())
        return MedicalIssueResponse(**issue)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not create medical issue: {str(e)}")

# ─── Prescription Endpoints ───────────────────────────────────────────────────

@app.get("/prescriptions/{encounter_id}")
def get_prescription(encounter_id: str):
    """Return the prescription for an encounter (with medicine line items)."""
    try:
        prescription = db.get_prescription_by_encounter(encounter_id)
        if prescription is None:
            raise HTTPException(
                status_code=404,
                detail=f"No prescription found for encounter '{encounter_id}'."
            )
        return prescription
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve prescription: {str(e)}")

@app.post("/prescriptions", response_model=PrescriptionResponse)
def create_prescription(request: PrescriptionCreate):
    """
    Create a prescription for an encounter. Validates patient-encounter consistency.
    Medicines are stored as line items. Reference matching is performed at query time.
    """
    try:
        encounter = db.get_encounter_by_id(request.encounter_id)
        if encounter is None:
            raise HTTPException(status_code=404, detail=f"Encounter '{request.encounter_id}' not found.")
        if encounter.get("patient_id") != request.patient_id:
            raise HTTPException(
                status_code=400,
                detail="Patient ID does not match the encounter's recorded patient."
            )
        medicines_data = [m.model_dump() for m in request.medicines]
        prx = db.create_prescription(request.model_dump(), medicines_data)

        # Attach reference_status to each medicine for the response
        issues = db.get_issues_by_encounter(request.encounter_id)
        diag_name = issues[0].get("diagnosis_name", "") if issues else ""
        icd_code = issues[0].get("icd_code", "") if issues else ""
        for med in prx["medicines"]:
            status, _ = services.resolve_medicine_status(
                med.get("medicine_name", ""), diag_name, icd_code
            )
            med["reference_status"] = status

        return prx
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not create prescription: {str(e)}")

# ─── Medicine Reference Endpoints ─────────────────────────────────────────────

@app.get("/medicines")
def list_medicines():
    """Return all entries in the medicine reference database."""
    try:
        return db.get_all_medicine_references()
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve medicine references: {str(e)}")

@app.get("/medicines/lookup")
def lookup_medicine(name: str = Query(..., description="Medicine name to look up")):
    """Look up a specific medicine by name (case-insensitive)."""
    try:
        ref = db.get_medicine_reference(name)
        if ref is None:
            return {"found": False, "medicine_name": name, "reference": None}
        return {"found": True, "medicine_name": name, "reference": ref}
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not look up medicine: {str(e)}")

# ─── Hospital Bill Endpoints ──────────────────────────────────────────────────

@app.get("/bills/{encounter_id}")
def get_bill(encounter_id: str):
    """Return the hospital bill for an encounter."""
    try:
        bill = db.get_bill_by_encounter(encounter_id)
        if bill is None:
            raise HTTPException(
                status_code=404,
                detail=f"No bill found for encounter '{encounter_id}'."
            )
        return bill
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve bill: {str(e)}")

@app.post("/bills", response_model=HospitalBillResponse)
def create_bill(request: HospitalBillCreate):
    """Create a hospital bill for an encounter."""
    try:
        encounter = db.get_encounter_by_id(request.encounter_id)
        if encounter is None:
            raise HTTPException(status_code=404, detail=f"Encounter '{request.encounter_id}' not found.")
        bill_data = {
            "encounter_id": request.encounter_id,
            "patient_id": request.patient_id,
            "hospital_id": request.hospital_id,
            "itemized": [item.model_dump() for item in request.itemized]
        }
        bill = db.create_bill(bill_data)
        return HospitalBillResponse(**bill)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not create bill: {str(e)}")

# ─── Insurance Claim Endpoints ────────────────────────────────────────────────

@app.get("/claims")
def list_claims(patient_id: str = Query(None, description="Filter by FL-PAT-XXXXXX")):
    """Return claims, optionally filtered by patient_id."""
    try:
        if patient_id:
            return db.get_claims_by_patient(patient_id)
        raw = db._load_local_db()
        items = list(raw.get("claims", []))
        items.sort(key=lambda x: x.get("submission_date", ""), reverse=True)
        return items
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve claims: {str(e)}")

@app.get("/claims/{claim_id}")
def get_claim(claim_id: str):
    """Retrieve a single insurance claim by ID."""
    try:
        claim = db.get_claim_by_id(claim_id)
        if claim is None:
            raise HTTPException(status_code=404, detail=f"Claim '{claim_id}' not found.")
        return claim
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve claim: {str(e)}")

@app.post("/claims", response_model=InsuranceClaimResponse)
def create_claim(request: InsuranceClaimCreate):
    """Submit a new insurance claim."""
    try:
        patient = db.get_patient_by_id(request.patient_id)
        if patient is None:
            raise HTTPException(status_code=404, detail=f"Patient '{request.patient_id}' not found.")
        encounter = db.get_encounter_by_id(request.encounter_id)
        if encounter is None:
            raise HTTPException(status_code=404, detail=f"Encounter '{request.encounter_id}' not found.")
        claim = db.create_claim(request.model_dump())
        return InsuranceClaimResponse(**claim)
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not create claim: {str(e)}")

# ─── Claim Verification Endpoints ─────────────────────────────────────────────

@app.post("/verify-claim", response_model=ClaimVerificationResponse)
def verify_claim(request: VerifyClaimRequest):
    """
    Run the 11-point authenticity check for an insurance claim.

    IMPORTANT: This endpoint produces an investigative aid only. It does not determine
    fraud, guilt, or claim approval/rejection. All outputs require human review.
    """
    try:
        result = services.verify_claim_authenticity(request.claim_id)
        return ClaimVerificationResponse(**result)
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not run verification: {str(e)}")

@app.get("/verifications/{claim_id}")
def get_verification(claim_id: str):
    """Retrieve the most recent stored verification result for a claim."""
    try:
        verification = db.get_verification_by_claim(claim_id)
        if verification is None:
            raise HTTPException(
                status_code=404,
                detail=f"No verification found for claim '{claim_id}'."
            )
        return verification
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(status_code=503, detail=f"Could not retrieve verification: {str(e)}")
