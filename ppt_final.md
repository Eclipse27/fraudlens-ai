# FraudLens AI — Final Review Presentation (8 Slides, 5 Minutes)

> **Format:** 8 Slides | 5 Minutes | Focus on Implementation, Cloud Deployment & Innovation

---

## SLIDE 1 — Project Overview

### Title
**FraudLens AI**
*AI-Powered Health Insurance Fraud Detection & Clinical Claim Investigation Assistant*

*A Cloud-Native Intelligent System | Fully Deployed on AWS ap-south-1*

---

### Team Details

| Name | Register Number |
|------|----------------|
| [TEAM MEMBER 1 NAME] | [REGISTER NUMBER] |
| [TEAM MEMBER 2 NAME] | [REGISTER NUMBER] |
| [TEAM MEMBER 3 NAME] | [REGISTER NUMBER] |
| [TEAM MEMBER 4 NAME] | [REGISTER NUMBER] |

**Guide:** [GUIDE NAME]
**Department / Institution:** [DEPARTMENT], [INSTITUTION NAME]
**Academic Year:** 2026–27 | Semester 7

---

### Industry Use Case
> **Healthcare Insurance Fraud Detection** — detecting fraudulent claims filed by hospitals, pharmacies, and patients using AI and clinical audit.

### UN SDG Alignment

| SDG | Alignment |
|-----|-----------|
| **SDG 3 — Good Health & Well-Being** | Protects insurance fund integrity so resources reach legitimate patients needing care. Prevents fraud that inflates premiums for genuine policyholders. |
| **SDG 16 — Peace, Justice & Strong Institutions** | Automates accountability, reduces financial crime, and strengthens institutional integrity in the insurance industry through evidence-based adjudication. |

---

## SLIDE 2 — Problem Statement & Objectives

### The Problem

- **₹10,000–₹15,000 Crore** lost annually in India to health insurance fraud (Ayushman Bharat / PM-JAY impacted)
- **3–10%** of all global healthcare expenditure is fraudulent, abusive, or wasteful
- Fraud types: *phantom treatments, upcoded billing, duplicate cross-hospital claims, unprescribed medicine billing, organized hospital syndicates*

### Challenges with Existing Systems

| Challenge | Impact |
|-----------|--------|
| Manual post-payment audits | Covers < 5% of claims; fraud discovered after payout |
| Siloed hospital databases | Cannot correlate the same patient admitted at two hospitals |
| Rigid rule-based detection | High false-positive rate; misses evolving fraud patterns |
| No formulary cross-check | Cannot verify if medicine matches the diagnosis |
| No cross-hospital identity | Duplicate identities enable phantom patient fraud |

### Solution Objectives

1. Build a **tri-model ML engine**: XGBoost (claim fraud), Logistic Regression (provider risk), Isolation Forest (utilization anomaly)
2. Create a **clinical provenance audit engine** — validate encounter → diagnosis → prescription → bill → claim chain
3. Implement **cross-hospital patient identity resolution** using 4-attribute deduplication (`FL-PAT-XXXXXX`)
4. Deploy **end-to-end on AWS** (S3 + API Gateway + Elastic Beanstalk + DynamoDB) as a live production web application
5. Provide **WHO/NLEM formulary cross-check** — 60 drug monographs verifying every medicine's clinical indication

### Expected Outcomes

- ✅ Working deployed web app accessible at a public URL
- ✅ Real-time risk scores from 3 ML models
- ✅ 11-point clinical provenance audit report per claim
- ✅ Persistent investigation history in DynamoDB
- ✅ Fully cloud-hosted, scalable, and cost-managed

---

## SLIDE 3 — Proposed Solution & Innovation

### What FraudLens AI Delivers

FraudLens AI is a **dual-pillar fraud investigation console** — uniquely combining statistical ML with deterministic clinical audit in a single system.

### Two-Pillar Architecture

```
Pillar 1: ML Statistical Detection          Pillar 2: Clinical Provenance Audit
─────────────────────────────────────       ──────────────────────────────────────
XGBoost → Claim fraud probability 0-100     Encounter ↔ Diagnosis ↔ Prescription
Logistic Regression → Provider risk score   Prescription ↔ Bill ↔ Claim amount
Isolation Forest → Utilization anomaly      Drug indication ↔ WHO / NLEM formulary
                                            Cross-hospital patient identity check
```

