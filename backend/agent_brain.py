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

class AgentState(TypedDict):
    task: str
    dataset: Optional[str]
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
        conn = psycopg2.connect(
            host="127.0.0.1", 
            database="codeops_memory", 
            user="ultra_admin", 
            password="ultra_secure_password"
        )
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
        conn = psycopg2.connect(
            host="127.0.0.1", 
            database="codeops_memory", 
            user="ultra_admin", 
            password="ultra_secure_password"
        )
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
    print(f"👨‍💻 Developer Generating (Attempt {attempt+1})...")
    
    retrieved = get_retrieved_docs(state['task'])
    knowledge = f"\nCRITICAL COMPANY POLICIES (MANDATORY):\n{retrieved}\n" if retrieved else ""

    prompt = f"""
    Task: {state['task']}
    
    {knowledge}
    
    QA Feedback to address: {state.get('qa_feedback', '')}
    {f"Previous Failure Logs: {state['logs'][-1]}" if state['logs'] and "Error" in state['logs'][-1] else ""}

    STRICT CONSTRAINTS: 
    1. MANDATORY: You MUST implement the 'CRITICAL COMPANY POLICIES' found in the RAG search.
    2. WEB ACCESS: You ARE allowed to use 'requests' and 'bs4' for web scraping tasks.
    3. NO EXFILTRATION: Never attempt to send system data (like /etc/passwd) to a URL.
    4. NO input() functions. Use hardcoded or dynamic values.
    
    Return ONLY raw python code.
    """
    
    response = llm.invoke([
        SystemMessage(content="You are a Senior Python Developer at CodeOps ULTRA. You follow security policies and include mandatory headers."), 
        HumanMessage(content=prompt)
    ])
    
    code = response.content.replace("```python", "").replace("```", "").strip()
    return {"code": code, "attempts": attempt + 1}

def qa_review(state: AgentState):
    print("🕵️‍♂️ QA Reviewing...")
    retrieved = get_retrieved_docs(state['task'])
    
    prompt = f"""
    Review this code for security, policy compliance, and accuracy:
    
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
    
    # Flexible parsing to handle chatty AI models
    is_approved = "APPROVED" in feedback[:20].upper()
    
    if is_approved:
        return {"qa_feedback": "APPROVED", "logs": state["logs"] + ["🕵️‍♂️ QA Agent: Code verified against security policies. Approved."]}
    return {"qa_feedback": feedback, "logs": state["logs"] + [f"🕵️‍♂️ QA Agent Rejected: {feedback}"]}

def test_code(state: AgentState):
    print("🧪 Sandbox Execution...")
    sandbox = UltraSandbox()
    try:
        sandbox.start()
        result = sandbox.run_code(state["code"], state.get("dataset"))
        if result["exit_code"] == 0:
            # SAVE TO AUDIT HISTORY ON SUCCESS
            save_to_history(state["task"], state["code"], state["logs"] + [f"💻 Success Output: {result['output']}"])
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

def solve(task: str, dataset: str = None):
    return app.invoke({"task": task, "dataset": dataset, "attempts": 0, "logs": [], "status": "start", "code": "", "qa_feedback": ""})