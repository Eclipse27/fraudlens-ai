# FraudLens AI – Cloud Architecture & Implementation Plan

This document outlines the complete cloud architecture and implementation strategy for migrating the local FraudLens AI project to AWS, satisfying all requirements for the Interim Review.

## SECTION 1 — CURRENT PROJECT CLOUD READINESS

### Current Local Components
- **Frontend:** React + Vite application currently running on a local development server (`localhost:5173`). Investigation history is temporarily saved in browser `localStorage`.
- **Backend:** Python FastAPI application running on Uvicorn (`localhost:8000`). It calculates risk on the fly but does not persist records to a real database.
- **ML Models:** Pre-trained `.pkl` files (XGBoost, Logistic Regression, Isolation Forest) and `validation_results.json` stored locally in the `/model` directory, loaded into memory when FastAPI starts.

### Cloud Migration Needs
- **Ready for Cloud:** The React frontend is completely ready to be built (`npm run build`) and hosted statically. The FastAPI backend is modular, stateless, and ready to be containerized or hosted. The ML models are serialized and ready for inference.
- **Needs Change Before Deployment:** 
  1. The frontend's `history.ts` must be updated to fetch/save from a real backend API instead of `localStorage`.
  2. The backend needs new endpoints (e.g., `GET /history`, `POST /history`) that read/write to a cloud database.
  3. API base URLs in the frontend must be updated from `localhost` to the cloud API URL.

---

## SECTION 2 — RECOMMENDED AWS SERVICES

Here are the AWS services selected specifically because they solve genuine architectural needs for this project, moving far beyond basic EC2 and S3 usage.

| AWS Service | Project Component | Exact Purpose | Input | Processing | Output |
| :--- | :--- | :--- | :--- | :--- | :--- |
| **Amazon S3** | Frontend & Storage | Hosts the built static React app files and securely stores the ML `.pkl` model artifacts. | HTTP Requests for static assets. | Serves files to CloudFront. | HTML/CSS/JS files and model weights. |
| **Amazon CloudFront** | CDN / Delivery | Distributes the frontend globally, provides HTTPS, and aggressively caches the React app for fast loading. | User browser requests. | Routes to nearest edge location and caches S3 data. | React app payload delivered to User. |
| **Amazon API Gateway** | API Management | Acts as the single entry point for the backend. Handles rate-limiting, CORS, and prevents backend overload. | REST API requests from React frontend. | Routes requests to the backend compute layer. | Proxies JSON responses back to Frontend. |
| **AWS Elastic Beanstalk** (or ECS Fargate) | API & ML Compute | Hosts the FastAPI backend and runs the ML inference in memory. Much more advanced and manageable than raw EC2. | JSON analysis payloads (Claim, Provider, Anomaly). | FastAPI parses data; ML models calculate fraud risk. | Risk scores and explanations (JSON). |
| **Amazon DynamoDB** | Database | A serverless NoSQL database used to permanently store Investigation History and system metrics. | JSON records containing risk scores and metadata. | Quickly indexes and stores the analysis record. | Acknowledgment of saved history. |
| **AWS Lambda & Amazon SNS** | Async Alerts | Automatically triggers an email alert if a "HIGH RISK" claim is detected. | DynamoDB Stream event (new high-risk record inserted). | Lambda parses the record and publishes to SNS. | Email alert sent to the fraud investigator. |
| **Amazon CloudWatch** | Monitoring | Centralized logging for the FastAPI application and health monitoring for the entire architecture. | Logs and metrics from Beanstalk, Gateway, and Lambda. | Aggregates and creates visual dashboards. | Alerts and system status metrics. |
| **AWS IAM** | Security | Ensures the backend can only access specific DynamoDB tables and S3 buckets. | N/A | Validates access policies. | Allow/Deny permissions. |

*Why this is better than just EC2 & S3:* 
Using raw EC2 requires manual OS patching, manual scaling, and manual web server configuration. This architecture utilizes **managed services** (Elastic Beanstalk/ECS, API Gateway, DynamoDB) which are auto-scaling, highly available, and represent modern enterprise-grade cloud engineering.

---