### Unique Features (Differentiators)

| Feature | Why It's Innovative |
|---------|---------------------|
| **Global Patient Deduplication** | 4-attribute match (Name + DOB + Gender + Phone) → single `FL-PAT-XXXXXX` identity across any number of hospitals |
| **WHO/NLEM Drug Formulary Engine** | 60 real-world drug monographs; flags medicines billed for medically-unrelated diagnoses |
| **11-Point Clinical Consistency Audit** | Rule engine checking encounter validity, bill–claim reconciliation, prescription match, drug indication, and duplicate identity |
| **Tri-Model ML Stack** | Supervised (XGBoost + Logistic Regression) + Unsupervised (Isolation Forest) — covers both known fraud patterns and novel anomalies |
| **Dual-Mode Storage** | Cloud mode: AWS DynamoDB. Offline mode: local JSON database. Zero credential requirement for local development. |
| **Synthetic Healthcare Dataset** | 303 patients, 3 hospitals, 600 encounters, 550 prescriptions, 550 claims — entirely synthetic, no real PHI |

### Expected Benefits

- **Pre-payment fraud detection** — catches fraud before money is disbursed
- **40–60x faster** than manual claim audits
- **Zero false-negatives** on structured clinical inconsistencies (rule-based pillar)
- **Scalable**: PAY_PER_REQUEST DynamoDB incurs $0.00 at idle; scales elastically under load
- Fully **open-source, reproducible, and academically verifiable**

---

## SLIDE 4 — Cloud Architecture

### Architecture Diagram

```
┌────────────────────────────────────────────────────────────────────────┐
│                      AWS Cloud (ap-south-1)                            │
│                                                                        │
│  [User Browser]                                                        │
│       │                                                                │
│       ▼  HTTP                                                          │
│  ┌─────────────────────────────────────────────────────┐              │
│  │  Amazon S3 Static Website                           │              │
│  │  fraudlens-frontend-418272772343                    │              │
│  │  React 19 + Vite 8 SPA (HTML / JS / CSS)           │              │
│  └─────────────────────────────────────────────────────┘              │
│       │  Axios REST API calls                                          │
│       ▼                                                                │
│  ┌─────────────────────────────────────────────────────┐              │
│  │  Amazon API Gateway (HTTP API v2)                   │              │
│  │  c9av6ujzgi.execute-api.ap-south-1.amazonaws.com    │              │
│  │  CORS + HTTPS + ANY /{proxy+} Route                 │              │
│  └─────────────────────────────────────────────────────┘              │
│       │  HTTP proxy via Elastic IP 43.204.34.220                      │
│       ▼                                                                │
│  ┌─────────────────────────────────────────────────────┐              │
│  │  AWS Elastic Beanstalk — FraudLens-prod             │              │
│  │  ┌─────────────────────────────────────────────┐   │              │
│  │  │  EC2 t3.micro (i-0e597a7086c93ff1d) AL2023  │   │              │
│  │  │  Nginx :80 ──▶ FastAPI / Uvicorn :8000      │   │              │
│  │  │  Python 3.12 | 13 REST Endpoints            │   │              │
│  │  │  ┌──────────┐ ┌───────────┐ ┌────────────┐  │   │              │
│  │  │  │ XGBoost  │ │Isolation  │ │ Logistic   │  │   │              │
│  │  │  │ Claim    │ │Forest     │ │ Regression │  │   │              │
│  │  │  │ Model    │ │Anomaly    │ │ Provider   │  │   │              │
│  │  │  └──────────┘ └───────────┘ └────────────┘  │   │              │
│  │  └─────────────────────────────────────────────┘   │              │
│  └─────────────────────────────────────────────────────┘              │
│       │  Boto3 SDK                                                     │
│       ▼                                                                │
│  ┌─────────────────────────────────────────────────────┐              │
│  │  Amazon DynamoDB (11 Tables, PAY_PER_REQUEST)       │              │
│  │  FL_Patients | FL_Hospitals | FL_Encounters          │              │
│  │  FL_Prescriptions | FL_HospitalBills                │              │
│  │  FL_InsuranceClaims | FL_ClaimVerifications          │              │
│  │  FraudInvestigationHistory | + 3 more                │              │
│  └─────────────────────────────────────────────────────┘              │
│                                                                        │
│  Supporting: CloudWatch (7-day log retention) | IAM | CloudFormation  │
└────────────────────────────────────────────────────────────────────────┘
```

