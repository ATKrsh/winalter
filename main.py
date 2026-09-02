"""
WinAlter - Windows Image Engineering Platform Entrypoint
"""

import sys
import os
import argparse
import webbrowser

sys.path.insert(0, os.path.abspath(os.path.dirname(__file__)))

from web.server import run_server
from cli import main as cli_main

def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["build", "validate", "inspect"]:
        cli_main()
    else:
        parser = argparse.ArgumentParser(description="WinAlter - Windows Image Engineering Platform")
        parser.add_argument("--port", type=int, default=5100, help="Web Studio port (default: 5100)")
        parser.add_argument("--no-browser", action="store_true", help="Do not open browser automatically")
        args, _ = parser.parse_known_args()

        url = f"http://localhost:{args.port}"
        if not args.no_browser:
            print(f"Opening WinAlter Visual OS Studio at {url}...")
            webbrowser.open(url)
        run_server(port=args.port)

if __name__ == "__main__":
    main()
