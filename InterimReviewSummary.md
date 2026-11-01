# FraudLens AI — Complete Project Summary

> **Purpose:** If you read this entire file before your Interim Review, you should understand your own project deeply enough to explain it to the faculty with confidence.

---

## 1. Project Overview

**FraudLens AI** is a cloud-native, AI-powered insurance fraud detection and claim investigation assistant. It is a full-stack web application that enables insurance fraud investigators to:

- Analyze individual healthcare insurance claims for fraud risk.
- Evaluate healthcare providers for fraudulent behavioral patterns.
- Detect anomalous utilization patterns in CMS (Centers for Medicare & Medicaid Services) billing data.
- Track and review all past investigations in a persistent history.
- Monitor ML model health and system connectivity.

The system is built with a **React/TypeScript frontend**, a **FastAPI/Python backend**, three **machine learning models** (XGBoost, Logistic Regression, Isolation Forest), and is deployed on **AWS** using S3, API Gateway, Elastic Beanstalk, and DynamoDB.

---

## 2. Industry Problem

Insurance fraud — particularly in healthcare — is one of the most pervasive and costly forms of financial crime. Key problems include:

- **Scale:** Insurance companies process millions of claims per year. Manual review of every claim is physically impossible.
- **Sophistication:** Fraud schemes range from simple overbilling to complex provider collusion, phantom patients, and upcoding of procedures.
- **Delayed Detection:** Most fraud is detected only after claims have been paid out, resulting in irrecoverable losses.
- **Financial Impact:** The National Health Care Anti-Fraud Association estimates that healthcare fraud costs the U.S. tens of billions of dollars annually.
- **Honest Policyholder Burden:** Fraud directly leads to higher premiums for legitimate policyholders.
- **Resource Constraints:** Investigation teams are understaffed relative to the volume of suspicious claims. Investigators need tools that prioritize the highest-risk cases.

---

## 3. Why Insurance Fraud Detection Matters

1. **Financial Protection:** Early detection prevents payout of fraudulent claims, saving billions.
2. **Premium Fairness:** Reducing fraud keeps insurance premiums affordable for honest customers.
3. **Healthcare Integrity:** Preventing phantom billing and upcoding ensures healthcare resources are directed to real patient needs.
4. **Regulatory Compliance:** Insurance companies are legally required to have fraud detection mechanisms.
5. **Investigator Productivity:** AI-assisted risk scoring allows investigators to focus on the most suspicious cases rather than reviewing everything manually.

---

## 4. SDG Alignment

### SDG 16 — Peace, Justice & Strong Institutions
Fraud detection promotes transparency, accountability, and the reduction of financial crime within insurance institutions. By automating the identification of fraudulent activity, FraudLens supports the goal of building effective, accountable institutions at all levels.

### SDG 3 — Good Health & Well-Being
Healthcare fraud diverts resources from legitimate patient care. By detecting fraudulent healthcare claims, FraudLens helps preserve the integrity of healthcare funding and ensures that insurance resources are available for genuine medical needs.

---

## 5. Project Objective

### Main Objective
To design and deploy a cloud-native AI-powered investigation assistant that enables insurance fraud investigators to analyze claims, evaluate providers, and detect anomalous utilization patterns through a unified web interface backed by machine learning and AWS cloud services.

### Specific Objectives
1. Build three specialized ML models for claim-level, provider-level, and utilization-level fraud/anomaly detection.
2. Develop a modern, interactive React frontend with investigator-focused UX including risk visualization, investigation history, and model transparency.
3. Create a FastAPI backend with RESTful API endpoints for ML inference, data validation, and database operations.
4. Deploy the complete system on AWS cloud infrastructure using S3, API Gateway, Elastic Beanstalk, and DynamoDB.
5. Persist investigation history in DynamoDB for auditability and case tracking.

---

## 6. Expected Outcomes

- A **working, deployed web application** accessible via public URL.
- **Three trained ML models** producing real-time risk scores and recommendations.
- **Cloud-native architecture** demonstrating real-world AWS deployment skills.
- **Persistent investigation history** stored in DynamoDB.
- **Scalable foundation** for future enhancements.
- **Technical documentation** covering architecture, deployment, and usage.

---

## 7. Complete Feature List

### 7.1 Claim Analysis
- **What it does:** Accepts 18 input features describing a healthcare insurance claim (amount, patient age, procedures, provider type, etc.) and returns a fraud risk score (0–100), risk level (LOW/MEDIUM/HIGH), AI-identified risk factors with impact labels, and actionable recommendations.
- **How it works:** The frontend form collects claim data, sends a POST request to `/analyze-claim`. FastAPI validates the input with Pydantic, constructs a feature vector with one-hot encoding for categorical features, and passes it to the Regularized XGBoost model. The model returns `predict_proba` (probability of fraud), which is scaled to 0–100. Feature importance is analyzed to identify the top contributing risk factors.
- **Status:** ✅ Implemented and Working

### 7.2 Provider Analysis
- **What it does:** Accepts 31 aggregate metrics for a healthcare provider (total claims, reimbursement sums, unique beneficiaries, chronic condition proportions, etc.) and returns a provider fraud risk score, risk level, and top risk indicators.
- **How it works:** The frontend collects provider aggregate data, sends a POST to `/analyze-provider`. FastAPI maps the input fields to the model's expected feature names (case-insensitive matching), runs Logistic Regression `predict_proba`, and extracts the highest positive coefficients as top risk factors.
- **Status:** ✅ Implemented and Working

### 7.3 CMS Anomaly Detection
- **What it does:** Accepts a procedure category, procedure count, and profile display indicator. Returns an anomaly score (0–100), anomaly status (NORMAL PATTERN / MODERATE ANOMALY / SUSPICIOUS PATTERN), and a recommendation.
- **How it works:** The Isolation Forest model (trained on 635,353 real CMS utilization records) uses `decision_function` to score how anomalous the input is. The raw score is transformed to a 0–100 percentage. Threshold-based classification determines the anomaly status.
- **Status:** ✅ Implemented and Working

### 7.4 Investigation History
- **What it does:** Automatically saves every analysis result to DynamoDB. Users can view all past investigations in a searchable/filterable table, click into individual records for full details, and clear all history.
- **How it works:** After each analysis, the frontend calls `POST /history` with the result. `GET /history` retrieves all records (sorted by timestamp, newest first). `GET /history/{id}` retrieves a single record. `DELETE /history` clears all records using batch delete.
- **Status:** ✅ Implemented and Working

### 7.5 Dashboard
- **What it does:** Central command screen showing total analyses run, high-risk cases count, suspicious pattern count, active models count, risk distribution pie chart, recent activity feed, quick action cards (navigate to Claim/Provider/Anomaly analysis), and AI investigation insights.
- **How it works:** On mount, fetches all history from DynamoDB and computes summary statistics. Recharts renders the risk distribution donut chart. Quick action cards navigate to respective analysis pages.
- **Status:** ✅ Implemented and Working

### 7.6 Model Intelligence
- **What it does:** Displays the status (loaded/not loaded), algorithm type, description, and validation metrics (Test F1, Test PR-AUC, Test Recall, Generalization Gap, CV statistics) for each of the three ML models.
- **How it works:** Calls `GET /model-info` which reads `validation_results.json` and checks model load status. The frontend renders metric bars and configuration cards.
- **Status:** ✅ Implemented and Working

### 7.7 System Status
- **What it does:** Real-time health monitoring page showing FastAPI backend status (ONLINE/OFFLINE), DynamoDB connectivity, individual model load states, API base URL, and last health check timestamp.
- **How it works:** Calls `GET /health` which checks DynamoDB connectivity (informational only) and model load status. The frontend displays status pills with color coding.
- **Status:** ✅ Implemented and Working

### 7.8 User Authentication
- **What it does:** Login/logout, role-based access control for investigators vs admins.
- **Status:** 📋 Planned — Not Yet Implemented

### 7.9 Automated Alerts (SNS)
- **What it does:** Email notifications when high-risk cases are detected.
- **Status:** 📋 Planned — Not Yet Implemented

---

## 8. Complete Frontend Explanation

### Framework & Language
- **React 19** with **TypeScript** (`.tsx` files)
- **Vite 8** as the build tool and dev server

### Styling
- **Tailwind CSS 4** with a custom design system using CSS custom properties (variables) for colors, risk levels, and theming.
- Custom Tailwind config (`tailwind.config.js`) maps CSS variables to Tailwind classes (e.g., `bg-risk-high`, `text-accent`, `bg-navy-900`).
- Inter font family for typography.

### Key Libraries
| Library | Version | Purpose |
|---------|---------|---------|
| `react-router-dom` | v7 | Client-side routing |
| `axios` | v1.19 | HTTP client for API calls |
| `recharts` | v3.10 | Chart/visualization (Pie chart on Dashboard) |
| `lucide-react` | v1.34 | Icon system |
| `clsx` + `tailwind-merge` | — | Conditional CSS class utilities |

