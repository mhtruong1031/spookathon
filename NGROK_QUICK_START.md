# Ngrok Quick Start Guide

## Installation

### macOS
```bash
brew install ngrok
```

### Or download from
https://ngrok.com/download

## First Time Setup

1. Sign up at https://dashboard.ngrok.com/get-started/setup
2. Get your authtoken from the dashboard
3. Configure ngrok:
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

## Usage

### Option 1: Use the automated script (Recommended)
```bash
./start_ngrok.sh
```

Or with Python:
```bash
python start_ngrok.py
```

### Option 2: Manual setup

**Terminal 1 - Start server:**
```bash
cd server
uvicorn main:app --reload --port 8000
```

**Terminal 2 - Start ngrok:**
```bash
ngrok http 8000
```

## Getting Your Public URL

After starting ngrok, you'll see output like:
```
Forwarding   https://abc123.ngrok.io -> http://localhost:8000
```

Copy the HTTPS URL and use it in your frontend configuration.

## Updating Frontend

Update your frontend API base URL to use the ngrok URL instead of `localhost:8000`.

## Important Notes

- The free tier provides random URLs that change each restart
- Keep both the server and ngrok running while testing
- For a stable URL, consider upgrading to a paid ngrok plan
- Press `Ctrl+C` to stop both server and ngrok

## Troubleshooting

| Issue | Solution |
|-------|----------|
| ngrok not found | Install ngrok or add to PATH |
| Port 8000 in use | Stop other services on port 8000 |
| Tunnel failed | Check your authtoken configuration |
