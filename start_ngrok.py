#!/usr/bin/env python3
"""
Ngrok startup script for Spookathon
This script starts the FastAPI server and ngrok tunnel automatically.
"""

import subprocess
import sys
import time
import os
import signal

def check_ngrok_installed():
    """Check if ngrok is installed."""
    try:
        subprocess.run(['ngrok', 'version'], capture_output=True, check=True)
        return True
    except (subprocess.CalledProcessError, FileNotFoundError):
        return False

def check_port_available(port):
    """Check if a port is available."""
    try:
        import socket
        with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
            s.bind(('localhost', port))
            return True
    except OSError:
        return False

def start_server():
    """Start the FastAPI server."""
    print("🚀 Starting FastAPI server...")
    process = subprocess.Popen(
        ['python', '-m', 'uvicorn', 'main:app', '--host', '0.0.0.0', '--port', '8000'],
        cwd='server',
        stdout=subprocess.PIPE,
        stderr=subprocess.PIPE
    )
    
    # Wait a bit for server to start
    time.sleep(3)
    
    # Check if process is still running
    if process.poll() is None:
        print("✅ Server started successfully!")
        return process
    else:
        print("❌ Failed to start server")
        stdout, stderr = process.communicate()
        print(stderr.decode())
        return None

def start_ngrok():
    """Start ngrok tunnel."""
    print("\n🌐 Starting ngrok tunnel...")
    print("Your server will be accessible via the ngrok URL shown below\n")
    
    try:
        # Start ngrok in the foreground so we can see the URL
        subprocess.run(['ngrok', 'http', '8000'])
    except KeyboardInterrupt:
        print("\n🛑 Stopping...")
    except FileNotFoundError:
        print("❌ ngrok not found. Please install ngrok first.")
        print("Visit: https://ngrok.com/download")

def main():
    """Main function."""
    print("=" * 50)
    print("   Spookathon Ngrok Setup")
    print("=" * 50)
    print()
    
    # Check if ngrok is installed
    if not check_ngrok_installed():
        print("❌ ngrok is not installed.")
        print("Please install ngrok first:")
        print("  - Visit https://ngrok.com/download")
        print("  - Or run: brew install ngrok (macOS)")
        print("  - Or run: npm install -g ngrok")
        sys.exit(1)
    
    # Check if port 8000 is available
    if not check_port_available(8000):
        print("❌ Port 8000 is already in use.")
        print("Please stop the existing service or use a different port.")
        sys.exit(1)
    
    # Start server
    server_process = start_server()
    if not server_process:
        sys.exit(1)
    
    # Handle cleanup
    def cleanup(signum, frame):
        print("\n🛑 Stopping server...")
        if server_process:
            server_process.terminate()
            server_process.wait()
        sys.exit(0)
    
    signal.signal(signal.SIGINT, cleanup)
    signal.signal(signal.SIGTERM, cleanup)
    
    # Start ngrok
    try:
        start_ngrok()
    finally:
        cleanup(None, None)

if __name__ == '__main__':
    main()
