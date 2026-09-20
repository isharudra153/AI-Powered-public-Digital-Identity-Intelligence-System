from pathlib import Path
from fastapi import FastAPI, HTTPException
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles

BASE = Path(__file__).parent               # the folder this file is in

app = FastAPI()
app.mount("/static", StaticFiles(directory=BASE / "demo_static"), name="static")

# Sample data (in your real project this comes from profiles.json)
PROFILES = [
    {"name": "Dr. Elena Rostova", "username": "elenarostova_ai",
     "photo": "/static/photos/elena_rostova.jpg",
     "platforms": ["GitHub", "LinkedIn", "ORCID", "ResearchGate"]},
    {"name": "Rahul Sharma", "username": "rahulsharma_dev",
     "photo": "/static/photos/rahul_sharma.jpg",
     "platforms": ["GitHub", "LinkedIn", "Kaggle", "Medium"]},
    {"name": "Ananya Reddy", "username": "ananya_ml",
     "photo": "/static/photos/ananya_reddy.jpg",
     "platforms": ["GitHub", "LinkedIn", "Kaggle"]},
]

@app.get("/")
def home():
    return FileResponse(BASE / "demo_static" / "index.html")

@app.get("/api/lookup")
def lookup(name: str = ""):
    typed = name.strip().lower()
    if not typed:
        raise HTTPException(status_code=400, detail="Please type a name")
    for p in PROFILES:
        if typed in p["name"].lower() or typed == p["username"].lower():
            return p
    # No match: say so. Do NOT fall back to the first profile.
    raise HTTPException(status_code=404, detail="No matching profile found")