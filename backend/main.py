# main.py
from fastapi import FastAPI
from app.api.routes import router
from fastapi.middleware.cors import CORSMiddleware

app = FastAPI()

# Add CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # For development only
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# Include router without additional prefix since routes.py already has /drives
app.include_router(router)

# Optional: Add root route for testing
@app.get("/")
async def root():
    return {"message": "API Running"}