### Folder Structure
```
frontend/src/
├── App.tsx                  # Root component with BrowserRouter and Routes
├── main.tsx                 # React DOM entry point
├── index.css                # Global CSS with custom properties
├── App.css                  # App-level styles
├── components/
│   ├── layout/index.tsx     # Sidebar, TopBar, PageHeader, Layout (Outlet)
│   ├── ui/index.tsx         # Card, Button, Input, Select, RiskScoreGauge, RiskBadge, cn()
│   └── feedback/index.tsx   # LoadingState, ErrorState, StatusPill
├── pages/
│   ├── Dashboard.tsx        # Main dashboard with metrics, chart, activity feed
│   ├── ClaimAnalysis.tsx    # Claim analysis form + result display
│   ├── ProviderAnalysis.tsx # Provider analysis form + result display
│   ├── AnomalyDetection.tsx # CMS anomaly detection form + result display
│   ├── HistoryList.tsx      # Investigation history table with search/filter
│   ├── HistoryDetail.tsx    # Individual investigation report view
│   ├── ModelIntelligence.tsx # ML model cards with validation metrics
│   └── SystemStatus.tsx     # Health check and system monitoring
└── services/
    ├── api.ts               # Axios instance, all API functions
    └── history.ts           # History service wrapper with error handling
```

### Pages & Routes
| Route | Page | Description |
|-------|------|-------------|
| `/` | Dashboard | Main overview with metrics and charts |
| `/claim-analysis` | ClaimAnalysis | Claim fraud risk analysis form |
| `/provider-analysis` | ProviderAnalysis | Provider fraud risk analysis form |
| `/anomaly-detection` | AnomalyDetection | CMS anomaly detection form |
| `/history` | HistoryList | Investigation history table |
| `/history/:id` | HistoryDetail | Individual investigation report |
| `/models` | ModelIntelligence | ML model status and metrics |
| `/system-status` | SystemStatus | Backend health monitoring |
| `*` | (redirect) | Redirects to Dashboard |

### API Communication
- Uses **Axios** with a centralized instance in `api.ts`.
- **Base URL:** Read from `VITE_API_URL` environment variable; defaults to `http://127.0.0.1:8000` in development.
- **Timeout:** 10 seconds.
- **Content-Type:** `application/json`.
- All API functions are exported individually (e.g., `analyzeClaim`, `getHealth`, `fetchHistory`).

### Environment Configuration
- `.env.example`: Contains `VITE_API_URL=https://c9av6ujzgi.execute-api.ap-south-1.amazonaws.com`
- `.env.production`: Same API Gateway URL for production builds.
- In development (no `.env` file), defaults to `http://127.0.0.1:8000`.

### Production Build & S3 Deployment
1. Set `VITE_API_URL` to the API Gateway URL.
2. Run `npm run build` (executes `tsc -b && vite build`).
3. Output goes to `frontend/dist/` directory.
4. Upload `dist/` contents to the S3 bucket (`fraudlens-frontend-*`).
5. S3 bucket has static website hosting enabled with `index.html` as both index and error document.
6. Bucket policy allows public read (`s3:GetObject` for `*` principal).

---

## 9. Complete Backend Explanation

### Framework & Language
- **FastAPI** (Python) — modern async-capable web framework with automatic OpenAPI docs.
- **Uvicorn** — ASGI server running the FastAPI app.
- **Python 3.9+** required.

### Application Entry Point
`backend/main.py` — Creates the FastAPI app instance, configures CORS middleware, defines all API route handlers.

### Folder Structure
```
backend/
├── main.py              # FastAPI app, route handlers, CORS config
├── services.py          # ML model loading, inference logic, feature engineering
├── schemas.py           # Pydantic request/response models
├── db.py                # DynamoDB abstraction layer (boto3)
├── requirements.txt     # Python dependencies
├── Procfile             # EB startup command: uvicorn main:app --host 0.0.0.0 --port 8000
└── .ebextensions/
    ├── 01_packages.config    # Nginx proxy + static files config
    ├── 01_swap.config        # Creates 2GB swap file for t3.micro memory constraints
    ├── 02_eb_config.config   # Instance type (t3.micro), volume, service role
    └── 02_xgboost.config     # Installs XGBoost separately with --no-deps to avoid nvidia_nccl
```

### Request Flow
1. HTTP request arrives at FastAPI.
2. FastAPI matches the route and calls the handler function.
3. Pydantic validates the request body against the schema (e.g., `ClaimRequest`).
4. Handler calls the appropriate `services.*` function.
5. Service function loads features, constructs DataFrame, calls model `.predict_proba()` or `.predict()`.
6. Service function generates risk score, risk level, factors, and recommendations.
7. Handler returns the response (auto-serialized by Pydantic model).

### Validation (Pydantic)
- `ClaimRequest`: 18 fields with type validation, minimum values (`ge=0`), and default values.
- `ProviderRequest`: 31 float fields for provider aggregate metrics.
- `AnomalyRequest`: 3 fields (procedure_category: str, count: int, profile_display_indicator: str).
- `HistoryRecord`: id, type, timestamp, riskScore, riskLevel, status, result (Any).

### Business Logic (services.py)
- **Model Loading:** At import time, `joblib.load()` loads all three `.pkl` model files into memory. If loading fails, models are set to `None`.
- **Model Path Resolution:** Detects whether running locally (models in `../model/`) or on EB (models in `./model/`).
- **Risk Level Calculation:** `_get_risk_level(score)` — ≤30 = LOW, ≤60 = MEDIUM, >60 = HIGH.
- **Recommendations:** `_get_recommendations(risk_level)` — returns a list of actionable strings based on risk level.
- **Feature Importance:** For XGBoost, extracts `feature_importances_` and identifies top active features. For Logistic Regression, uses `coef_` to find top positive coefficients.

### CORS Configuration
```python
cors_origins = [
    "http://localhost:5173",    # Vite dev server
    "http://127.0.0.1:5173",   # Vite dev server (alternative)
    "http://localhost:3000",    # Alternative dev port
]
if FRONTEND_ORIGIN:            # Production S3 URL added dynamically
    cors_origins.append(FRONTEND_ORIGIN)
```
All methods and headers are allowed. Credentials are allowed.

### DynamoDB Integration (db.py)
- Uses **boto3** with the standard AWS credential provider chain (EC2 instance profile in production, `aws configure` locally).
- No hardcoded credentials.
- Handles `float → Decimal` conversion for DynamoDB writes and `Decimal → float/int` conversion for JSON responses.
- Implements pagination for `scan()` operations.
- Health check is informational only — does NOT determine API health.

---

## 10. API Endpoints

| Endpoint | Method | Purpose | Input | Output | Database Interaction |
|----------|--------|---------|-------|--------|---------------------|
| `/health` | GET | API health check | None | Status, model load states, DynamoDB connectivity | READ (DynamoDB DescribeTable) |
| `/model-info` | GET | ML model status + validation metrics | None | Model load states + validation_results.json | None (reads local JSON file) |
| `/analyze-claim` | POST | Claim fraud risk analysis | `ClaimRequest` (18 fields) | `ClaimResponse` (claim_id, fraud_risk_score, risk_level, prediction, risk_factors, recommendation, model_information) | None |
| `/analyze-provider` | POST | Provider fraud risk analysis | `ProviderRequest` (31 fields) | `ProviderResponse` (provider_id, fraud_risk_score, risk_level, top_factors) | None |
| `/analyze-anomaly` | POST | CMS anomaly detection | `AnomalyRequest` (3 fields) | `AnomalyResponse` (anomaly_score, anomaly_status, recommendation) | None |
| `/history` | POST | Save investigation record | `HistoryRecord` (id, type, timestamp, riskScore, riskLevel, status, result) | `{message, id}` | WRITE (DynamoDB PutItem) |
| `/history` | GET | Get all investigation records | None | `List[HistoryRecord]` sorted by timestamp descending | READ (DynamoDB Scan with pagination) |
| `/history/{id}` | GET | Get single investigation record | Path param: `record_id` | `HistoryRecord` or 404 | READ (DynamoDB GetItem) |
| `/history` | DELETE | Delete all investigation records | None | `{message, deleted: count}` | DELETE (DynamoDB Scan + BatchWriteItem DeleteItem) |

---

## 11. Machine Learning Architecture

### Model 1: Claim Fraud Detection (Regularized XGBoost)

