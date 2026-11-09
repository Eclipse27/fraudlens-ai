# FraudLens AI — Full Project Explanation
### (Easy English — For Final Review Presentation)

> This document explains the entire FraudLens AI project in simple language.
> First, Achintya's part (the Website + ML models) is explained.
> Then, your part (the full AWS cloud setup) is explained in complete detail.
> At the end, there is a step-by-step guide on how to navigate AWS during the demo.

---

# PART 1 — ACHINTYA'S WORK: The Website and ML Models

---

## What is FraudLens AI? (In one line)

FraudLens AI is a **web application** where an insurance company employee can check whether an insurance claim is real or fake — using artificial intelligence.

---

## A. The Problem We Are Solving

Imagine you are an insurance company.

A hospital sends you a bill saying:
> *"Patient Ramesh was admitted for 5 days. Bill = ₹1,00,000. Please pay us."*

How do you know:
- Was Ramesh actually admitted?
- Was he really there for 5 days?
- Was the medicine given to him actually for his disease?
- Did he already claim money for the same visit from another hospital?

**Right now, insurance companies check this manually.** It takes days. It's expensive. And they only check a tiny % of all claims. So fraud happens all the time.

**₹10,000–₹15,000 crore** is lost every year in India due to this.

FraudLens AI fixes this using AI + clinical rules.

---

## B. The Website — What Achintya Built

The website is what you see and click on. It has **8 pages**, built using:
- **React** — a popular tool for building websites (like how WhatsApp Web is built)
- **Tailwind CSS** — for making it look clean and professional
- **TypeScript** — a stricter version of JavaScript so code doesn't break
- **Vite** — a tool that builds/compiles the website super fast
- **Recharts** — for drawing charts and graphs on the page
- **Axios** — for sending data from the website to the backend server

### The 8 Pages of the Website:

**1. Dashboard (Home Page)**
- When you open the app, this is the first thing you see.
- It shows big numbers: how many patients, claims, hospitals are in the system.
- It shows how many claims are VERIFIED vs need REVIEW.
- It shows a pie chart of risk levels.
- It pulls all this data from the backend every time the page loads.

**2. Patient Registry**
- Shows a list of all 303 patients in the system.
- Each patient has an ID like `FL-PAT-000001`.
- You can search by name. You can register a new patient.
- **Special feature:** If the same person goes to two different hospitals, they get the SAME patient ID. The system figures this out by comparing name + date of birth + gender + phone number. This is called **deduplication**.

**3. Patient Detail Page**
- When you click on a patient, you see their full history.
- It shows which hospitals they visited, what diseases they had, what medicines were prescribed, and all their bills — all in one place.
- This is very useful for detecting fraud across multiple hospitals.

