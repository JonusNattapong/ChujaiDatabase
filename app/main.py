from fastapi import FastAPI, Request, HTTPException
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
from dotenv import load_dotenv
import os
from app.api import notes


# โหลด environment variables
load_dotenv()

# ตรวจสอบ required environment variables
REQUIRED_ENV_VARS = ["MODEL_NAME", "EMBEDDING_MODEL"]
missing_vars = [var for var in REQUIRED_ENV_VARS if not os.getenv(var)]
if missing_vars:
    raise ValueError(f"Missing required environment variables: {', '.join(missing_vars)}")

# สร้าง FastAPI app
app = FastAPI(
    title=os.getenv("APP_NAME", "ChujAI Database"),
    description="AI-powered Database with Note-taking and RAG capabilities",
    version="0.1.0",
    debug=os.getenv("DEBUG", "False").lower() == "true"
)

# CORS middleware
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],  # ในโปรดักชั่นควรระบุ origins ที่แน่นอน
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

# รวม routers
app.include_router(notes.router, prefix="/api")

@app.get("/")
async def root():
    return {
        "message": "ยินดีต้อนรับสู่ ChujAI Database API",
        "status": "online",
        "version": "0.1.0"
    }

if __name__ == "__main__":
    # รัน server ด้วย uvicorn
    uvicorn.run("app.main:app", host="0.0.0.0", port=8000, reload=True)