```
INPUT: 18 claim features
  ├── 12 numeric: claim_amount, patient_age, number_of_procedures,
  │     length_of_stay_days, deductible_amount, copay_amount,
  │     number_of_previous_claims_patient, number_of_previous_claims_provider,
  │     provider_patient_distance_miles, claim_submitted_late,
  │     service_to_claim_days, policy_days_left
  └── 6 categorical (one-hot encoded → 29 binary features):
        patient_gender, provider_type, provider_specialty,
        admission_type, discharge_type, service_type

TOTAL FEATURES: 41 (after one-hot encoding)

PROCESSING:
  1. Initialize feature vector with zeros for all 41 features.
  2. Map numeric values directly.
  3. One-hot encode categoricals (set matching column to 1).
  4. Wrap in pandas DataFrame.
  5. Call pipeline: StandardScaler → XGBClassifier

MODEL: Regularized XGBoost (Pipeline with StandardScaler)
  - max_depth=4, learning_rate=0.05, subsample=0.8
  - colsample_bytree=0.8, reg_alpha=1.0, reg_lambda=10.0
  - class_weight handled via scale_pos_weight

OUTPUT:
  - predict_proba()[0][1] → probability of fraud (0.0 to 1.0)
  - Scaled to 0–100 as fraud_risk_score
  - Risk level: LOW (≤30), MEDIUM (≤60), HIGH (>60)
  - Top 3 active risk factors with importance scores
  - Actionable recommendations based on risk level
```

**Verbal Explanation (simple):**
"The claim model takes 18 pieces of information about a claim — like the amount, patient age, procedures, provider type — and uses an XGBoost algorithm to predict how likely it is to be fraudulent. It gives a score from 0 to 100, where higher means more suspicious. It also tells you which specific factors contributed most to that score."

**Validation Metrics:**
- Train F1: 0.6985 | Test F1: 0.6860
- Test PR-AUC: 0.7505
- Test Recall: 0.8325
- Generalization Gap: 0.0125 (NONE — no overfitting)
- 5-Fold CV Mean F1: 0.6908
- Leakage Risk: NO
- Training Records: 16,057 | Test Records: 4,015

---

### Model 2: Provider Fraud Profiling (Logistic Regression)

```
INPUT: 31 aggregate provider features
  ├── Volume: num_unique_beneficiaries, total_claims,
  │     total_inpatient_claims, total_outpatient_claims
  ├── Financial: insc_claim_amt_reimbursed_sum/mean/max,
  │     deductible_amt_paid_sum/mean/max
  ├── Patient Demographics: age_mean, gender_mean, claim_duration_mean,
  │     num_diagnosis_mean, num_procedures_mean
  ├── Reimbursement: ip/op_annual_reimbursement/deductible_amt_mean
  └── Chronic Conditions (10): alzheimer, heartfailure, kidneydisease,
        cancer, obstrpulmonary, depression, diabetes, ischemicheart,
        osteoporasis, rheumatoidarthritis, stroke (all as means)

PROCESSING:
  1. Map request fields to model feature names (case-insensitive matching).
  2. Default unmatched features to 0.0.
  3. Wrap in pandas DataFrame.
  4. Call LogisticRegression.predict_proba()

MODEL: Logistic Regression
  - class_weight='balanced'
  - Trained on provider-level aggregated data from CMS provider fraud dataset.

OUTPUT:
  - predict_proba()[0][1] → probability of fraudulent provider (0.0 to 1.0)
  - Scaled to 0–100 as fraud_risk_score
  - Risk level: LOW (≤30), MEDIUM (≤60), HIGH (>60)
  - Top 3 positive-coefficient features as risk indicators
```

**Verbal Explanation (simple):**
"The provider model looks at a provider's overall behavior pattern — how many patients they serve, how much they bill, how long claims take, what chronic conditions their patients have. Using Logistic Regression, it calculates how similar this provider's behavior is to known fraudulent providers."

**Validation Metrics:**
- Train F1: 0.5512 | Test F1: 0.5401
- Test PR-AUC: 0.7558
- Test Recall: 0.9010
- Generalization Gap: 0.0112 (NONE — no overfitting)
- 5-Fold CV Mean PR-AUC: 0.6913
- Leakage Risk: NO
- Training Records: 4,328 | Test Records: 1,082

---

### Model 3: CMS Anomaly Detection (Isolation Forest)

```
INPUT: 3 utilization features
  ├── procedure_category (str) — e.g., "Cardiology Services"
  ├── count (int) — procedure volume
  └── profile_display_indicator (str) — "Y" or "N"

PROCESSING:
  1. Wrap input in DataFrame.
  2. Pipeline: ColumnTransformer(
       StandardScaler for 'Count',
       OneHotEncoder for 'Procedure_Category' and 'Profile_Display_Indicator'
     ) → IsolationForest

MODEL: Isolation Forest (unsupervised)
  - contamination=0.01 (assume 1% anomalies)
  - Trained on 635,353 real CMS utilization records
  - No labeled fraud data (unsupervised)

OUTPUT:
  - decision_function() → raw anomaly score
  - Transformed to 0–100 anomaly percentage
  - Status: NORMAL PATTERN (≤30), MODERATE ANOMALY (≤60), SUSPICIOUS PATTERN (>60)
  - Recommendation text based on status
```

**Verbal Explanation (simple):**
"The anomaly model uses an Isolation Forest — an unsupervised algorithm — trained on over 635,000 real CMS billing records. It doesn't know what fraud looks like; instead, it learns what normal utilization patterns look like and flags anything that deviates significantly. If a provider is billing an unusual volume or unusual category compared to the norm, it gets flagged."

**Training Stats:**
- Records: 635,353
- Anomalies Detected: 6,309 (~0.99%)
- Leakage Risk: NO

---

## 12. DynamoDB

### Table Configuration
| Setting | Value |
|---------|-------|
| Table Name | `FraudInvestigationHistory` |
| Region | `us-east-1` (configurable via `AWS_REGION` env var) |
| Partition Key | `id` (String) — UUID generated by the frontend |
| Sort Key | None |
| Capacity Mode | On-Demand (pay-per-request) |

### Record Structure
Each investigation record stored in DynamoDB:
```json
{
  "id": "uuid-string",
  "type": "Claim | Provider | Anomaly",
  "timestamp": "2026-08-25T22:30:00.000Z",
  "riskScore": 85.5,
  "riskLevel": "HIGH",
  "status": "HIGH",
  "result": {
    "claim_id": "...",
    "fraud_risk_score": 85.5,
    "risk_level": "HIGH",
    "prediction": "HIGH RISK - INVESTIGATION RECOMMENDED",
    "risk_factors": [...],
    "recommendation": [...],
    "model_information": {...}
  }
}
```

### Read/Write Operations
| Operation | Endpoint | DynamoDB API | Details |
|-----------|----------|-------------|---------|
| Save record | `POST /history` | `PutItem` | Converts floats to Decimal before write |
| Get all records | `GET /history` | `Scan` + pagination | Converts Decimals back to float, sorts by timestamp DESC |
| Get by ID | `GET /history/{id}` | `GetItem` | Returns single record or 404 |
| Delete all | `DELETE /history` | `Scan` + `BatchWriteItem(DeleteItem)` | Scans for all IDs, batch deletes |
| Health check | `GET /health` | `DescribeTable` (implicit via `table.table_status`) | Informational only |

### Why DynamoDB Was Selected
- **Serverless / On-Demand:** No capacity planning needed for a low-traffic academic project.
- **Cost-Effective:** Pay-per-request pricing means near-zero cost when idle.
- **Simple Schema:** Investigation records are key-value documents — no relational joins needed.
- **AWS-Native Integration:** Seamlessly integrates with the EC2 instance profile via boto3.
- **No Database Server Management:** No need to provision, patch, or manage an RDS instance.

---

## 13. AWS Architecture

### Amazon S3 (Simple Storage Service)
- **What it is:** Object storage service that can serve static websites.
- **Why we use it:** To host the production React/Vite frontend as a static website accessible via a public URL.
- **What it does in FraudLens:** Stores and serves the compiled frontend files (HTML, JS, CSS, assets) from the `dist/` build output.
- **What goes into it:** `index.html`, compiled JavaScript bundles, CSS files, static assets.
- **What comes out of it:** The complete frontend web application served to the user's browser via HTTP.
- **How it connects:** Users access the S3 website URL in their browser. The frontend JavaScript running in the browser makes API requests to the API Gateway URL (configured via `VITE_API_URL` at build time).
- **Configuration:** Static website hosting enabled, `index.html` as both index and error document, public-read bucket policy.

### Amazon API Gateway
- **What it is:** Fully managed API proxy service.
- **Why we use it:** To provide a single HTTPS endpoint for the frontend to call, abstracting away the Elastic Beanstalk internal URL. Also handles CORS at the API level.
- **What it does in FraudLens:** Receives all API requests from the frontend (e.g., `POST /analyze-claim`) and proxies them to the Elastic Beanstalk environment.
- **What goes into it:** HTTPS requests from the frontend (via `VITE_API_URL`).
- **What comes out of it:** Proxied requests forwarded to the EB environment; responses returned to the frontend.
- **How it connects:** Frontend → API Gateway → Elastic Beanstalk. Configured with `ANY /{proxy+}` route for full passthrough.
- **Configuration:** HTTP API type, `ANY /{proxy+}` integration to EB URL, CORS enabled.

