import os
import joblib
import pandas as pd
import numpy as np
import uuid
from datetime import datetime, timezone
from schemas import ClaimRequest, ProviderRequest, AnomalyRequest
import db

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(BASE_DIR, 'model')):
    MODEL_DIR = os.path.join(BASE_DIR, 'model')
else:
    MODEL_DIR = os.path.join(BASE_DIR, '../model')

# ─── Load Models ──────────────────────────────────────────────────────────────
try:
    claim_model = joblib.load(os.path.join(MODEL_DIR, 'best_claim_model.pkl'))
    provider_model = joblib.load(os.path.join(MODEL_DIR, 'best_provider_model.pkl'))
    cms_model = joblib.load(os.path.join(MODEL_DIR, 'cms_anomaly_model.pkl'))
except Exception as e:
    print(f"Error loading models: {e}")
    claim_model, provider_model, cms_model = None, None, None

# ─── Existing ML Inference Helpers ────────────────────────────────────────────

def _get_risk_level(score: float) -> str:
    if score <= 30: return "LOW"
    elif score <= 60: return "MEDIUM"
    else: return "HIGH"

def _get_recommendations(risk_level: str) -> list:
    if risk_level == "HIGH":
        return [
            "Verify the submitted invoice immediately.",
            "Review previous claims associated with the policyholder.",
            "Validate provider and claimant information.",
            "Suspend payment until manual review is complete."
        ]
    elif risk_level == "MEDIUM":
        return [
            "Flag for secondary review.",
            "Request additional supporting documents from the provider.",
            "Check for recent anomalies in provider history."
        ]
    return [
        "Process claim automatically.",
        "No further action required."
    ]

# ─── Existing ML Inference Functions (unchanged) ──────────────────────────────