## SECTION 3 — COMPLETE CLOUD ARCHITECTURE

### Architecture Flow

**1. PRESENTATION LAYER**
`User` → `Amazon CloudFront` → `Amazon S3 (Static Website Hosting)`
The user accesses the FraudLens AI URL. CloudFront delivers the React application securely and rapidly from the nearest edge location. S3 acts as the origin for these files.

**2. API MANAGEMENT LAYER**
`React App` → `Amazon API Gateway`
When the user submits a claim, the React app sends a POST request. API Gateway receives this, applies rate-limiting (preventing DDoS attacks), and securely routes it to the backend compute layer.

**3. ML PROCESSING & COMPUTE LAYER**
`API Gateway` → `AWS Elastic Beanstalk (FastAPI)`
Elastic Beanstalk runs the Python FastAPI application. On startup, FastAPI fetches the `.pkl` models securely from an internal `S3 Bucket`. It receives the request, processes the features, and runs inference using the loaded ML models in memory.

**4. DATA STORAGE LAYER**
`FastAPI` → `Amazon DynamoDB`
Once the fraud risk score is calculated, FastAPI immediately saves the analysis result into a DynamoDB table named `FraudInvestigationHistory`.

**5. EVENT-DRIVEN ALERTING LAYER (Advanced Cloud Feature)**
`DynamoDB Streams` → `AWS Lambda` → `Amazon SNS`
If the saved claim is marked as "HIGH RISK", DynamoDB Streams automatically triggers a Lambda function. The Lambda function formats an alert and triggers Amazon SNS to instantly email the SIU (Special Investigations Unit) team.

**6. MONITORING & SECURITY LAYER**
`AWS IAM` secures all interactions (e.g., ensuring only the Beanstalk role can write to DynamoDB). `Amazon CloudWatch` collects logs from the FastAPI application and API Gateway for debugging and health tracking.

---

## SECTION 4 — INPUT → PROCESSING → CLOUD SERVICE INTERACTION → OUTPUT

### Example 1: Claim Analysis Flow

**INPUT:**
The user enters 18 claim details (e.g., Claim Amount: $1500, Provider Specialty, Deductible) on the frontend and clicks "Analyze Claim".

**FRONTEND:**
The React application (delivered via CloudFront) constructs a JSON payload and sends an HTTPS `POST /analyze-claim` request.

**AWS SERVICE INTERACTION:**
The request hits **Amazon API Gateway**, which validates the endpoint and proxies the payload to **AWS Elastic Beanstalk** (where FastAPI is running). 

**PROCESSING:**
FastAPI receives the payload. It passes the 18 features into the pre-loaded **Regularized XGBoost** model. The model calculates a probability (e.g., 85%) and identifies the top 3 contributing risk factors.

**STORAGE & ALERTS:**
FastAPI writes this JSON result to **Amazon DynamoDB**. Because the risk is HIGH, a **DynamoDB Stream** triggers **AWS Lambda**, which sends an **SNS Email Alert** to the fraud team.

**OUTPUT:**
FastAPI returns the 85% risk score, the "HIGH RISK" badge, and the explanatory risk factors back through API Gateway to the React frontend, which visually renders the Risk Gauge for the user.

### Example 2: Provider Analysis Flow
- **Input:** Aggregated provider stats (Total claims, Mean reimbursed amount).
- **Processing:** Routed through API Gateway to Beanstalk. FastAPI runs the **Logistic Regression** model to find anomalous provider behavior patterns.
- **Storage:** Saved to DynamoDB `History` table.
- **Output:** Returns a 0-100 provider risk score highlighting the features that increased their risk.

### Example 3: CMS Anomaly Detection Flow
- **Input:** Raw CMS utilization data (Procedure Category, Count).
- **Processing:** Routed to FastAPI. The **Isolation Forest** model evaluates the data against the training distribution using its decision function.
- **Storage:** Result saved to DynamoDB.
- **Output:** Returns a 0-100 anomaly percentage indicating how far the utilization deviates from the norm.

---

## SECTION 5 — ARCHITECTURE DIAGRAM PLAN

To create the architecture diagram for your PPT, use these exact boxes and arrows:

