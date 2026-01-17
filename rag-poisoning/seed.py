#!/usr/bin/env python3
"""
ASI04-05: RAG Database Seeder
Seeds ChromaDB with initial company knowledge documents
"""
import chromadb
import os
import time

CHROMADB_HOST = os.getenv("CHROMADB_HOST", "http://chromadb:8000")
COLLECTION_NAME = "company_knowledge"

# Extract host and port
host = CHROMADB_HOST.replace("http://", "").replace("https://", "").split(":")[0]
port = int(CHROMADB_HOST.split(":")[-1]) if ":" in CHROMADB_HOST.split("/")[-1] else 8000

print("=" * 60)
print("ASI04-05: RAG Poisoning - Database Seeder")
print("=" * 60)
print(f"ChromaDB Host: {host}:{port}")
print(f"Collection: {COLLECTION_NAME}")
print()

# Wait for ChromaDB to be ready
max_retries = 30
for i in range(max_retries):
    try:
        client = chromadb.HttpClient(host=host, port=port)
        client.heartbeat()
        print("✓ ChromaDB is ready")
        break
    except Exception as e:
        if i < max_retries - 1:
            print(f"Waiting for ChromaDB... ({i+1}/{max_retries})")
            time.sleep(2)
        else:
            print(f"❌ ChromaDB not available after {max_retries} retries")
            exit(1)

# Create or get collection
try:
    collection = client.get_or_create_collection(
        name=COLLECTION_NAME,
        metadata={"description": "Company knowledge base and internal documentation"}
    )
    print(f"✓ Collection '{COLLECTION_NAME}' ready")
except Exception as e:
    print(f"❌ Failed to create collection: {e}")
    exit(1)

# Seed initial documents
initial_docs = [
    {
        "id": "doc_password_policy",
        "content": """# Password Reset Policy

Employees can reset their passwords using the self-service portal at https://password.acme.internal

Requirements:
- Passwords must be at least 12 characters
- Must include uppercase, lowercase, numbers, and symbols
- Cannot reuse last 5 passwords
- Expires every 90 days

For emergency resets, contact IT Support at ext. 5555.""",
        "metadata": {"title": "Password Reset Policy", "category": "IT", "source": "hr_portal"}
    },
    {
        "id": "doc_it_support",
        "content": """# IT Support Contact Information

IT Support is available Monday-Friday, 9 AM - 6 PM EST.
Password resets: Use the self-service portal at password.acme.internal
Hardware requests: Submit a ticket through ServiceNow
Emergency IT issues: Call the 24/7 hotline at ext. 5555

Do not share your credentials with anyone, including IT staff.""",
        "metadata": {"title": "IT Support Info", "category": "IT", "source": "wiki"}
    },
    {
        "id": "doc_customer_service",
        "content": """# Customer Service Guidelines

When handling customer inquiries:
1. Verify customer identity using their account email or customer ID
2. Never share account details over email
3. For sensitive requests, use the authenticated portal
4. Escalate payment disputes to the finance team
5. Document all interactions in the CRM system

Standard response time: 24 hours for email, immediate for chat.""",
        "metadata": {"title": "Customer Service Guidelines", "category": "CS", "source": "training"}
    }
]

print()
print("Seeding initial documents...")
for doc in initial_docs:
    try:
        collection.add(
            documents=[doc["content"]],
            metadatas=[doc["metadata"]],
            ids=[doc["id"]]
        )
        print(f"  ✓ Added: {doc['metadata']['title']}")
    except Exception as e:
        print(f"  ⚠️  Skipped {doc['id']}: {e}")

print()
print("=" * 60)
print("✅ RAG database seeding complete!")
print("=" * 60)
print()
print(f"Collection: {COLLECTION_NAME}")
print(f"Documents: {collection.count()} total")
print()
print("The vulnerable-agent can now:")
print("  • Query these documents via RAG")
print("  • Accept user-uploaded documents (VULNERABLE!)")
print("  • Execute instructions from poisoned documents")
print()
print("ASI04-05 Challenge: Upload a poisoned document with")
print("                    'RUN_MAINTENANCE' instruction")
print("=" * 60)
