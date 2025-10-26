# Ngrok Deployment Setup

This project includes automated ngrok setup for local development with public access.

## 📁 Files Created

- `start_ngrok.sh` - Bash script to start server + ngrok
- `start_ngrok.py` - Python alternative script
- `ngrok_setup.md` - Detailed setup instructions
- `NGROK_QUICK_START.md` - Quick reference guide
- Updated `.gitignore` - Added ngrok logs

## 🚀 Quick Start

1. **Install ngrok** (if not already installed):
   ```bash
   brew install ngrok  # macOS
   ```

2. **Get your authtoken**:
   - Sign up at https://dashboard.ngrok.com
   - Copy your authtoken
   - Run: `ngrok config add-authtoken YOUR_AUTHTOKEN`

3. **Start the server with ngrok**:
   ```bash
   ./start_ngrok.sh
   ```
   
   Or with Python:
   ```bash
   python start_ngrok.py
   ```

4. **Get your public URL**:
   - Look for the forwarding URL in the ngrok output
   - Example: `https://abc123.ngrok.io`
   - Update your frontend to use this URL

## 📖 Documentation

- For detailed instructions, see `ngrok_setup.md`
- For quick reference, see `NGROK_QUICK_START.md`

## ⚙️ What It Does

The automation scripts:
1. Check if ngrok is installed
2. Verify port 8000 is available
3. Start the FastAPI server on port 8000
4. Start ngrok tunnel pointing to port 8000
5. Handle cleanup when stopped (Ctrl+C)

## 🔑 Key Features

- ✅ Automated server startup
- ✅ Port availability checking
- ✅ Clean process management
- ✅ Error handling
- ✅ Cross-platform scripts (Bash + Python)

## 💡 Usage Tips

- The free ngrok tier provides random URLs that change on restart
- For stable URLs, consider upgrading to a paid plan
- Keep both server and ngrok running during development
- Use the HTTPS URL in your frontend configuration
