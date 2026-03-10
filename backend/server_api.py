from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
from pydantic import BaseModel
from typing import Optional, List
import psycopg2
from agent_brain import solve

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

@app.post("/api/solve")
async def run_agent(req: TaskRequest):
    result = solve(req.task, req.dataset)
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