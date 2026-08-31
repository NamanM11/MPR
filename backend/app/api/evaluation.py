from fastapi import APIRouter, HTTPException
import json
import os

router = APIRouter()

@router.get("/metrics")
def get_evaluation_metrics():
    metrics_path = os.environ.get("METRICS_PATH", "ml/models/catalog_slm/metadata.json")
    if not os.path.exists(metrics_path):
        metrics_path = "ml/models/catalog_slm/metadata.json"
        
    if not os.path.exists(metrics_path):
        # Fallback empty metrics if model is not trained yet
        return {
            "status": "awaiting_training",
            "model_name": "Catalog-SLM",
            "version": "1.0",
            "framework": "TensorFlow/Keras",
            "training_examples": 0,
            "overall_accuracy": 0.0,
            "metrics": {},
            "history": {}
        }
        
    try:
        with open(metrics_path, "r", encoding="utf-8") as f:
            metadata = json.load(f)
        metadata["status"] = "trained"
        return metadata
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))