**4. Claim Verification (The Most Important Feature)**
- You type a claim ID (like `FL-CLM-000480`) and click verify.
- The system then checks **11 things** automatically:
  1. Does this claim exist?
  2. Does the patient exist?
  3. Does the hospital exist?
  4. Was there actually a hospital visit (encounter)?
  5. Was the encounter linked to the right patient?
  6. Was the encounter at the right hospital?
  7. Was a prescription issued?
  8. Are the medicines from the prescription real and approved?
  9. Do the medicines match the disease the patient had? (e.g., a heart medicine shouldn't be billed for a fever patient)
  10. Does the bill amount match the claim amount?
  11. Was this same encounter already claimed before? (duplicate)
- At the end, it shows a report card: **VERIFIED** or **REVIEW REQUIRED** with the reason.

**5. ML Claim Analysis**
- Here you manually type claim details (amount, patient age, number of procedures, etc.)
- The website sends this to the **XGBoost ML model**.
- The model gives a **fraud risk score from 0 to 100**.
- 0–30 = LOW RISK (probably genuine), 70–100 = HIGH RISK (probably fraud).
- It also tells you WHY it thinks it's risky (e.g., "claim amount is very high for this procedure").

**6. Provider Analysis**
- Here you check if a DOCTOR or HOSPITAL is behaving suspiciously overall.
- You enter their billing history (total claims, total patients, etc.).
- The **Logistic Regression model** gives a risk score.
- Example: A doctor who files 500 claims/month but most other doctors file 50 is suspicious.

**7. Anomaly Detection**
- This uses the **Isolation Forest model** (trained on 6 lakh+ real CMS records).
- CMS = Centers for Medicare & Medicaid Services (US health data).
- It detects unusual billing patterns even when we don't have specific fraud labels.
- Example: A hospital billing for 10,000 MRI scans/month in a small town is anomalous.

**8. Investigation History**
- Every time a claim is verified or analyzed, the result is saved.
- This page shows all past investigations with their results.
- Data is stored in AWS DynamoDB (the cloud database).

---

## C. The Backend — What Achintya Built

The backend is the "engine" of the app. The website (frontend) just shows things. The backend **does the actual work**.

Built using:
- **FastAPI** — a Python framework for building APIs (like a waiter between the website and the database/ML)
- **Python 3.12** — the programming language
- **Uvicorn** — the server that runs FastAPI (like a motor running the engine)
- **Pydantic** — validates that the data coming in is correct format
- **Pandas / NumPy** — for processing data before feeding to ML
- **Joblib** — saves and loads the ML models from `.pkl` files

### The Backend has 13 API Endpoints:

An **API endpoint** is like a URL that the website calls to get or send data.

| URL | What it does |
|-----|-------------|
| `GET /health` | "Is the backend running? Are ML models loaded?" |
| `GET /dashboard/stats` | Returns all the counts (patients, claims, etc.) |
| `GET /hospitals` | Returns the list of 3 hospitals |
| `GET /patients` | Returns all 303 patients |
| `GET /patients/{id}` | Returns one specific patient's details |
| `POST /patients` | Register a new patient (with deduplication) |
| `GET /encounters` | Returns hospital visits |
| `GET /claims` | Returns insurance claims |
| `POST /verify-claim` | Does the 11-point audit on a claim |
| `POST /analyze-claim` | Runs XGBoost and returns fraud score |
| `POST /analyze-provider` | Runs Logistic Regression on provider |
| `POST /detect-anomaly` | Runs Isolation Forest |
| `GET/POST /history` | Saves or retrieves investigation records from DynamoDB |

---

## D. The ML Models — What Achintya Built

Three separate AI models were trained for this project. All three are saved as `.pkl` files in the `model/` folder.

### Model 1: XGBoost — Claim Fraud Detector
- **What it does:** Takes a claim's numbers (amount, age, procedures, days, etc.) and predicts whether it's fraud.
- **How it was trained:** On a dataset with labeled "fraud" and "not fraud" claims.
- **Why XGBoost?** It's very good at catching patterns in numbers (tabular data). It's also the most accurate model for this type of task.
- **Output:** A score from 0–100. Above 70 = suspicious.

### Model 2: Logistic Regression — Provider Risk
- **What it does:** Looks at a doctor/hospital's overall billing behavior and says if they're risky.
- **Why Logistic Regression?** Because the relationship between billing patterns and fraud risk is fairly straightforward — a linear model works well and is easy to explain.
- **Output:** A risk score and the top reasons (which factors pushed the score up).

### Model 3: Isolation Forest — Anomaly Detection
- **What it does:** Trained on 6,35,000+ real CMS records. Finds billing patterns that are "outliers" — things that are very different from the norm.
- **Why Isolation Forest?** Because we don't have labels for "this billing is fraudulent." We just know what's NORMAL. Isolation Forest finds what's NOT normal.
- **Output:** Anomaly score 0–100. Higher = more unusual.

---

## E. The Synthetic Dataset

Since we can't use real patient data (privacy laws), Achintya wrote code (`generate_dataset.py`) to create **fake but realistic** data:

- **303 synthetic patients** with Indian names, Prayagraj addresses, phone numbers
- **3 hospitals**: SRN Hospital, Colvin Hospital, KNMH
- **600 hospital visits** (encounters)
- **550 prescriptions** with medicines matched to diseases
- **60 real drug monographs** from WHO and India's NLEM (national medicine list)
- **550 insurance claims** — some with injected fraud (amount mismatch, duplicate claim, wrong medicine)

This data is stored in a local JSON file (`data/synthetic_database.json`) and also uploaded to AWS DynamoDB.

---

# PART 2 — YOUR WORK: The Complete AWS Setup

---

## What is AWS?

**AWS (Amazon Web Services)** is like renting computer infrastructure from Amazon instead of buying your own servers. You pay only for what you use.

We used **5 main AWS services** for this project.

---

## Why Do We Need AWS?

The website and backend can run on our laptop. But only we can access it.

For the project to be a **real, live website** that anyone with an internet connection can open — we need to put it on the internet. That's what AWS does.

Think of it like this:
- **Our laptop** = kitchen where food is cooked
- **AWS** = the restaurant where the food is served to everyone

---

## The 5 AWS Services We Used and WHY

---

### AWS Service 1: Amazon S3 (Simple Storage Service)

**What is it?**
S3 is like Google Drive or Dropbox — but for websites. It stores files.

**What we used it for:**
We uploaded the compiled website (HTML, CSS, JavaScript files) to S3. S3 then serves it as a **public website** so anyone can open it in a browser.

**Key details:**
- Bucket name: `fraudlens-frontend-418272772343`
- Website URL: `http://fraudlens-frontend-418272772343.s3-website.ap-south-1.amazonaws.com`
- We set `index.html` as both the Index Document AND the Error Document — this is important! It means if someone types `/patients` in the URL directly, S3 doesn't give a "file not found" error — it loads `index.html` and React handles the routing.

**Why not just host it on the same server as the backend?**
Because S3 is:
- Extremely cheap (< ₹1 per month for our size)
- Always up — no server crashes
- Global delivery

---

### AWS Service 2: Amazon API Gateway

**What is it?**
API Gateway is like a **receptionist at an office**. The website (which lives on S3) can't talk directly to the backend server for security reasons. API Gateway sits in the middle.

When the website wants to verify a claim:
1. Website sends request to API Gateway
2. API Gateway forwards it to the backend
3. Backend sends back the answer
4. API Gateway passes the answer back to the website

**Why do we need this?**
1. **Security:** The website and backend are on different addresses. Without API Gateway managing CORS (Cross-Origin Resource Sharing), the browser would block the request.
2. **HTTPS:** API Gateway gives us a free HTTPS (secure) URL automatically.
3. **Single entry point:** One URL for all API calls.

**Key details:**
- API ID: `c9av6ujzgi`
- Full URL: `https://c9av6ujzgi.execute-api.ap-south-1.amazonaws.com`
- It has one route: `ANY /{proxy+}` — meaning ALL requests (GET, POST, etc.) to any URL get forwarded to the backend.

---

### AWS Service 3: AWS Elastic Beanstalk (The Most Complex One)

**What is it?**
Elastic Beanstalk is a service that takes your code, creates a server for it, sets it up, and keeps it running. You don't need to manually set up Linux, install Python, configure Nginx, etc. — Elastic Beanstalk does all that automatically.

**What we used it for:**
We uploaded the backend code (FastAPI) as a ZIP file. Elastic Beanstalk:
1. Created an EC2 (virtual computer) automatically
2. Installed Python 3.12
3. Installed all our Python libraries (from `requirements.txt`)
4. Set up Nginx (a web server that sits in front of FastAPI)
5. Started our FastAPI application
6. Keeps it running 24/7

**Key details:**
- Application name: `FraudLens`
- Environment name: `FraudLens-prod`
- Region: `ap-south-1` (Mumbai)
- The actual EC2 machine: `i-0e597a7086c93ff1d` — type `t3.micro` (the cheapest option, 2 CPU, 1GB RAM)
- Elastic IP: `43.204.34.220` — a fixed public IP address assigned to this machine so API Gateway always knows where to send requests

**The tricky parts we solved:**

**Problem 1: XGBoost was too big to install**
XGBoost is a 305MB file. When EB tried to install it normally, it timed out and failed 6 times.
- **Fix:** We removed XGBoost from `requirements.txt` and created a special config file (`.ebextensions/02_xgboost.config`) that installs XGBoost separately, without the packages that cause the timeout.

**Problem 2: The server only has 1GB RAM**
XGBoost needs more than 1GB to install. Linux was running out of memory and killing the install.
- **Fix:** We created a **swap file** — a 2GB area on the hard drive that acts like extra RAM. This is configured in `.ebextensions/01_swap.config`.

**Problem 3: Pydantic version conflict**
Pydantic is a library for data validation. There are two versions (v1 and v2) with different rules. Our code was mixing both.
- **Fix 1:** Removed `min_length=1` from List fields in `schemas.py` (not supported in Pydantic v1)
- **Fix 2:** Added one line of code at the top of `schemas.py` that makes v1 understand v2 commands: `BaseModel.model_dump = BaseModel.dict`

**How we deployed:**
```
Step 1: Run python package_eb.py → creates FraudLens-Backend-v7.zip
Step 2: Upload ZIP to S3 (EB uses S3 to store code)
Step 3: Tell EB to create a new version from that ZIP
Step 4: Tell EB environment to deploy that version
Step 5: Wait for EB to say "Green" (healthy)
```

---

### AWS Service 4: Amazon DynamoDB

**What is it?**
DynamoDB is Amazon's cloud database. It's a **NoSQL** database — meaning it stores data as flexible "documents" (like JSON), not as strict rows and columns like Excel.

**What we used it for:**
We store all the healthcare data in DynamoDB:
- Patient records
- Hospital records
- Encounter (hospital visit) records
- Prescriptions
- Bills
- Insurance claims
- Fraud investigation history

**11 tables total:**

| Table | What's inside |
|-------|--------------|
| `FL_Patients` | All 303 synthetic patients |
| `FL_Hospitals` | 3 hospitals |
| `FL_Encounters` | 600 hospital visits |
| `FL_MedicalIssues` | Diseases diagnosed |
| `FL_Prescriptions` | Prescriptions issued |
| `FL_PrescriptionMedicines` | Medicines in each prescription |
| `FL_MedicineReference` | 60 real drug info (WHO/NLEM) |
| `FL_HospitalBills` | Itemized bills |
| `FL_InsuranceClaims` | 550 insurance claims |
| `FL_ClaimVerifications` | Audit results |
| `FraudInvestigationHistory` | All past investigations |

**Why DynamoDB and not MySQL?**
- **PAY_PER_REQUEST** billing: When we're not using it (like at night), we pay ₹0. We only pay when queries are made. Perfect for a demo/academic project.
- **No server to manage:** It just works. No installation needed.
- **Scales automatically:** If 1000 people use the app at once, it handles it without crashing.

**Smart feature — Dual Mode:**
The backend has a clever trick. If AWS DynamoDB is not reachable (e.g., running offline on laptop), it automatically uses the local `synthetic_database.json` file instead. No crash. No error. Just seamless fallback.

---

### AWS Service 5: AWS IAM (Identity and Access Management)

**What is it?**
IAM is the **security guard** of AWS. It controls who can do what.

Without IAM, anyone could access your database or modify your server.

**What we set up:**

**1. FraudLensDeployUser**
This is our user account that runs AWS CLI commands from the laptop.
- Has permission to: Deploy to Elastic Beanstalk, upload to S3, manage DynamoDB tables
- Does NOT have permission to: Create budgets, modify IAM policies, access other AWS services
- This is called "Least Privilege" — only give the minimum permissions needed

**2. FraudLensEC2RuntimeRole**
This is the role given to the EC2 machine (the server) itself.
- Allows the FastAPI backend to read/write DynamoDB without needing a username/password
- The server just "knows" it has permission because it's wearing this role (like a staff ID badge)
- This is much safer than storing AWS keys in the code

**3. FraudLensEBServiceRole**
This is the role Elastic Beanstalk itself uses to manage everything — checking EC2 health, deploying updates, etc.

---

### Supporting AWS Services

**CloudWatch**
- Amazon's logging and monitoring tool.
- Every time FastAPI prints something (logs), it goes to CloudWatch.
- We configured **7-day retention** — logs older than 7 days are automatically deleted. This prevents storage charges from piling up.

**CloudFormation**
- Elastic Beanstalk uses this automatically behind the scenes.
- When we deploy to EB, CloudFormation creates all the networking infrastructure (VPC, subnets, security groups) for us.
- We didn't manually configure this — EB does it automatically.

**Elastic IP**
- Normally, when an EC2 server restarts, it gets a new IP address.
- An Elastic IP is a **fixed IP address** that stays the same even after restart.
- Our Elastic IP: `43.204.34.220`
- API Gateway always sends requests to this address, so it never breaks.

---

## How Everything Works Together (The Full Journey of a Request)

Let's say you click "Verify Claim FL-CLM-000480" on the website.

```
Step 1: Your browser loads the website from Amazon S3
        (S3 serves the HTML/JS/CSS files)

Step 2: The React website (running in your browser) sends a request:
        POST https://c9av6ujzgi.execute-api.ap-south-1.amazonaws.com/verify-claim
        {"claim_id": "FL-CLM-000480"}

Step 3: API Gateway receives this HTTPS request.
        It checks CORS headers (is this website allowed to call us? Yes.)
        It forwards the request to our EC2 server at Elastic IP 43.204.34.220

Step 4: Nginx (running on EC2 at port 80) receives the request.
        Nginx forwards it to FastAPI running on port 8000.

Step 5: FastAPI's /verify-claim endpoint runs:
        - Fetches the claim from DynamoDB
        - Fetches the patient, hospital, encounter, bill, prescription
        - Runs all 11 audit checks
        - Runs XGBoost ML model to get fraud score
        - Saves the verification result to DynamoDB

Step 6: FastAPI sends back a JSON response with the audit result.

Step 7: Nginx passes it back → API Gateway passes it back → Browser receives it.

Step 8: React website renders the beautiful audit report on your screen.
```

**Total time for all this:** Under 2 seconds.

---

## Cost Management (What We Did to Keep Costs Low)

The project runs for about **10 days** (Nov 1 to Nov 11). After that, everything is shut down.

**Daily cost: approximately ₹20–30/day**

| Resource | Cost |
|---------|------|
| EC2 t3.micro | ~$0.0104/hour = ~$0.25/day |
| DynamoDB | $0 (PAY_PER_REQUEST, only charged per query) |
| S3 (< 2MB website) | < $0.01/month |
| API Gateway | Free tier (1 million calls/month free) |

**What we configured:**
1. **AWS Budget of $7 USD** with alerts at 50%, 80%, 100% — so if something runs unexpectedly, we get an email.
2. **CloudWatch log 7-day retention** — logs auto-delete, no surprise storage charges.
3. **Scale-to-Zero** capability — we can set EC2 instances to 0 to stop charges between demos.

---

## Resource Tagging (What We Did for Organization)

We put tags (labels) on every AWS resource so they're easy to identify and track:

| Tag | Value |
|-----|-------|
| Project | FraudLens-AI |
| Environment | Demo |
| Owner | Project-Team |
| ReviewDate | 2026-11-10 |
| CleanupDate | 2026-11-11 |

Resources tagged: EC2, EBS storage, Elastic IP, Security Group, API Gateway, all 11 DynamoDB tables.

---

## Security Audit — What We Checked

✅ No AWS access keys or passwords in any code file
✅ No real patient data — 100% synthetic
✅ CORS only allows our S3 website domain (not all websites)
✅ EC2 uses IAM role (no username/password stored on server)
✅ DynamoDB only accessible via IAM (not public internet)
✅ FraudLensDeployUser has minimum necessary permissions

---

# PART 3 — HOW TO NAVIGATE AWS IN THE DEMO

## Before You Start

Open your browser and go to: **https://aws.amazon.com**
Log in with the account that has the `fraudlens` profile.
Make sure you are in **Asia Pacific (Mumbai) = ap-south-1** region (top right corner dropdown).

---

## Stop 1: Show Amazon S3 (The Website Hosting)

1. Go to **AWS Console → S3** (search "S3" in the top search bar)
2. You'll see a list of buckets. Click on **`fraudlens-frontend-418272772343`**
3. Click the **Properties** tab
4. Scroll down to **Static website hosting** — it should say "Enabled"
5. You'll see the website URL: `http://fraudlens-frontend-418272772343.s3-website.ap-south-1.amazonaws.com`

**What to say:**
> "This is Amazon S3. We uploaded our compiled React website here. S3 serves it as a public website. It's like Google Drive but for hosting websites. Cost: less than ₹1/month."

6. Click the **Objects** tab — show them `index.html` and the `assets/` folder (these are the actual website files).

---

## Stop 2: Show Amazon API Gateway

1. Go to **AWS Console → API Gateway** (search "API Gateway")
2. Click on **`FraudLensAPI`** (or find API ID `c9av6ujzgi`)
3. Click **Routes** in the left sidebar — you'll see `ANY /{proxy+}`
4. Click **Integrations** — you'll see it pointing to the Elastic Beanstalk URL

**What to say:**
> "This is API Gateway. It's like a receptionist. The website can't directly talk to our backend server due to security rules. API Gateway sits in the middle, accepts all requests, and forwards them to our FastAPI backend. It also gives us a free HTTPS link."

5. Show the **Invoke URL**: `https://c9av6ujzgi.execute-api.ap-south-1.amazonaws.com`

---

## Stop 3: Show AWS Elastic Beanstalk (The Backend Server)

1. Go to **AWS Console → Elastic Beanstalk** (search "Elastic Beanstalk")
2. You'll see **FraudLens** (Application name) with **FraudLens-prod** environment
3. Click on **FraudLens-prod**
4. The main page shows:
   - Health: **Green** ✅
   - Running version: **v7**
   - Platform: Python 3.12 on Amazon Linux 2023
5. Click **Configuration** (left sidebar):
   - Under Instance traffic and scaling → shows Min: 1, Max: 1 (single instance)
6. Click **Events** tab — shows the deployment history and all the steps that happened

**What to say:**
> "This is Elastic Beanstalk. We uploaded our FastAPI backend as a ZIP file. Elastic Beanstalk automatically created a server, installed Python, set up Nginx, installed all our libraries, and started our application. The Health is Green, meaning everything is running perfectly."

7. If asked about the XGBoost fix: Show the `.ebextensions/` folder concept and explain that you created config files to install XGBoost separately to avoid the timeout issue.

---

## Stop 4: Show Amazon EC2 (The Actual Server)

1. Go to **AWS Console → EC2** (search "EC2")
2. Click **Instances** in the left sidebar
3. Find the instance: **`i-0e597a7086c93ff1d`** — it should show "Running" in green
4. Click on it and show:
   - Instance type: **t3.micro** (cheapest, 2 CPU, 1GB RAM)
   - Public IPv4: **43.204.34.220** (Elastic IP)
   - Security Group: `sg-0ec4a0144ffd0a882`
   - Availability Zone: `ap-south-1c`

**What to say:**
> "This is the actual virtual computer (EC2) that is running our FastAPI backend. We use t3.micro — the smallest and cheapest option. It has 2 CPUs and 1GB RAM. The Elastic IP 43.204.34.220 is a fixed public IP address. Even if this server restarts, the IP stays the same."

5. Click **Tags** tab — show the governance tags (Project=FraudLens-AI, etc.)

---

## Stop 5: Show Amazon DynamoDB (The Database)

1. Go to **AWS Console → DynamoDB** (search "DynamoDB")
2. Click **Tables** in the left sidebar
3. You'll see **11 tables** starting with `FL_` and `FraudInvestigationHistory`
4. Click on **`FL_Patients`** → click **Explore table items** → you'll see real patient data rows
5. Click on **`FraudInvestigationHistory`** → show past investigation records

**What to say:**
> "This is Amazon DynamoDB — our cloud database. It stores all 11 tables of healthcare data: patients, hospitals, encounters, prescriptions, bills, and claims. The billing mode is PAY_PER_REQUEST — meaning we pay zero rupees when no one is using it. We only pay per query. Total cost: ₹0 per day when idle."

6. If asked about billing: Click on a table → **Overview** tab → shows "Billing mode: On-demand"

---

## Stop 6: Show IAM (Security Setup)

1. Go to **AWS Console → IAM** (search "IAM")
2. Click **Users** → show **FraudLensDeployUser** (the user we use for CLI)
3. Click **Roles** → show **FraudLensEC2RuntimeRole** and **FraudLensEBServiceRole**

**What to say:**
> "IAM controls security. Our FraudLensDeployUser is the account I use from my laptop to deploy things. FraudLensEC2RuntimeRole is attached to the EC2 server — it gives the server permission to access DynamoDB without storing any password in the code. This is called Least Privilege — only give minimum required access."

---

## Stop 7: Show the Live Website

Open: `http://fraudlens-frontend-418272772343.s3-website.ap-south-1.amazonaws.com`

1. **Dashboard** — show the live numbers (303 patients, 550 claims, etc.)
2. **Patient Registry** — show the list, search for a name
3. **Claim Verification** — type `FL-CLM-000480` → show the 11-point audit report → show VERIFIED result
4. **ML Claim Analysis** — enter some values → show the XGBoost risk score
5. **Investigation History** — show past records stored in DynamoDB

---

## Questions They Might Ask — Your Answers

**Q: Why did you use Elastic Beanstalk and not just EC2 directly?**
A: Elastic Beanstalk manages everything automatically — OS setup, Nginx, Python environment, deployment, health monitoring, auto-restart. If we used raw EC2, we'd have to do all of this manually every time we deploy.

**Q: Why t3.micro? Isn't it too slow?**
A: For a demo/academic project with limited simultaneous users, t3.micro is more than enough. It has 2 vCPUs and 1GB RAM. We also added a 2GB swap file to handle the memory-intensive ML model loading.

**Q: Why not use a Load Balancer?**
A: An Application Load Balancer costs ~$18/month fixed, regardless of usage. For a 10-day demo, that's not justified. Our SingleInstance setup with Elastic IP achieves the same routing result at zero extra cost.

**Q: Why DynamoDB instead of MySQL/PostgreSQL?**
A: DynamoDB PAY_PER_REQUEST = ₹0 at idle. A MySQL RDS database would cost $15–25/month fixed. Also, DynamoDB requires no server management — it scales automatically.

**Q: What happens if someone types a URL like /patients directly?**
A: We set the S3 Error Document to `index.html`. So even if S3 can't find `/patients` as a file, it serves `index.html` and React Router handles the navigation. Without this fix, you'd get an S3 404 error.

**Q: How does the backend know to use DynamoDB or the local JSON file?**
A: At startup, the backend tries to connect to DynamoDB. If it succeeds → use DynamoDB. If it fails (like on a laptop without AWS credentials) → automatically load from the local `synthetic_database.json` file. No crash, no error.

**Q: What is CORS and why did it cause issues?**
A: CORS (Cross-Origin Resource Sharing) is a browser security rule. The website is at one URL (S3), the backend is at another URL (EB). The browser blocks requests between different URLs by default. We configured FastAPI to allow requests from the S3 origin. API Gateway also passes these headers correctly.

**Q: What is a Pydantic error and how did you fix it?**
A: Pydantic is used for data validation in FastAPI. Version 1 and version 2 have different rules. Our code had v2 syntax (`model_dump`, `min_length` on lists) but the server had v1. We added a compatibility line so v1 understands v2 commands.

**Q: How much did this whole AWS setup cost?**
A: Approximately ₹20–30 per day for the EC2. DynamoDB, S3, and API Gateway are practically free. Total for the 10-day demo: approximately ₹200–300.

**Q: Is the data real patient data?**
A: No — 100% synthetic. We generated fake Indian names, phone numbers, and medical records using code. No real Protected Health Information (PHI) is stored anywhere.

**Q: What is the Elastic IP?**
A: When an EC2 server restarts, AWS normally assigns a new random public IP. API Gateway would then not know where to send requests. An Elastic IP is a permanent fixed IP (`43.204.34.220`) that we attached to our EC2. Even after restart, the IP doesn't change.

---

*FraudLens AI — Project Explanation Document | November 2026*
*GitHub: https://github.com/Eclipse27/fraudlens-ai*
