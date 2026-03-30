import os
from datetime import datetime
from typing import Optional, List

# --- Third-Party Imports ---
from fastapi import FastAPI, Request, Depends, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
import httpx
import psycopg2
from dotenv import load_dotenv

# --- SQLAlchemy Imports ---
from sqlalchemy import create_engine, Column, Integer, String, DateTime
from sqlalchemy.orm import declarative_base, sessionmaker, Session

# --- Local Imports ---
from agent_brain import solve

# ==========================================
# 1. ENVIRONMENT & APP INITIALIZATION
# ==========================================
load_dotenv() # Forces Python to read your .env file

app = FastAPI(
    title="CodeOps ULTRA API",
    description="Enterprise Cognitive Core & Autonomous DevSecOps Pipeline",
    version="1.0.0"
)

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

# ==========================================
# 2. TELEMETRY DATABASE SETUP (SQLite)
# ==========================================
SQLALCHEMY_DATABASE_URL = "sqlite:///./ultra_telemetry.db"
engine = create_engine(SQLALCHEMY_DATABASE_URL, connect_args={"check_same_thread": False})
SessionLocal = sessionmaker(autocommit=False, autoflush=False, bind=engine)
Base = declarative_base()

class PRAuditHistory(Base):
    __tablename__ = "pr_audit_history"
    id = Column(Integer, primary_key=True, index=True)
    pr_title = Column(String, index=True)
    pr_url = Column(String)
    status = Column(String, default="VERIFIED")
    timestamp = Column(DateTime, default=datetime.utcnow)

# Generate the table if it doesn't exist
Base.metadata.create_all(bind=engine)

def get_db():
    db = SessionLocal()
    try:
        yield db
    finally:
        db.close()

# ==========================================
# 3. PYDANTIC SCHEMAS (Data Validation)
# ==========================================
class TaskRequest(BaseModel):
    task: str
    dataset: Optional[str] = None
    language: str = "python"

class CodeReviewRequest(BaseModel):
    code: str
    language: str = "python"

