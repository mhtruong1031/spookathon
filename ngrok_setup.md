# Ngrok Setup for Spookathon

This guide will help you set up ngrok to expose your local development server.

## Prerequisites

1. Install ngrok if you haven't already:
   - Visit https://ngrok.com/download
   - Or install via Homebrew on macOS: `brew install ngrok`
   - Or via npm: `npm install -g ngrok`

2. Create a free ngrok account at https://dashboard.ngrok.com/get-started/setup

## Setup Steps

### 1. Get your authtoken

After signing up for ngrok, get your authtoken from the dashboard.

### 2. Configure ngrok

Run this command (replace `YOUR_AUTHTOKEN` with your actual token):
```bash
ngrok config add-authtoken YOUR_AUTHTOKEN
```

### 3. Start your FastAPI server

In one terminal, start your server:
```bash
cd server
uvicorn main:app --reload --port 8000
```

### 4. Start ngrok

In another terminal, run:
```bash
ngrok http 8000
```

Or for a custom subdomain (requires paid plan):
```bash
ngrok http 8000 --subdomain=spookathon
```

### 5. Get your public URL

ngrok will display a forwarding URL like:
```
Forwarding   https://abc123.ngrok.io -> http://localhost:8000
```

Copy the HTTPS URL and update your frontend to use this URL instead of `localhost:8000`.

## Quick Start Script

Use the `start_ngrok.sh` script to automate this process:
```bash
chmod +x start_ngrok.sh
./start_ngrok.sh
```

## Notes

- The free tier provides random URLs that change each time you restart ngrok
- For a stable URL, consider upgrading to a paid plan
- Your local server must be running before starting ngrok
- The ngrok tunnel will work as long as both the server and ngrok are running

## Troubleshooting

- **Port already in use**: Make sure no other service is using port 8000
- **ngrok command not found**: Make sure ngrok is in your PATH
- **Tunnel failed**: Check your authtoken is correct
