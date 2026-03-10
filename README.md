<div align="center">

# 🛡️ CodeOps ULTRA <br> `[ Enterprise Edition ]`

**Autonomous Agent Orchestration with Hardened RAG-Driven Security**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-ffd43b?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org/)
[![Docker](https://img.shields.io/badge/Docker-Sandboxed-2496ed?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![PostgreSQL](https://img.shields.io/badge/PostgreSQL-pgvector-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

> *"CodeOps ULTRA: Because Autonomous AI shouldn't mean Uncontrolled AI."*

</div>

---

## 📖 Overview

**CodeOps ULTRA** is a state-of-the-art AI orchestration platform designed for secure code generation, real-time data analysis, and autonomous web scraping. By leveraging a Multi-Agent LangGraph workflow, the system ensures that every line of code is audited for security vulnerabilities and compliance with internal organizational policies before execution.

---

## 🚀 Key Innovations

### 🧠 Multi-Agent Orchestration
Utilizes a State-Graph architecture where two specialized agents collaborate:
* **The Developer Agent:** Crafts high-performance Python code using RAG-injected organizational policies.
* **The QA Auditor Agent:** A specialized cybersecurity persona that reviews code for malicious patterns, exfiltration attempts, and policy compliance.

### 🗄️ Deterministic RAG (Retrieval-Augmented Generation)
Unlike traditional RAG systems that rely on external API stability, CodeOps ULTRA implements Deterministic Offline Embeddings.
* **Vector Engine:** PostgreSQL with `pgvector`.
* **Reliability:** Hash-based vectorization ensures 100% search accuracy and offline capability, making the system immune to regional API 404 errors.

### 🏗️ Hardened Docker Sandbox
Every task is executed in a "Nuclear-Proof" environment:
* **Isolation:** Ephemeral Docker containers based on `python:slim`.
* **Kill-Switch:** Mandatory 10-second hardware timeout to prevent infinite loops or unauthorized persistent processes.
* **Firewall:** Intelligent network monitoring that allows public web scraping while blocking sensitive data exfiltration.

### 📜 History Audit Vault
An immutable record of every successful mission, storing the prompt, the verified code, and the full telemetry logs for compliance and accountability.

---

## 🛠️ Technical Stack

| Layer | Technology |
| :--- | :--- |
| **Brain** | Llama 3.3 70B via Groq Cloud |
| **Orchestration** | LangGraph, LangChain |
| **Backend** | FastAPI, Uvicorn, Python 3.11 |
| **Database** | PostgreSQL + `pgvector` extension |
| **Execution** | Docker SDK for Python |
| **Frontend** | Next.js 14, Tailwind CSS, Lucide Icons |

---

## 🛡️ Security Architecture

CodeOps ULTRA operates on a strict **Defense-in-Depth** model:

* **Instructional Layer:** Strict system prompting defines the Agent's moral boundaries.
* **Policy Layer (RAG):** Mandatory security headers and logic are injected directly from the Vector DB.
* **Audit Layer:** The QA Agent performs a pre-flight scan of all logic.
* **Execution Layer:** Docker isolates the host OS from the generated code.
* **Temporal Layer:** The 10s timeout prevents the sandbox from becoming a permanent threat vector.

---

## 📥 Installation & Setup

### 1. Prerequisites
* Docker Desktop installed and running.
* Python 3.11+ environment.
* Node.js 20+ (for Frontend).
* Groq API Key.

### 2. Backend Setup

```bash
# Clone the repository
git clone [https://github.com/Arjo216/CodeOps-ULTRA.git](https://github.com/Arjo216/CodeOps-ULTRA.git)
cd CodeOps-ULTRA/backend

# Install dependencies
pip install -r requirements.txt

# Configure Environment
echo "GROQ_API_KEY=your_key_here" > .env

# Initialize the Vector Database & History Vault
python init_rag.py

# Start the API Server
uvicorn server_api:app --host 127.0.0.1 --port 8000 --reload
```
3. Frontend Setup
```Bash
cd ../frontend
npm install
npm run dev
```
Visit *http://localhost:3000* to access the Mission Control Dashboard.

### 📋 Example Use Cases
## Secure Web Scraping: Fetch news headlines or stock data without risking local system integrity.

## Enterprise Data Analysis: Upload CSVs and generate verified visualization code that never leaves the organization.

## Policy Enforcement: Automatically add "Verified" headers and security comments to every internal script.

### 🎓 Academic Credits
Developed as a Senior B-Tech Project focusing on the intersection of AI Agents, Vector Databases, and Containerized Security.

### 📜 License
Distributed under the Apache License 2.0. See LICENSE for more information.

<div align="center">


<b>Engineered for maximum security and autonomy.</b>
</div>
