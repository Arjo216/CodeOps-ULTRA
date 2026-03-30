<div align="center">

# 🛡️ CodeOps ULTRA <br> `[ Enterprise DevSecOps Platform ]`

**An autonomous, polyglot AI orchestration platform with native IDE integration, stateless CI/CD webhooks, and hardened Docker execution.**

[![License](https://img.shields.io/badge/License-Apache%202.0-blue.svg?style=for-the-badge)](https://opensource.org/licenses/Apache-2.0)
[![Python](https://img.shields.io/badge/Python-3.11+-ffd43b?style=for-the-badge&logo=python&logoColor=blue)](https://www.python.org/)
[![TypeScript](https://img.shields.io/badge/TypeScript-007ACC?style=for-the-badge&logo=typescript&logoColor=white)](https://www.typescriptlang.org/)
[![Next.js](https://img.shields.io/badge/Next.js-14-000000?style=for-the-badge&logo=next.js&logoColor=white)](https://nextjs.org/)
[![Docker](https://img.shields.io/badge/Docker-Sandboxed-2496ed?style=for-the-badge&logo=docker&logoColor=white)](https://www.docker.com/)
[![PostgreSQL](https://img.shields.io/badge/pgvector-Memory-336791?style=for-the-badge&logo=postgresql&logoColor=white)](https://www.postgresql.org/)

> *"Bridging the gap between Cognitive AI and Secure Systems Engineering."*

*(📸 Insert a GIF or Video link of your VS Code Extension and Dashboard working here!)*

</div>

---

## 📖 The Architecture Overview

**CodeOps ULTRA** is not just a chatbot; it is a full-stack, distributed DevSecOps ecosystem. Engineered for the modern tech landscape, it provides a seamless bridge between a developer's local environment and a highly secure, autonomous AI agent capable of writing, auditing, and compiling polyglot code in real-time.

By leveraging a LangGraph multi-agent workflow grounded in a custom `pgvector` Vector Database, CodeOps ULTRA ensures zero-trust execution. It features a Next.js mission control dashboard, a native VS Code Extension, a Python CLI, and an autonomous GitHub Webhook Bot for automated Pull Request auditing.

---

## 🚀 Key Innovations

## 🌐 The ULTRA Ecosystem

CodeOps ULTRA is accessible through four distinct enterprise interfaces, all powered by a centralized asynchronous FastAPI gateway:

### 1. 💻 Native IDE Integration (VS Code)
* **Instant Audits:** Right-click any Python, Java, C++, JS, Rust, or Go file to trigger a deep static analysis.
* **Live Telemetry:** Streams secure Docker execution logs directly into the native VS Code Output Channel.
* **Built with:** TypeScript, VS Code Extension API.

### 2. 🐙 Autonomous CI/CD (GitHub PR Bot)
* **Stateless Webhooks:** Listens to repository events via public tunneling.
* **Auto-Verification:** Automatically pulls PR diffs, runs the Multi-Agent security audit, and posts verified approvals directly into the GitHub comment thread.
* **Telemetry:** Backed by an asynchronous SQLite database for real-time observability.

### 3. 🖥️ Mission Control (Web Dashboard)
* **Enterprise UI:** A dark-mode, cyberpunk-themed Next.js 14 dashboard using Tailwind CSS.
* **Live Observability:** View live execution telemetry, PR audit histories, and memory vault logs in real-time.

### 4. ⚡ The Hacker's CLI
* **Terminal Native:** A rich, interactive command-line interface built with `Typer` and `Rich` for developers who prefer the terminal.
* **Polyglot Execution:** Request code generation and watch it compile inside Docker directly from your prompt.

---

## 🛡️ The Cognitive & Security Core

* **Multi-Agent Debates:** A LangGraph State-Graph where a Developer Agent and a strict QA Auditor Agent iteratively debate and refine code until it meets corporate security standards.
* **Deterministic RAG:** Uses PostgreSQL + `pgvector` for offline, hash-based retrieval of security policies, immune to external API outages.
* **Polyglot Docker Sandbox:** Code is executed in ephemeral `eclipse-temurin` (Java) or `python:slim` containers with a strict 10-second hardware kill-switch to prevent infinite loops and unauthorized exfiltration.

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

### 🏗️ System Architecture

```mermaid
graph TD
    %% Custom Enterprise Styling
    classDef interface fill:#0f172a,stroke:#38bdf8,stroke-width:2px,color:#fff,rx:8px,ry:8px
    classDef gateway fill:#1e1b4b,stroke:#8b5cf6,stroke-width:2px,color:#fff,rx:8px,ry:8px
    classDef agent fill:#022c22,stroke:#10b981,stroke-width:2px,color:#fff,rx:8px,ry:8px
    classDef db fill:#450a0a,stroke:#ef4444,stroke-width:2px,color:#fff,rx:8px,ry:8px
    classDef docker fill:#082f49,stroke:#0ea5e9,stroke-width:2px,color:#fff,rx:8px,ry:8px

    %% Interface Layer
    subgraph Interfaces["🌐 The Interface Ecosystem"]
        direction LR
        UI["🖥️ Next.js Dashboard"]:::interface
        VSC["💻 VS Code Extension<br>(TypeScript)"]:::interface
        CLI["⚡ Terminal CLI<br>(Rich/Typer)"]:::interface
        GH["🐙 GitHub Webhook<br>(PR Bot)"]:::interface
    end

    %% Gateway
    API["⚡ FastAPI Async Gateway<br>(Uvicorn + REST)"]:::gateway

    %% Cognitive Core
    subgraph Cognitive["🧠 LangGraph Cognitive Core"]
        direction LR
        Dev["👨‍💻 Developer Agent<br>(Llama 3.3 70B)"]:::agent
        QA["🕵️‍♂️ QA Auditor Agent<br>(Middleware Sanitizer)"]:::agent
        Dev -->|Submits Code| QA
        QA -.->|Rejects & Prompts| Dev
    end

    %% Memory & Telemetry
    subgraph Storage["🗄️ State & Memory Storage"]
        direction TB
        VectorDB["🗂️ RAG Memory<br>(PostgreSQL + pgvector)"]:::db
        SQLite["📊 Observability DB<br>(SQLite Telemetry)"]:::db
    end

    %% Execution Engine
    subgraph Execution["🏗️ Polyglot Docker Sandbox"]
        direction TB
        Docker["🐳 Docker Daemon"]:::docker
        Sandbox["📦 Ephemeral Containers<br>(Python, Java, C++, JS)"]:::docker
        Docker --- Sandbox
    end

    %% Routing
    Interfaces ==>|JSON Payloads| API
    API ==>|Orchestrates| Cognitive
    API ==>|Logs Events| SQLite
    
    VectorDB -.->|Injects Policies| Dev
    QA ==>|Approved Code| Docker
    Sandbox ==>|Streams Stdout/Logs| API
```
---

## 📥 Installation & Setup

### 1. Prerequisites
* Docker Desktop installed and running.
* Python 3.11+ environment.
* Node.js 20+ (for Frontend).
* Groq API Key.

### 2. Backend Engine Setup

```bash
# Clone the repository
git clone https://github.com/Arjo216/CodeOps-ULTRA.git
cd CodeOps-ULTRA/backend

# Install dependencies
pip install -r requirements.txt

# Configure Environment Variables
# Create a .env file in the root directory
echo "GROQ_API_KEY=your_groq_key_here" >> ../.env
echo "GITHUB_TOKEN=your_github_pat_here" >> ../.env
echo "DATABASE_URL=postgresql://ultra_admin:ultra_secure_password@127.0.0.1:5432/codeops_memory" >> ../.env

# Initialize the Vector Database
python init_rag.py

# Start the Async API Server (Auto-generates SQLite Telemetry DB)
uvicorn server_api:app --host 127.0.0.1 --port 8000 --reload
```

### 3. Frontend Setup
```Bash
cd ../frontend
npm install
npm run dev
```
Visit *http://localhost:3000* to access the Mission Control Dashboard.

### 4. VS Code Extension Packaging
```bash
# Navigate to the extension folder
cd ../codeops-ultra 

# Install dependencies and the packaging tool
npm install
npm install -g @vscode/vsce

# Package the extension into a .vsix binary file
vsce package

# Install the packaged extension directly into your local VS Code IDE
code --install-extension codeops-ultra-0.0.1.vsix
```

### 📋 Example Use Cases
* **Secure Web Scraping:** Fetch news headlines or stock data without risking local system integrity.

* **Enterprise Data Analysis:** Upload CSVs and generate verified visualization code that never leaves the organization.

* **Policy Enforcement:** Automatically add "Verified" headers and security comments to every internal script.

### 🎓 Academic Credits
Developed as a Senior B-Tech Project focusing on the intersection of AI Agents, Vector Databases, and Containerized Security.

### 📜 License
Distributed under the **Apache License 2.0**. See LICENSE for more information.

<div align="center">


<b>Engineered for maximum security and autonomy.</b>
</div>
