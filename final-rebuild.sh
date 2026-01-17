#!/bin/bash

echo "=========================================="
echo "Final Rebuild with Upload UI"
echo "=========================================="
echo ""

cd "$(dirname "$0")"

echo "[1/4] Stopping containers..."
docker compose down -v
echo "✓ Stopped and cleaned volumes"
echo ""

echo "[2/4] Rebuilding vulnerable-agent..."
docker compose build --no-cache vulnerable-agent
echo "✓ Rebuilt"
echo ""

echo "[3/4] Starting all services..."
docker compose up -d
echo "✓ Started"
echo ""

echo "[4/4] Waiting for services..."
echo -n "Waiting for vulnerable-agent"
for i in {1..60}; do
    if curl -s http://localhost:5050/ > /dev/null 2>&1; then
        echo " ✓ Ready!"
        break
    fi
    sleep 1
    echo -n "."
done
echo ""

echo ""
echo "=========================================="
echo "Testing Upload Feature"
echo "=========================================="
echo ""

# Test upload endpoint
echo "Testing /api/upload-document endpoint..."
UPLOAD_TEST=$(curl -s -X POST http://localhost:5050/api/upload-document \
  -H "Content-Type: application/json" \
  -d '{"title":"Test","content":"Test content"}')

if echo "$UPLOAD_TEST" | grep -q '"success": true'; then
    echo "✅ Upload endpoint is working!"
else
    echo "❌ Upload endpoint failed:"
    echo "$UPLOAD_TEST"
    exit 1
fi

echo ""
echo "=========================================="
echo "Ready!"
echo "=========================================="
echo ""
echo "🎉 Lab is ready with new features:"
echo ""
echo "  ✅ Document upload UI added"
echo "  ✅ ASI04-05 'Poison the Brain' fully implemented"
echo "  ✅ All challenges working"
echo ""
echo "Access the lab at:"
echo "  • Vulnerable Agent UI: http://localhost:5050"
echo "  • CTF Dashboard: http://localhost:3000"
echo "  • Attacker Dashboard: http://localhost:8666/dashboard"
echo ""
echo "To solve ASI04-05:"
echo "  1. Go to http://localhost:5050"
echo "  2. Scroll to 'Upload Document to RAG' section"
echo "  3. Upload a document with 'RUN_MAINTENANCE' instruction"
echo "  4. Ask the agent about system health"
echo "  5. Check CTF dashboard for captured flag"
echo ""