### AWS Elastic Beanstalk
- **What it is:** Platform-as-a-Service (PaaS) that automates EC2 instance provisioning, deployment, scaling, and monitoring.
- **Why we use it:** To simplify deployment of the FastAPI backend without manually configuring EC2, security groups, auto-scaling, etc. Handles deployment lifecycle, environment variables, and health monitoring.
- **What it does in FraudLens:** Hosts the FastAPI application with all three ML models on a managed EC2 instance. Handles deployment versioning (v1–v6), log management, and instance health.
- **What goes into it:** A ZIP file containing `backend/` source code + `model/` pickle files + `.ebextensions/` configs + `Procfile` + `requirements.txt`.
- **What comes out of it:** A running FastAPI API accessible via the EB environment URL.
- **How it connects:** API Gateway proxies requests to EB URL. EB runs uvicorn → FastAPI → ML models. FastAPI connects to DynamoDB via boto3 using the EC2 instance profile.
- **Configuration:**
  - Platform: Python 3.9+
  - Environment type: Single Instance (no load balancer)
  - Instance type: `t3.micro` (free-tier eligible)
  - Region: `ap-south-1` (Mumbai)
  - Service role: `FraudLensEBServiceRole`
  - Proxy: nginx
  - 2GB swap file for memory-constrained model loading

### Amazon DynamoDB
- **What it is:** Fully managed NoSQL key-value database.
- **Why we use it:** To persistently store investigation history records with zero server management.
- **What it does in FraudLens:** Stores every analysis result (claim, provider, anomaly) as a document with risk scores, risk levels, and full result objects. Supports retrieval, filtering, and deletion.
- **What goes into it:** Investigation records via `PutItem` from the `POST /history` endpoint.
- **What comes out of it:** Individual or all investigation records via `GetItem` or `Scan`.
- **How it connects:** FastAPI backend connects to DynamoDB via boto3 using the EC2 instance profile (IAM role). No hardcoded credentials.
- **Configuration:** Table `FraudInvestigationHistory`, partition key `id` (String), On-Demand capacity.

### AWS IAM (Identity and Access Management)
- **What it is:** AWS security service for managing access permissions.
- **Why we use it:** To control who can deploy to EB, what the EC2 instance can access, and what DynamoDB operations are permitted.
- **What it does in FraudLens:** Provides three distinct roles/policies for different access scopes.
- **Roles:**
  1. `FraudLensEBServiceRole` — EB service role (trusts `elasticbeanstalk.amazonaws.com`), has `AWSElasticBeanstalkService` managed policy.
  2. `FraudLensEC2RuntimeRole` — EC2 instance profile role (trusts `ec2.amazonaws.com`), has `AWSElasticBeanstalkWebTier` + custom DynamoDB inline policy (`PutItem`, `GetItem`, `Scan`, `DeleteItem`, `BatchWriteItem` on `FraudInvestigationHistory` table).
  3. `FraudLensDeployUser` — IAM user with deployment permissions (EB, S3, IAM passrole, DynamoDB, CloudFormation, EC2, Auto Scaling).

### Amazon CloudWatch
- **What it is:** AWS monitoring and observability service.
- **Why we use it:** Automatically provisioned by Elastic Beanstalk for basic instance monitoring.
- **What it does in FraudLens:** Monitors EC2 instance CPU utilization, health status, and deployment events. Provides deployment logs and application logs.
- **Note:** CloudWatch is automatically enabled by EB. No custom dashboards or alarms have been configured (beyond basic EB health monitoring). A billing alarm may be set separately.

### AWS CloudFormation
- **What it is:** Infrastructure-as-Code service that provisions AWS resources from templates.
- **Why we use it:** Automatically managed by Elastic Beanstalk — not directly configured.
- **What it does in FraudLens:** EB uses CloudFormation internally to create and manage the infrastructure stack (EC2 instance, security groups, auto-scaling group, etc.).
- **Evidence:** CloudFormation stack name visible in EB logs: `awseb-e-epfecvcqq2-stack`.

---

## 14. Complete Request Flow

### What Happens When a User Clicks "Analyze Claim"

1. **User** fills out the Claim Analysis form on the frontend (18 fields: claim amount, patient age, procedures, etc.) and clicks **"Analyze Claim"**.

2. **React frontend** (`ClaimAnalysis.tsx`) collects form data via `FormData`, constructs a JSON object with all 18 fields, and calls `analyzeClaim(data)` from `api.ts`.

3. **Axios** sends a `POST` request to `{VITE_API_URL}/analyze-claim` — in production, this is `https://c9av6ujzgi.execute-api.ap-south-1.amazonaws.com/analyze-claim`.

4. **Amazon API Gateway** receives the HTTPS request and proxies it via the `ANY /{proxy+}` route to the **Elastic Beanstalk** environment URL.

5. **Elastic Beanstalk (nginx)** receives the request on the EC2 instance and forwards it to **uvicorn** on port 8000.

6. **FastAPI** matches the route to `api_analyze_claim(request: ClaimRequest)` in `main.py`. Pydantic validates all 18 fields.

7. **`services.analyze_claim(request)`** is called:
   - Initializes a 41-feature vector (all zeros).
   - Maps the 12 numeric fields directly.
   - One-hot encodes the 6 categorical fields.
   - Creates a pandas DataFrame.
   - Calls `claim_model.predict_proba(df)[0][1]` — the XGBoost pipeline (StandardScaler → XGBClassifier).
   - Multiplies probability by 100 to get `fraud_risk_score`.
   - Determines `risk_level` (LOW/MEDIUM/HIGH).
   - Extracts top 3 active feature importances as `risk_factors`.
   - Generates `recommendation` list based on risk level.
   - Returns a dict matching `ClaimResponse` schema.

8. **FastAPI** serializes the response as JSON and returns it through nginx → EB → API Gateway → browser.

9. **React frontend** receives the response, updates state with `setResult(res)`, and renders:
   - Risk score gauge (0–100 circular visualization)
   - Risk level badge (color-coded)
   - Prediction text
   - Risk factors with impact labels
   - Recommendations list

10. **Immediately after displaying results**, the frontend calls `saveHistory()`:
    - Constructs a `HistoryRecord` with the result.
    - Sends `POST /history` to save it to **DynamoDB**.
    - DynamoDB stores the complete investigation record.

11. **User can view this record later** on the Investigation History page, which calls `GET /history` to retrieve all records from DynamoDB sorted by timestamp.

---

## 15. Deployment Architecture

### Region & Infrastructure
| Component | Value |
|-----------|-------|
| AWS Region | `ap-south-1` (Mumbai) |
| EB Environment ID | `e-epfecvcqq2` |
| EC2 Instance ID | `i-01ec6ae3c06acf8f3` |
| EC2 Instance Type | `t3.micro` (2 vCPU, 1 GB RAM) |
| Root Volume | 10 GB gp2 |
| Swap File | 2 GB (configured via `.ebextensions/01_swap.config`) |
| EB Platform | Python 3.9+ |
| Proxy Server | nginx |
| Application Server | uvicorn |
| S3 Bucket | `fraudlens-frontend-418272772343` |
| API Gateway URL | `https://c9av6ujzgi.execute-api.ap-south-1.amazonaws.com` |
| DynamoDB Table | `FraudInvestigationHistory` (On-Demand) |

### Deployment Process
1. **Package backend:** Run `package_eb.py` — creates a ZIP file containing `backend/` files (at root level) + `model/` folder with `.pkl` files. Uses forward slashes for Linux compatibility.
2. **Upload to EB:** Upload ZIP via EB console or CLI.
3. **EB deploys:** Extracts ZIP, creates virtual environment, installs `requirements.txt`, runs `.ebextensions` configs (swap file, nginx config, XGBoost install), starts uvicorn via Procfile.
4. **Build frontend:** Set `VITE_API_URL` to API Gateway URL, run `npm run build`.
5. **Upload to S3:** Upload `dist/` contents to S3 bucket with static website hosting.
6. **Set CORS:** Set `FRONTEND_ORIGIN` environment variable in EB to the S3 website URL.

---

## 16. IAM

### Deployment User: `FraudLensDeployUser`
- An IAM user used for deployment operations (EB deploy, S3 upload, DynamoDB table creation).
- Has a custom policy granting permissions for EB, S3, CloudFormation, EC2, Auto Scaling, DynamoDB, and IAM:PassRole.
- Used only from the developer's machine; no programmatic access from the application itself.

### EB Service Role: `FraudLensEBServiceRole`
- Trust relationship: `elasticbeanstalk.amazonaws.com`
- Managed policy: `AWSElasticBeanstalkService`
- Allows EB to manage EC2 instances, security groups, CloudFormation stacks, and health monitoring.
- Referenced in `.ebextensions/02_eb_config.config`: `ServiceRole: FraudLensEBServiceRole`

