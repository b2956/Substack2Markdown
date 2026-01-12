#!/usr/bin/env python3
"""
Simple HTTP server to serve the article explorer
Run this to view the interface with working article navigation
"""
import http.server
import socketserver
import os
import webbrowser
from threading import Timer

PORT = 8000

def open_browser():
    """Open browser after a short delay"""
    webbrowser.open(f'http://localhost:{PORT}/substack_html_pages/blog.html')

# Change to project root directory
os.chdir(os.path.dirname(os.path.abspath(__file__)))

Handler = http.server.SimpleHTTPRequestHandler
Handler.extensions_map['.html'] = 'text/html'
Handler.extensions_map['.css'] = 'text/css'
Handler.extensions_map['.js'] = 'application/javascript'

with socketserver.TCPServer(("", PORT), Handler) as httpd:
    print(f"🚀 Starting Article Explorer...")
    print(f"📡 Server running at http://localhost:{PORT}")
    print(f"🌐 Opening http://localhost:{PORT}/substack_html_pages/blog.html")
    print(f"\n✨ Press Ctrl+C to stop the server\n")

    # Open browser after 1 second
    Timer(1.0, open_browser).start()

    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\n\n👋 Shutting down server...")