### Boxes Needed
1. **User / Browser** (Icon: Laptop) - *End-user accessing the dashboard.*
2. **Amazon CloudFront** (AWS Icon) - *Global Content Delivery Network.*
3. **Amazon S3** (AWS Icon) - *Hosts React Frontend & Stores ML Models.*
4. **Amazon API Gateway** (AWS Icon) - *API Routing & Rate Limiting.*
5. **AWS Elastic Beanstalk / ECS** (AWS Icon) - *Hosts FastAPI & ML Inference.*
6. **Amazon DynamoDB** (AWS Icon) - *Stores Investigation History.*
7. **AWS Lambda** (AWS Icon) - *Processes High-Risk Alerts.*
8. **Amazon SNS** (AWS Icon) - *Sends Email Notifications.*
9. **Amazon CloudWatch** (AWS Icon) - *System Logging & Health Monitoring.*
10. **AWS IAM** (AWS Icon) - *Security & Permissions (Place as a wrap-around or side box).*

### Arrows (Data Flow)
- `User` → (HTTPS Request) → `Amazon CloudFront`
- `Amazon CloudFront` ← (Fetches Static UI) → `Amazon S3 (Frontend)`
- `User` → (REST API POST) → `Amazon API Gateway`
- `Amazon API Gateway` → (Proxies Request) → `AWS Elastic Beanstalk`
- `AWS Elastic Beanstalk` ← (Loads Models on Startup) → `Amazon S3 (Models)`
- `AWS Elastic Beanstalk` → (Saves JSON Result) → `Amazon DynamoDB`
- `Amazon DynamoDB` → (Triggers via Stream) → `AWS Lambda`
- `AWS Lambda` → (Publishes Alert) → `Amazon SNS`
- `Amazon SNS` → (Sends Email) → `Investigator (User)`
- `AWS Elastic Beanstalk & API Gateway` → (Sends Logs) → `Amazon CloudWatch`

---

## SECTION 6 — ACTUAL IMPLEMENTATION RESPONSIBILITY

Here is the exact step-by-step guide for your teammate handling the AWS implementation.

### PHASE 1: AWS Account and IAM Setup
- **Console:** IAM (Identity and Access Management)
- **Action:** Create an IAM User for development with programmatic access. Create an IAM Role for Elastic Beanstalk allowing it to read S3 and write to DynamoDB.
- **Test:** Successfully log into the AWS CLI locally using `aws configure`.

### PHASE 2: Data/Model Storage
- **Console:** Amazon S3
- **Action:** Create two buckets. 
  1. `fraudlens-frontend-hosting` (Enable Static Website Hosting, unblock public access, attach public read policy).
  2. `fraudlens-ml-models` (Keep private).
- **Action:** Upload the 3 `.pkl` files and `validation_results.json` to the private models bucket.

### PHASE 3: Database Integration
- **Console:** Amazon DynamoDB
- **Action:** Create a table named `FraudInvestigationHistory`. Set Partition Key to `id` (String).
- **Code Change:** In the FastAPI `services.py`, replace the concept of local history with the `boto3` library to execute `dynamodb.put_item()` to save the analysis results.

### PHASE 4: Backend Deployment (API & ML)
- **Console:** AWS Elastic Beanstalk
- **Action:** Create a new application. Choose "Python 3.9+" platform. 
- **Code Change:** Ensure `requirements.txt` includes `boto3` and `mangum` (if using Lambda instead) or standard FastAPI reqs. Upload the zipped `backend/` folder.
- **Configuration:** Set Environment Variables in Beanstalk for the S3 bucket name where models live. 
- **Test:** Go to the Beanstalk URL (e.g., `http://my-env.elasticbeanstalk.com/health`) and verify it returns healthy.

### PHASE 5: API Gateway Integration
- **Console:** Amazon API Gateway
- **Action:** Create an HTTP API. Add a route `ANY /{proxy+}`. Set the Integration to the Elastic Beanstalk URL. Enable CORS for the frontend URL.
- **Test:** Use Postman to hit the API Gateway URL `/analyze-claim` and get a successful response.