### EC2 Runtime Role: `FraudLensEC2RuntimeRole`
- Trust relationship: `ec2.amazonaws.com`
- Policies:
  1. `AWSElasticBeanstalkWebTier` (managed) — health reporting, log uploads, basic EC2 operations.
  2. Custom inline policy — DynamoDB access:
     - Actions: `dynamodb:PutItem`, `dynamodb:GetItem`, `dynamodb:Scan`, `dynamodb:DeleteItem`, `dynamodb:BatchWriteItem`
     - Resource: `arn:aws:dynamodb:<REGION>:<ACCOUNT>:table/FraudInvestigationHistory`
- This role is assumed by the EC2 instance via the instance profile. The FastAPI application uses boto3 which automatically picks up these credentials via the EC2 metadata service.

### Why Permissions Were Required
- Without the EC2 runtime role, the FastAPI backend would receive `NoCredentialsError` when trying to access DynamoDB.
- Without the EB service role, Elastic Beanstalk cannot manage the infrastructure (create/terminate EC2 instances, update CloudFormation stacks).
- Without the deployment user, the developer cannot upload application versions to EB or upload frontend files to S3.

> ⚠️ **No AWS credentials, access keys, secret keys, or tokens are stored in the application code.** The backend uses the EC2 instance profile (standard AWS credential provider chain) in production.

---

## 17. Important Deployment Problems We Solved