def analyze_claim(request: ClaimRequest):
    if not claim_model:
        raise RuntimeError("Claim model not loaded.")
        
    features = claim_model.named_steps['model'].feature_names_in_ if hasattr(claim_model.named_steps['model'], 'feature_names_in_') else []
    if not len(features):
        features = ['Claim_Amount', 'Patient_Age', 'Number_of_Procedures', 'Length_of_Stay_Days', 'Deductible_Amount', 'CoPay_Amount', 'Number_of_Previous_Claims_Patient', 'Number_of_Previous_Claims_Provider', 'Provider_Patient_Distance_Miles', 'Claim_Submitted_Late', 'Service_to_Claim_Days', 'Policy_Days_Left', 'Patient_Gender_Male', 'Patient_Gender_Other', 'Provider_Type_Hospital', 'Provider_Type_Laboratory', 'Provider_Type_Pharmacy', 'Provider_Type_Specialist Office', 'Provider_Type_Urgent Care', 'Provider_Specialty_Dermatology', 'Provider_Specialty_General Practice', 'Provider_Specialty_Neurology', 'Provider_Specialty_Oncology', 'Provider_Specialty_Orthopedics', 'Provider_Specialty_Pediatrics', 'Provider_Specialty_Physical Therapy', 'Provider_Specialty_Psychiatry', 'Provider_Specialty_Radiology', 'Admission_Type_Emergency', 'Admission_Type_Newborn', 'Admission_Type_Trauma', 'Admission_Type_Urgent', 'Discharge_Type_Deceased', 'Discharge_Type_Home', 'Discharge_Type_Rehab/Skilled Nursing', 'Discharge_Type_Transfer to another facility', 'Service_Type_Emergency Room', 'Service_Type_Inpatient', 'Service_Type_Laboratory', 'Service_Type_Outpatient', 'Service_Type_Pharmacy']

    data = {f: 0 for f in features}
    data['Claim_Amount'] = request.claim_amount
    data['Patient_Age'] = request.patient_age
    data['Number_of_Procedures'] = request.number_of_procedures
    data['Length_of_Stay_Days'] = request.length_of_stay_days
    data['Deductible_Amount'] = request.deductible_amount
    data['CoPay_Amount'] = request.copay_amount
    data['Number_of_Previous_Claims_Patient'] = request.number_of_previous_claims_patient
    data['Number_of_Previous_Claims_Provider'] = request.number_of_previous_claims_provider
    data['Provider_Patient_Distance_Miles'] = request.provider_patient_distance_miles
    data['Claim_Submitted_Late'] = request.claim_submitted_late
    data['Service_to_Claim_Days'] = request.service_to_claim_days
    data['Policy_Days_Left'] = request.policy_days_left
    
    if f"Patient_Gender_{request.patient_gender}" in data:
        data[f"Patient_Gender_{request.patient_gender}"] = 1
    if f"Provider_Type_{request.provider_type}" in data:
        data[f"Provider_Type_{request.provider_type}"] = 1
    if f"Provider_Specialty_{request.provider_specialty}" in data:
        data[f"Provider_Specialty_{request.provider_specialty}"] = 1
    if f"Admission_Type_{request.admission_type}" in data:
        data[f"Admission_Type_{request.admission_type}"] = 1
    if f"Discharge_Type_{request.discharge_type}" in data:
        data[f"Discharge_Type_{request.discharge_type}"] = 1
    if f"Service_Type_{request.service_type}" in data:
        data[f"Service_Type_{request.service_type}"] = 1
        
    df = pd.DataFrame([data])
    prob = claim_model.predict_proba(df)[0][1]
    score = float(prob * 100)
    risk_level = _get_risk_level(score)
    
    risk_factors = []
    model_step = claim_model.named_steps['model']
    if hasattr(model_step, 'feature_importances_'):
        imp = model_step.feature_importances_
        active_features = []
        for i, f in enumerate(features):
            val = data[f]
            if val > 0:
                active_features.append((f, imp[i], val))
        active_features.sort(key=lambda x: x[1], reverse=True)
        for f, importance, val in active_features[:3]:
            if risk_level == "HIGH":
                impact = "HIGH" if importance > 0.05 else "MODERATE SIGNAL"
            elif risk_level == "MEDIUM":
                impact = "ELEVATED SIGNAL" if importance > 0.05 else "MODERATE SIGNAL"
            else:
                impact = "MODERATE SIGNAL" if importance > 0.05 else "MINOR INDICATOR"
            risk_factors.append({
                "factor": f.replace('_', ' '),
                "impact": impact,
                "explanation": f"The value for {f.replace('_', ' ')} contributes to the model's risk assessment."
            })
            
    prediction_text = "HIGH RISK - INVESTIGATION RECOMMENDED" if risk_level == "HIGH" else "NORMAL - LOW RISK"
    
    return {
        "claim_id": str(uuid.uuid4()),
        "fraud_risk_score": round(score, 2),
        "risk_level": risk_level,
        "prediction": prediction_text,
        "risk_factors": risk_factors,
        "recommendation": _get_recommendations(risk_level),
        "model_information": {
            "model": "Regularized XGBoost",
            "prediction_type": "Fraud Risk Assessment"
        }
    }

