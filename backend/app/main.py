import os
import logging
from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from .database import init_db
from .ml.model_loader import load_global_model, get_model
from .api import catalog, taxonomy, history, analytics, evaluation

# Setup logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("Catalog-SLM")

app = FastAPI(
    title="Catalog-SLM API",
    description="Lightweight Small Language Model API for Automated Product Cataloging",
    version="1.0"
)

# Enable CORS for React frontend (default local port is 5173 for Vite)
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Startup handler
@app.on_event("startup")
def startup_event():
    logger.info("Initializing SQLite database...")
    init_db()
    
    # Paths for model and tokenizer
    model_path = os.environ.get("MODEL_PATH", "ml/models/catalog_slm/model.keras")
    tokenizer_path = os.environ.get("TOKENIZER_PATH", "ml/models/catalog_slm/tokenizer.json")
    
    # Try loading the model, but don't crash startup if it's not trained yet
    try:
        logger.info(f"Attempting to load Catalog-SLM model...")
        load_global_model(model_path, tokenizer_path)
    except FileNotFoundError as fe:
        logger.warning(f"Model files not found at startup: {fe}")
        logger.warning("The model must be trained before inference can be performed.")
    except Exception as e:
        logger.error(f"Error loading model at startup: {e}")

# Register routers
app.include_router(catalog.router, prefix="/api/catalog", tags=["Catalog"])
app.include_router(history.router, prefix="/api/catalog/history", tags=["Catalog History"])
app.include_router(taxonomy.router, prefix="/api/taxonomy", tags=["Taxonomy"])
app.include_router(analytics.router, prefix="/api/analytics", tags=["Analytics"])
app.include_router(evaluation.router, prefix="/api/evaluation", tags=["Evaluation"])

@app.get("/api/health")
def health_check():
    model = get_model()
    model_status = "loaded" if model is not None else "not_loaded_or_training"
    
    # Test SQLite connection
    db_status = "unhealthy"
    try:
        from .database import DB_PATH
        import sqlite3
        conn = sqlite3.connect(DB_PATH)
        conn.execute("SELECT 1")
        conn.close()
        db_status = "healthy"
    except Exception:
        pass
        
    return {
        "status": "healthy" if db_status == "healthy" else "unhealthy",
        "database": db_status,
        "model_status": model_status,
        "framework": "TensorFlow/Keras"
    }

if __name__ == "__main__":
    import uvicorn
    uvicorn.run("main:app", host="0.0.0.0", port=8000, reload=True)
