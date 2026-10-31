import requests
import json
import sys

base_url = 'http://localhost:8000'

def test_health():
    res = requests.get(f"{base_url}/health")
    print("GET /health:", res.json())

def test_model_info():
    res = requests.get(f"{base_url}/model-info")
    print("GET /model-info status:", res.status_code)

def test_claim():
    # High risk
    payload_high = {
        "claim_amount": 100000.0,
        "patient_age": 45,
        "number_of_procedures": 15,
        "length_of_stay_days": 2,
        "deductible_amount": 0,
        "copay_amount": 0,
        "number_of_previous_claims_patient": 10,
        "number_of_previous_claims_provider": 500,
        "provider_patient_distance_miles": 500.0,
        "claim_submitted_late": 1,
        "service_to_claim_days": 100,
        "policy_days_left": 5,
        "patient_gender": "Male",
        "provider_type": "Specialist Office",
        "provider_specialty": "General Practice",
        "admission_type": "Emergency",
        "discharge_type": "Home",
        "service_type": "Inpatient"
    }
    res = requests.post(f"{base_url}/analyze-claim", json=payload_high)
    print("\nPOST /analyze-claim (HIGH RISK):", json.dumps(res.json(), indent=2))
    
    # Low risk
    payload_low = payload_high.copy()
    payload_low.update({
        "claim_amount": 100.0,
        "number_of_procedures": 1,
        "provider_patient_distance_miles": 2.0,
        "claim_submitted_late": 0,
        "service_to_claim_days": 1,
        "provider_type": "Hospital"
    })
    res = requests.post(f"{base_url}/analyze-claim", json=payload_low)
    print("\nPOST /analyze-claim (LOW RISK):", json.dumps(res.json(), indent=2))

def test_provider():
    payload = {
        "num_unique_beneficiaries": 1500,
        "total_claims": 5000,
        "insc_claim_amt_reimbursed_sum": 1000000.0,
        "deductible_amt_paid_max": 1068.0,
        "total_outpatient_claims": 2000
    }
    res = requests.post(f"{base_url}/analyze-provider", json=payload)
    print("\nPOST /analyze-provider:", json.dumps(res.json(), indent=2))

def test_anomaly():
    payload = {
        "procedure_category": "TestCategory",
        "count": 99999,
        "profile_display_indicator": "N"
    }
    res = requests.post(f"{base_url}/analyze-anomaly", json=payload)
    print("\nPOST /analyze-anomaly:", json.dumps(res.json(), indent=2))

# ─── Phase 2 Tests: Healthcare Identity & Claim Provenance ──────────────────

def test_hospitals():
    res = requests.get(f"{base_url}/hospitals")
    data = res.json()
    print(f"\nGET /hospitals: {len(data)} hospitals retrieved")
    for h in data:
        print(f"  - [{h['hospital_id']}] {h['name']} ({h['city']}, {h['type']})")

def test_medicines():
    res = requests.get(f"{base_url}/medicines")
    data = res.json()
    print(f"\nGET /medicines: {len(data)} reference entries loaded")
    
    # Lookup specific verified medicine
    lookup_res = requests.get(f"{base_url}/medicines/lookup?name=Metformin")
    print("GET /medicines/lookup?name=Metformin:", json.dumps(lookup_res.json(), indent=2))

def test_patients():
    res = requests.get(f"{base_url}/patients")
    pts = res.json()
    print(f"\nGET /patients: {len(pts)} registered patients found")
    
    # Test deduplication with known patient 1
    dup_payload = {
        "full_name": "Ramesh Kumar Verma",
        "date_of_birth": "1978-04-12",
        "gender": "Male",
        "phone": "9876543201",
        "address": "Civil Lines, Prayagraj"
    }
    dup_res = requests.post(f"{base_url}/patients", json=dup_payload)
    print("POST /patients (Duplicate Check):", json.dumps(dup_res.json(), indent=2))

def test_claim_verification():
    print("\n─── 11-Point Claim Verification Tests ───")
    
    # 1. Clean claim
    res1 = requests.post(f"{base_url}/verify-claim", json={"claim_id": "FL-CLM-000001"})
    print("Test 1 (FL-CLM-000001 - Clean):", res1.json().get("overall_status"))
    
    # 2. Duplicate claim
    res2 = requests.post(f"{base_url}/verify-claim", json={"claim_id": "FL-CLM-000002"})
    print("Test 2 (FL-CLM-000002 - Duplicate):", res2.json().get("overall_status"))
    
    # 3. Billing mismatch claim
    res4 = requests.post(f"{base_url}/verify-claim", json={"claim_id": "FL-CLM-000004"})
    print("Test 3 (FL-CLM-000004 - Mismatch):", res4.json().get("overall_status"), res4.json().get("discrepancies"))

if __name__ == '__main__':
    test_health()
    test_model_info()
    test_claim()
    test_provider()
    test_anomaly()
    # Phase 2
    try:
        test_hospitals()
        test_medicines()
        test_patients()
        test_claim_verification()
    except Exception as e:
        print(f"\nPhase 2 endpoints test note: {e}")
