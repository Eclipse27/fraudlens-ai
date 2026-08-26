import os
from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
from fastapi.middleware.cors import CORSMiddleware
import json

from schemas import ClaimRequest, ClaimResponse, ProviderRequest, ProviderResponse, AnomalyRequest, AnomalyResponse, HistoryRecord
import services
import db

app = FastAPI(
    title="AI Insurance Fraud Detection and Claim Investigation Assistant",
    description="Backend API for fraud detection and investigation",
    version="1.0.0"
)

# --- CORS Configuration ---
# Allow localhost origins during development.
# In production, set FRONTEND_ORIGIN to the S3/CloudFront URL.
FRONTEND_ORIGIN = os.environ.get("FRONTEND_ORIGIN", "")

cors_origins = [
    "http://localhost:5173",
    "http://127.0.0.1:5173",
    "http://localhost:3000",
]

if FRONTEND_ORIGIN:
    cors_origins.append(FRONTEND_ORIGIN)

app.add_middleware(
    CORSMiddleware,
    allow_origins=cors_origins,
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

BASE_DIR = os.path.dirname(os.path.abspath(__file__))
MODEL_DIR = os.path.join(BASE_DIR, '../model')

# ─── Health & Info Endpoints ─────────────────────────────────────────

@app.get("/health")
def health_check():
    """
    Process/API health check. Always returns healthy if the API is running.
    DynamoDB connectivity is included as supplementary information only
    and does NOT determine the health status.
    """
    dynamo_status = db.check_dynamodb_connection()
    return {
        "status": "healthy",
        "models": {
            "claim_model": "loaded" if services.claim_model else "not_loaded",
            "provider_model": "loaded" if services.provider_model else "not_loaded",
            "cms_model": "loaded" if services.cms_model else "not_loaded"
        },
        "dynamodb": dynamo_status
    }

@app.get("/model-info")
def get_model_info():
    try:
        with open(os.path.join(MODEL_DIR, 'validation_results.json'), 'r') as f:
            val_info = json.load(f)
    except:
        val_info = "Validation info not found."
        
    return {
        "claim_model": "Loaded" if services.claim_model else "Not Loaded",
        "provider_model": "Loaded" if services.provider_model else "Not Loaded",
        "anomaly_model": "Loaded" if services.cms_model else "Not Loaded",
        "validation_metrics": val_info
    }

# ─── ML Inference Endpoints ─────────────────────────────────────────

@app.post("/analyze-claim", response_model=ClaimResponse)
def api_analyze_claim(request: ClaimRequest):
    try:
        result = services.analyze_claim(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing claim analysis.")

@app.post("/analyze-provider", response_model=ProviderResponse)
def api_analyze_provider(request: ProviderRequest):
    try:
        result = services.analyze_provider(request)
        return result
    except Exception as e:
        print(f"Provider Error: {e}")
        raise HTTPException(status_code=500, detail=str(e))

@app.post("/analyze-anomaly", response_model=AnomalyResponse)
def api_analyze_anomaly(request: AnomalyRequest):
    try:
        result = services.analyze_anomaly(request)
        return result
    except Exception as e:
        raise HTTPException(status_code=500, detail="Error processing anomaly analysis.")

# ─── Investigation History Endpoints ─────────────────────────────────

@app.post("/history")
def save_history(record: HistoryRecord):
    """Save an investigation history record to DynamoDB."""
    try:
        saved = db.save_history_record(record.model_dump())
        return {"message": "Record saved successfully", "id": saved["id"]}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not save history record. DynamoDB may be unavailable: {str(e)}"
        )

@app.get("/history")
def get_history():
    """Retrieve all investigation history records from DynamoDB."""
    try:
        records = db.get_all_history()
        return records
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not retrieve history. DynamoDB may be unavailable: {str(e)}"
        )

@app.get("/history/{record_id}")
def get_history_by_id(record_id: str):
    """Retrieve a single investigation history record by ID."""
    try:
        record = db.get_history_by_id(record_id)
        if record is None:
            raise HTTPException(status_code=404, detail="Record not found")
        return record
    except HTTPException:
        raise
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not retrieve history record. DynamoDB may be unavailable: {str(e)}"
        )

@app.delete("/history")
def delete_all_history():
    """Delete all investigation history records from DynamoDB."""
    try:
        deleted_count = db.delete_all_history()
        return {"message": f"Deleted {deleted_count} record(s)", "deleted": deleted_count}
    except Exception as e:
        raise HTTPException(
            status_code=503,
            detail=f"Could not delete history. DynamoDB may be unavailable: {str(e)}"
        )
