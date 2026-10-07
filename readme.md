### 1. Apply the database migration once

Open PowerShell in `E:\chetan\CODE\MPR`. The default database is the root-level `catalog_history.db`; this applies the new product-knowledge schema while retaining existing catalog records:

```powershell
.\.venv\Scripts\python.exe -c "import sqlite3,pathlib; db=sqlite3.connect('catalog_history.db'); db.executescript(pathlib.Path('backend/migrations/001_product_knowledge_resolution.sql').read_text(encoding='utf-8')); db.close()"
```

Run this **only once**. If you use a custom `DATABASE_URL`, apply the migration to that database instead.

### 2. Start the backend

In a PowerShell window, from the repository root:

```powershell
.\.venv\Scripts\python.exe -m uvicorn backend.app.main:app --reload --port 8000
```

Check that the backend and model are ready at [http://localhost:8000/api/health](http://localhost:8000/api/health). You can also open [http://localhost:8000/docs](http://localhost:8000/docs) for the API interface.

### 3. Start the frontend

In a **second** PowerShell window:

```powershell
cd E:\chetan\CODE\MPR\frontend
npm run dev
```

Open the Vite URL printed in the terminal, usually [http://localhost:5173](http://localhost:5173).

If frontend dependencies are missing, run `npm install` inside `frontend` and then start it again.

### Optional: retrain the model

Retraining is **not needed to run the app**: the existing model is at `model.keras`, and the backend loads it at startup. To deliberately retrain it, run this from the repository root:

```powershell
.\.venv\Scripts\python.exe ml\training\train.py
```

That updates the saved model and its evaluation metadata in `ml/models/catalog_slm/`.