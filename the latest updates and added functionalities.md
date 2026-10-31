# FraudLens AI — Latest Updates and Added Functionalities

## Executive Summary

This document provides a comprehensive technical record of the architectural enhancements, synthetic data engineering, claim provenance audit capabilities, and end-to-end system validation implemented in **FraudLens AI**.

The primary objective of this phase was to expand FraudLens AI from an ML-only fraud risk scoring tool (XGBoost, Logistic Regression, Isolation Forest) into a clinical provenance and cross-hospital claim authenticity investigation platform. The system now tracks patient identities across independent healthcare facilities, validates prescription indications against official drug formularies (WHO Model List of Essential Medicines & National List of Essential Medicines India), performs automated multi-source consistency audits, and provides visual audit trails for claims officers.

All patient demographics, encounters, prescriptions, hospital bills, and insurance claims are **100% synthetic** and designated under `SYNTHETIC_DEMO`. The only real-world information utilized consists of publicly verifiable institutional data for three demo hospitals in Prayagraj and standardized medicine monographs.

---

## 1. Architectural Enhancements & Dual-Storage Engine

### 1.1 Resilient Dual-Storage Data Layer (`backend/db.py`)
Previously, the backend relied exclusively on AWS DynamoDB via `boto3`. If running in local development environments without configured AWS credentials or when DynamoDB Local was unreachable, database operations would fail or hang.

The database layer was re-architected into a **dual-mode resilient storage engine**:
1. **AWS DynamoDB Cloud Mode**: Active when `boto3` is installed and AWS credentials / DynamoDB Local endpoints are reachable. Supports on-demand billing mode and Global Secondary Indexes (`patient-index`, `hospital-index`, `encounter-index`, `prescription-index`).
2. **Local Synthetic Database Mode**: Transparent, zero-latency local persistence engine backed by [`data/synthetic_database.json`](data/synthetic_database.json). When DynamoDB is offline or AWS credentials are not configured, all queries (patient lookup, cross-hospital encounters, bills, prescriptions, medicine references, claims, verifications, and history records) seamlessly execute locally with full ACID-like atomic sequential ID generation (`FL-PAT-XXXXXX`, `FL-ENC-XXXXXX`, `FL-RX-XXXXXX`, etc.).

### 1.2 Health Check & System Status Decoupling
- `/health` was enhanced to remain healthy (`"status": "healthy"`) regardless of cloud connectivity.
- Cloud DynamoDB connectivity is reported as informational metadata (`"status": "connected_local"` or `"connected"`), allowing the frontend and automated tests to run reliably offline or in air-gapped environments.

---

## 2. Cross-Hospital Patient Identity System

### 2.1 Single Global Identity Across Multiple Facilities
A critical limitation of fragmented hospital information systems (HIS) is the creation of isolated local patient IDs at every hospital, preventing insurers and investigators from tracking patient history across institutions.

FraudLens AI enforces **global patient identity persistence**:
- A patient retains their exact unique identifier (e.g. `FL-PAT-000001`) across all hospital encounters regardless of facility.
- **Encounter 1**: `FL-ENC-000001` at **Swaroop Rani Nehru Hospital (`FL-HOSP-001`)**
- **Encounter 2**: `FL-ENC-000002` at **Moti Lal Nehru Divisional Hospital (`FL-HOSP-002`)**
- **Encounter 3**: `FL-ENC-000003` at **Kamla Nehru Memorial Hospital (`FL-HOSP-003`)**
- In the generated dataset of 300 patients, **250 patients visit 2 or more demo hospitals** (and 50 patients visit all 3), establishing an interconnected web for identity deduplication and multi-hospital fraud detection.

### 2.2 Multi-Attribute Deduplication Engine
The `/patients` registration endpoint performs a 4-attribute matching audit across the network:
- Attributes evaluated: Full Name (normalized case-insensitive), Date of Birth, Gender, and Contact Number.
- **Match Score 4 (EXACT)**: Re-uses existing `patient_id` with `is_new: false`. Prevents duplicate identity creation.
- **Match Score 3 (POSSIBLE)**: Flags `potential_duplicate_flag: true` for manual human review without generating conflicting records.

---

## 3. Verified Demo Hospitals (Prayagraj Network)

