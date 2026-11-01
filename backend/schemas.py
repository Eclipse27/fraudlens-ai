from pydantic import BaseModel, Field
from typing import Any, List, Optional

if not hasattr(BaseModel, 'model_dump'):
    BaseModel.model_dump = BaseModel.dict

# ─── Existing ML Analysis Models (unchanged) ─────────────────────────────────

class ClaimRequest(BaseModel):
    claim_amount: float = Field(..., ge=0, description="Total amount claimed")
    patient_age: int = Field(..., ge=0, description="Age of the patient")
    number_of_procedures: int = Field(..., ge=0, description="Number of procedures in the claim")
    length_of_stay_days: int = Field(0, ge=0, description="Days stayed in hospital, if applicable")
    deductible_amount: float = Field(0, ge=0, description="Deductible paid")
    copay_amount: float = Field(0, ge=0, description="Copay paid")
    number_of_previous_claims_patient: int = Field(0, ge=0)
    number_of_previous_claims_provider: int = Field(0, ge=0)
    provider_patient_distance_miles: float = Field(0, ge=0)
    claim_submitted_late: int = Field(0, description="1 if late, 0 otherwise")
    service_to_claim_days: int = Field(0, ge=0)
    policy_days_left: int = Field(0)
    
    # Categoricals
    patient_gender: str = Field("Female", description="Male, Female, Other")
    provider_type: str = Field("Hospital", description="Hospital, Laboratory, Pharmacy, Specialist Office, Urgent Care, Clinic")
    provider_specialty: str = Field("General Practice", description="e.g. Cardiology, Dermatology, etc")
    admission_type: str = Field("Elective", description="Elective, Emergency, Newborn, Trauma, Urgent")
    discharge_type: str = Field("Home", description="Home, Deceased, Rehab/Skilled Nursing, Transfer to another facility")
    service_type: str = Field("Inpatient", description="Inpatient, Outpatient, Emergency Room, Laboratory, Pharmacy")

class RiskFactor(BaseModel):
    factor: str
    impact: str
    explanation: str

class ClaimResponse(BaseModel):
    claim_id: str
    fraud_risk_score: float
    risk_level: str
    prediction: str
    risk_factors: List[RiskFactor]
    recommendation: List[str]
    model_information: dict

class ProviderRequest(BaseModel):
    num_unique_beneficiaries: float = 0
    total_claims: float = 0
    insc_claim_amt_reimbursed_sum: float = 0
    insc_claim_amt_reimbursed_mean: float = 0
    insc_claim_amt_reimbursed_max: float = 0
    deductible_amt_paid_sum: float = 0
    deductible_amt_paid_mean: float = 0
    deductible_amt_paid_max: float = 0
    total_inpatient_claims: float = 0
    claim_duration_mean: float = 0
    age_mean: float = 0
    num_diagnosis_mean: float = 0
    num_procedures_mean: float = 0
    renal_disease_indicator_mean: float = 0
    gender_mean: float = 0
    ip_annual_reimbursement_amt_mean: float = 0
    ip_annual_deductible_amt_mean: float = 0
    op_annual_reimbursement_amt_mean: float = 0
    op_annual_deductible_amt_mean: float = 0
    chronic_cond_alzheimer_mean: float = 0
    chronic_cond_heartfailure_mean: float = 0
    chronic_cond_kidneydisease_mean: float = 0
    chronic_cond_cancer_mean: float = 0
    chronic_cond_obstrpulmonary_mean: float = 0
    chronic_cond_depression_mean: float = 0
    chronic_cond_diabetes_mean: float = 0
    chronic_cond_ischemicheart_mean: float = 0
    chronic_cond_osteoporasis_mean: float = 0
    chronic_cond_rheumatoidarthritis_mean: float = 0
    chronic_cond_stroke_mean: float = 0
    total_outpatient_claims: float = 0

class ProviderResponse(BaseModel):
    provider_id: str
    fraud_risk_score: float
    risk_level: str
    top_factors: List[dict]

class AnomalyRequest(BaseModel):
    procedure_category: str
    count: int
    profile_display_indicator: str = Field("Y", description="Y or N")

class AnomalyResponse(BaseModel):
    anomaly_score: float
    anomaly_status: str
    recommendation: str

class HistoryRecord(BaseModel):
    id: str
    type: str  # 'Claim' | 'Provider' | 'Anomaly'
    timestamp: str
    riskScore: float
    riskLevel: str
    status: str
    result: Any  # The full analysis result object

# ─── New Healthcare Records Models ───────────────────────────────────────────

class PatientCreate(BaseModel):
    full_name: str = Field(..., min_length=2, description="Full name of the patient")
    date_of_birth: str = Field(..., description="Date of birth in YYYY-MM-DD format")
    gender: str = Field(..., description="Male / Female / Other")
    phone: str = Field(..., description="10-digit phone number, e.g. 9876543210")
    address: Optional[str] = Field("", description="City-level address")

class PatientResponse(BaseModel):
    patient_id: str
    full_name: str
    date_of_birth: str
    gender: str
    phone: str
    address: str
    created_at: str
    potential_duplicate_flag: bool = False

