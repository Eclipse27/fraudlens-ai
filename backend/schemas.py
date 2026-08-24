from pydantic import BaseModel, Field
from typing import List, Optional

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