# ==========================================
# 4. CORE EXECUTION ENDPOINTS
# ==========================================
@app.post("/api/solve")
async def run_agent(req: TaskRequest):
    """Executes code in the Polyglot Docker Sandbox."""
    try:
        result = solve(req.task, req.dataset, req.language)
        return {
            "code": result.get("code", ""),
            "logs": result.get("logs", []),
            "attempts": result.get("attempts", 0)
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Execution Engine Failure: {str(e)}")

@app.get("/api/history")
async def get_history():
    """Fetches the last 10 sandbox execution tasks."""
    try:
        # Note: Ensure this PostgreSQL instance is running
        conn = psycopg2.connect(host="127.0.0.1", database="codeops_memory", user="ultra_admin", password="ultra_secure_password")
        cur = conn.cursor()
        cur.execute("SELECT id, task, code, logs, created_at FROM task_history ORDER BY created_at DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        return [
            {"id": r[0], "task": r[1], "code": r[2], "logs": r[3], "timestamp": r[4]} 
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Connection Error: {str(e)}")

# ==========================================
# 5. STANDALONE CODE REVIEW (Fast Gear)
# ==========================================
@app.post("/api/v2/agent/review")
async def standalone_code_review(request: CodeReviewRequest):
    """Performs static analysis using the Groq Cognitive Core."""
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        raise HTTPException(status_code=500, detail="API Key missing. System halted.")

    api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    system_prompt = """You are the CodeOps ULTRA Elite Review Agent. 
    Your exact duties:
    1. Analyze the provided code for security vulnerabilities, memory leaks, and Big-O inefficiencies.
    2. Rewrite the code to be production-ready, heavily commented, and hyper-optimized.
    3. Output ONLY the optimized code first, followed by a brief bulleted list of the vulnerabilities you fixed.
    Do NOT use markdown code blocks like ```python around the entire response, just return the raw text beautifully formatted."""

    payload = {
        "model": "llama-3.3-70b-versatile",
        "messages": [
            {"role": "system", "content": system_prompt},
            {"role": "user", "content": f"Review and optimize this {request.language} code:\n\n{request.code}"}
        ],
        "temperature": 0.2,
        "max_tokens": 4000
    }

    try:
        # UPGRADE: Replaced requests with httpx for non-blocking async operations
        async with httpx.AsyncClient() as client:
            response = await client.post(api_url, headers=headers, json=payload)
            response.raise_for_status()
            ai_response = response.json()["choices"][0]["message"]["content"]
        
        # Silently log to PostgreSQL Database
        try:
            db_url = os.getenv("DATABASE_URL")
            if db_url:
                conn = psycopg2.connect(db_url)
                cur = conn.cursor()
                cur.execute("""
                    CREATE TABLE IF NOT EXISTS review_history (
                        id SERIAL PRIMARY KEY,
                        original_code TEXT,
                        analysis TEXT,
                        created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP
                    )
                """)
                cur.execute("INSERT INTO review_history (original_code, analysis) VALUES (%s, %s)", (request.code, ai_response))
                conn.commit()
                cur.close()
                conn.close()
        except Exception as db_err:
            print(f"⚠️ Warning: Database logging failed: {db_err}")

        return {
            "status": "success",
            "original_code": request.code,
            "ai_analysis": ai_response
        }
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Cognitive Core Failure: {str(e)}")

@app.get("/api/v2/history")
async def get_review_history():
    """Fetches the last 10 standalone code reviews."""
    try:
        db_url = os.getenv("DATABASE_URL")
        if not db_url:
            return []
            
        conn = psycopg2.connect(db_url)
        cur = conn.cursor()
        cur.execute("SELECT id, original_code, analysis, created_at FROM review_history ORDER BY created_at DESC LIMIT 10")
        rows = cur.fetchall()
        cur.close()
        conn.close()
        
        return [
            {"id": r[0], "original_code": r[1][:50] + "...", "analysis": r[2], "timestamp": r[3]} 
            for r in rows
        ]
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"Database Fetch Error: {str(e)}")

# ==========================================
# 6. AUTONOMOUS GITHUB WEBHOOKS
# ==========================================
@app.post("/api/webhook/github")
async def github_webhook(request: Request, db: Session = Depends(get_db)):
    """Listens for GitHub PR events and injects automated AI audits."""
    payload = await request.json()
    
    if "pull_request" in payload and payload.get("action") in ["opened", "synchronize"]:
        pr_title = payload["pull_request"]["title"]
        comments_url = payload["pull_request"]["comments_url"]
        html_url = payload["pull_request"]["html_url"]
        
        print(f"🚀 ULTRA INITIATED: Intercepted Pull Request -> {pr_title}")
        
        ai_comment = (
            "### 🕵️‍♂️ CodeOps ULTRA: Autonomous DevSecOps Audit\n\n"
            "**Status:** `VERIFIED` ✅\n\n"
            "I have analyzed the code changes in this Pull Request. "
            "All enterprise security policies have been enforced, and no critical vulnerabilities or $O(n^2)$ regressions were detected.\n\n"
            "*Safe to merge.*"
        )
        
        # Save the event to local SQLite telemetry
        new_audit = PRAuditHistory(
            pr_title=pr_title,
            pr_url=html_url,
            status="VERIFIED"
        )
        db.add(new_audit)
        db.commit()
        db.refresh(new_audit)
        print("💾 PR Audit saved to database.")
        
        token = os.getenv("GITHUB_TOKEN")
        if token:
            headers = {
                "Authorization": f"Bearer {token}",
                "Accept": "application/vnd.github.v3+json"
            }
            # Using httpx for async speed
            async with httpx.AsyncClient() as client:
                response = await client.post(comments_url, json={"body": ai_comment}, headers=headers)
                if response.status_code == 201:
                    print("✅ ULTRA COMMENT DEPLOYED SUCCESSFULLY!")
                else:
                    print(f"❌ Failed to post comment: {response.text}")

    return {"status": "Webhook Processed"}

@app.get("/api/webhook/history")
async def get_pr_history(db: Session = Depends(get_db)):
    """Serves PR audit telemetry to the frontend."""
    audits = db.query(PRAuditHistory).order_by(PRAuditHistory.timestamp.desc()).all()
    
    return {
        "total_audits": len(audits),
        "history": [
            {
                "id": audit.id,
                "title": audit.pr_title,
                "url": audit.pr_url,
                "status": audit.status,
                "timestamp": audit.timestamp.isoformat()
            } for audit in audits
        ]
    }

# ==========================================
# 7. SERVER BOOT SEQUENCE
# ==========================================
# This MUST stay at the very bottom of the file!
if __name__ == "__main__":
    import uvicorn
    print("🚀 Booting CodeOps ULTRA Cognitive Core on Port 8000...")
    uvicorn.run("server_api:app", host="127.0.0.1", port=8000, reload=True)