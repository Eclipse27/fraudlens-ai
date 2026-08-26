import os
import joblib
import pandas as pd
import numpy as np
import uuid
from schemas import ClaimRequest, ProviderRequest, AnomalyRequest

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
if os.path.exists(os.path.join(BASE_DIR, 'model')):
    # When deployed to EB, the model folder is packaged at the same level as services.py
    MODEL_DIR = os.path.join(BASE_DIR, 'model')
else:
    # Local development where backend/ and model/ are sibling directories
    MODEL_DIR = os.path.join(BASE_DIR, '../model')

# Load Models
try:
    claim_model = joblib.load(os.path.join(MODEL_DIR, 'best_claim_model.pkl'))
    provider_model = joblib.load(os.path.join(MODEL_DIR, 'best_provider_model.pkl'))
    cms_model = joblib.load(os.path.join(MODEL_DIR, 'cms_anomaly_model.pkl'))
except Exception as e:
    print(f"Error loading models: {e}")
    claim_model, provider_model, cms_model = None, None, None

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

def analyze_claim(request: ClaimRequest):
    if not claim_model:
        raise RuntimeError("Claim model not loaded.")
        
    features = claim_model.named_steps['model'].feature_names_in_ if hasattr(claim_model.named_steps['model'], 'feature_names_in_') else []
    if not len(features):
        # Fallback if pipeline doesn't expose it easily
        features = ['Claim_Amount', 'Patient_Age', 'Number_of_Procedures', 'Length_of_Stay_Days', 'Deductible_Amount', 'CoPay_Amount', 'Number_of_Previous_Claims_Patient', 'Number_of_Previous_Claims_Provider', 'Provider_Patient_Distance_Miles', 'Claim_Submitted_Late', 'Service_to_Claim_Days', 'Policy_Days_Left', 'Patient_Gender_Male', 'Patient_Gender_Other', 'Provider_Type_Hospital', 'Provider_Type_Laboratory', 'Provider_Type_Pharmacy', 'Provider_Type_Specialist Office', 'Provider_Type_Urgent Care', 'Provider_Specialty_Dermatology', 'Provider_Specialty_General Practice', 'Provider_Specialty_Neurology', 'Provider_Specialty_Oncology', 'Provider_Specialty_Orthopedics', 'Provider_Specialty_Pediatrics', 'Provider_Specialty_Physical Therapy', 'Provider_Specialty_Psychiatry', 'Provider_Specialty_Radiology', 'Admission_Type_Emergency', 'Admission_Type_Newborn', 'Admission_Type_Trauma', 'Admission_Type_Urgent', 'Discharge_Type_Deceased', 'Discharge_Type_Home', 'Discharge_Type_Rehab/Skilled Nursing', 'Discharge_Type_Transfer to another facility', 'Service_Type_Emergency Room', 'Service_Type_Inpatient', 'Service_Type_Laboratory', 'Service_Type_Outpatient', 'Service_Type_Pharmacy']

    data = {f: 0 for f in features}
    
    # Map numerics
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
    
    # Map categoricals
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
    
    # Feature importance reasoning
    risk_factors = []
    model_step = claim_model.named_steps['model']
    
    if hasattr(model_step, 'feature_importances_'):
        imp = model_step.feature_importances_
        # Find highest positive contributing features for THIS input
        # Since tree feature importances are global, we just show top global features that are active in this claim.
        active_features = []
        for i, f in enumerate(features):
            val = data[f]
            if val > 0: # Active boolean or non-zero numeric
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
    # Map camelCase/snake_case to original names
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
    
    # Top factors
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
    
    # Score samples (lower means more anomalous in sklearn isolation forest)
    score_val = cms_model.decision_function(df)[0] 
    pred = cms_model.predict(df)[0]

    # Transform decision_function to a 0-100 anomaly percentage.
    # decision_function usually ranges from roughly -0.5 (very anomalous) to 0.5 (normal)
    # We shift so 0.5 is 0% and -0.5 is 100%
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
