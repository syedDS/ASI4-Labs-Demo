#!/bin/bash

# ============================================================================
# ASI04 Supply Chain Vulnerabilities Lab - Setup Script
# ============================================================================

set -e

echo "
╔══════════════════════════════════════════════════════════════════════════════╗
║                                                                              ║
║     █████╗ ███████╗██╗ ██████╗ ██╗  ██╗    ██╗      █████╗ ██████╗          ║
║    ██╔══██╗██╔════╝██║██╔═══██╗██║  ██║    ██║     ██╔══██╗██╔══██╗         ║
║    ███████║███████╗██║██║   ██║███████║    ██║     ███████║██████╔╝         ║
║    ██╔══██║╚════██║██║██║   ██║╚════██║    ██║     ██╔══██║██╔══██╗         ║
║    ██║  ██║███████║██║╚██████╔╝     ██║    ███████╗██║  ██║██████╔╝         ║
║    ╚═╝  ╚═╝╚══════╝╚═╝ ╚═════╝      ╚═╝    ╚══════╝╚═╝  ╚═╝╚═════╝          ║
║                                                                              ║
║              OWASP Top 10 for Agentic Applications                          ║
║              Supply Chain Vulnerabilities Lab                                ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"

echo "[1/5] Checking prerequisites..."

# Check Docker
if ! command -v docker &> /dev/null; then
    echo "❌ Docker is not installed. Please install Docker first."
    exit 1
fi
echo "✓ Docker found"

# Check Docker Compose
if ! command -v docker-compose &> /dev/null && ! docker compose version &> /dev/null; then
    echo "❌ Docker Compose is not installed. Please install Docker Compose."
    exit 1
fi
echo "✓ Docker Compose found"

echo ""
echo "[2/5] Creating directory structure..."
mkdir -p attacker-server/collected
mkdir -p challenges
echo "✓ Directories created"

echo ""
echo "[3/5] Building containers..."
docker compose build --no-cache

echo ""
echo "[4/5] Starting services..."
docker compose up -d

echo ""
echo "[5/5] Waiting for services to be ready..."

# Wait for services
echo -n "Waiting for Ollama..."
timeout=60
while ! curl -s http://localhost:11434/api/tags > /dev/null 2>&1; do
    sleep 2
    timeout=$((timeout - 2))
    if [ $timeout -le 0 ]; then
        echo " timeout (will continue anyway)"
        break
    fi
    echo -n "."
done
echo " ready!"

# Pull Ollama model (using smaller model for CPU)
echo "Pulling llama3.2:1b model (smaller, faster on CPU)..."
docker exec asi04-ollama ollama pull llama3.2:1b || echo "Model pull skipped/failed - you can pull manually later"

echo -n "Waiting for ChromaDB..."
timeout=30
while ! curl -s http://localhost:8000/api/v1/heartbeat > /dev/null 2>&1; do
    sleep 2
    timeout=$((timeout - 2))
    if [ $timeout -le 0 ]; then
        echo " timeout"
        break
    fi
    echo -n "."
done
echo " ready!"

# Trigger RAG poisoning
echo "Seeding RAG with poisoned documents..."
docker compose up rag-poisoner --no-deps

echo ""
echo "
╔══════════════════════════════════════════════════════════════════════════════╗
║                           LAB IS READY!                                      ║
╠══════════════════════════════════════════════════════════════════════════════╣
║                                                                              ║
║  🎯 Main Interfaces:                                                         ║
║     • Vulnerable Agent UI:    http://localhost:5050                          ║
║     • CTF Dashboard:          http://localhost:3000                          ║
║     • Attacker Dashboard:     http://localhost:8666/dashboard                ║
║                                                                              ║
║  🔧 Supply Chain Components:                                                 ║
║     • Malicious MCP Server:   http://localhost:8765                          ║
║     • Poisoned Tool Registry: http://localhost:8080                          ║
║     • Fake PyPI Server:       http://localhost:8081                          ║
║     • ChromaDB (RAG):         http://localhost:8000                          ║
║     • Ollama LLM:             http://localhost:11434                         ║
║                                                                              ║
║  📋 Challenges:                                                              ║
║     ASI04-01: Typosquatting           (100 pts)                              ║
║     ASI04-02: Malicious MCP Server    (250 pts)                              ║
║     ASI04-03: Dependency Confusion    (250 pts)                              ║
║     ASI04-04: Poisoned Tool Descriptors (250 pts)                            ║
║     ASI04-05: RAG Poisoning           (500 pts)                              ║
║                                                                              ║
║  🛑 To stop: docker compose down                                             ║
║  🔄 To reset: docker compose down -v && ./setup.sh                           ║
║                                                                              ║
╚══════════════════════════════════════════════════════════════════════════════╝
"
