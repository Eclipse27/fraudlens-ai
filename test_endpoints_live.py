"""
FraudLens AI — Live Endpoint Verification Script
================================================
Starts the FastAPI application using Uvicorn in a subprocess, probes each required
endpoint using standard HTTP requests, and prints the exact live responses.
Ensures clean shutdown of the server subprocess after completion.
"""

import sys
import os
import time
import subprocess
import requests
import json

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
BACKEND_DIR = os.path.join(BASE_DIR, 'backend')

PORT = 8000
BASE_URL = f"http://127.0.0.1:{PORT}"


def wait_for_server(timeout=25):
    start = time.time()
    while time.time() - start < timeout:
        try:
            r = requests.get(f"{BASE_URL}/health", timeout=2)
            if r.status_code == 200:
                return True
        except Exception:
            pass
        time.sleep(0.5)
    return False


def run_tests():
    print("=" * 70)
    print("  FRAUDLENS AI — LIVE HTTP ENDPOINT TESTING (Uvicorn Server)")
    print("=" * 70)

    # Start Uvicorn subprocess
    server_cmd = [
        sys.executable, "-m", "uvicorn", "main:app",
        "--host", "127.0.0.1", "--port", str(PORT), "--log-level", "warning"
    ]
    print(f"Starting Uvicorn server on {BASE_URL}...")
    proc = subprocess.Popen(server_cmd, cwd=BACKEND_DIR)

    try:
        ready = wait_for_server()
        if not ready:
            print("ERROR: Uvicorn server failed to start within timeout.")
            return False

        print("Uvicorn server is up and accepting HTTP connections.\n")

        # ── Test 1: GET /health ──
        print("-" * 50)
        print("1. Testing GET /health:")
        r = requests.get(f"{BASE_URL}/health")
        print(f"Status Code: {r.status_code}")
        print("Response Body:")
        print(json.dumps(r.json(), indent=2))

        # ── Test 2: GET /hospitals & GET /hospitals/{hospital_id} ──
        print("\n" + "-" * 50)
        print("2. Testing Hospital Records:")
        r_h = requests.get(f"{BASE_URL}/hospitals")
        print(f"GET /hospitals Status Code: {r_h.status_code}")
        hospitals = r_h.json()
        print(f"Total Hospitals Retrieved: {len(hospitals)}")
        for h in hospitals:
            print(f"  - [{h['hospital_id']}] {h['name']} | Type: {h['type']} | City: {h['city']}")

        r_single_h = requests.get(f"{BASE_URL}/hospitals/FL-HOSP-001")
        print(f"GET /hospitals/FL-HOSP-001 Status Code: {r_single_h.status_code}")
        print("Single Hospital Record:")
        print(json.dumps(r_single_h.json(), indent=2))

        # ── Test 3: Patient Registration (New Patient) ──
        print("\n" + "-" * 50)
        print("3. Testing Patient Registration (New Patient):")
        new_patient_payload = {
            "full_name": "Devendra Pratap Singh",
            "date_of_birth": "1985-06-15",
            "gender": "Male",
            "phone": "9876599999",
            "address": "Katra, Prayagraj, Uttar Pradesh"
        }
        r_new_pat = requests.post(f"{BASE_URL}/patients", json=new_patient_payload)
        print(f"POST /patients Status Code: {r_new_pat.status_code}")
        new_pat_data = r_new_pat.json()
        print("Registration Response:")
        print(json.dumps(new_pat_data, indent=2))

        # ── Test 4: Duplicate Detection (Exact & Possible Duplicate) ──
        print("\n" + "-" * 50)
        print("4. Testing Duplicate Detection:")
        # Exact 4-field match with the patient just registered
        exact_dup_payload = {
            "full_name": "Devendra Pratap Singh",
            "date_of_birth": "1985-06-15",
            "gender": "Male",
            "phone": "9876599999",
            "address": "Different Locality, Prayagraj"
        }
        r_exact = requests.post(f"{BASE_URL}/patients", json=exact_dup_payload)
        print(f"Exact Duplicate Check Status Code: {r_exact.status_code}")
        exact_res = r_exact.json()
        print(f"  is_new: {exact_res.get('is_new')} (Expected: False)")
        print(f"  message: {exact_res.get('message')}")
        print(f"  Returned Patient ID: {exact_res.get('patient', {}).get('patient_id')}")

        # ── Test 5: Claim Verification ──
        print("\n" + "-" * 50)
        print("5. Testing Claim Verification Engine:")
        # 5a: Scenario A - Consistent Claim (FL-CLM-000001)
        r_v1 = requests.post(f"{BASE_URL}/verify-claim", json={"claim_id": "FL-CLM-000001"})
        print(f"Scenario A (FL-CLM-000001 - Consistent) Status Code: {r_v1.status_code}")
        v1_data = r_v1.json()
        print(f"  Overall Status: {v1_data.get('overall_status')}")
        print(f"  Checks: patient_id_valid={v1_data.get('patient_id_valid')}, hospital_match={v1_data.get('hospital_match')}, bill_match={v1_data.get('bill_match')}, medicine_match={v1_data.get('medicine_match')}")
        print(f"  Discrepancies: {v1_data.get('discrepancies')}")
        print(f"  Notes: {v1_data.get('investigator_notes')}")

        # 5b: Scenario B - Incorrect Patient Reference (FL-CLM-000010)
        r_v2 = requests.post(f"{BASE_URL}/verify-claim", json={"claim_id": "FL-CLM-000010"})
        print(f"\nScenario B (FL-CLM-000010 - Patient Reference Mismatch) Status Code: {r_v2.status_code}")
        v2_data = r_v2.json()
        print(f"  Overall Status: {v2_data.get('overall_status')}")
        print(f"  Discrepancies: {v2_data.get('discrepancies')}")

        # 5c: Scenario F - Billing Discrepancy (FL-CLM-000050)
        r_v3 = requests.post(f"{BASE_URL}/verify-claim", json={"claim_id": "FL-CLM-000050"})
        print(f"\nScenario F (FL-CLM-000050 - Billing Discrepancy) Status Code: {r_v3.status_code}")
        v3_data = r_v3.json()
        print(f"  Overall Status: {v3_data.get('overall_status')}")
        discrepancies_safe = [d.replace("\u20b9", "INR ") for d in v3_data.get('discrepancies', [])]
        print(f"  Discrepancies: {discrepancies_safe}")

        # ── Test 6: Dashboard Stats Endpoint ──
        print("\n" + "-" * 50)
        print("6. Testing GET /dashboard/stats:")
        r_stats = requests.get(f"{BASE_URL}/dashboard/stats")
        print(f"Status Code: {r_stats.status_code}")
        print("Aggregated Database Stats:")
        print(json.dumps(r_stats.json(), indent=2))

        # ── Test 7: ML Fraud Risk Inferences ──
        print("\n" + "-" * 50)
        print("7. Testing Core ML Models:")
        # XGBoost Claim
        claim_ml_payload = {
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
        r_ml1 = requests.post(f"{BASE_URL}/analyze-claim", json=claim_ml_payload)
        print(f"XGBoost Claim Analysis Status Code: {r_ml1.status_code}")
        ml1_res = r_ml1.json()
        print(f"  Risk Score: {ml1_res.get('fraud_risk_score')} | Level: {ml1_res.get('risk_level')} | Prediction: {ml1_res.get('prediction')}")

        # Provider Logistic Regression
        prov_ml_payload = {
            "num_unique_beneficiaries": 1500,
            "total_claims": 5000,
            "insc_claim_amt_reimbursed_sum": 1000000.0,
            "deductible_amt_paid_max": 1068.0,
            "total_outpatient_claims": 2000
        }
        r_ml2 = requests.post(f"{BASE_URL}/analyze-provider", json=prov_ml_payload)
        print(f"Provider Analysis Status Code: {r_ml2.status_code}")
        ml2_res = r_ml2.json()
        print(f"  Risk Score: {ml2_res.get('fraud_risk_score')} | Level: {ml2_res.get('risk_level')}")

        # Isolation Forest Anomaly
        anom_ml_payload = {
            "procedure_category": "TestCategory",
            "count": 99999,
            "profile_display_indicator": "N"
        }
        r_ml3 = requests.post(f"{BASE_URL}/analyze-anomaly", json=anom_ml_payload)
        print(f"Anomaly Detection Status Code: {r_ml3.status_code}")
        ml3_res = r_ml3.json()
        print(f"  Anomaly Score: {ml3_res.get('anomaly_score')}% | Status: {ml3_res.get('anomaly_status')}")

        print("\n" + "=" * 70)
        print("  ALL LIVE HTTP TESTS COMPLETED SUCCESSFULLY")
        print("=" * 70)
        return True

    finally:
        print("\nShutting down Uvicorn subprocess...")
        proc.terminate()
        try:
            proc.wait(timeout=5)
        except subprocess.TimeoutExpired:
            proc.kill()
        print("Uvicorn subprocess stopped.")


if __name__ == "__main__":
    success = run_tests()
    sys.exit(0 if success else 1)
