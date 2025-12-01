from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from app.routers import roast_router

app = FastAPI(title="Cooked.ai Backend", version="2.0.0")

# Configure CORS
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # Allow all origins for dev
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include Routers
app.include_router(roast_router.router, prefix="/api/v1", tags=["Roast"])

@app.get("/")
async def health_check():
    return {"status": "ok", "message": "Cooked.ai Backend is running! 🔥"}
