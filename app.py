from pathlib import Path
from fastapi import FastAPI, UploadFile, File, HTTPException
from fastapi.responses import JSONResponse
import uvicorn
from utils.pandoc_supported import pandoc_supported
from utils.embed import generate_embedding
from utils.extractors.doc_extractor import doc_extractor
from contextlib import asynccontextmanager
import asyncpg
import os

# Database configuration
DB_HOST = os.getenv("PGHOST")
DB_PORT = os.getenv("PGPORT")
DB_NAME = os.getenv("PGDATABASE")
DB_USER = os.getenv("PGUSER")
DB_PASSWORD = os.getenv("PGPASSWORD")

print(DB_HOST, DB_PORT, DB_NAME, DB_USER, DB_PASSWORD)

# Global connection pool
db_pool = None

async def create_pool():
    """Create database connection pool"""
    return await asyncpg.create_pool(
        host=DB_HOST,
        port=DB_PORT,
        database=DB_NAME,
        user=DB_USER,
        password=DB_PASSWORD,
        min_size=2,
        max_size=10
    )


@asynccontextmanager
async def lifespan(app: FastAPI):
    """Manage application lifespan events"""
    global db_pool
    # Startup: Create connection pool
    db_pool = await create_pool()
    print("Database connection pool created")
    yield
    # Shutdown: Close connection pool
    await db_pool.close()
    print("Database connection pool closed")

# Directory to store uploaded files
UPLOAD_DIR = Path("uploads")
UPLOAD_DIR.mkdir(parents=True, exist_ok=True)

# Initialize FastAPI app
app = FastAPI(title="Upload & Embeddings API", lifespan=lifespan)

@app.post("/upload")
async def upload_file(file: UploadFile = File(...)):
    if not file.filename:
        raise HTTPException(status_code=400, detail="Uploaded file must include a filename.")
    
    # Save the uploaded file
    destination = UPLOAD_DIR / file.filename
    print(f"Saving uploaded file to: {destination}")
    try:
        with destination.open("wb") as buffer:
            while chunk := await file.read(1024 * 1024):
                buffer.write(chunk)
    finally:
        await file.close()

    file_extension = file.filename.split(".")[-1].lower()
    content = ""
    if file_extension in pandoc_supported():
        content = doc_extractor(destination)
    else:
        raise HTTPException(status_code=400, detail="Unsupported file type for extraction.")

    # Generate embeddings
    embeddings = generate_embedding(content)

    # Return JSON response
    return JSONResponse(
        status_code=201,
        content={
            "filename": file.filename,
            "content_type": file.content_type,
            "size_bytes": destination.stat().st_size,
            "embeddings": embeddings
        }
    )


if __name__ == "__main__":
    uvicorn.run("app:app", host="0.0.0.0", port=8000, reload=True)