class PatientRegistrationResponse(BaseModel):
    patient: PatientResponse
    is_new: bool
    message: str

class HospitalResponse(BaseModel):
    hospital_id: str
    name: str
    address: str
    city: str
    state: str
    type: str
    pincode: str

class EncounterCreate(BaseModel):
    patient_id: str = Field(..., description="FL-PAT-XXXXXX patient identifier")
    hospital_id: str = Field(..., description="FL-HOSP-XXX hospital identifier")
    admission_date: str = Field(..., description="Admission date YYYY-MM-DD")
    discharge_date: Optional[str] = Field(None, description="Discharge date YYYY-MM-DD or null if ongoing")
    encounter_type: str = Field("OPD", description="OPD / IPD / Emergency")
    attending_doctor: Optional[str] = Field("", description="Name of attending doctor")
    department: Optional[str] = Field("", description="e.g. Cardiology, General Medicine")
    notes: Optional[str] = Field("", description="Clinical notes")

class EncounterResponse(BaseModel):
    encounter_id: str
    patient_id: str
    hospital_id: str
    admission_date: str
    discharge_date: Optional[str]
    encounter_type: str
    attending_doctor: str
    department: str
    notes: str
    created_at: str

class MedicalIssueCreate(BaseModel):
    encounter_id: str
    patient_id: str
    diagnosis_name: str = Field(..., description="Diagnosis name, e.g. Type 2 Diabetes Mellitus")
    icd_code: Optional[str] = Field("", description="ICD-10 code, e.g. E11")
    severity: str = Field("Moderate", description="Mild / Moderate / Severe")

class MedicalIssueResponse(BaseModel):
    issue_id: str
    encounter_id: str
    patient_id: str
    diagnosis_name: str
    icd_code: str
    severity: str
    recorded_at: str

class PrescriptionMedicineCreate(BaseModel):
    medicine_name: str
    generic_name: Optional[str] = ""
    strength: Optional[str] = ""
    dosage: str = Field(..., description="e.g. 500mg")
    frequency: str = Field(..., description="e.g. Twice daily")
    duration_days: int = Field(..., ge=1)
    quantity: Optional[int] = Field(0, ge=0)

class PrescriptionCreate(BaseModel):
    encounter_id: str
    patient_id: str
    issue_id: str
    prescribed_by: str
    medicines: List[PrescriptionMedicineCreate] = Field(...)

class MedicineVerificationDetail(BaseModel):
    medicine_name: str
    reference_status: str  # VERIFIED_MATCH / POSSIBLE_MATCH / NO_VERIFIED_MATCH / INSUFFICIENT_INFORMATION
    explanation: str

class PrescriptionMedicineResponse(BaseModel):
    pm_id: str
    prescription_id: str
    medicine_name: str
    generic_name: str
    strength: str
    dosage: str
    frequency: str
    duration_days: int
    quantity: int
    reference_status: str

class PrescriptionResponse(BaseModel):
    prescription_id: str
    encounter_id: str
    patient_id: str
    issue_id: str
    prescribed_by: str
    prescribed_at: str
    medicines: List[PrescriptionMedicineResponse]

class MedicineReferenceResponse(BaseModel):
    medicine_name: str
    generic_name: str
    indications: List[str]
    drug_class: str
    dosage_forms: List[str]
    source: str
    source_url: str
    verification_status: str  # VERIFIED / UNVERIFIED

class BillItemCreate(BaseModel):
    description: str
    amount: float = Field(..., ge=0)

class HospitalBillCreate(BaseModel):
    encounter_id: str
    patient_id: str
    hospital_id: str
    itemized: List[BillItemCreate] = Field(...)

class HospitalBillResponse(BaseModel):
    bill_id: str
    encounter_id: str
    patient_id: str
    hospital_id: str
    total_amount: float
    itemized: List[dict]
    billed_at: str

class InsuranceClaimCreate(BaseModel):
    patient_id: str
    hospital_id: str
    encounter_id: str
    bill_id: str
    claim_amount: float = Field(..., ge=0)
    policy_number: str
    insurer: str

class InsuranceClaimResponse(BaseModel):
    claim_id: str
    patient_id: str
    hospital_id: str
    encounter_id: str
    bill_id: str
    claim_amount: float
    submission_date: str
    policy_number: str
    insurer: str
    status: str

class VerifyClaimRequest(BaseModel):
    claim_id: str

class ClaimVerificationResponse(BaseModel):
    verification_id: str
    claim_id: str
    verified_at: str
    # Individual check results
    patient_id_valid: bool
    hospital_match: bool
    encounter_exists: bool
    encounter_patient_match: bool
    encounter_hospital_match: bool
    prescription_match: bool
    medicine_details: List[MedicineVerificationDetail]
    medicine_match: bool
    bill_match: bool
    duplicate_claim: bool
    # Summary
    missing_records: List[str]
    discrepancies: List[str]
    overall_status: str  # VERIFIED / REVIEW_REQUIRED / INCOMPLETE / INVALID_REFERENCE
    investigator_notes: str