def analyze_provider(request: ProviderRequest):
    if not provider_model:
        raise RuntimeError("Provider model not loaded.")
        
    features = provider_model.feature_names_in_ if hasattr(provider_model, 'feature_names_in_') else []
    if not len(features):
        features = ['Num_Unique_Beneficiaries', 'Total_Claims', 'InscClaimAmtReimbursed_sum', 'InscClaimAmtReimbursed_mean', 'InscClaimAmtReimbursed_max', 'DeductibleAmtPaid_sum', 'DeductibleAmtPaid_mean', 'DeductibleAmtPaid_max', 'Total_Inpatient_Claims', 'Claim_Duration_mean', 'Age_mean', 'Num_Diagnosis_mean', 'Num_Procedures_mean', 'RenalDiseaseIndicator_mean', 'Gender_mean', 'IPAnnualReimbursementAmt_mean', 'IPAnnualDeductibleAmt_mean', 'OPAnnualReimbursementAmt_mean', 'OPAnnualDeductibleAmt_mean', 'ChronicCond_Alzheimer_mean', 'ChronicCond_Heartfailure_mean', 'ChronicCond_KidneyDisease_mean', 'ChronicCond_Cancer_mean', 'ChronicCond_ObstrPulmonary_mean', 'ChronicCond_Depression_mean', 'ChronicCond_Diabetes_mean', 'ChronicCond_IschemicHeart_mean', 'ChronicCond_Osteoporasis_mean', 'ChronicCond_rheumatoidarthritis_mean', 'ChronicCond_stroke_mean', 'Total_Outpatient_Claims']
        
    data = {}
    for f in features:
        req_dict = request.model_dump()
        matched = False
        for k, v in req_dict.items():
            if k.replace('_', '').lower() == f.replace('_', '').lower():
                data[f] = v
                matched = True
                break
        if not matched:
            data[f] = 0.0
            
    df = pd.DataFrame([data])
    prob = provider_model.predict_proba(df)[0][1]
    score = float(prob * 100)
    risk_level = _get_risk_level(score)
    
    top_factors = []
    if hasattr(provider_model, 'coef_'):
        coef = provider_model.coef_[0]
        indices = np.argsort(coef)[::-1]
        for i in range(3):
            if coef[indices[i]] > 0:
                f_name = features[indices[i]]
                top_factors.append({
                    "factor": f_name,
                    "impact": "INCREASES RISK",
                    "explanation": f"High values in {f_name} strongly correlate with fraudulent provider behavior."
                })
                
    return {
        "provider_id": str(uuid.uuid4()),
        "fraud_risk_score": round(score, 2),
        "risk_level": risk_level,
        "top_factors": top_factors
    }

def analyze_anomaly(request: AnomalyRequest):
    if not cms_model:
        raise RuntimeError("CMS anomaly model not loaded.")
        
    data = {
        'Procedure_Category': request.procedure_category,
        'Count': request.count,
        'Profile_Display_Indicator': request.profile_display_indicator
    }
    df = pd.DataFrame([data])
    score_val = cms_model.decision_function(df)[0]
    pred = cms_model.predict(df)[0]
    anomaly_percentage = max(0.0, min(100.0, float((0.5 - score_val) * 100)))
    
    if anomaly_percentage > 60:
        status = "SUSPICIOUS PATTERN"
        rec = "High anomaly detected. This utilization pattern significantly deviates from the norm."
    elif anomaly_percentage > 30:
        status = "MODERATE ANOMALY"
        rec = "Moderate anomaly detected. Monitor this provider's billing patterns."
    else:
        status = "NORMAL PATTERN"
        rec = "No unusual patterns detected."
    
    return {
        "anomaly_score": round(anomaly_percentage, 2),
        "anomaly_status": status,
        "recommendation": rec
    }


# ─── New: Medicine Reference Matching ────────────────────────────────────────

# Mapping of ICD-10 code prefixes to canonical diagnosis names (for matching flexibility)
_ICD_ALIASES: dict[str, list[str]] = {
    "E11": ["type 2 diabetes", "diabetes mellitus", "t2dm"],
    "I10": ["hypertension", "essential hypertension", "high blood pressure"],
    "J18": ["pneumonia", "community acquired pneumonia", "cap", "lower respiratory"],
    "A09": ["gastroenteritis", "diarrhoea", "diarrhea", "acute gastroenteritis", "watery diarrhoea"],
    "A07": ["giardiasis", "giardia", "protozoal", "intestinal protozoa", "amoebiasis", "amebiasis"],
    "N39": ["urinary tract infection", "uti", "cystitis", "uncomplicated uti"],
    "N10": ["pyelonephritis", "complicated uti", "upper urinary tract", "kidney infection"],
    "J45": ["asthma", "bronchial asthma", "bronchospasm"],
    "D50": ["anaemia", "anemia", "iron deficiency", "iron deficiency anaemia"],
    "E03": ["hypothyroidism", "underactive thyroid", "thyroid deficiency"],
    "K35": ["appendicitis", "acute appendicitis", "perforated appendix"],
    "A90": ["dengue", "dengue fever", "dengue haemorrhagic"],
}


