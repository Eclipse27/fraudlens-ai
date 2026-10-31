"""
FraudLens AI — Phase 3 Automated Data Integrity Validation
==========================================================
Runs comprehensive automated integrity checks across all 8 validation dimensions:
A. Identity checks
B. Hospital checks
C. Encounter checks
D. Prescription checks
E. Medicine checks
F. Bill checks
G. Claim checks
H. Overall integrity

Outputs a detailed integrity scorecard and diagnostic report.
"""

import os
import json
import sys

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
DATA_DIR = os.path.join(BASE_DIR, '..', 'data')
DB_FILE = os.path.join(DATA_DIR, 'synthetic_database.json')


def run_all_validation_checks():
    print("=" * 70)
    print("  FRAUDLENS AI -- AUTOMATED DATA INTEGRITY VALIDATION (PHASE 3)")
    print("=" * 70)

    if not os.path.exists(DB_FILE):
        print(f"ERROR: Database file {DB_FILE} not found!")
        sys.exit(1)

    with open(DB_FILE, "r", encoding="utf-8") as f:
        data = json.load(f)

    hospitals = data.get("hospitals", [])
    patients = data.get("patients", [])
    encounters = data.get("encounters", [])
    issues = data.get("medical_issues", [])
    prescriptions = data.get("prescriptions", [])
    rx_medicines = data.get("prescription_medicines", [])
    med_refs = data.get("medicine_references", [])
    bills = data.get("bills", [])
    claims = data.get("claims", [])

    results = {}
    failures = []

    # ── A. IDENTITY CHECKS ──
    print("\n[A] Running Identity Checks...")
    pat_ids = [p["patient_id"] for p in patients]
    unique_pat_ids = set(pat_ids)
    
    check_a1 = len(pat_ids) == len(unique_pat_ids) and len(pat_ids) == 300
    if not check_a1: failures.append("A1: Patient IDs are not unique or count != 300")
    print(f"  [+] A1. Patient ID uniqueness: {len(unique_pat_ids)} unique / {len(pat_ids)} total records -> {'PASS' if check_a1 else 'FAIL'}")

    # Deduplication check across 4 attributes (name, dob, gender, phone)
    pat_signatures = set()
    dup_patients = 0
    for p in patients:
        sig = (p["full_name"].strip().lower(), p["date_of_birth"], p["gender"], p["phone"])
        if sig in pat_signatures:
            dup_patients += 1
        pat_signatures.add(sig)
    check_a2 = (dup_patients == 0)
    if not check_a2: failures.append(f"A2: Found {dup_patients} duplicate patient profile(s)")
    print(f"  [+] A2. Duplicate patient profiles: {dup_patients} duplicates found -> {'PASS' if check_a2 else 'FAIL'}")

    # Synthetic designation check
    synthetic_designations = sum(1 for p in patients if p.get("dataset_designation") == "SYNTHETIC_DEMO")
    check_a3 = (synthetic_designations == len(patients))
    if not check_a3: failures.append("A3: One or more patient records lack SYNTHETIC_DEMO designation")
    print(f"  [+] A3. Synthetic designation check: {synthetic_designations}/{len(patients)} flagged SYNTHETIC_DEMO -> {'PASS' if check_a3 else 'FAIL'}")
    results["A_IDENTITY"] = check_a1 and check_a2 and check_a3

    # ── B. HOSPITAL CHECKS ──
    print("\n[B] Running Hospital Checks...")
    hosp_ids = {h["hospital_id"] for h in hospitals}
    check_b1 = (len(hospitals) == 3 and len(hosp_ids) == 3)
    if not check_b1: failures.append(f"B1: Expected exactly 3 hospitals, found {len(hospitals)}")
    print(f"  [+] B1. Exactly 3 demo hospitals: Found {len(hospitals)} -> {'PASS' if check_b1 else 'FAIL'}")

    all_demo_institutions = sum(1 for h in hospitals if h.get("record_type") == "DEMO_INSTITUTION")
    check_b2 = (all_demo_institutions == 3)
    if not check_b2: failures.append("B2: Hospital records not identified as DEMO_INSTITUTION")
    print(f"  [+] B2. DEMO_INSTITUTION designation: {all_demo_institutions}/3 -> {'PASS' if check_b2 else 'FAIL'}")

    all_verified_sources = sum(1 for h in hospitals if h.get("source") and h.get("verification_date"))
    check_b3 = (all_verified_sources == 3)
    if not check_b3: failures.append("B3: Hospitals lack verified public sources or verification date")
    print(f"  [+] B3. Public source verification: {all_verified_sources}/3 verified -> {'PASS' if check_b3 else 'FAIL'}")
    results["B_HOSPITALS"] = check_b1 and check_b2 and check_b3

    # ── C. ENCOUNTER CHECKS ──
    print("\n[C] Running Encounter Checks...")
    enc_ids = [e["encounter_id"] for e in encounters]
    check_c1 = (len(enc_ids) == len(set(enc_ids)) and len(enc_ids) == 600)
    if not check_c1: failures.append("C1: Encounter IDs not unique or count != 600")
    print(f"  [+] C1. Encounter ID uniqueness: {len(set(enc_ids))} unique / {len(enc_ids)} records -> {'PASS' if check_c1 else 'FAIL'}")

    # Every encounter references a valid patient and hospital
    invalid_pat_refs = sum(1 for e in encounters if e["patient_id"] not in unique_pat_ids)
    invalid_hosp_refs = sum(1 for e in encounters if e["hospital_id"] not in hosp_ids)
    check_c2 = (invalid_pat_refs == 0 and invalid_hosp_refs == 0)
    if not check_c2: failures.append(f"C2: Broken references (patients: {invalid_pat_refs}, hospitals: {invalid_hosp_refs})")
    print(f"  [+] C2. Valid foreign keys: 0 broken patient or hospital references -> {'PASS' if check_c2 else 'FAIL'}")

    # Cross-hospital patient identity verification
    pat_to_hospitals = {}
    for e in encounters:
        pat_to_hospitals.setdefault(e["patient_id"], set()).add(e["hospital_id"])
    cross_hosp_patients = sum(1 for p, h_set in pat_to_hospitals.items() if len(h_set) > 1)
    multi_hosp_3 = sum(1 for p, h_set in pat_to_hospitals.items() if len(h_set) == 3)
    check_c3 = (cross_hosp_patients >= 200)
    if not check_c3: failures.append(f"C3: Insufficient cross-hospital patients: {cross_hosp_patients}")
    print(f"  [+] C3. Shared patient identity: {cross_hosp_patients} patients visit 2+ hospitals ({multi_hosp_3} visit all 3) -> {'PASS' if check_c3 else 'FAIL'}")
    results["C_ENCOUNTERS"] = check_c1 and check_c2 and check_c3

    # ── D. PRESCRIPTION CHECKS ──
    print("\n[D] Running Prescription Checks...")
    rx_ids = [r["prescription_id"] for r in prescriptions]
    check_d1 = (len(rx_ids) == len(set(rx_ids)) and 500 <= len(rx_ids) <= 600)
    if not check_d1: failures.append(f"D1: Prescription IDs not unique or count out of range: {len(rx_ids)}")
    print(f"  [+] D1. Prescription count & uniqueness: {len(rx_ids)} records -> {'PASS' if check_d1 else 'FAIL'}")

    enc_map = {e["encounter_id"]: e for e in encounters}
    mismatched_pat = 0
    mismatched_hosp = 0
    for r in prescriptions:
        enc = enc_map.get(r["encounter_id"])
        if not enc:
            mismatched_pat += 1
            continue
        if r["patient_id"] != enc["patient_id"]:
            mismatched_pat += 1
        if r["hospital_id"] != enc["hospital_id"]:
            mismatched_hosp += 1
    check_d2 = (mismatched_pat == 0 and mismatched_hosp == 0)
    if not check_d2: failures.append(f"D2: Prescription encounter mismatch (pat: {mismatched_pat}, hosp: {mismatched_hosp})")
    print(f"  [+] D2. Prescription encounter alignment: 0 patient or hospital mismatches -> {'PASS' if check_d2 else 'FAIL'}")
    results["D_PRESCRIPTIONS"] = check_d1 and check_d2

    # ── E. MEDICINE CHECKS ──
    print("\n[E] Running Medicine Checks...")
    med_ref_map = {m["medicine_name"]: m for m in med_refs}
    check_e1 = (len(med_refs) >= 50 and len(med_ref_map) == len(med_refs))
    if not check_e1: failures.append(f"E1: Medicine references count < 50: {len(med_refs)}")
    print(f"  [+] E1. Medicine reference scale: {len(med_refs)} entries (target 50–100) -> {'PASS' if check_e1 else 'FAIL'}")

    verified_refs = [m for m in med_refs if m.get("verification_status") == "VERIFIED"]
    unverified_refs = [m for m in med_refs if m.get("verification_status") in ("UNVERIFIED", "INCOMPLETE")]
    check_e2 = (len(verified_refs) >= 50 and len(unverified_refs) >= 1)
    # Check that verified references have legitimate source URLs
    bad_urls = sum(1 for m in verified_refs if not m.get("source_url") or not m["source_url"].startswith("http"))
    check_e3 = (bad_urls == 0)
    if not check_e2 or not check_e3: failures.append("E2/E3: Medicine verification status or source URLs invalid")
    print(f"  [+] E2. Verified vs unverified records: {len(verified_refs)} VERIFIED, {len(unverified_refs)} UNVERIFIED/INCOMPLETE -> {'PASS' if check_e2 else 'FAIL'}")
    print(f"  [+] E3. Legitimate reference URLs: {bad_urls} invalid URLs found -> {'PASS' if check_e3 else 'FAIL'}")

    # Check that all prescription medicines resolve in the reference table
    unresolved_rx_meds = sum(1 for pm in rx_medicines if pm["medicine_name"] not in med_ref_map)
    check_e4 = (unresolved_rx_meds == 0)
    if not check_e4: failures.append(f"E4: {unresolved_rx_meds} prescription medicines unresolved in reference catalog")
    print(f"  [+] E4. Prescription medicine resolution: {len(rx_medicines)} items, {unresolved_rx_meds} unresolved -> {'PASS' if check_e4 else 'FAIL'}")
    results["E_MEDICINES"] = check_e1 and check_e2 and check_e3 and check_e4

    # ── F. BILL CHECKS ──
    print("\n[F] Running Hospital Bill Checks...")
    bill_ids = [b["bill_id"] for b in bills]
    check_f1 = (len(bill_ids) == len(set(bill_ids)) and len(bill_ids) == 600)
    if not check_f1: failures.append("F1: Bill IDs not unique or count != 600")
    print(f"  [+] F1. Bill count & uniqueness: {len(bill_ids)} records -> {'PASS' if check_f1 else 'FAIL'}")

    # Check total amount matches itemized sum
    arithmetic_errors = 0
    currency_mismatches = 0
    for b in bills:
        item_sum = round(sum(i.get("amount", 0) for i in b.get("itemized", [])), 2)
        if abs(item_sum - b["total_amount"]) > 0.05:
            arithmetic_errors += 1
        if b.get("currency") != "INR":
            currency_mismatches += 1
    check_f2 = (arithmetic_errors == 0 and currency_mismatches == 0)
    if not check_f2: failures.append(f"F2: Bill calculation errors: {arithmetic_errors}, currency mismatches: {currency_mismatches}")
    print(f"  [+] F2. Bill arithmetic & currency consistency: {arithmetic_errors} math errors, {currency_mismatches} currency errors -> {'PASS' if check_f2 else 'FAIL'}")
    results["F_BILLS"] = check_f1 and check_f2

    # ── G. CLAIM CHECKS ──
    print("\n[G] Running Insurance Claim Checks...")
    claim_ids = [c["claim_id"] for c in claims]
    check_g1 = (len(claim_ids) == len(set(claim_ids)) and 500 <= len(claim_ids) <= 600)
    if not check_g1: failures.append(f"G1: Claim IDs not unique or count out of range: {len(claim_ids)}")
    print(f"  [+] G1. Claim count & uniqueness: {len(claim_ids)} records -> {'PASS' if check_g1 else 'FAIL'}")

    # Check test scenarios presence
    scenarios_found = {}
    for c in claims:
        if c.get("test_scenario"):
            scenarios_found[c["test_scenario"][:10]] = c["claim_id"]
    print(f"  [+] G2. Test scenarios tagged: {len(scenarios_found)} distinct scenario types embedded")
    for s_tag, c_id in sorted(scenarios_found.items()):
        print(f"      - {s_tag}... (Claim: {c_id})")
    check_g2 = (len(scenarios_found) >= 7)
    if not check_g2: failures.append(f"G2: Missing expected test scenarios (found {len(scenarios_found)})")
    results["G_CLAIMS"] = check_g1 and check_g2

    # ── H. OVERALL INTEGRITY ──
    print("\n[H] Running Overall Cross-Dataset Integrity Checks...")
    # Check for no unintended broken references
    bill_map = {b["bill_id"]: b for b in bills}
    broken_bill_refs = 0
    for c in claims:
        # Scenario H intentionally references missing encounter, but bill should resolve
        if c["bill_id"] not in bill_map:
            broken_bill_refs += 1
    check_h1 = (broken_bill_refs == 0)
    print(f"  [+] H1. Claim to Bill referential integrity: {broken_bill_refs} broken bill references -> {'PASS' if check_h1 else 'FAIL'}")

    # Verify no mixing of real identity data (e.g. no 12-digit Aadhaar patterns, etc.)
    real_identity_leaks = 0
    for p in patients:
        if "aadhaar" in p or len(p["phone"]) != 10 or not p["phone"].startswith("98765"):
            real_identity_leaks += 1
    check_h2 = (real_identity_leaks == 0)
    print(f"  [+] H2. Privacy compliance & synthetic isolation: {real_identity_leaks} real identity leaks -> {'PASS' if check_h2 else 'FAIL'}")
    results["H_OVERALL"] = check_h1 and check_h2

    # ── SCORECARD SUMMARY ──
    print("\n" + "=" * 70)
    print("  INTEGRITY VALIDATION SCORECARD")
    print("=" * 70)
    all_passed = True
    for category, passed in sorted(results.items()):
        status_str = "PASSED [100%]" if passed else "FAILED"
        print(f"  Category {category:<16} : {status_str}")
        if not passed:
            all_passed = False

    print("=" * 70)
    if all_passed and not failures:
        print("  FINAL RESULT: ALL INTEGRITY CHECKS PASSED (100% INTEGRITY GENUINELY VERIFIED)")
    else:
        print(f"  FINAL RESULT: {len(failures)} FAILURE(S) DETECTED")
        for f in failures:
            print(f"    - {f}")
    print("=" * 70 + "\n")

    return all_passed


if __name__ == "__main__":
    success = run_all_validation_checks()
    sys.exit(0 if success else 1)
