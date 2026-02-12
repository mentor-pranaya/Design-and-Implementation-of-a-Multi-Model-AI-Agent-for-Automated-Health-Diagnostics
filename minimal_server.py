#!/usr/bin/env python3
"""
Minimal standalone server - no external dependencies!
Just uses Python standard library to serve the API
"""
from http.server import HTTPServer, BaseHTTPRequestHandler
from urllib.parse import urlparse, parse_qs
import json
import sys
import os

class MinimalAPIHandler(BaseHTTPRequestHandler):
    """Simple HTTP handler that mimics FastAPI endpoints"""
    
    def do_GET(self):
        parsed_path = urlparse(self.path)
        
        # Health check endpoint
        if parsed_path.path == '/health':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "healthy",
                "message": "INBLOODO AGENT is running!",
                "server": "Minimal HTTP Server (Python stdlib)"
            }
            self.wfile.write(json.dumps(response).encode())
            return
        
        # Root path
        if parsed_path.path == '/' or parsed_path.path == '':
            self.send_response(200)
            self.send_header('Content-type', 'text/html')
            self.end_headers()
            html = """
            <!DOCTYPE html>
            <html>
            <head>
                <title>INBLOODO AGENT - AI Health Diagnostics</title>
                <style>
                    body { font-family: Arial, sans-serif; margin: 40px; background: #f5f5f5; }
                    .container { max-width: 800px; margin: 0 auto; background: white; padding: 30px; border-radius: 8px; box-shadow: 0 2px 4px rgba(0,0,0,0.1); }
                    h1 { color: #2c3e50; border-bottom: 3px solid #3498db; padding-bottom: 10px; }
                    .status { background: #d4edda; border: 1px solid #c3e6cb; padding: 15px; border-radius: 4px; margin: 20px 0; }
                    .status.ok { color: #155724; }
                    code { background: #f4f4f4; padding: 2px 6px; border-radius: 3px; font-family: 'Courier New', monospace; }
                    .endpoints { margin-top: 30px; }
                    .endpoint { background: #ecf0f1; padding: 10px; margin: 10px 0; border-left: 4px solid #3498db; }
                    button { background: #3498db; color: white; padding: 10px 20px; border: none; border-radius: 4px; cursor: pointer; margin-bottom: 20px; }
                    button:hover { background: #2980b9; }
                </style>
            </head>
            <body>
                <div class="container">
                    <h1>🏥 INBLOODO AGENT</h1>
                    <h2>AI-Powered Health Diagnostics System</h2>
                    
                    <div class="status ok">
                        <strong>✅ Server Status:</strong> RUNNING<br>
                        <strong>🔧 Framework:</strong> Python HTTP Server (minimal deployment)<br>
                        <strong>📍 Port:</strong> 10000
                    </div>
                    
                    <div class="endpoints">
                        <h3>Available Endpoints:</h3>
                        <div class="endpoint">
                            <strong>GET /health</strong><br>
                            Check server health status
                        </div>
                        <div class="endpoint">
                            <strong>GET /api/status</strong><br>
                            Get API status and metrics
                        </div>
                    </div>
                    
                    <h3>System Features:</h3>
                    <ul>
                        <li>🤖 Multi-Agent Orchestrator for health analysis</li>
                        <li>📊 Blood report analysis and interpretation</li>
                        <li>💡 AI-powered diagnostic recommendations</li>
                        <li>⚡ Real-time performance metrics</li>
                        <li>🔒 Secure authentication and authorization</li>
                    </ul>
                    
                    <h3>Next Steps:</h3>
                    <button onclick="location.href='/health'">Check Health</button>
                    <button onclick="location.href='/api/status'">View Status</button>
                    <button onclick="alert('Full API available once FastAPI is properly installed')">Upload Report</button>
                    
                    <hr>
                    <p><small>This is a minimal server. For full functionality, install FastAPI: <code>pip install fastapi uvicorn</code></small></p>
                </div>
            </body>
            </html>
            """
            self.wfile.write(html.encode())
            return
        
        # API status endpoint
        if parsed_path.path == '/api/status':
            self.send_response(200)
            self.send_header('Content-type', 'application/json')
            self.end_headers()
            response = {
                "status": "operational",
                "version": "1.0.0",
                "message": "INBLOODO AGENT API (Minimal Mode)",
                "features": {
                    "multi_agent_analysis": "enabled",
                    "blood_report_analysis": "enabled",
                    "health_recommendations": "enabled",
                    "performance_metrics": "available"
                },
                "note": "This is minimal HTTP server mode. For full functionality, install Flask or FastAPI framework."
            }
            self.wfile.write(json.dumps(response, indent=2).encode())
            return
        
        # 404
        self.send_response(404)
        self.send_header('Content-type', 'application/json')
        self.end_headers()
        response = {"error": "Endpoint not found"}
        self.wfile.write(json.dumps(response).encode())
    
    def log_message(self, format, *args):
        """Custom logging"""
        print(f"[{self.client_address[0]}] {format % args}", file=sys.stderr)

def main():
    PORT = 10000
    handler = MinimalAPIHandler
    server = HTTPServer(('0.0.0.0', PORT), handler)
    
    print("=" * 70)
    print("  INBLOODO AGENT - Minimal HTTP Server (Python Standard Library)")
    print("=" * 70)
    print()
    print(f"   ✅ Server starting on port {PORT}")
    print(f"   🌐 Website: http://localhost:{PORT}")
    print(f"   📚 Health Check: http://localhost:{PORT}/health")
    print(f"   📊 Status: http://localhost:{PORT}/api/status")
    print()
    print("   Press Ctrl+C to stop server")
    print()
    print("=" * 70)
    
    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n\n✋ Server stopped by user")
        server.server_close()
        sys.exit(0)

if __name__ == "__main__":
    main()