def _resolve_indication_match(medicine_ref: dict, diagnosis_name: str, icd_code: str) -> str:
    """
    Determine the match status between a medicine reference entry and a given diagnosis.

    Returns one of:
      VERIFIED_MATCH        — medicine's indication list explicitly covers the ICD code or diagnosis name
      POSSIBLE_MATCH        — medicine is in the correct drug class for the condition (alias match)
      NO_VERIFIED_MATCH     — medicine found in reference but no link to this diagnosis
      INSUFFICIENT_INFORMATION — no diagnosis name or ICD code provided
    """
    if not diagnosis_name and not icd_code:
        return "INSUFFICIENT_INFORMATION"

    indications: list = medicine_ref.get("indications", [])
    indications_lower = [str(i).lower() for i in indications]

    # Step 1: Direct ICD code match
    if icd_code:
        code_prefix = icd_code[:3].upper()
        for ind in indications:
            if str(ind).upper().startswith(code_prefix):
                return "VERIFIED_MATCH"

    # Step 2: Diagnosis name substring match against indications
    diag_lower = diagnosis_name.strip().lower()
    for ind in indications_lower:
        if diag_lower in ind or ind in diag_lower:
            return "VERIFIED_MATCH"

    # Step 3: ICD alias lookup for possible match
    if icd_code:
        code_prefix = icd_code[:3].upper()
        aliases = _ICD_ALIASES.get(code_prefix, [])
        for alias in aliases:
            for ind in indications_lower:
                if alias in ind or ind in alias:
                    return "VERIFIED_MATCH"

    # Step 4: Cross-check diagnosis name against alias table
    for code_prefix, aliases in _ICD_ALIASES.items():
        for alias in aliases:
            if alias in diag_lower or diag_lower in alias:
                # The diagnosis matches an alias group — check if medicine's indications match that group
                for ind in indications_lower:
                    if any(a in ind for a in aliases):
                        return "POSSIBLE_MATCH"
                break

    return "NO_VERIFIED_MATCH"


def resolve_medicine_status(medicine_name: str, diagnosis_name: str, icd_code: str) -> tuple[str, str]:
    """
    Look up a medicine in the reference database and return (status, explanation).
    """
    if not medicine_name or not medicine_name.strip():
        return ("INSUFFICIENT_INFORMATION", "No medicine name provided.")

    ref = db.get_medicine_reference(medicine_name)
    if ref is None:
        return (
            "NO_VERIFIED_MATCH",
            f"'{medicine_name}' was not found in the medicine reference database. "
            "This does not automatically indicate fraud; the medicine may be valid but unlisted."
        )

    status = _resolve_indication_match(ref, diagnosis_name, icd_code)
    source = ref.get("source", "WHO EML")

    if status == "VERIFIED_MATCH":
        explanation = (
            f"'{medicine_name}' is listed in the reference database ({source}) "
            f"with a confirmed indication matching the recorded diagnosis."
        )
    elif status == "POSSIBLE_MATCH":
        explanation = (
            f"'{medicine_name}' is listed in the reference database ({source}) "
            f"but its recorded indications do not exactly match the diagnosis '{diagnosis_name}'. "
            "A clinical review is recommended."
        )
    else:
        explanation = (
            f"'{medicine_name}' is listed in the reference database ({source}) "
            f"but no indication matching '{diagnosis_name}' was found. "
            "This warrants investigation."
        )

    return (status, explanation)


# ─── New: Claim Verification Logic ───────────────────────────────────────────

