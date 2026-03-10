import os
import psycopg2
import hashlib
import numpy as np
from pgvector.psycopg2 import register_vector
from dotenv import load_dotenv
import time

load_dotenv()

def connect_with_retry():
    for i in range(5):
        try:
            conn = psycopg2.connect(
                host="127.0.0.1",
                database="codeops_memory",
                user="ultra_admin",
                password="ultra_secure_password",
                port="5432"
            )
            return conn
        except psycopg2.OperationalError:
            print(f"Waiting for database... ({i+1}/5)")
            time.sleep(2)
    raise Exception("Could not connect to DB.")

def get_deterministic_embedding(text, dimensions=768):
    seed = int(hashlib.md5(text.encode()).hexdigest(), 16) % (2**32)
    np.random.seed(seed)
    vector = np.random.uniform(-1, 1, dimensions)
    return (vector / np.linalg.norm(vector)).tolist()

conn = connect_with_retry()
cur = conn.cursor()

# 1. Extensions
cur.execute("CREATE EXTENSION IF NOT EXISTS vector")
conn.commit()

# 2. RAG Table
cur.execute("DROP TABLE IF EXISTS company_memory")
cur.execute("CREATE TABLE company_memory (id serial PRIMARY KEY, content text, embedding vector(768))")

# 3. NEW: Task History Table
cur.execute("DROP TABLE IF EXISTS task_history")
cur.execute("""
    CREATE TABLE task_history (
        id serial PRIMARY KEY,
        task text,
        code text,
        logs text[],
        created_at timestamp DEFAULT CURRENT_TIMESTAMP
    )
""")
conn.commit()

register_vector(conn)

documents = [
    "CodeOps Policy: All scripts MUST include a comment at the top saying '# Verified by CodeOps ULTRA'.",
    "Security Rule: Use of the 'subprocess' module is strictly forbidden unless authorized by an admin.",
    "Data Rule: When processing CSV files, always use 'engine=python' in the pandas read_csv function."
]

print("🧠 Generating Deterministic Embeddings & History Vault...")
for doc in documents:
    try:
        vector = get_deterministic_embedding(doc)
        cur.execute("INSERT INTO company_memory (content, embedding) VALUES (%s, %s)", (doc, vector))
        print(f"  ✅ Memorized: {doc[:45]}...")
    except Exception as e:
        print(f"  ❌ Error: {e}")

conn.commit()
cur.close()
conn.close()
print("\n✅ Database Fully Initialized with History Vault!")