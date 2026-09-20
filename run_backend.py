import os
import uvicorn

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from fastapi.staticfiles import StaticFiles
from fastapi.responses import FileResponse

from app.api.routes import router as api_router


app = FastAPI(
    title="DigitalTrace AI – Footprint & Profile Intelligence",
    description="Authorized AI-powered public profile discovery, correlation, entity resolution and confidence ledger.",
    version="1.0.0"
)


# -----------------------------
# CORS
# -----------------------------
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)


# -----------------------------
# API ROUTES
# -----------------------------
app.include_router(api_router)


# -----------------------------
# STATIC UI
# -----------------------------
current_dir = os.path.dirname(os.path.abspath(__file__))

# index.html is inside backend/app/static
static_dir = os.path.join(current_dir, "app", "static")


if os.path.exists(static_dir):
    app.mount(
        "/static",
        StaticFiles(directory=static_dir),
        name="static"
    )


# -----------------------------
# HOME PAGE
# -----------------------------
@app.get("/")
def serve_index():

    index_file = os.path.join(
        static_dir,
        "index.html"
    )

    if os.path.exists(index_file):
        return FileResponse(index_file)

    return {
        "message": "DigitalTrace AI Backend Running"
    }


# -----------------------------
# START SERVER
# -----------------------------
if __name__ == "__main__":

    uvicorn.run(
        app,
        host="127.0.0.1",
        port=8000,
        reload=False
    )