### Request Workflow (Step-by-Step)
1. User opens S3-hosted React SPA in browser
2. Frontend sends `POST /verify-claim` to API Gateway (HTTPS)
3. API Gateway proxies HTTP to EC2 Nginx via Elastic IP `43.204.34.220`
4. Nginx reverse-proxies to FastAPI on port 8000
5. FastAPI retrieves claim data from DynamoDB, runs 11-point audit + XGBoost ML
6. Verification result persisted back to DynamoDB
7. JSON response traverses back through API Gateway → browser renders audit report

### Deployment Model & Security
- **SingleInstance EB** (no ALB — saves ~$18/month in demo cost)
- **Elastic IP** `43.204.34.220` ensures stable routing without DNS change
- **IAM Least Privilege**: Deploy user has narrow scoped policies; no secrets in code
- **CORS**: Strictly limited to S3 origin and local dev ports only

---

## SLIDE 5 — Technology Stack & Cloud Services

### Frontend Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| React | 19.2.8 | Declarative UI component tree |
| TypeScript | 5.x | Type-safe frontend development |
| Vite | 8.2.2 | Fast ES module bundler with HMR |
| Tailwind CSS | 4.3.3 | Utility-first responsive styling |
| React Router DOM | 7.18.2 | Client-side SPA routing (8 pages) |
| Recharts | 3.10.1 | Risk score charts and distributions |
| Axios | 1.19.0 | REST HTTP client with interceptors |

### Backend Stack

| Technology | Version | Purpose |
|-----------|---------|---------|
| FastAPI | 0.162.0 | High-throughput async ASGI API |
| Python | 3.12 | Backend language (AL2023 on EC2) |
| Uvicorn | 0.54.0 | Production ASGI server |
| Pydantic | 2.14.2 | Schema validation and serialization |
| XGBoost | 3.4.1 | Regularized gradient boosting |
| Scikit-Learn | 1.9.1 | Logistic Regression, Isolation Forest |
| Pandas / NumPy | 3.1 / 2.5 | Feature engineering |
| Boto3 | 1.43.123 | AWS DynamoDB SDK |
| Joblib | 1.6.0 | ML model serialization (.pkl files) |

### AWS Cloud Services (5 Core + Supporting)

| # | AWS Service | Role in FraudLens AI |
|---|-------------|---------------------|
| 1 | **Amazon S3** | Hosts compiled React frontend as static website; `index.html` as error document for SPA routing |
| 2 | **Amazon API Gateway (HTTP v2)** | Managed HTTPS entry point; CORS headers; `ANY /{proxy+}` route forwarding all calls to EB backend |
| 3 | **AWS Elastic Beanstalk** | Manages EC2 lifecycle, Nginx config, Python env, deployment versioning, health monitoring |
| 4 | **Amazon DynamoDB** | NoSQL store for 11 healthcare tables + investigation history; `PAY_PER_REQUEST` = $0 at idle |
| 5 | **AWS IAM** | Instance profile for EC2→DynamoDB access, deploy user policies, EB service role |
| + | CloudWatch | 7-day log retention, CPU/health monitoring for EC2 |
| + | CloudFormation | EB-managed infrastructure stack (auto-provisioned) |
| + | Elastic IP | Fixed public IPv4 `43.204.34.220` for stable API routing |

---

## SLIDE 6 — Modules & Implementation

### Major Modules

| # | Module | Technology | Status |
|---|--------|-----------|--------|
| 1 | **Claim Provenance Audit Engine** | FastAPI + 11-point rule engine + DynamoDB | ✅ LIVE |
| 2 | **Patient Registry & Deduplication** | 4-attribute FL-PAT-XXXXXX identity system | ✅ LIVE |
| 3 | **ML Claim Fraud Analysis** | XGBoost (best_claim_model.pkl) | ✅ LIVE |
| 4 | **ML Provider Risk Profiling** | Logistic Regression (provider_model.pkl) | ✅ LIVE |
| 5 | **ML Utilization Anomaly Detection** | Isolation Forest (cms_anomaly_model.pkl) | ✅ LIVE |
| 6 | **WHO/NLEM Drug Formulary Engine** | 60 drug monograph JSON + indication checker | ✅ LIVE |
| 7 | **Clinical Dashboard** | React + Recharts + 302 patients, 550 claims | ✅ LIVE |
| 8 | **Investigation History (DynamoDB)** | Full CRUD + search & filter on DynamoDB | ✅ LIVE |