### PHASE 6: Frontend Deployment
- **Code Change:** In the React app, update `src/services/api.ts` so `API_BASE_URL` points to the API Gateway URL instead of `localhost:8000`. Run `npm run build`.
- **Console:** Amazon CloudFront & S3
- **Action:** Upload the `/dist` folder to the `fraudlens-frontend-hosting` S3 bucket. Create a CloudFront Distribution pointing to that S3 bucket.
- **Test:** Open the CloudFront URL in a browser. The app should load, and running an analysis should successfully communicate with the cloud backend.

---

## SECTION 7 — MINIMUM VERSION VS IDEAL VERSION

### A. MINIMUM INTERIM REVIEW IMPLEMENTATION (Realistic & Achievable)
*Perfect for hitting the 5-service requirement before the deadline while ensuring a working demo.*
1. **Amazon S3** (Frontend Hosting)
2. **Amazon EC2 / Elastic Beanstalk** (FastAPI Backend)
3. **Amazon API Gateway** (In front of backend)
4. **Amazon DynamoDB** (Storing Investigation History)
5. **AWS IAM** (Security roles for EC2 to write to DynamoDB)
*Note: In this version, ML models are simply zipped and uploaded inside the backend folder rather than fetched from S3.*

### B. IDEAL FINAL PROJECT ARCHITECTURE
*Includes advanced event-driven features for the final presentation.*
- All of the above, PLUS:
- **Amazon CloudFront** (Global CDN for frontend)
- **AWS Lambda & Amazon SNS** (Real-time email alerts for high-risk claims triggered by DynamoDB Streams)
- **Amazon S3** (Dedicated private bucket for ML model artifact versioning)
- **Amazon CloudWatch** (Custom dashboards showing fraud trends based on API metrics)

---

## SECTION 8 — WHAT SHOULD ACTUALLY BE IMPLEMENTED NOW

**MUST IMPLEMENT BEFORE INTERIM REVIEW:**
1. Host Frontend statically (S3).
2. Host Backend securely (Elastic Beanstalk).
3. Route API traffic (API Gateway).
4. Persist data (DynamoDB instead of local storage).
*(This guarantees a 100% working cloud demo with 4-5 core services).*

**SHOULD IMPLEMENT (If time permits before review):**
- CloudFront CDN in front of S3 (Takes 5 minutes to setup, looks highly professional).

**OPTIONAL / FUTURE ENHANCEMENT (Save for Final Review):**
- Lambda + SNS alerting system.
- Moving ML models out of the backend zip file and into a dedicated secure S3 bucket fetched at runtime.
- SageMaker (SageMaker is **NOT RECOMMENDED** right now. The models are standard Scikit-Learn/XGBoost `.pkl` files that execute inference in milliseconds. Deploying SageMaker Endpoints would introduce unnecessary network latency, massive complexity, and high AWS costs for a student project. Keeping inference inside the FastAPI container is the industry-standard approach for lightweight models).

---

## SIMPLE TEAM EXPLANATION (2-Minute Viva Script)

**Student 1 (The Problem & Flow):**
"Our project, FraudLens AI, solves the problem of detecting insurance fraud using machine learning. When a user or investigator enters claim details into our **React Frontend**, the request is sent securely over the internet through **Amazon API Gateway**, which acts as our traffic manager. The frontend itself is hosted on **Amazon S3** and distributed globally via **Amazon CloudFront** for high performance."

**Student 2 (The AI & Processing):**
"API Gateway forwards the data to our Python backend, which is hosted on **AWS Elastic Beanstalk**. Inside this server, we have our trained Machine Learning models loaded into memory. For example, our Claim Analysis uses a Regularized XGBoost model. The backend processes the input, generates a fraud risk score, and determines the top risk factors."

**Student 3 (Storage & Monitoring):**
"Once the AI generates the result, the backend immediately saves the record into **Amazon DynamoDB**, a highly scalable NoSQL database, ensuring our investigation history is permanently secured. The result is then returned to the user's dashboard. Throughout this entire process, **AWS IAM** ensures strict security permissions, and **Amazon CloudWatch** monitors our system health and logs. This architecture moves us completely away from basic local hosting into an advanced, enterprise-grade cloud environment."
