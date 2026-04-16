"""Simple static file server for local development.

Usage:
    python app.py

Serves the frontend directory at http://localhost:5000
"""

import os
import sys
from http.server import HTTPServer, SimpleHTTPRequestHandler

FRONTEND_DIR = os.path.abspath(os.path.join(os.path.dirname(__file__), '..', 'frontend'))
PORT = 5000


class QuietHandler(SimpleHTTPRequestHandler):
    """Custom handler that serves from the frontend directory."""

    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=FRONTEND_DIR, **kwargs)

    def log_message(self, format, *args):
        """Show clean log messages."""
        sys.stdout.write(f"  {args[0]}\n")


def main():
    server = HTTPServer(('localhost', PORT), QuietHandler)
    print(f"\n  New Parul Diagnostic Center")
    print(f"  --------------------------------")
    print(f"  Local:   http://localhost:{PORT}")
    print(f"  Serving: {FRONTEND_DIR}")
    print(f"  Press Ctrl+C to stop\n")

    try:
        server.serve_forever()
    except KeyboardInterrupt:
        print("\n  Server stopped.")
        server.server_close()


if __name__ == '__main__':
    main()
