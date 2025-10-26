#!/bin/bash

# Colors for output
GREEN='\033[0;32m'
BLUE='\033[0;34m'
YELLOW='\033[1;33m'
NC='\033[0m' # No Color

echo -e "${BLUE}========================================${NC}"
echo -e "${BLUE}   Spookathon Ngrok Setup${NC}"
echo -e "${BLUE}========================================${NC}"
echo ""

# Check if ngrok is installed
if ! command -v ngrok &> /dev/null; then
    echo -e "${YELLOW}ngrok is not installed.${NC}"
    echo "Please install ngrok first:"
    echo "  - Visit https://ngrok.com/download"
    echo "  - Or run: brew install ngrok (macOS)"
    echo "  - Or run: npm install -g ngrok"
    exit 1
fi

# Check if server is already running on port 8000
if lsof -Pi :8000 -sTCP:LISTEN -t >/dev/null 2>&1 ; then
    echo -e "${YELLOW}Port 8000 is already in use.${NC}"
    echo "Please stop the existing service or use a different port."
    exit 1
fi

echo -e "${GREEN}Starting FastAPI server...${NC}"
cd server
python -m uvicorn main:app --host 0.0.0.0 --port 8000 &
SERVER_PID=$!

# Wait for server to start
sleep 3

# Check if server started successfully
if kill -0 $SERVER_PID 2>/dev/null; then
    echo -e "${GREEN}Server started successfully (PID: $SERVER_PID)${NC}"
else
    echo -e "${YELLOW}Failed to start server${NC}"
    exit 1
fi

echo ""
echo -e "${BLUE}Starting ngrok tunnel...${NC}"
echo -e "${GREEN}Your server will be accessible via the ngrok URL shown below${NC}"
echo ""

# Start ngrok
ngrok http 8000

# Cleanup when script exits
cleanup() {
    echo ""
    echo -e "${YELLOW}Stopping server...${NC}"
    kill $SERVER_PID 2>/dev/null
    exit 0
}

trap cleanup EXIT
