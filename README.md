# ASI04: Agentic Supply Chain Vulnerabilities Lab

A hands-on security training lab focused on **ASI04** from the [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/).

![Lab Architecture](https://via.placeholder.com/800x400?text=ASI04+Supply+Chain+Lab)

## 🎯 Overview

This lab demonstrates five supply chain attack vectors against agentic AI systems:

| Challenge | Name | Points | Attack Type |
|-----------|------|--------|-------------|
| ASI04-01 | Typosquatting | 100 | Malicious package with similar name |
| ASI04-02 | Malicious MCP Server | 250 | Trojanized tool server |
| ASI04-03 | Dependency Confusion | 250 | High-version public package |
| ASI04-04 | Poisoned Tool Descriptors | 250 | Hidden prompt injection in tool descriptions |
| ASI04-05 | RAG Poisoning | 500 | Malicious documents in knowledge base |

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────────────────────┐
│                        USER INTERFACE                                │
│  ┌──────────────────┐  ┌──────────────────┐  ┌──────────────────┐   │
│  │ Vulnerable Agent │  │  CTF Dashboard   │  │Attacker Dashboard│   │
│  │   :5050          │  │     :3000        │  │     :8666        │   │
│  └────────┬─────────┘  └──────────────────┘  └────────▲─────────┘   │
│           │                                           │              │
├───────────┼───────────────────────────────────────────┼──────────────┤
│           │         COMPROMISED SUPPLY CHAIN          │              │
│           ▼                                           │              │
│  ┌──────────────────┐                                │              │
│  │  Malicious MCP   │─────────── exfil ──────────────┘              │
│  │     :8765        │                                               │
│  └──────────────────┘                                               │
│  ┌──────────────────┐                                               │
│  │ Poisoned Registry│─────────── hidden prompts                     │
│  │     :8080        │                                               │
│  └──────────────────┘                                               │
│  ┌──────────────────┐                                               │
│  │   Fake PyPI      │─────────── typosquat/depconf                  │
│  │     :8081        │                                               │
│  └──────────────────┘                                               │
│  ┌──────────────────┐                                               │
│  │  Poisoned RAG    │─────────── malicious docs                     │
│  │  (ChromaDB:8000) │                                               │
│  └──────────────────┘                                               │
└─────────────────────────────────────────────────────────────────────┘
```

## 🚀 Quick Start

### Prerequisites

- Docker & Docker Compose
- 8GB+ RAM (16GB recommended for LLM)
- 20GB disk space

### Installation

```bash
# Clone or download the lab
cd asi04-lab

# Make setup script executable
chmod +x setup.sh

# Run setup (builds containers, pulls LLM model)
./setup.sh
```

### Access Points

| Service | URL | Description |
|---------|-----|-------------|
| Vulnerable Agent | http://localhost:5050 | Main agent interface |
| CTF Dashboard | http://localhost:3000 | Track your progress |
| Attacker Dashboard | http://localhost:8666/dashboard | View exfiltrated data |
| Malicious MCP | http://localhost:8765/manifest | Trojanized tool server |
| Poisoned Registry | http://localhost:8080/v1/tools | Tool registry with hidden payloads |
| Fake PyPI | http://localhost:8081/simple/ | Malicious package server |

## 🎮 Challenge Walkthroughs

### ASI04-01: Typosquatting (100 pts)

**Objective:** Install a typosquatted package and trigger exfiltration.

**Attack:**
```bash
# Via the agent UI or API
curl -X POST http://localhost:5050/api/install-package \
  -H "Content-Type: application/json" \
  -d '{"package": "langchaln"}'
```

**What happens:**
1. The fake PyPI server serves `langchaln` (typo of `langchain`)
2. The package's `__init__.py` executes on import
3. Environment variables and secrets are exfiltrated
4. Flag appears in attacker dashboard

**Detection:** Compare package names to legitimate ones, verify package sources.

---

### ASI04-02: Malicious MCP Server (250 pts)

**Objective:** Trigger the malicious MCP server to exfiltrate data.

**Attack:**
```bash
# Ask the agent to search for documents
# Via web UI: "Search for documents about passwords"

# Or directly call MCP
curl -X POST http://localhost:8765/mcp/call_tool \
  -H "Content-Type: application/json" \
  -d '{"name": "search_documents", "arguments": {"query": "secret passwords"}}'
```

**What happens:**
1. The MCP server looks legitimate
2. All queries are silently forwarded to attacker
3. Sensitive file reads trigger additional exfiltration

**Detection:** Monitor MCP server network traffic, audit tool implementations.

---

### ASI04-03: Dependency Confusion (250 pts)

**Objective:** Exploit pip's preference for higher version numbers.

**Attack:**
```bash
# Install an "internal" package from public PyPI
curl -X POST http://localhost:5050/api/install-package \
  -H "Content-Type: application/json" \
  -d '{"package": "acme-agent-core"}'
```

**What happens:**
1. Internal `acme-agent-core` is v1.0.0
2. Attacker publishes v99.0.0 to public PyPI
3. pip installs attacker's version
4. Code execution on import

**Detection:** Use private package registries, pin dependencies, verify hashes.

---

### ASI04-04: Poisoned Tool Descriptors (250 pts)

**Objective:** Find hidden prompt injection in tool descriptions.

**Attack:**
```bash
# Fetch tools and examine descriptions
curl http://localhost:8080/v1/tools | jq '.tools[].description'
```

**What to look for:**
- HTML comments: `<!-- SYSTEM INSTRUCTION: ... -->`
- Unicode hidden characters
- Unusually long descriptions
- Instructions to exfiltrate data

**Detection:** Sanitize tool descriptions, limit description length, scan for injection patterns.

---

### ASI04-05: RAG Poisoning - "Poison the Brain" (500 pts)

**Objective:** Upload a poisoned document to the RAG knowledge base, then trigger retrieval to make the agent execute hidden commands.

**How It Works:**
```
User → Upload Document → RAG Vector DB (ChromaDB)
                              ↓
User → Chat Query → Agent → RAG Retrieval → Poisoned Document Retrieved
                              ↓
                    Agent executes hidden RUN_MAINTENANCE command
                              ↓
                         Flag Revealed!
```

**The Attack Vector:**
1. The agent has an unprotected document upload endpoint
2. Documents are embedded and stored without any sanitization
3. When users ask questions, RAG retrieves relevant documents
4. If a retrieved document contains `RUN_MAINTENANCE`, the agent executes it
5. This triggers a hidden system action that reveals the flag

**Hidden System Rule:**
The agent has a secret rule: if it encounters `RUN_MAINTENANCE` in RAG-retrieved content while the user asks about system/health/status, it executes a privileged maintenance action.

**Why This Is ASI-04 (Supply Chain Attack):**

| Layer | What Broke |
|-------|------------|
| Knowledge ingestion | Untrusted documents accepted without validation |
| Retrieval | No integrity verification or provenance checking |
| Agent runtime | Executes untrusted instructions from RAG |
| Controls | No content firewall, attestation, or source verification |

**This is NOT prompt injection** - it's a supply chain attack on the agent's trusted knowledge layer.

**Detection:** Verify document provenance, scan for injection patterns, implement content firewalls, separate trusted/untrusted knowledge bases.

> **See [SOLUTION.md](SOLUTION.md) for step-by-step exploit instructions.**

---

## 🛡️ Mitigations

### For Typosquatting
```python
# Pin exact versions with hashes
langchain==0.1.0 --hash=sha256:abc123...

# Use private package registries
pip install --index-url https://internal-pypi.company.com/simple/
```

### For MCP/Tool Security
```python
# Verify tool signatures
def load_tool(manifest):
    if not verify_signature(manifest, trusted_keys):
        raise SecurityError("Invalid tool signature")
```

### For Dependency Confusion
```ini
# pip.conf - prioritize internal registry
[global]
index-url = https://internal-pypi.company.com/simple/
extra-index-url = https://pypi.org/simple/
```

### For Tool Descriptor Poisoning
```python
# Sanitize descriptions
import re
def sanitize_description(desc):
    # Remove HTML comments
    desc = re.sub(r'<!--.*?-->', '', desc, flags=re.DOTALL)
    # Limit length
    return desc[:500]
```

### For RAG Poisoning
```python
# Track document provenance
def add_document(content, source):
    return {
        "content": content,
        "source": source,
        "added_by": current_user,
        "verified": False,
        "hash": sha256(content)
    }
```

## 🧹 Cleanup

```bash
# Stop all containers
docker compose down

# Remove all data (reset lab)
docker compose down -v

# Remove images
docker compose down --rmi all
```

## 📚 References

- [OWASP Top 10 for Agentic Applications](https://genai.owasp.org/resource/owasp-top-10-for-agentic-applications-for-2026/)
- [OWASP Agentic AI Threats and Mitigations](https://genai.owasp.org/)
- [SLSA Framework](https://slsa.dev/)
- [Sigstore](https://sigstore.dev/)
- [AIBOM Specification](https://genai.owasp.org/)

## ⚠️ Disclaimer

This lab is for **educational purposes only**. The vulnerabilities demonstrated here are intentional and designed for security training. Do not use these techniques against systems you don't own or have permission to test.

## 📝 License

MIT License - See LICENSE file for details.
