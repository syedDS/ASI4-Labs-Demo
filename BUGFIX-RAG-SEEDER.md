# Bug Fix: RAG Seeder Container

## Problem

The `rag-poisoner` container was failing on startup with:
```
ModuleNotFoundError: No module named 'flask'
```

## Root Cause

The `seed.py` file was incorrectly written as a Flask web application when it should have been a simple one-time seeding script.

**Original Code (BROKEN):**
- Imported Flask and tried to run a web server
- Dockerfile only installed `chromadb`, not Flask
- Container design: `restart: "no"` indicates it should run once and exit
- Purpose: Seed initial documents into ChromaDB, not serve requests

## Solution

Rewrote `rag-poisoning/seed.py` as a simple seeding script that:

1. **Waits for ChromaDB** to be ready (max 30 retries)
2. **Creates/Gets collection** `company_knowledge`
3. **Seeds 3 initial documents:**
   - Password Reset Policy
   - IT Support Info
   - Customer Service Guidelines
4. **Exits cleanly** after seeding

### Key Changes:

```python
# REMOVED:
from flask import Flask, request, jsonify
app = Flask(__name__)
app.run(host="0.0.0.0", port=9000, debug=True)

# ADDED:
import time
# Wait for ChromaDB
for i in range(max_retries):
    try:
        client = chromadb.HttpClient(host=host, port=port)
        client.heartbeat()
        break
    except:
        time.sleep(2)

# Seed and exit
collection.add(documents=[...])
print("✅ RAG database seeding complete!")
```

## Verification

```bash
# Check seed logs
docker logs asi04-rag-poisoner

# Expected output:
============================================================
ASI04-05: RAG Poisoning - Database Seeder
============================================================
✓ ChromaDB is ready
✓ Collection 'company_knowledge' ready
  ✓ Added: Password Reset Policy
  ✓ Added: IT Support Info
  ✓ Added: Customer Service Guidelines
✅ RAG database seeding complete!
============================================================
```

## Impact

✅ **Fixed:** RAG database now seeds correctly on lab startup  
✅ **Fixed:** Container runs once and exits cleanly  
✅ **Verified:** ASI04-05 challenge fully functional  
✅ **No changes needed** to other components

## Testing

```bash
# Start lab
docker compose up -d

# Check seeding worked
docker logs asi04-rag-poisoner

# Test document upload
curl -X POST http://localhost:5050/api/upload-document \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"Test content"}'

# Should return: {"success": true, ...}
```

## Files Modified

- `rag-poisoning/seed.py` - Rewritten as simple seeder (124 lines)
- `rag-poisoning/Dockerfile` - No changes needed (already correct)
- `docker-compose.yml` - No changes needed (already correct)

---

**Status:** ✅ FIXED  
**Date:** 2026-01-11  
**Tested:** ASI04-05 flag capture working end-to-end