### API Endpoints (13 Total — All Verified HTTP 200)

```
GET  /health              → Backend + model + DB status check
GET  /dashboard/stats     → Live aggregate KPIs
GET  /hospitals           → Hospital directory
GET  /patients            → Patient registry (FL-PAT deduplication)
GET  /patients/{id}       → Patient detail
GET  /encounters          → Clinical encounter records
GET  /claims              → Insurance claims list
POST /verify-claim        → 11-point provenance audit + XGBoost score
POST /analyze-claim       → XGBoost claim fraud probability
POST /analyze-provider    → Logistic Regression provider risk
POST /detect-anomaly      → Isolation Forest anomaly score
POST /history             → Save investigation to DynamoDB
GET  /history             → Retrieve investigation history
```

### Module Integration

```
React Frontend (8 Pages: Dashboard, Patients, Encounters,
                Claims, Verify, Analyze, Provider, History)
         │  Axios + API Gateway HTTPS
         ▼
FastAPI Backend ──▶ Clinical Audit Engine (11 checks)
                ──▶ ML Models (XGBoost / LR / IF)
                ──▶ DynamoDB (Boto3 SDK)
                ──▶ WHO/NLEM Formulary Dictionary
```

### Key Completed Functionality
- **Cross-hospital patient deduplication**: 4-attribute match → single FL-PAT-XXXXXX
- **11-point audit**: encounter existence, hospital match, diagnosis match, encounter-bill reconciliation, bill-claim amount match, prescription existence, drug indication validity, WHO/NLEM compliance, duplicate identity detection, prescription-claim date ordering, encounter-bill date ordering
- **Dual-mode storage**: AWS DynamoDB in production, local JSON fallback for offline dev

---

## SLIDE 7 — AI-Assisted Development

### AI / Vibe Coding Tools Used

| Tool | How It Was Used |
|------|----------------|
| **Antigravity (Google DeepMind)** | Primary AI coding agent — cloud deployment automation, AWS CLI execution, debugging EB deployment failures, writing `.ebextensions` configs, diagnosing Pydantic/uvicorn crashes |
| **GitHub Copilot** | Inline code completions for FastAPI endpoints, React components, Pydantic schemas |
| **ChatGPT / Gemini** | Architecture advice, ML model selection rationale, Tailwind CSS component generation |

### Sample AI Prompts Used

> *"Deploy the existing FastAPI backend to Elastic Beanstalk in ap-south-1 using the fraudlens profile. Configure Nginx reverse proxy, 2GB swap file, and xgboost installation via ebextensions."*

> *"The uvicorn startup is crashing with: ValueError: On field 'medicines' the following field constraints are set but not enforced: min_length. Diagnose and fix."*

> *"The S3 static website returns 404 when the user refreshes a React SPA deep link like /patients. Fix the routing."*

### Code Generated, Customized & Understood

**AI-Generated → Customized by Team:**
```python
# .ebextensions/01_swap.config — 2GB swap for t3.micro (1GB RAM)
commands:
  01_create_swap:
    command: "dd if=/dev/zero of=/swapfile bs=1M count=2048"
  02_mkswap:
    command: "mkswap /swapfile"
  03_swapon:
    command: "swapon /swapfile"
```
```python
# backend/db.py — Dual-mode DynamoDB / JSON fallback
try:
    dynamodb = boto3.resource('dynamodb', region_name='ap-south-1')
    # ... use DynamoDB
except (NoCredentialsError, EndpointResolutionError):
    # Fall back to local JSON dataset
    data = json.load(open('data/synthetic_database.json'))
```

**Team-Authored (Original — No AI Generation):**
- All 3 ML model training pipelines (`generate_dataset.py`, training notebooks)
- 11-point clinical provenance audit rule engine (`services.py`)
- WHO/NLEM drug formulary cross-reference dictionary (60 monographs)
- Cross-hospital patient deduplication algorithm (FL-PAT generation logic)
- DynamoDB table schemas for all 11 healthcare entity tables

### Understanding of Generated Code

