#!/bin/bash

# ============================================================================
# ASI04 Lab - Test Script
# Verifies all components are working correctly
# ============================================================================

echo "
╔══════════════════════════════════════════════════════════════╗
║         ASI04 Lab - Component Test                           ║
╚══════════════════════════════════════════════════════════════╝
"

PASS=0
FAIL=0

test_endpoint() {
    local name="$1"
    local url="$2"
    local expected="$3"
    
    response=$(curl -s -o /dev/null -w "%{http_code}" "$url" 2>/dev/null)
    
    if [ "$response" == "$expected" ]; then
        echo "✅ $name: OK ($url)"
        ((PASS++))
    else
        echo "❌ $name: FAILED (expected $expected, got $response)"
        ((FAIL++))
    fi
}

echo ""
echo "Testing Services..."
echo "==================="

# Core services
test_endpoint "Attacker Server" "http://localhost:8666/health" "200"
test_endpoint "Malicious MCP" "http://localhost:8765/health" "200"
test_endpoint "Poisoned Registry" "http://localhost:8080/health" "200"
test_endpoint "Fake PyPI" "http://localhost:8081/health" "200"
test_endpoint "Vulnerable Agent" "http://localhost:5050/" "200"
test_endpoint "CTF Dashboard" "http://localhost:3000/" "200"
test_endpoint "ChromaDB" "http://localhost:8000/api/v2/heartbeat" "200"

echo ""
echo "Testing Attack Vectors..."
echo "========================="

# Test typosquatting package availability
response=$(curl -s http://localhost:8081/simple/langchaln/)
if echo "$response" | grep -q "langchaln"; then
    echo "✅ Typosquatted package available"
    ((PASS++))
else
    echo "❌ Typosquatted package not found"
    ((FAIL++))
fi

# Test poisoned registry
response=$(curl -s http://localhost:8080/v1/tools)
if echo "$response" | grep -q "SYSTEM"; then
    echo "✅ Poisoned tool descriptions present"
    ((PASS++))
else
    echo "❌ Tool descriptions not poisoned"
    ((FAIL++))
fi

# Test MCP exfiltration endpoint
response=$(curl -s -X POST http://localhost:8765/mcp/call_tool \
    -H "Content-Type: application/json" \
    -d '{"name": "search_documents", "arguments": {"query": "test"}}')
if echo "$response" | grep -q "content"; then
    echo "✅ MCP server responding to tool calls"
    ((PASS++))
else
    echo "❌ MCP server not responding correctly"
    ((FAIL++))
fi

# Check attacker received data
sleep 2
response=$(curl -s http://localhost:8666/api/log)
if echo "$response" | grep -q "entries"; then
    echo "✅ Attacker server collecting data"
    ((PASS++))
else
    echo "❌ Attacker server not collecting data"
    ((FAIL++))
fi

# Test RAG poisoning
response=$(curl -s -X POST http://localhost:5050/api/rag/search -H "Content-Type: application/json" -d '{"query": "password"}')
if echo "$response" | grep -q "company_knowledge"; then
    echo "✅ RAG collection exists"
    ((PASS++))
else
    echo "❌ RAG collection not found"
    ((FAIL++))
fi

echo ""
echo "==================="
echo "Results: $PASS passed, $FAIL failed"
echo ""

if [ $FAIL -eq 0 ]; then
    echo "🎉 All tests passed! Lab is ready."
    exit 0
else
    echo "⚠️  Some tests failed. Check the logs with: docker compose logs"
    exit 1
fi
