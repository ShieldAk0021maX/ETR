# Escape The Room API

## Run
```bash
python -m venv .venv
. .venv/Scripts/activate
pip install -r requirements.txt
uvicorn server:app --reload --port 8000
```

## Endpoints
- `GET /health`
- `POST /predict` (multipart field name: `file`)