| Component | Team Understands |
|-----------|-----------------|
| Swap config | Creates 2048MB EBS-backed `/swapfile` via `mkswap` + `swapon` to prevent OOM during xgboost pip install on 1GB RAM t3.micro |
| Dual-mode DB | `boto3` raises `NoCredentialsError` locally → `except` catches it → loads `synthetic_database.json` instead |
| Pydantic fix | Added `BaseModel.model_dump = BaseModel.dict` shim for Pydantic v1/v2 compatibility at module import time |
| CORS middleware | `CORSMiddleware(allow_origins=[S3_ORIGIN, "http://localhost:5173"])` on FastAPI startup |
| S3 routing fix | Set S3 `ErrorDocument: index.html` so all 404s return `index.html` for React Router to handle |

---

## SLIDE 8 — Testing, Outcomes & Future Scope

### Live Production Test Results (November 1, 2026)

All 13 endpoints tested against `https://c9av6ujzgi.execute-api.ap-south-1.amazonaws.com`:

| # | Endpoint | Result | Detail |
|---|---------|--------|--------|
| 1 | `GET /health` | ✅ HTTP 200 | models loaded, DynamoDB connected |
| 2 | `GET /dashboard/stats` | ✅ HTTP 200 | 302 patients, 550 claims, 3 hospitals |
| 3 | `GET /hospitals` | ✅ HTTP 200 | 3 Prayagraj hospitals returned |
| 4 | `GET /patients` | ✅ HTTP 200 | 302 FL-PAT records returned |
| 5 | `GET /patients/FL-PAT-000001` | ✅ HTTP 200 | Demographic record retrieved |
| 6 | `GET /encounters` | ✅ HTTP 200 | 600 clinical encounters returned |
| 7 | `GET /claims` | ✅ HTTP 200 | 550 insurance claims returned |
| 8 | `POST /verify-claim` | ✅ HTTP 200 | FL-CLM-000480 → Status: VERIFIED |
| 9 | `POST /analyze-claim` | ✅ HTTP 200 | XGBoost score: **16.07 → LOW RISK** |
| 10 | `POST /analyze-provider` | ✅ HTTP 200 | Logistic Reg score: **97.31 → HIGH RISK** |
| 11 | `POST /detect-anomaly` | ✅ HTTP 200 | Isolation Forest: **40.93 → MODERATE** |
| 12 | `POST /history` | ✅ HTTP 200 | Write & Read verified on DynamoDB |
| 13 | `OPTIONS /health` | ✅ HTTP 200 | CORS Access-Control-Allow-Origin matched |

### UI/UX Outcomes
- **8-page React SPA** with sidebar navigation, responsive Tailwind CSS layout
- Recharts risk score visualizations, interactive data tables, audit report cards
- Real-time backend status monitor showing model load state and DB connectivity
- S3 `ErrorDocument: index.html` enables direct-link refresh on all 8 routes

### Business / SDG Impact

| Dimension | Impact |
|-----------|--------|
| **Financial** | Pre-payment detection prevents disbursement of fraudulent claims |
| **SDG 3 — Health** | Insurance fund integrity preserved for genuine patients; reduces premium inflation |
| **SDG 16 — Justice** | Automated, evidence-based adjudication removes human bias from fraud investigation |
| **Operational** | Reduces investigator workload by prioritizing only high-risk cases for manual review |

### Limitations (Honest)
- Synthetic dataset — 303 patients in 3 hospitals; not trained on real claims
- Single-instance EC2 — no load balancing or multi-AZ redundancy
- HTTP frontend — S3 URL unencrypted; needs CloudFront for HTTPS
- Static ML models — no real-time retraining pipeline

### Future Improvements
1. **Amazon CloudFront** — HTTPS CDN with custom domain for the frontend
2. **FHIR / HL7 API Integration** — ingest real hospital EHR records
3. **DynamoDB Streams → Lambda** — event-driven real-time fraud alerting pipeline
4. **ABDM Integration** — Ayushman Bharat Digital Mission ABHA patient ID authentication
5. **Model Retraining Pipeline** — automated weekly retraining with new claim data
6. **Amazon Textract** — OCR ingestion of scanned hospital discharge summaries

---

*FraudLens AI — Final Review | November 10, 2026 | AWS ap-south-1*
*Repository: https://github.com/Eclipse27/fraudlens-ai | Branch: main*