def verify_claim_authenticity(claim_id: str) -> dict:
    """
    Run all 11 authenticity checks for an insurance claim and return a structured
    ClaimVerification record.

    IMPORTANT: This function produces an investigation aid only. It does NOT determine
    guilt, fraud, or claim rejection. Every flagged item requires human review.
    """
    now = datetime.now(timezone.utc).isoformat()
    verification_id = f"FL-VER-{uuid.uuid4().hex[:8].upper()}"

    missing_records: list[str] = []
    discrepancies: list[str] = []
    medicine_details: list[dict] = []

    # Initialise all check flags to False (pessimistic)
    patient_id_valid = False
    hospital_match = False
    encounter_exists = False
    encounter_patient_match = False
    encounter_hospital_match = False
    prescription_match = False
    medicine_match = False
    bill_match = False
    duplicate_claim = False

    # ── Check 1: Claim exists ─────────────────────────────────────────────────
    claim = db.get_claim_by_id(claim_id)
    if claim is None:
        return {
            "verification_id": verification_id,
            "claim_id": claim_id,
            "verified_at": now,
            "patient_id_valid": False,
            "hospital_match": False,
            "encounter_exists": False,
            "encounter_patient_match": False,
            "encounter_hospital_match": False,
            "prescription_match": False,
            "medicine_details": [],
            "medicine_match": False,
            "bill_match": False,
            "duplicate_claim": False,
            "missing_records": ["Claim record not found in database"],
            "discrepancies": [f"Claim ID '{claim_id}' does not exist."],
            "overall_status": "INCOMPLETE",
            "investigator_notes": "The claim ID provided was not found. Verification cannot proceed."
        }

    # ── Check 2: Patient exists ───────────────────────────────────────────────
    patient = db.get_patient_by_id(claim["patient_id"])
    if patient is not None:
        patient_id_valid = True
    else:
        missing_records.append("Patient record")
        discrepancies.append(
            f"Patient ID '{claim['patient_id']}' on the claim does not match any registered patient."
        )

    # ── Check 3: Hospital exists ──────────────────────────────────────────────
    hospital = db.get_hospital_by_id(claim["hospital_id"])
    if hospital is not None:
        hospital_match = True
    else:
        missing_records.append("Hospital record")
        discrepancies.append(
            f"Hospital ID '{claim['hospital_id']}' on the claim is not a registered hospital."
        )

    # ── Check 4: Encounter exists ─────────────────────────────────────────────
    encounter = db.get_encounter_by_id(claim["encounter_id"])
    if encounter is not None:
        encounter_exists = True

        # ── Check 5: Encounter belongs to the claimed patient ─────────────────
        if encounter.get("patient_id") == claim["patient_id"]:
            encounter_patient_match = True
        else:
            discrepancies.append(
                f"Encounter '{claim['encounter_id']}' belongs to patient "
                f"'{encounter.get('patient_id')}', not '{claim['patient_id']}' as claimed."
            )

        # ── Check 6: Encounter belongs to the claimed hospital ────────────────
        if encounter.get("hospital_id") == claim["hospital_id"]:
            encounter_hospital_match = True
        else:
            discrepancies.append(
                f"Encounter '{claim['encounter_id']}' is recorded at hospital "
                f"'{encounter.get('hospital_id')}', not '{claim['hospital_id']}' as claimed."
            )
    else:
        missing_records.append("Hospital encounter record")
        discrepancies.append(
            f"Encounter ID '{claim['encounter_id']}' was not found in the records system."
        )

    # ── Check 7 & 8: Prescription and medicines ───────────────────────────────
    prescription = db.get_prescription_by_encounter(claim["encounter_id"])
    if prescription is not None:
        prescription_match = True
        medicines = prescription.get("medicines", [])

        # Retrieve diagnosis for medicine matching context
        issues = db.get_issues_by_encounter(claim["encounter_id"])
        diag_name = issues[0].get("diagnosis_name", "") if issues else ""
        icd_code = issues[0].get("icd_code", "") if issues else ""

        # ── Check 9: Medicine reference matching ──────────────────────────────
        all_verified = True
        for med in medicines:
            med_name = med.get("medicine_name", "")
            status, explanation = resolve_medicine_status(med_name, diag_name, icd_code)
            medicine_details.append({
                "medicine_name": med_name,
                "reference_status": status,
                "explanation": explanation
            })
            if status not in ("VERIFIED_MATCH",):
                all_verified = False

        medicine_match = all_verified
        if not all_verified:
            non_verified = [
                d["medicine_name"] for d in medicine_details
                if d["reference_status"] != "VERIFIED_MATCH"
            ]
            discrepancies.append(
                f"Medicine(s) without a verified reference match: {', '.join(non_verified)}. "
                "Review required — absence from the reference database does not confirm fraud."
            )
    else:
        missing_records.append("Prescription record")
        discrepancies.append(
            f"No prescription found for encounter '{claim['encounter_id']}'."
        )

    # ── Check 10: Billing consistency ────────────────────────────────────────
    bill = db.get_bill_by_encounter(claim["encounter_id"])
    if bill is not None:
        bill_total = float(bill.get("total_amount", 0))
        claim_amount = float(claim.get("claim_amount", 0))
        # Allow a 10% tolerance for rounding / co-pay / insurer-specific deductions
        tolerance = bill_total * 0.10
        if abs(bill_total - claim_amount) <= tolerance:
            bill_match = True
        else:
            discrepancies.append(
                f"Billing discrepancy: Hospital bill total is ₹{bill_total:,.2f} but claimed amount is "
                f"₹{claim_amount:,.2f} (difference: ₹{abs(bill_total - claim_amount):,.2f}, "
                f"exceeds 10% tolerance of ₹{tolerance:,.2f})."
            )
    else:
        missing_records.append("Hospital bill record")
        discrepancies.append(
            f"No hospital bill found for encounter '{claim['encounter_id']}'."
        )

    # ── Check 11: Duplicate claim detection ───────────────────────────────────
    existing_claim = db.get_claim_by_encounter(claim["encounter_id"])
    if existing_claim and existing_claim.get("claim_id") != claim_id:
        duplicate_claim = True
        discrepancies.append(
            f"A claim for encounter '{claim['encounter_id']}' already exists "
            f"(Claim ID: '{existing_claim['claim_id']}'). This may be a duplicate submission."
        )

    # ── Determine overall status ──────────────────────────────────────────────
    critical_checks = [patient_id_valid, encounter_exists, encounter_patient_match, encounter_hospital_match]
    if missing_records and not encounter_exists:
        overall_status = "INCOMPLETE"
    elif not patient_id_valid or not encounter_patient_match or not encounter_hospital_match or duplicate_claim:
        overall_status = "INVALID_REFERENCE"
    elif discrepancies:
        overall_status = "REVIEW_REQUIRED"
    else:
        overall_status = "VERIFIED"

    # ── Generate investigator notes ───────────────────────────────────────────
    check_summary = sum([
        patient_id_valid, hospital_match, encounter_exists,
        encounter_patient_match, encounter_hospital_match,
        prescription_match, medicine_match, bill_match
    ])
    notes_lines = [
        f"Automated consistency check completed. {check_summary}/8 core checks passed.",
        f"Overall status: {overall_status}.",
    ]
    if overall_status == "VERIFIED":
        notes_lines.append(
            "All records are consistent. This is an investigative aid — "
            "final claim decisions must be made by a qualified claims officer."
        )
    elif overall_status == "REVIEW_REQUIRED":
        notes_lines.append(
            f"{len(discrepancies)} discrepancy(ies) identified. "
            "A qualified claims officer should review the flagged items before making a determination. "
            "Discrepancies do not constitute proof of fraud."
        )
    elif overall_status == "INVALID_REFERENCE":
        notes_lines.append(
            "One or more core identity references failed validation. "
            "Escalate to a senior investigator. Do not automatically reject the claim."
        )
    else:
        notes_lines.append(
            "Records are incomplete. Obtain missing documentation before proceeding."
        )

    result = {
        "verification_id": verification_id,
        "claim_id": claim_id,
        "verified_at": now,
        "patient_id_valid": patient_id_valid,
        "hospital_match": hospital_match,
        "encounter_exists": encounter_exists,
        "encounter_patient_match": encounter_patient_match,
        "encounter_hospital_match": encounter_hospital_match,
        "prescription_match": prescription_match,
        "medicine_details": medicine_details,
        "medicine_match": medicine_match,
        "bill_match": bill_match,
        "duplicate_claim": duplicate_claim,
        "missing_records": missing_records,
        "discrepancies": discrepancies,
        "overall_status": overall_status,
        "investigator_notes": " ".join(notes_lines),
    }

    # Persist the verification record
    db.save_verification(result)
    return result