### Problem 1: Backslash Path Separators in ZIP File
- **Problem:** The initial deployment ZIP was created on Windows, which used backslash (`\`) path separators. When EB extracted the ZIP on Linux, it failed with: `"source bundle appears to use backslashes as path separators"`.
- **Cause:** Python's `os.path.join()` on Windows produces `backend\main.py` instead of `backend/main.py` inside the ZIP archive.
- **Fix:** Updated `package_eb.py` to use `.replace('\\', '/')` to normalize all paths to forward slashes. Also restructured the ZIP so backend files are at the root level (not inside a `backend/` subfolder).
- **Result:** Deployment ZIP extracts correctly on Linux.

### Problem 2: XGBoost / nvidia_nccl_cu13 Dependency Failure
- **Problem:** When EB installed `requirements.txt`, pip tried to install `xgboost` which pulled in `nvidia_nccl_cu13` (252 MB GPU library). The download repeatedly failed on the t3.micro instance due to network timeout/memory constraints: `"Download failed after 6 attempts because not enough bytes were received (145.8 MB/252.4 MB)"`.
- **Cause:** XGBoost's PyPI package includes optional GPU/CUDA dependencies that pip resolves transitively. On a 1GB RAM t3.micro, the download would stall and fail.
- **Fix:** Removed `xgboost` from `requirements.txt`. Added `.ebextensions/02_xgboost.config` which runs `pip install xgboost --no-deps` as a container command after the main install. The `--no-deps` flag prevents pip from pulling nvidia_nccl and other unnecessary transitive dependencies.
- **Result:** XGBoost installs successfully in ~2 seconds without GPU dependencies.

### Problem 3: Memory Constraints on t3.micro
- **Problem:** The t3.micro instance has only 1 GB RAM. Loading three ML model pickle files (total ~1 MB compressed but expand in memory) plus pandas, numpy, scikit-learn, and XGBoost at startup could exhaust available memory.
- **Cause:** Python processes, nginx, and system processes compete for the 1 GB memory.
- **Fix:** Added `.ebextensions/01_swap.config` which creates a 2 GB swap file on first deployment. This extends effective memory from 1 GB to 3 GB at the cost of slower swapping to disk.
- **Result:** All three models load successfully; API responds within acceptable latency.

### Problem 4: Frontend Pointing to localhost in Production
- **Problem:** The production frontend build was initially calling `http://127.0.0.1:8000` instead of the API Gateway URL.
- **Cause:** The `VITE_API_URL` environment variable was not set before running `npm run build`. Vite embeds environment variables at build time, not runtime.
- **Fix:** Created `.env.production` with `VITE_API_URL=https://c9av6ujzgi.execute-api.ap-south-1.amazonaws.com`. Rebuilt the frontend and re-uploaded to S3.
- **Result:** Frontend correctly calls the API Gateway URL in production.

### Problem 5: CORS Errors in Production
- **Problem:** Browser blocked API requests from the S3 frontend with CORS errors.
- **Cause:** The FastAPI CORS middleware only included localhost origins. The S3 website URL was not in the allowed origins list.
- **Fix:** Added the `FRONTEND_ORIGIN` environment variable to the EB environment, set to the S3 website URL. The backend code dynamically appends this to the CORS allowed origins list.
- **Result:** CORS requests from S3 frontend to API Gateway succeed.

### Problem 6: Auto Scaling Group Permissions
- **Problem:** EB deployment failed with permission errors related to Auto Scaling.
- **Cause:** The deployment user lacked `autoscaling:*` permissions needed by CloudFormation when EB manages the Auto Scaling Group.
- **Fix:** Added Auto Scaling permissions to the deployment user's IAM policy.
- **Result:** EB deployment completes successfully.

---

## 18. Production Configuration

### Environment Variables

**Backend (EB Environment):**
| Variable | Value | Purpose |
|----------|-------|---------|
| `AWS_REGION` | `us-east-1` | DynamoDB region |
| `DYNAMODB_TABLE_NAME` | `FraudInvestigationHistory` | Table name |
| `FRONTEND_ORIGIN` | `http://fraudlens-frontend-*.s3-website-us-east-1.amazonaws.com` | S3 URL for CORS |

**Frontend (build-time):**
| Variable | Value | Purpose |
|----------|-------|---------|
| `VITE_API_URL` | `https://c9av6ujzgi.execute-api.ap-south-1.amazonaws.com` | API Gateway URL |

### Local vs Production
| Aspect | Local | Production |
|--------|-------|------------|
| Frontend URL | `http://localhost:5173` | S3 website URL |
| API URL | `http://127.0.0.1:8000` | API Gateway URL |
| DynamoDB | Requires `aws configure` or returns 503 | Uses EC2 instance profile |
| ML Inference | ✅ Works | ✅ Works |
| History | ⚠️ Requires AWS credentials | ✅ Works via IAM role |

---

## 19. CORS

### What Is CORS?
Cross-Origin Resource Sharing (CORS) is a browser security mechanism that restricts web pages from making requests to a different domain/origin than the one that served the page. If the frontend (S3) is at `http://fraudlens.s3-website.amazonaws.com` and the API is at `https://c9av6ujzgi.execute-api.amazonaws.com`, the browser will block API requests unless the server explicitly allows that origin.

### Why It Matters for FraudLens
The frontend (served from S3) and the backend (served via API Gateway → EB) are on different domains. Without CORS configuration, no API calls from the frontend would work in production.

### The Problem We Encountered
After deploying the frontend to S3 and the backend to EB with API Gateway, the browser blocked all API requests with a CORS error. The frontend could not reach the backend.

### How It Was Diagnosed & Fixed
1. **Diagnosis:** Browser DevTools → Network tab showed `CORS policy: No 'Access-Control-Allow-Origin' header` errors.
2. **Root cause:** The FastAPI CORS middleware only listed localhost origins. The S3 origin was not included.
3. **Fix:** Added the `FRONTEND_ORIGIN` environment variable in the EB configuration, set to the S3 website URL. The `main.py` code checks for this variable and appends it to `cors_origins`:
   ```python
   FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "")
   if FRONTEND_ORIGIN:
       cors_origins.append(FRONTEND_ORIGIN)
   ```
4. **Result:** The `Access-Control-Allow-Origin` header now includes the S3 URL, and CORS requests succeed.

### How the Final Frontend Communicates
Frontend (S3) → HTTPS request → API Gateway (handles CORS at proxy level) → EB → FastAPI (also handles CORS) → Response with CORS headers → Browser allows the response.

---

## 20. Cost Optimization

### t3.micro Instance
- Free-tier eligible (750 hours/month for 12 months).
- 2 vCPU (burstable), 1 GB RAM.
- Adequate for a low-traffic academic project.
- Swap file extends effective memory to 3 GB.

### Single-Instance Elastic Beanstalk
- **No load balancer** — saves ~$16/month (ALB cost).
- Single-instance EB environments directly expose the EC2 instance with a public IP.
- Suitable because FraudLens is a demo/academic project with minimal concurrent users.

### DynamoDB On-Demand
- Pay-per-request pricing — near-zero cost for academic use.
- No need to provision read/write capacity units.
- No charges when idle.

### Billing Alarm
- An AWS billing alarm should be configured to alert if costs exceed a threshold (e.g., $5/month).
- CloudWatch billing alarms are available in the `us-east-1` region.

### Scale-to-Zero Strategy
After the interim/final review:
- **Terminate the EB environment** to stop EC2 charges.
- **Keep DynamoDB table** (zero cost when idle on On-Demand).
- **Keep S3 bucket** (minimal storage cost for static files).
- **Delete API Gateway** if not needed.
- This reduces monthly cost to effectively $0.

---

## 21. Current Status

| Component | Status | Evidence |
|-----------|--------|----------|
| Frontend (React/TS/Vite) | ✅ DONE | 8 pages, layout, components, routing all functional |
| Backend (FastAPI/Python) | ✅ DONE | 9 endpoints, Pydantic schemas, error handling |
| Claim Model (XGBoost) | ✅ DONE | `best_claim_model.pkl` (178 KB), validated (F1=0.686) |
| Provider Model (LogReg) | ✅ DONE | `best_provider_model.pkl` (2 KB), validated (PR-AUC=0.756) |
| Anomaly Model (IsoForest) | ✅ DONE | `cms_anomaly_model.pkl` (644 KB), trained on 635K records |
| DynamoDB Integration | ✅ DONE | CRUD operations via boto3, float/Decimal handling |
| S3 Frontend Hosting | ✅ DONE | Bucket created, static hosting enabled, policy applied |
| API Gateway | ✅ DONE | HTTP API with ANY proxy route |
| Elastic Beanstalk | ✅ DONE | Environment running, v4+ deployed with XGBoost fix |
| IAM Roles & Policies | ✅ DONE | EB service role, EC2 runtime role, deploy user |
| CORS Configuration | ✅ DONE | Frontend origin dynamically added |
| Data Preprocessing | ✅ DONE | 3 datasets preprocessed (provider, claim, CMS) |
| Model Training Pipeline | ✅ DONE | `train_models.py` + `fix_claim_model.py` |
| Model Validation | ✅ DONE | `validation_results.json` with metrics |
| Authentication | ❌ NOT IMPLEMENTED | Planned for Final Review |
| Alerting (SNS) | ❌ NOT IMPLEMENTED | Planned for Final Review |
| Unit/Integration Tests | ⚠️ PARTIAL | `test_api.py` exists (manual); no automated test suite |
| CI/CD Pipeline | ❌ NOT IMPLEMENTED | Planned for Final Review |

---

## 22. What Is Already Working

1. ✅ Full React frontend with 8 pages and sidebar navigation.
2. ✅ Claim Analysis with Regularized XGBoost — produces risk scores, risk factors, and recommendations.
3. ✅ Provider Analysis with Logistic Regression — produces risk scores and top risk indicators.
4. ✅ CMS Anomaly Detection with Isolation Forest — produces anomaly scores and status.
5. ✅ Investigation History with DynamoDB — save, list, view details, delete all.
6. ✅ Dashboard with summary metrics, risk distribution chart, and recent activity.
7. ✅ Model Intelligence page showing model status and validation metrics.
8. ✅ System Status page with real-time health checking.
9. ✅ FastAPI backend with 9 REST endpoints.
10. ✅ Pydantic validation on all request/response models.
11. ✅ Full AWS deployment: S3 → API Gateway → EB → FastAPI → ML → DynamoDB.
12. ✅ Production frontend calling API Gateway (not localhost).
13. ✅ CORS properly configured for S3 → API Gateway flow.
14. ✅ XGBoost dependency issue resolved via `--no-deps` installation.
15. ✅ Swap file configured for t3.micro memory constraints.

---

## 23. What Is Still Remaining

1. ❌ User authentication and role-based access control.
2. ❌ SNS email notifications for high-risk detections.
3. ❌ CloudFront CDN for frontend performance and HTTPS.
4. ❌ Comprehensive automated test suite (unit + integration).
5. ❌ CI/CD pipeline for automated deployment.
6. ❌ Batch analysis (upload CSV, analyze multiple claims at once).
7. ❌ PDF report export.
8. ❌ CloudWatch custom dashboards and alerts.
9. ❌ Multi-tenant support.
10. ❌ Model retraining pipeline.

---

## 24. Interim Review Demo Procedure

### Step-by-Step Demo Script

**Step 1:** Open the application URL in the browser (S3 hosted URL or localhost if not deployed).

**Step 2:** "This is the FraudLens AI dashboard. You can see summary metrics here — total analyses run, high-risk cases, suspicious patterns, and active ML models. The pie chart shows the distribution of risk levels across all past investigations."

**Step 3:** Click on **Claim Analysis** in the sidebar.

**Step 4:** "This is the Claim Analysis module. The investigator enters 18 fields about a claim — claim amount, patient age, number of procedures, provider type, and so on."

**Step 5:** Enter suspicious values: **Claim Amount = $100,000**, **Number of Procedures = 15**, **Provider Type = Specialist Office**, **Provider Patient Distance = 500 miles**, **Claim Submitted Late = 1**, **Service to Claim Days = 100**. Leave other fields at defaults.

**Step 6:** Click **"Analyze Claim"**. "The request goes from the browser to API Gateway, then to Elastic Beanstalk, where FastAPI invokes the Regularized XGBoost model."

**Step 7:** Show the result: "The model returned a risk score of [X]%, classified as [HIGH/MEDIUM/LOW]. It identified these specific risk factors — you can see Provider Type Specialist Office, high claim amount, and high provider-patient distance are flagged. The system also provides actionable recommendations."

**Step 8:** Navigate to **Investigation History**. "The analysis was automatically saved to DynamoDB. You can see it here with the timestamp and risk level."

**Step 9:** Click on the record. "This is the full investigation report — all input data and analysis results are stored and retrievable."

**Step 10:** Navigate to **System Status**. "This page shows that the FastAPI backend is online, all three ML models are loaded, and DynamoDB is connected."

**Step 11:** Navigate to **Model Intelligence**. "This page shows the validation metrics for each model. The claim model has a Test F1 of 0.686 and PR-AUC of 0.751. The provider model has PR-AUC of 0.756. The anomaly model is unsupervised and was trained on 635,353 real CMS records."

**Step 12:** "The entire system is deployed on AWS: frontend on S3, API routing through API Gateway, backend on Elastic Beanstalk with a t3.micro instance, and DynamoDB for persistent storage."

---

## 25. How to Explain the Architecture Verbally (60 seconds)

> "FraudLens AI is a full-stack web application for insurance fraud detection. The frontend is a React application built with TypeScript and Vite, hosted on Amazon S3 as a static website. When the user submits a claim for analysis, the request goes to Amazon API Gateway, which proxies it to our Elastic Beanstalk environment — that's a managed EC2 instance running a FastAPI backend on Python. The backend loads three machine learning models at startup: a Regularized XGBoost for claim-level fraud detection, a Logistic Regression for provider risk profiling, and an Isolation Forest for anomaly detection on CMS utilization data. The model performs inference in real time and returns a risk score, risk factors, and recommendations. Every analysis is automatically saved to DynamoDB for investigation history. The system uses IAM roles for security — no hardcoded credentials — and the whole thing costs near-zero when idle because we use On-Demand DynamoDB and a t3.micro free-tier instance."

---

## 26. How to Explain the Project in 30 Seconds (Elevator Pitch)

> "FraudLens AI is a cloud-native investigation assistant for insurance fraud detection. An investigator enters claim or provider details into our React web interface, and three machine learning models — XGBoost, Logistic Regression, and Isolation Forest — analyze the data in real time to produce fraud risk scores, identify suspicious factors, and recommend actions. The entire system is deployed on AWS using S3, API Gateway, Elastic Beanstalk, and DynamoDB. It's designed to help investigators prioritize the highest-risk cases instead of reviewing every claim manually."

---

## 27. How to Explain the ML Component

> "We have three machine learning models. The first is a Regularized XGBoost classifier trained on 20,000 healthcare claims to predict fraud probability based on 41 features — things like claim amount, provider type, number of procedures, and patient-provider distance. The second is a Logistic Regression model that profiles providers by aggregating their claim history — total reimbursements, patient volume, chronic condition proportions — over 31 features. The third is an Isolation Forest, which is an unsupervised anomaly detection algorithm trained on 635,000 real CMS utilization records. It doesn't know what fraud looks like; instead, it learns what normal billing patterns look like and flags anything that significantly deviates. All three models were validated for overfitting using train/test splits and cross-validation, and none showed significant overfitting."

---

## 28. How to Explain Each AWS Service (Memorizable Sentences)

**Amazon S3:**
> "S3 hosts our frontend as a static website. We upload the built React files to an S3 bucket with public read access, and users access it through a public URL."

**Amazon API Gateway:**
> "API Gateway is the front door for our backend API. It provides a single HTTPS endpoint that the frontend calls, and it proxies all requests to our Elastic Beanstalk environment."

**AWS Elastic Beanstalk:**
> "Elastic Beanstalk is a Platform-as-a-Service that manages our EC2 instance. We upload a ZIP file with our code and models, and EB handles deployment, environment setup, and health monitoring automatically."

**Amazon DynamoDB:**
> "DynamoDB is our NoSQL database for storing investigation history. It's serverless and on-demand, so it costs nothing when idle and requires no server management."

**AWS IAM:**
> "IAM manages security permissions. We have a service role for Elastic Beanstalk, an instance profile role that gives the EC2 instance permission to access DynamoDB, and a deployment user for uploading code."

**Amazon CloudWatch:**
> "CloudWatch is automatically enabled by Elastic Beanstalk for monitoring. It tracks CPU usage, health status, and deployment logs for our EC2 instance."

**AWS CloudFormation:**
> "CloudFormation is used behind the scenes by Elastic Beanstalk to provision and manage our infrastructure as code. It creates the EC2 instance, security groups, and auto-scaling configuration."

---

## 29. Likely Faculty Questions

### Q1: Why did you choose AWS over other cloud providers?
**Short Answer:** AWS has the broadest range of managed services, strong free-tier offerings for academic projects, and excellent documentation.
**Deeper Answer:** AWS was selected because it offers Elastic Beanstalk (simplifies deployment without manual EC2 management), DynamoDB (serverless NoSQL with zero idle cost), API Gateway (managed API proxy with built-in CORS), and S3 (static website hosting). The free-tier eligibility of t3.micro and DynamoDB On-Demand makes it cost-effective for a student project. Additionally, AWS skills are highly valued in the industry.

### Q2: Why Elastic Beanstalk instead of deploying directly on EC2?
**Short Answer:** EB automates deployment, environment management, and health monitoring that we'd have to configure manually on bare EC2.
**Deeper Answer:** With raw EC2, we'd need to manually install Python, configure nginx, set up systemd services, manage security groups, handle deployment rollbacks, and set up health monitoring. EB handles all of this through a simple ZIP upload. It also manages environment variables, log rotation, and deployment versioning. For a student project, this significantly reduces DevOps complexity while still using real EC2 instances underneath.

### Q3: Why API Gateway? Why not call Elastic Beanstalk directly?
**Short Answer:** API Gateway provides a stable HTTPS endpoint, handles CORS, and decouples the frontend from the backend infrastructure.
**Deeper Answer:** The EB environment URL can change if the environment is rebuilt. API Gateway provides a fixed, human-readable URL. It also provides automatic HTTPS (SSL/TLS), request/response logging, throttling capabilities, and a clean separation between the frontend's API contract and the backend implementation. If we switch from EB to Lambda in the future, the frontend URL doesn't change.

### Q4: Why DynamoDB instead of a relational database like RDS?
**Short Answer:** DynamoDB is serverless with zero idle cost, requires no server management, and our data is simple key-value records that don't need relational joins.
**Deeper Answer:** Our investigation history records are self-contained documents — each record has an ID and a JSON blob with the full analysis result. There are no foreign keys, no joins, no complex queries. DynamoDB's on-demand pricing means we pay nothing when the system is idle (critical for an academic project). RDS would require a minimum instance running 24/7 (~$12+/month) even when idle, plus database administration overhead.

### Q5: Why S3 for frontend hosting?
**Short Answer:** S3 provides free, scalable static website hosting — perfect for a React SPA with no server-side rendering.
**Deeper Answer:** Our frontend is a compiled React application — just HTML, JS, and CSS files. S3 serves these files with high availability and low latency at minimal cost. There's no server-side rendering, so we don't need a Node.js server. S3 static website hosting is effectively free for our usage levels. In the future, we could add CloudFront for CDN caching and custom HTTPS.

### Q6: Why XGBoost for claim fraud detection?
**Short Answer:** XGBoost was selected as the best-performing model after comparing Logistic Regression, Random Forest, and XGBoost on PR-AUC metric.
**Deeper Answer:** We trained three models and compared them on PR-AUC (Precision-Recall AUC), which is the right metric for imbalanced classification problems like fraud detection. XGBoost achieved the best PR-AUC. We also applied regularization (max_depth=4, reg_alpha=1.0, reg_lambda=10.0) to prevent overfitting, resulting in a generalization gap of only 0.0125 between train and test F1 scores.

### Q7: Why not use deep learning for fraud detection?
**Short Answer:** Tabular data with <50 features doesn't benefit much from deep learning. XGBoost is known to outperform neural networks on structured/tabular data.
**Deeper Answer:** Our dataset has 41 structured features with 20,000 records. Research consistently shows that gradient-boosted trees (XGBoost, LightGBM) outperform deep learning on tabular datasets of this size. Deep learning requires much more data, is harder to interpret, and has higher computational requirements that would be problematic on a t3.micro instance.

### Q8: How does the request flow work end-to-end?
**Short Answer:** Browser → S3 (frontend) → API Gateway → Elastic Beanstalk → FastAPI → ML Model → DynamoDB → Response → Frontend.
**Deeper Answer:** (See Section 14 for the detailed 11-step flow.)

### Q9: How is fraud detected by the claim model?
**Short Answer:** The XGBoost model calculates the probability of fraud based on 41 features and returns a score from 0–100, with feature importance explaining which factors contributed most.
**Deeper Answer:** The model uses one-hot encoded categorical features and raw numerical features. It produces `predict_proba` — the probability of the positive class (fraud). This is scaled to 0–100. Feature importances from the tree model are used to identify which active features had the highest importance for the prediction. The risk level is determined by thresholds: ≤30 = LOW, ≤60 = MEDIUM, >60 = HIGH.

### Q10: How is investigation data stored?
**Short Answer:** Every analysis result is stored as a document in DynamoDB with the investigation ID, type, timestamp, risk score, and full result object.
**Deeper Answer:** After each analysis, the frontend constructs a `HistoryRecord` containing the UUID, analysis type (Claim/Provider/Anomaly), ISO timestamp, risk score, risk level, and the complete analysis result JSON. This is sent to `POST /history`, where the backend converts Python floats to DynamoDB Decimals and writes the item to the `FraudInvestigationHistory` table using `PutItem`.

### Q11: How is the system scalable?
**Short Answer:** The architecture supports scaling — EB can scale to multiple instances with a load balancer, DynamoDB auto-scales on-demand, API Gateway handles up to 10,000 requests/second.
**Deeper Answer:** Currently running as single-instance for cost reasons. To scale: (1) switch EB to load-balanced environment with auto-scaling policies, (2) DynamoDB already auto-scales with on-demand capacity, (3) API Gateway supports burst capacity. The stateless FastAPI backend means any instance can handle any request — no session stickiness needed.

### Q12: How is the system secured?
**Short Answer:** IAM roles with least-privilege access, no hardcoded credentials, HTTPS via API Gateway, CORS restrictions.
**Deeper Answer:** Security measures: (1) No AWS credentials in code — uses EC2 instance profile. (2) EC2 runtime role only has DynamoDB permissions for the specific table. (3) IMDSv1 disabled (IMDSv2 only) to prevent SSRF attacks. (4) API Gateway provides HTTPS encryption. (5) CORS middleware restricts which origins can make API calls. (6) Pydantic validates all inputs server-side to prevent injection.

### Q13: What happens if Elastic Beanstalk goes down?
**Short Answer:** The frontend on S3 remains accessible but shows backend connection errors. DynamoDB data is preserved. The system can be redeployed quickly.
**Deeper Answer:** S3 and DynamoDB are independent services — they continue running even if EB is down. The frontend will show error messages when API calls fail (the code handles this gracefully with try/catch). EB can be restored by redeploying the application version. In production, you'd configure EB auto-scaling to automatically replace unhealthy instances.

### Q14: What happens if DynamoDB is unavailable?
**Short Answer:** ML inference still works normally. Only investigation history save/retrieve fails, and the API returns 503 errors for history endpoints.
**Deeper Answer:** The health check endpoint returns `"status": "healthy"` even when DynamoDB is unreachable — DynamoDB status is informational only. All ML endpoints (`/analyze-claim`, `/analyze-provider`, `/analyze-anomaly`) work independently of DynamoDB. History endpoints return 503 with a descriptive error message. The frontend handles this gracefully (logs a warning, shows empty history).

### Q15: How do you control AWS costs?
**Short Answer:** t3.micro free tier, single-instance EB (no load balancer), on-demand DynamoDB, and terminate EB after reviews.
**Deeper Answer:** (See Section 20 for detailed cost optimization.)

### Q16: What is CORS and why did you need to configure it?
**Short Answer:** CORS is a browser security feature that blocks API calls between different domains. We configured it because our frontend (S3) and backend (API Gateway) are on different domains.
**Deeper Answer:** (See Section 19.)

### Q17: What is API Gateway in one sentence?
**Short Answer:** API Gateway is a managed AWS service that provides a single HTTPS URL for our backend API and routes requests to Elastic Beanstalk.

### Q18: What is Elastic Beanstalk in one sentence?
**Short Answer:** Elastic Beanstalk is an AWS Platform-as-a-Service that manages the deployment, scaling, and monitoring of our FastAPI backend on EC2 instances.

### Q19: What is serverless in this context?
**Short Answer:** "Serverless" means we don't manage any servers directly. DynamoDB and API Gateway are serverless — AWS manages all infrastructure, and we only pay for what we use.
**Deeper Answer:** While our EB backend runs on an EC2 instance (not truly serverless), DynamoDB and API Gateway are fully serverless. We don't provision servers, patch operating systems, or manage capacity for these services. A future enhancement could replace the EB backend with AWS Lambda for a fully serverless architecture.

### Q20: What is your current limitation?
**Short Answer:** No user authentication, no automated alerts, single-instance deployment, and limited to batch sizes of one claim at a time.
**Deeper Answer:** The main limitations are: (1) No authentication — anyone with the URL can access the system. (2) No automated alerting — high-risk detections require manual review. (3) Single-instance deployment — no redundancy or auto-scaling in current config. (4) No batch processing — one claim at a time. (5) Models are static — no retraining pipeline. These are all planned for the Final Review.

### Q21: How did you handle the XGBoost deployment problem?
**Short Answer:** XGBoost was pulling a 252MB GPU dependency (nvidia_nccl) that couldn't download on the t3.micro. We fixed it by installing XGBoost with `--no-deps` in an EB extension config.
**Deeper Answer:** (See Problem 2 in Section 17.)

### Q22: What datasets did you use?
**Short Answer:** Three datasets: (1) CMS Provider Fraud dataset (5,410 providers), (2) Synthetic Health Claims dataset (20,072 claims), (3) Real CMS Utilization data (635,353 records).
**Deeper Answer:** The provider dataset comes from a publicly available Medicare fraud dataset with labeled providers (PotentialFraud: Yes/No). It was preprocessed by merging beneficiary, inpatient, and outpatient data, then aggregating to provider level (31 features). The claim dataset is synthetic healthcare claims with 18 meaningful features and an Is_Fraudulent label. The CMS utilization dataset is real, unlabeled data from CMS — used for unsupervised anomaly detection.

### Q23: How did you validate that your models aren't overfitting?
**Short Answer:** We used train/test splits, 5-fold cross-validation, and measured the generalization gap (difference between train and test F1).
**Deeper Answer:** For both supervised models, we used an 80/20 train/test split with stratification. We computed F1, PR-AUC, and Recall on the test set. We also ran 5-fold stratified cross-validation to check consistency. The Claim model has a train F1 of 0.698 vs test F1 of 0.686 (gap = 0.012) — classified as "NONE" overfitting. The Provider model has a gap of 0.011 — also "NONE". Both validation_results.json files confirm `"Leakage_Found": "NO"` and `"Overfitting": "NONE"`.

### Q24: Why did you use PR-AUC as the primary model selection metric?
**Short Answer:** PR-AUC is the right metric for imbalanced classification problems where the positive class (fraud) is rare.
**Deeper Answer:** With only ~25% fraud in claims and ~9% in providers, standard accuracy would be misleading (a model that always predicts "not fraud" would get 75%+ accuracy). PR-AUC specifically measures performance on the minority (fraud) class across all thresholds. A high PR-AUC means the model can identify fraud cases without excessive false positives.

### Q25: What is the Isolation Forest and how does it work?
**Short Answer:** Isolation Forest is an unsupervised anomaly detection algorithm that isolates outliers by recursively partitioning data. Points that are easy to isolate (require fewer splits) are more anomalous.
**Deeper Answer:** Unlike supervised models, Isolation Forest doesn't need fraud labels. It builds random trees by selecting a random feature and a random split value. Normal data points require many splits to isolate (they're similar to many other points), while anomalies require few splits (they're dissimilar). The algorithm produces a decision score — more negative means more anomalous. We transform this into a 0–100 percentage for user-friendly display.

---

## 30. Faculty Follow-Up Questions

### Q: "You say XGBoost is best. But your test F1 is only 0.686. Isn't that low?"
**Answer:** For fraud detection, F1 alone isn't the right measure. We prioritize Recall (catching actual fraud) — our recall is 0.832, meaning we catch 83% of fraudulent claims. The F1 is a balance of precision and recall. With a 25% fraud rate, a model that perfectly predicts "not fraud" would get 0 F1 on the fraud class. Our 0.686 F1 with 0.832 recall is strong for this problem domain. The PR-AUC of 0.751 further confirms good ranking ability.

### Q: "Why is the Provider model's F1 only 0.54?"
**Answer:** The provider dataset has severe class imbalance — only 9.3% of providers are fraudulent. With such imbalance, achieving high F1 is inherently difficult. However, our Recall is 0.901 (catching 90% of fraudulent providers), and PR-AUC is 0.756. The model was selected with `class_weight='balanced'` to prioritize detecting fraud even at the cost of some false positives. In practice, false positives simply mean extra manual review — a better outcome than missing real fraud.

### Q: "Your anomaly model uses only 3 features. Isn't that too few?"
**Answer:** The CMS utilization data we used has limited structured features after preprocessing (procedure category, count, display indicator). However, the Isolation Forest works well even with few features because it measures deviations from the entire distribution. A provider billing 50,000 units of a rare procedure category will be flagged regardless of having only 3 features. In future work, we could incorporate additional features like geographic data, speciality type, and temporal patterns.

### Q: "How do you ensure data privacy?"
**Answer:** We do not store any real patient or provider PII (Personally Identifiable Information) in our system. The training data is either publicly available CMS data or synthetic. The system processes user-entered data for analysis but does not store the raw claim inputs — only the analysis results (risk scores, risk levels, recommendations) are persisted in DynamoDB. No AWS credentials are stored in code.

### Q: "What would you do differently if you started over?"
**Answer:** (1) Start with containerized deployment (Docker + ECS or Fargate) for better reproducibility. (2) Implement authentication from day one. (3) Use CloudFront from the start for HTTPS and CDN. (4) Set up CI/CD pipeline early to automate deployments. (5) Consider AWS Lambda for a truly serverless backend. These are exactly the improvements planned for the Final Review.

### Q: "How would this work with real insurance company data?"
**Answer:** The architecture is designed to be data-agnostic. The claim analysis form fields match standard healthcare claim fields (claim amount, procedures, admission type). For real deployment: (1) The preprocessing pipeline would be adapted to the company's data format. (2) Models would be retrained on the company's historical data. (3) Authentication and HIPAA-compliant encryption would be added. (4) DynamoDB encryption at rest and in transit would be enabled. (5) VPC and private subnets would isolate the backend.

### Q: "Your system is stateless. How would you handle concurrent users?"
**Answer:** FastAPI is an ASGI framework running on uvicorn, which can handle multiple concurrent requests. The ML models are loaded once into memory at startup and are read-only during inference — no locking needed. DynamoDB handles concurrent writes automatically. For higher concurrency, we'd switch EB to load-balanced mode with auto-scaling, and the stateless design means any instance can handle any request.

---

## 31. Final Review Roadmap

### Between Interim Review and Final Review

| Priority | Task | Description |
|----------|------|-------------|
| HIGH | User Authentication | Implement login/registration with JWT tokens. Add role-based access control (investigator, admin). |
| HIGH | Automated Alerts | Integrate Amazon SNS to send email notifications when HIGH risk detections occur. |
| HIGH | Testing | Write unit tests for backend services, integration tests for API endpoints, and frontend component tests. |
| MEDIUM | CloudFront CDN | Add CloudFront distribution in front of S3 for HTTPS, caching, and global performance. |
| MEDIUM | Batch Analysis | Allow uploading a CSV of claims for bulk analysis. |
| MEDIUM | Enhanced Reporting | PDF/Excel export of investigation reports. |
| LOW | CloudWatch Dashboards | Custom monitoring dashboards for API latency, error rates, and usage patterns. |
| LOW | CI/CD Pipeline | Automate deployment with GitHub Actions or AWS CodePipeline. |
| LOW | API Documentation | Generate and host interactive API documentation (FastAPI's built-in Swagger UI). |

### Final Review Deliverables
1. Fully authenticated system with role-based access.
2. At least one additional AWS service (SNS for alerts).
3. Comprehensive test suite with results.
4. Complete project documentation.
5. Live demo of all modules including new features.

---

## 32. Future Enhancements

These are realistic improvements specifically relevant to FraudLens:

1. **Model Retraining Pipeline:** Periodically retrain models with new labeled claims data, potentially using Amazon SageMaker for managed training jobs.
2. **DynamoDB Streams + Lambda:** Trigger an automated workflow when a HIGH risk investigation is saved — e.g., notify a supervisor, create an audit trail, or escalate to a review queue.
3. **Batch Analysis Endpoint:** Allow uploading a CSV of claims and return analysis results for all claims in one response.
4. **Multi-Model Ensemble:** Combine outputs from all three models into a composite risk score for claims that match across provider and anomaly analyses.
5. **Temporal Analysis:** Track how a provider's risk score changes over time and flag providers with rapidly increasing risk.
6. **Geographic Visualization:** Plot provider-patient distances on a map to visually identify suspicious provider networks.
7. **Explainable AI Dashboard:** Use SHAP or LIME to provide per-prediction feature explanations instead of global feature importance.
8. **Mobile Responsive PWA:** Convert the frontend to a Progressive Web App for field investigators.
9. **Multi-Tenant Architecture:** Support multiple insurance companies with data isolation.
10. **Compliance Features:** HIPAA-compliant data handling, audit logging, data retention policies.