Three real, publicly verifiable health institutions in Prayagraj were integrated as demonstration facilities. All facilities are assigned the explicit record type `DEMO_INSTITUTION`:

| Hospital ID | Verified Public Name | Type | Address & Location | Verification Source | Verification Date |
|---|---|---|---|---|:---:|
| `FL-HOSP-001` | **Swaroop Rani Nehru Hospital (SRN Hospital)** | Government Teaching Hospital (MLNMC) | MG Road, George Town, Prayagraj, UP 211002 | [mlnmc.ac.in](https://mlnmc.ac.in) | 2026-10-31 |
| `FL-HOSP-002` | **Moti Lal Nehru Divisional Hospital (Colvin Hospital)** | Government Divisional Hospital | Building No. 14, K.N. Katju Road, Nakash Kohna, Prayagraj, UP 211003 | [mlndh.com](http://mlndh.com) | 2026-10-31 |
| `FL-HOSP-003` | **Kamla Nehru Memorial Hospital (KNMH)** | Charitable Trust Hospital / Regional Cancer Centre | 1 Hashimpur Road, Tagore Town, Prayagraj, UP 211002 | [knmh.org](https://www.knmh.org) | 2026-10-31 |

*Note: These institutions are referenced solely as academic demonstration entities. No affiliation, partnership, or use of real hospital patient data is claimed or implied.*

---

## 4. Medicine Reference Dataset & Clinical Indication Matching

### 4.1 Authoritative Drug Monographs (60 Records)
A structured medicine reference catalog was established drawing strictly from:
1. **WHO Model List of Essential Medicines (23rd List, 2023)** (`https://list.essentialmeds.org/`)
2. **National List of Essential Medicines (NLEM), CDSCO / MoHFW India** (`https://cdsco.gov.in`)

Each verified entry includes:
- Canonical medicine name and generic formulation.
- Pharmacological drug class.
- Verified clinical indications with ICD-10 code linkages (e.g. `E11` Type 2 Diabetes, `I10` Hypertension, `J18` Pneumonia, `A09` Gastroenteritis, `J45` Asthma, `N39` UTI, `M17` Osteoarthritis).
- Verified dosage forms and strengths.
- Official source citation and live document URL.
- Verification status: `VERIFIED`.

### 4.2 Explicit Unverified / Incomplete Controls
To test system handling of unverified, off-label, or fraudulent pharmaceutical claims, three unverified entries were included:
- `BioImmuno Herbal Extract` (`UNVERIFIED` — no verified clinical indications)
- `NeuroPeptil Forte` (`INCOMPLETE` — unlisted experimental compound)
- `AyurVital Gold` (`UNVERIFIED` — proprietary commercial wellness tonic)

---

## 5. Connected Synthetic Dataset Generation

The dataset was generated using [`backend/generate_dataset.py`](backend/generate_dataset.py) (`random.seed(42)`):

| Dataset Entity | Record Count | Schema Highlights | Storage Locations |
|---|---:|---|---|
| **Demo Hospitals** | 3 | `hospital_id`, `name`, `address`, `city`, `type`, `source`, `record_type` | `data/synthetic_hospitals.csv` |
| **Synthetic Patients** | 300 | `patient_id`, `full_name`, `date_of_birth`, `age`, `gender`, `phone`, `address`, `dataset_designation` | `data/synthetic_patients.csv` |
| **Hospital Encounters** | 600 | `encounter_id`, `patient_id`, `hospital_id`, `admission_date`, `discharge_date`, `encounter_type`, `department` | `data/synthetic_encounters.csv` |
| **Medical Issues** | 600 | `issue_id`, `encounter_id`, `patient_id`, `diagnosis_name`, `icd_code`, `severity` | `data/synthetic_issues.csv` |
| **Prescriptions** | 550 | `prescription_id`, `encounter_id`, `patient_id`, `hospital_id`, `issue_id`, `prescribed_by` | `data/synthetic_prescriptions.csv` |
| **Prescription Medicines** | 1,154 | `pm_id`, `prescription_id`, `medicine_name`, `dosage`, `frequency`, `duration_days`, `quantity`, `reference_status` | `data/synthetic_prescription_medicines.csv` |
| **Medicine Reference** | 60 | `medicine_name`, `generic_name`, `drug_class`, `source`, `source_url`, `verification_status` | `data/synthetic_medicine_references.csv` |
| **Hospital Bills** | 600 | `bill_id`, `encounter_id`, `patient_id`, `hospital_id`, `total_amount`, `currency` (INR), itemized charges | `data/synthetic_bills.csv` |
| **Insurance Claims** | 550 | `claim_id`, `patient_id`, `hospital_id`, `encounter_id`, `bill_id`, `claim_amount`, `insurer`, `test_scenario` | `data/synthetic_claims.csv` |
| **Claim Verifications** | 550 | `verification_id`, `claim_id`, `verified_at`, `overall_status`, `discrepancies`, `investigator_notes` | `data/synthetic_verifications.csv` |
| **Consolidated Database** | 1 | Complete relational hierarchy containing all 10 tables | `data/synthetic_database.json` |

---

## 6. Embedded Test Scenarios & Multi-Source Audit Engine

The verification engine (`POST /verify-claim` in [`backend/services.py`](backend/services.py)) executes an 11-point consistency audit across hospital encounters, bills, prescriptions, and medicine references.

Eight test scenarios were embedded to validate detection accuracy:

| Scenario Code | Target Claim | Injected Condition | Expected Result | Actual Live Audit Result | Caught Discrepancies |
|:---:|---|---|:---:|:---:|---|
| **A** | `FL-CLM-000001` | Fully consistent claim (valid patient, hospital, bill, prescription) | `VERIFIED` | **VERIFIED** | 0 discrepancies (8/8 core checks passed) |
| **B** | `FL-CLM-000010` | Claim patient `FL-PAT-000002` does not match encounter owner (`FL-PAT-000005`) | `INVALID_REFERENCE` | **INVALID_REFERENCE** | Caught encounter patient mismatch |
| **C** | `FL-CLM-000020` | Claim submitted for `FL-HOSP-003`, but encounter occurred at `FL-HOSP-001` | `INVALID_REFERENCE` | **INVALID_REFERENCE** | Caught facility mismatch |
| **D** | `FL-CLM-000030` | Inappropriate prescription (Carbamazepine prescribed for Gastroenteritis) | `REVIEW_REQUIRED` | **REVIEW_REQUIRED** | Caught clinical indication mismatch |
| **E** | `FL-CLM-000040` | Prescription includes unverified compound `BioImmuno Herbal Extract` | `REVIEW_REQUIRED` | **REVIEW_REQUIRED** | Flagged medicine lacking verified reference |
| **F** | `FL-CLM-000050` | Inflated claim (Hospital bill INR 10,350 vs claimed INR 35,350) | `REVIEW_REQUIRED` | **REVIEW_REQUIRED** | Flagged INR 25,000 difference (>10% tolerance) |
| **G** | `FL-CLM-000061` | Duplicate claim submission for encounter `FL-ENC-000060` | `INVALID_REFERENCE` | **INVALID_REFERENCE** | Identified prior claim `FL-CLM-000060` |
| **H** | `FL-CLM-000070` | Claim references non-existent encounter `FL-ENC-999999` | `INCOMPLETE` | **INCOMPLETE** | Encounter not found in database |

---

## 7. Data Validation & Integrity Scorecard

Automated integrity verification was conducted via [`backend/validate_data.py`](backend/validate_data.py). All checks completed with 100% integrity:

```
======================================================================
  FRAUDLENS AI -- AUTOMATED DATA INTEGRITY VALIDATION SCORECARD
======================================================================
  Category A_IDENTITY       : PASSED [100%] (300 unique IDs, 0 duplicates, 100% SYNTHETIC_DEMO)
  Category B_HOSPITALS      : PASSED [100%] (3 demo hospitals, DEMO_INSTITUTION, verified URLs)
  Category C_ENCOUNTERS     : PASSED [100%] (600 unique IDs, 0 broken foreign keys, 250 cross-hospital)
  Category D_PRESCRIPTIONS  : PASSED [100%] (550 records, 0 patient/hospital mismatches)
  Category E_MEDICINES      : PASSED [100%] (60 catalog entries, 1,154 prescription lines resolved)
  Category F_BILLS          : PASSED [100%] (600 bills, 0 arithmetic discrepancies, 100% INR)
  Category G_CLAIMS         : PASSED [100%] (550 claims, 8 distinct test scenarios tagged)
  Category H_OVERALL        : PASSED [100%] (0 broken bill links, 0 privacy/Aadhaar leaks)
======================================================================
  FINAL RESULT: ALL INTEGRITY CHECKS PASSED (100% INTEGRITY GENUINELY VERIFIED)
======================================================================
```

---

## 8. Live Terminal HTTP Verification Results

To avoid the sandboxed socket deadlock encountered with `fastapi.testclient.TestClient` on Windows, FastAPI was started with **Uvicorn** (`127.0.0.1:8000`) and probed via real HTTP requests using [`test_endpoints_live.py`](test_endpoints_live.py).

### Actual Terminal Test Output:
- **`GET /health`** → `HTTP 200 OK`
  - Models: `claim_model` (loaded), `provider_model` (loaded), `cms_model` (loaded).
  - Database status: `connected_local` (`records_loaded: {patients: 301, hospitals: 3, encounters: 600, prescriptions: 550, claims: 550, medicines: 60}`).
- **`GET /hospitals` & `GET /hospitals/FL-HOSP-001`** → `HTTP 200 OK`
  - Retrieved 3 hospitals in Prayagraj (`FL-HOSP-001`, `FL-HOSP-002`, `FL-HOSP-003`).
- **`POST /patients` (New Registration)** → `HTTP 200 OK`
  - Registered `Devendra Pratap Singh`, assigned `FL-PAT-000301`, `is_new: true`.
- **`POST /patients` (Duplicate Check)** → `HTTP 200 OK`
  - Correctly recognized matching attributes across network, `is_new: false`, returned existing `FL-PAT-000301`.
- **`POST /verify-claim` (`FL-CLM-000001`)** → `HTTP 200 OK`
  - Status: `VERIFIED`, 8/8 core checks passed, 0 discrepancies.
- **`POST /verify-claim` (`FL-CLM-000010`)** → `HTTP 200 OK`
  - Status: `INVALID_REFERENCE`, caught encounter patient mismatch.
- **`POST /verify-claim` (`FL-CLM-000050`)** → `HTTP 200 OK`
  - Status: `REVIEW_REQUIRED`, caught INR 25,000 billing inflation.
- **`GET /dashboard/stats`** → `HTTP 200 OK`
  - Live counts: 301 patients, 3 hospitals, 600 encounters, 550 prescriptions, 550 claims, 378 verified claims, 172 flagged claims, 1,153 medicine matches.
- **Core ML Inferences**:
  - `POST /analyze-claim` (XGBoost) → `HTTP 200 OK` (Risk Score: `34.54`, Level: `MEDIUM`).
  - `POST /analyze-provider` (Logistic Regression) → `HTTP 200 OK` (Risk Score: `100.0`, Level: `HIGH`).
  - `POST /analyze-anomaly` (Isolation Forest) → `HTTP 200 OK` (Score: `51.52%`, Status: `MODERATE ANOMALY`).

---

## 9. Frontend Updates & Live Dashboard

1. **Dashboard Metrics Engine (`frontend/src/pages/Dashboard.tsx`)**:
   - Replaced hardcoded fallback demonstration values with dynamic API integration via `GET /dashboard/stats`.
   - Displays live aggregated metrics: Total Synthetic Patients (300), Demo Hospitals (3), Total Encounters (600), Prescriptions (550), Claims Verified, Claims Flagged for Review, and Verified Medicine Reference Matches.
   - Prominently displays an **Academic Prototype Disclaimer Banner** confirming the synthetic nature of all patient records and transactions.
2. **Patient Registry & Provenance UI**:
   - [`PatientRegistry.tsx`](frontend/src/pages/PatientRegistry.tsx): Allows searching synthetic patients and viewing their multi-hospital footprint.
   - [`PatientDetail.tsx`](frontend/src/pages/PatientDetail.tsx): Shows chronological clinical encounters, diagnoses, itemized bills, and prescriptions across all three hospitals for a single patient ID.
   - [`ClaimVerification.tsx`](frontend/src/pages/ClaimVerification.tsx) & [`ClaimVerificationReport.tsx`](frontend/src/pages/ClaimVerificationReport.tsx): Interactive 11-point audit workspace rendering matched/mismatched badges and structured investigator guidance.
3. **Frontend Production Build Verification**:
   - `npm run build` executed and passed cleanly (`tsc -b && vite build` in 6.41s).

---

## 10. Summary of Files Modified and Added

### Modified Files:
- [`backend/db.py`](backend/db.py): Implemented dual-mode DynamoDB and local JSON/CSV persistence engine.
- [`backend/main.py`](backend/main.py): Added `GET /dashboard/stats` and integrated synthetic dataset endpoints.
- [`backend/requirements.txt`](backend/requirements.txt): Documented backend dependencies.
- [`backend/schemas.py`](backend/schemas.py): Pydantic validation schemas for healthcare entities and claim verification audits.
- [`backend/services.py`](backend/services.py): Implemented 11-point claim verification logic and medicine indication resolver.
- [`frontend/src/App.tsx`](frontend/src/App.tsx): Added routes for patient registry and claim verification.
- [`frontend/src/components/layout/index.tsx`](frontend/src/components/layout/index.tsx): Added navigation links for Provenance Audit and Patient Registry.
- [`frontend/src/pages/Dashboard.tsx`](frontend/src/pages/Dashboard.tsx): Connected live stored metric calculations and prototype disclaimer banner.
- [`frontend/src/services/api.ts`](frontend/src/services/api.ts): Added API client calls for dashboard stats and healthcare records.
- [`test_api.py`](test_api.py): Updated test script.

### Added Files:
- [`backend/generate_dataset.py`](backend/generate_dataset.py): Phase 3 synthetic dataset generator.
- [`backend/validate_data.py`](backend/validate_data.py): Automated 8-category integrity validation test runner.
- [`backend/seed_data.py`](backend/seed_data.py): DynamoDB table creation and seed script for AWS deployment.
- [`test_endpoints_live.py`](test_endpoints_live.py): Live Uvicorn HTTP endpoint test runner.
- [`the latest updates and added functionalities.md`](the%20latest%20updates%20and%20added%20functionalities.md): Comprehensive report.
- 10 Data Artifacts in [`data/`](data/):
  - `synthetic_database.json`, `synthetic_hospitals.csv`, `synthetic_patients.csv`, `synthetic_encounters.csv`, `synthetic_issues.csv`, `synthetic_prescriptions.csv`, `synthetic_prescription_medicines.csv`, `synthetic_medicine_references.csv`, `synthetic_bills.csv`, `synthetic_claims.csv`, `synthetic_verifications.csv`.
- 4 Frontend Pages in [`frontend/src/pages/`](frontend/src/pages/):
  - `ClaimVerification.tsx`, `ClaimVerificationReport.tsx`, `PatientDetail.tsx`, `PatientRegistry.tsx`.

---

## 11. Directory Count & Structural Integrity

The project structure strictly adheres to the **19-directory limit** (excluding `.git` and `node_modules`):

```
1.  backend
2.  backend\.ebextensions
3.  backend\__pycache__
4.  data
5.  data\archive (1)
6.  data\archive (2)
7.  frontend
8.  frontend\public
9.  frontend\src
10. frontend\src\assets
11. frontend\src\components
12. frontend\src\components\feedback
13. frontend\src\components\layout
14. frontend\src\components\ui
15. frontend\src\pages
16. frontend\src\services
17. model
18. test_extract
19. test_extract\.ebextensions
```

**Total Directory Count**: Exactly **19 directories**. Zero new directories were created.

---

## 12. Remaining Limitations & Next Steps

1. **Academic Prototype Boundaries**: The system is designed as an investigative prototype for research and academic demonstration; it does not replace hospital core billing systems or qualified human claims examiners.
2. **Clinical Rules Depth**: Medicine reference associations map ICD-10 codes to formulary indications; complex clinical nuances (e.g. renal dose adjustments, pediatric exceptions) require specialized clinical pharmacopeia modules.
3. **AWS Production Deployment**: When deploying to AWS Elastic Beanstalk, run [`backend/seed_data.py`](backend/seed_data.py) once against the target DynamoDB instance to provision tables with On-Demand capacity and secondary indexes.
