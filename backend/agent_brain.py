# backend/agent_brain.py
import os
import psycopg2
import hashlib
import numpy as np
import requests
from typing import TypedDict, List, Optional
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv
from langchain_groq import ChatGroq
from langchain_core.messages import SystemMessage, HumanMessage
from langgraph.graph import StateGraph, END
from sandbox_engine import UltraSandbox

load_dotenv()

# 1. UPGRADED STATE: Added 'language' to the State tracker
class AgentState(TypedDict):
    task: str
    dataset: Optional[str]
    language: str 
    code: str
    qa_feedback: str
    logs: List[str]
    attempts: int
    status: str

# Our AI Engine (Llama 3.3 70B via Groq)
llm = ChatGroq(model="llama-3.3-70b-versatile", temperature=0)

def save_to_history(task: str, code: str, logs: List[str]):
    """Saves a successful run and its security audit trail to the history table."""
    try:
        conn = psycopg2.connect(os.getenv("DATABASE_URL")) # Updated to use the .env variable dynamically!
        cur = conn.cursor()
        cur.execute("INSERT INTO task_history (task, code, logs) VALUES (%s, %s, %s)", (task, code, logs))
        conn.commit()
        cur.close()
        conn.close()
    except Exception as e:
        print(f"History Vault Error: {e}")

def get_offline_embedding(text, dimensions=768):
    """Generates a deterministic vector for RAG without calling an external API."""
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed)
    vector = np.random.uniform(-1, 1, dimensions)
    return (vector / np.linalg.norm(vector)).tolist()

def get_retrieved_docs(query: str):
    """Searches the Vector DB for relevant company security policies."""
    try:
        vector = get_offline_embedding(query)
        conn = psycopg2.connect(os.getenv("DATABASE_URL"))
        register_vector(conn)
        cur = conn.cursor()
        # Explicit type cast to ::vector is required for pgvector distance math
        cur.execute("SELECT content FROM company_memory ORDER BY embedding <=> %s::vector LIMIT 2", (vector,))
        docs = cur.fetchall()
        cur.close()
        conn.close()
        return "\n".join([f"- {d[0]}" for d in docs])
    except Exception as e:
        print(f"RAG Retrieval Error: {e}")
        return ""

def write_code(state: AgentState):
    attempt = state["attempts"]
    lang = state["language"]
    print(f"👨‍💻 Polyglot Developer Generating {lang.upper()} (Attempt {attempt+1})...")
    
    retrieved = get_retrieved_docs(state['task'])
    knowledge = f"\nCRITICAL COMPANY POLICIES (MANDATORY):\n{retrieved}\n" if retrieved else ""

    # 2. UPGRADED PROMPT: Dynamically targets the requested language
    prompt = f"""
    Task: {state['task']}
    
    {knowledge}
    
    QA Feedback to address: {state.get('qa_feedback', '')}
    {f"Previous Failure Logs: {state['logs'][-1]}" if state['logs'] and "Error" in state['logs'][-1] else ""}

    STRICT CONSTRAINTS: 
    1. MANDATORY: You MUST implement the 'CRITICAL COMPANY POLICIES' found in the RAG search.
    2. NO EXFILTRATION: Never attempt to send system data (like /etc/passwd) to a URL.
    3. NO input() or prompt() functions. Use hardcoded or dynamic values.
    
    Return ONLY raw {lang} code. Do not wrap it in markdown blocks.
    """
    
    # 3. UPGRADED SYSTEM PERSONA: It is now a Polyglot developer!
    response = llm.invoke([
        SystemMessage(content=f"You are a Senior Polyglot Developer at CodeOps ULTRA. You write elite {lang} code. You follow security policies and include mandatory headers."), 
        HumanMessage(content=prompt)
    ])
    
    code = response.content.replace(f"```{lang}", "").replace("```python", "").replace("```javascript", "").replace("```", "").strip()
    
    # --- NEW: Programmatic Watermarking ---
    # Auto-detect the correct comment syntax for the requested language
    comment_symbol = "//" if lang.lower() in ["c", "cpp", "java", "javascript", "rust", "go"] else "#"
    watermark = f"{comment_symbol} Verified by CodeOps ULTRA Enterprise Edition\n\n"
    
    # Force the header into the code if the AI forgot it
    if "Verified by CodeOps ULTRA" not in code:
        code = watermark + code

    return {"code": code, "attempts": attempt + 1}

def qa_review(state: AgentState):
    print("🕵️‍♂️ QA Reviewing...")
    retrieved = get_retrieved_docs(state['task'])
    
    prompt = f"""
    Review this {state['language']} code for security, policy compliance, and accuracy:
    
    CODE:
    {state['code']}
    
    POLICIES TO ENFORCE:
    {retrieved}
    
    Reply EXACTLY with the word 'APPROVED' if the code is safe and follows policy.
    Otherwise, explain why it must be REJECTED.
    """
    
    response = llm.invoke([
        SystemMessage(content="You are a Strict Code QA Auditor. If code is good, the word APPROVED must be in your response."), 
        HumanMessage(content=prompt)
    ])
    feedback = response.content.strip()
    
    is_approved = "APPROVED" in feedback[:20].upper()
    
    if is_approved:
        return {"qa_feedback": "APPROVED", "logs": state["logs"] + [f"🕵️‍♂️ QA Agent: {state['language'].upper()} Code verified against security policies. Approved."]}
    return {"qa_feedback": feedback, "logs": state["logs"] + [f"🕵️‍♂️ QA Agent Rejected: {feedback}"]}

def test_code(state: AgentState):
    print(f"🧪 Sandbox Execution [{state['language'].upper()}]...")
    sandbox = UltraSandbox()
    try:
        sandbox.start()
        # 4. UPGRADED EXECUTION: Pass the language down to the Docker Router!
        result = sandbox.run_code(state["code"], state.get("dataset"), state["language"])
        
        if result["exit_code"] == 0:
            save_to_history(f"[{state['language'].upper()}] {state['task']}", state["code"], state["logs"] + [f"💻 Success Output: {result['output']}"])
            return {"logs": state["logs"] + [f"💻 Success: {result['output']}"], "status": "success"}
        return {"logs": state["logs"] + [f"💻 Error: {result['output']}"], "status": "error"}
    finally:
        sandbox.stop()

def qa_router(state):
    if state["qa_feedback"] == "APPROVED":
        return "test_code"
    if state["attempts"] >= 3:
        return END
    return "write_code"

# Building the Graph workflow
workflow = StateGraph(AgentState)
workflow.add_node("write_code", write_code)
workflow.add_node("qa_review", qa_review)
workflow.add_node("test_code", test_code)

workflow.set_entry_point("write_code")
workflow.add_edge("write_code", "qa_review")
workflow.add_conditional_edges("qa_review", qa_router, {"test_code": "test_code", "write_code": "write_code", END: END})
workflow.add_conditional_edges("test_code", lambda x: END if x["status"] == "success" or x["attempts"] >= 3 else "write_code")

app = workflow.compile()

# 5. UPGRADED ENTRYPOINT: Accept the language from server_api.py
def solve(task: str, dataset: str = None, language: str = "python"):
    return app.invoke({
        "task": task, 
        "dataset": dataset, 
        "language": language, # Initialize the new state variable!
        "attempts": 0, 
        "logs": [], 
        "status": "start", 
        "code": "", 
        "qa_feedback": ""
    })