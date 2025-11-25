#!/usr/bin/env python
"""
Simple HTTP server to serve the frontend
"""
import http.server
import socketserver
import os
import webbrowser
import threading

PORT = 8010

# Change to frontend directory
# os.chdir('frontend')

Handler = http.server.SimpleHTTPRequestHandler

def open_browser():
    """Open browser after a short delay"""
    import time
    time.sleep(1)
    webbrowser.open(f'http://localhost:{PORT}')

# Open browser in a separate thread
threading.Thread(target=open_browser, daemon=True).start()

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"=" * 50)
    print(f"Frontend server running at http://localhost:{PORT}")
    print(f"Backend should be running at http://localhost:5000")
    print(f"=" * 50)
    print(f"Press Ctrl+C to stop the server")
    print(f"=" * 50)
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nServer stopped.")

