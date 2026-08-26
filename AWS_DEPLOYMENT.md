# FraudLens AI — AWS Deployment Guide

## Current Architecture (Interim Review)

```
User (Browser)
     ↓
Amazon S3 (Static Website Hosting)
     ↓  serves React/Vite frontend
Amazon API Gateway (HTTP API)
     ↓  routes API requests
AWS Elastic Beanstalk (Single Instance)
     ↓  runs FastAPI + ML models
Amazon DynamoDB
     ↓  persists investigation history
```

ML models (.pkl files) are bundled inside the Elastic Beanstalk deployment package.

---

## API Endpoints

| Method | Path | Description |
|--------|------|-------------|
| `GET` | `/health` | API health check (always returns healthy if running) |
| `GET` | `/model-info` | ML model status and validation metrics |
| `POST` | `/analyze-claim` | Run fraud risk analysis on a single claim (XGBoost) |
| `POST` | `/analyze-provider` | Run provider risk analysis (Logistic Regression) |
| `POST` | `/analyze-anomaly` | Run CMS anomaly detection (Isolation Forest) |
| `POST` | `/history` | Save an investigation history record to DynamoDB |
| `GET` | `/history` | Retrieve all investigation history records |
| `GET` | `/history/{id}` | Retrieve a single history record by ID |
| `DELETE` | `/history` | Delete all investigation history records |

---

## Environment Variables

### Backend (FastAPI)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `AWS_REGION` | No | `us-east-1` | AWS region for DynamoDB |
| `DYNAMODB_TABLE_NAME` | No | `FraudInvestigationHistory` | DynamoDB table name |
| `DYNAMODB_ENDPOINT_URL` | No | (none) | Optional: custom DynamoDB endpoint (e.g. for DynamoDB Local) |
| `FRONTEND_ORIGIN` | No | (none) | Production frontend URL for CORS (e.g. `http://fraudlens-frontend.s3-website-us-east-1.amazonaws.com`) |

**Do NOT set `AWS_ACCESS_KEY_ID` or `AWS_SECRET_ACCESS_KEY` in the application.** The backend uses the EC2 instance profile / IAM role when running on Elastic Beanstalk.

### Frontend (Vite)

| Variable | Required | Default | Description |
|----------|----------|---------|-------------|
| `VITE_API_URL` | No | `http://127.0.0.1:8000` | Backend API base URL. Set to the API Gateway URL in production. |

---

## DynamoDB Schema

| Setting | Value |
|---------|-------|
| Table Name | `FraudInvestigationHistory` |
| Partition Key | `id` (String) |
| Capacity Mode | On-Demand (recommended for low-traffic) |

### Record Structure

```json
{
  "id": "uuid-string",
  "type": "Claim | Provider | Anomaly",
  "timestamp": "ISO-8601 datetime string",
  "riskScore": 85.5,
  "riskLevel": "HIGH | MEDIUM | LOW",
  "status": "HIGH | MEDIUM | LOW | SUSPICIOUS PATTERN | MODERATE ANOMALY | NORMAL PATTERN",
  "result": { /* full analysis result object */ }
}
```

---

## Elastic Beanstalk Startup

The backend uses a `Procfile` for startup:

```
web: uvicorn main:app --host 0.0.0.0 --port 8000
```

**Platform:** Python 3.9+  
**Environment type:** Single Instance (no load balancer)  
**Instance type:** `t2.micro` or `t3.micro` (Free Tier eligible)

---

## Local Development & Testing

### Prerequisites
- Python 3.9+
- Node.js 18+
- npm

### Backend

```bash
cd backend
pip install -r requirements.txt
uvicorn main:app --reload
```

The backend will start on `http://127.0.0.1:8000`.

**Without AWS credentials:**
- `GET /health` → returns healthy (DynamoDB status will show `no_credentials`)
- `POST /analyze-claim` → works normally (ML inference is local)
- `POST /history` → returns 503 (DynamoDB unavailable)
- `GET /history` → returns 503 (DynamoDB unavailable)

**With AWS credentials (after DynamoDB table is created):**
- All history endpoints work normally
- Run `aws configure` to set up local credentials, or set `AWS_ACCESS_KEY_ID` and `AWS_SECRET_ACCESS_KEY` env vars for local testing only

### Frontend

```bash
cd frontend
npm install
npm run dev
```

The frontend will start on `http://localhost:5173`.

### Build for Production

```bash
cd frontend
# Set VITE_API_URL to your API Gateway URL before building
VITE_API_URL=https://your-api-gateway-url npm run build
```

The built files in `dist/` are uploaded to S3.

---

## IAM Roles Required

### 1. Elastic Beanstalk Service Role (`FraudLensEBServiceRole`)
- **Trust:** `elasticbeanstalk.amazonaws.com`
- **Policy:** `AWSElasticBeanstalkService` (managed)

### 2. EC2 Instance Profile Role (`FraudLensEC2RuntimeRole`)
- **Trust:** `ec2.amazonaws.com`
- **Policies:**
  - `AWSElasticBeanstalkWebTier` (managed — for health reporting and log upload)
  - Custom inline policy for DynamoDB access:
    - `dynamodb:PutItem`, `dynamodb:GetItem`, `dynamodb:Scan`, `dynamodb:DeleteItem`, `dynamodb:BatchWriteItem`
    - Resource: `arn:aws:dynamodb:<REGION>:<ACCOUNT_ID>:table/FraudInvestigationHistory`

### 3. Deployment Identity (`FraudLensDeployUser`)
- See the IAM Requirements Report for the full deployment policy.

---

## AWS Deployment Steps (Future)

> **These steps should only be performed after the IAM identity is created and reviewed.**

1. **Create DynamoDB table** — `FraudInvestigationHistory` with partition key `id` (String), On-Demand capacity
2. **Create IAM roles** — Service role and EC2 instance profile as documented above
3. **Create Elastic Beanstalk application** — Python platform, Single Instance, upload zipped `backend/` + `model/` directory
4. **Set EB environment variables** — `AWS_REGION`, `DYNAMODB_TABLE_NAME`, `FRONTEND_ORIGIN`
5. **Create API Gateway HTTP API** — Route `ANY /{proxy+}` to the EB URL, enable CORS
6. **Build frontend** — Set `VITE_API_URL` to the API Gateway URL, run `npm run build`
7. **Create S3 bucket** — Enable Static Website Hosting, upload `dist/`
8. **Update CORS** — Set `FRONTEND_ORIGIN` in EB to the S3 website URL

---

## Services NOT Implemented Yet (Future Enhancements)

The following services are documented in the project architecture but are **intentionally excluded** from the interim implementation:

| Service | Purpose | Status |
|---------|---------|--------|
| Amazon CloudFront | CDN for frontend | Not implemented |
| AWS Lambda | High-risk alert processing | Not implemented |
| Amazon SNS | Email notifications | Not implemented |
| DynamoDB Streams | Event-driven triggers | Not implemented |
| Private S3 ML bucket | Separate model storage | Not implemented (models bundled with backend) |
| Amazon SageMaker | Model hosting | Not recommended for this project |
| CloudWatch Dashboards | Custom monitoring | Not implemented (basic logging only) |
