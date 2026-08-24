from fastapi import FastAPI, HTTPException
from fastapi.responses import JSONResponse
import json

from backend.schemas import ClaimRequest, ClaimResponse, ProviderRequest, ProviderResponse, AnomalyRequest, AnomalyResponse
import backend.services as services

app = FastAPI(
    title="AI Insurance Fraud Detection and Claim Investigation Assistant",
    description="Backend API for fraud detection and investigation",
    version="1.0.0"
)

@app.get("/health")
def health_check():
    return {
        "status": "healthy",
        "models_loaded": (services.claim_model is not None and 
                         services.provider_model is not None and 
                         services.cms_model is not None)
    }

@app.get("/model-info")
def get_model_info():
    try:
        with open('model/validation_results.json', 'r') as f:
            val_info = json.load(f)
    except:
        val_info = "Validation info not found."
        
    return {
        "claim_model": "Loaded" if services.claim_model else "Not Loaded",
        "provider_model": "Loaded" if services.provider_model else "Not Loaded",
        "anomaly_model": "Loaded" if services.cms_model else "Not Loaded",
        "validation_metrics": val_info
    }

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
