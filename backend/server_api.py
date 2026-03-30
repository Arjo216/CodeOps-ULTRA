from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import psycopg2
from agent_brain import solve
from dotenv import load_dotenv
load_dotenv() # This forces Python to read your .env file

app = FastAPI(title="CodeOps ULTRA API")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

class TaskRequest(BaseModel):
    task: str
    dataset: Optional[str] = None
    language: str = "python" # <-- NEW: Defaults to python if not provided

@app.post("/api/solve")
async def run_agent(req: TaskRequest):
   # Pass the language down into your solver engine!
    result = solve(req.task, req.dataset, req.language)
    return {
        "code": result["code"],
        "logs": result["logs"],
        "attempts": result["attempts"]
    }

@app.get("/api/history")
async def get_history():
    """Fetches the last 10 successful tasks from the audit log."""
    try:
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
        return {"error": str(e)}

# backend/server_api.py (Append this to your existing file)

from pydantic import BaseModel
import requests
import os

# Define the strictly typed input schema
class CodeReviewRequest(BaseModel):
    code: str
    language: str = "python"

@app.post("/api/v2/agent/review")
async def standalone_code_review(request: CodeReviewRequest):
    groq_api_key = os.getenv("GROQ_API_KEY")
    if not groq_api_key:
        return {"error": "API Key missing. System halted."}

    api_url = "https://api.groq.com/openai/v1/chat/completions"
    headers = {
        "Authorization": f"Bearer {groq_api_key}",
        "Content-Type": "application/json"
    }

    # Enterprise-grade System Prompt focused on Cybersecurity and Optimization
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
        # 1. Get AI Response
        response = requests.post(api_url, headers=headers, json=payload)
        response.raise_for_status()
        ai_response = response.json()["choices"][0]["message"]["content"]
        
        # 2. Silently log to PostgreSQL Database
        try:
            conn = psycopg2.connect(os.getenv("DATABASE_URL"))
            cur = conn.cursor()
            # Auto-create table if it doesn't exist
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
        return {"error": f"Cognitive Core Failure: {str(e)}"}
 
    
@app.get("/api/v2/history")
async def get_review_history():
    """Fetches the last 10 standalone code reviews."""
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
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
        return {"error": str(e)}


if __name__ == "__main__":
    import uvicorn
    print("🚀 Booting CodeOps ULTRA Cognitive Core on Port 8000...")
    # Using the string "server_api:app" is required when reload=True
    uvicorn.run("server_api:app", host="127.0.0.1", port=8000, reload=True)