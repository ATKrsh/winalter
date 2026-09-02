"""
Web Server for WinAlter Visual OS Studio
Serves REST API, live AST compiler preview, and SSE build log streaming.
"""

import os
import sys
import json
import threading
import urllib.parse
from http.server import ThreadingHTTPServer, BaseHTTPRequestHandler
import logging

sys.path.insert(0, os.path.abspath(os.path.join(os.path.dirname(__file__), "..")))

from winalter.core.config import WinAlterSpec
from winalter.core.ast_compiler import WinAlterCompiler
from winalter.analyzer.iso_importer import ISOImporter
from winalter.analyzer.wim_analyzer import WIMAnalyzer
from winalter.engine.build_pipeline import WinAlterBuildEngine
from winalter.presets.default_specs import PRESET_SPECS

logger = logging.getLogger("WinAlter.WebServer")
logging.basicConfig(level=logging.INFO)

sse_clients = []

def broadcast_log(message: str):
    data = f"data: {json.dumps({'message': message})}\n\n"
    dead = []
    for client in sse_clients:
        try:
            client.wfile.write(data.encode('utf-8'))
            client.wfile.flush()
        except Exception:
            dead.append(client)
    for d in dead:
        if d in sse_clients:
            sse_clients.remove(d)

class StudioRequestHandler(BaseHTTPRequestHandler):
    def log_message(self, format, *args):
        pass

    def _set_headers(self, content_type="application/json", status=200):
        self.send_response(status)
        self.send_header("Content-Type", content_type)
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Access-Control-Allow-Methods", "GET, POST, OPTIONS")
        self.send_header("Access-Control-Allow-Headers", "Content-Type")
        self.end_headers()

    def do_OPTIONS(self):
        self._set_headers()

    def do_GET(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        if path == "/api/presets":
            self._set_headers()
            presets_resp = {
                k: v.model_dump() for k, v in PRESET_SPECS.items()
            }
            self.wfile.write(json.dumps(presets_resp).encode('utf-8'))

        elif path == "/api/events":
            self.send_response(200)
            self.send_header("Content-Type", "text/event-stream")
            self.send_header("Cache-Control", "no-cache")
            self.send_header("Connection", "keep-alive")
            self.send_header("Access-Control-Allow-Origin", "*")
            self.end_headers()

            sse_clients.append(self)
            try:
                while True:
                    self.wfile.write(": keepalive\n\n".encode('utf-8'))
                    self.wfile.flush()
                    threading.Event().wait(15)
            except Exception:
                if self in sse_clients:
                    sse_clients.remove(self)

        else:
            if getattr(sys, 'frozen', False):
                base_web_dir = os.path.join(sys._MEIPASS, "web")
            else:
                base_web_dir = os.path.dirname(__file__)

            if path == "/":
                file_path = os.path.join(base_web_dir, "static", "index.html")
                content_type = "text/html"
            else:
                rel_path = path.lstrip("/")
                file_path = os.path.join(base_web_dir, "static", rel_path)
                if file_path.endswith(".css"):
                    content_type = "text/css"
                elif file_path.endswith(".js"):
                    content_type = "application/javascript"
                elif file_path.endswith(".png"):
                    content_type = "image/png"
                elif file_path.endswith(".svg"):
                    content_type = "image/svg+xml"
                else:
                    content_type = "text/plain"

            if os.path.exists(file_path) and os.path.isfile(file_path):
                self._set_headers(content_type=content_type)
                with open(file_path, "rb") as f:
                    self.wfile.write(f.read())
            else:
                self.send_error(404, "File Not Found")

    def do_POST(self):
        parsed = urllib.parse.urlparse(self.path)
        path = parsed.path

        content_len = int(self.headers.get('Content-Length', 0))
        body = self.rfile.read(content_len).decode('utf-8')
        data = json.loads(body) if body else {}

        if path == "/api/compile-ast":
            spec_data = data.get("spec", {})
            try:
                spec = WinAlterSpec(**spec_data)
                compiler = WinAlterCompiler(spec)
                plan = compiler.compile()
                self._set_headers()
                self.wfile.write(json.dumps({
                    "success": True,
                    "yaml": spec.to_yaml(),
                    "plan": plan.to_dict()
                }).encode('utf-8'))
            except Exception as e:
                self._set_headers(status=400)
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

        elif path == "/api/inspect-iso":
            iso_path = data.get("iso_path", "")
            if not os.path.exists(iso_path):
                self._set_headers(status=400)
                self.wfile.write(json.dumps({"error": f"ISO path does not exist: {iso_path}"}).encode('utf-8'))
                return

            try:
                broadcast_log(f"WinAlter Importer: Extracting ISO {iso_path} into workspace...")
                importer = ISOImporter("project_workspace/source")
                importer.import_iso(iso_path, progress_callback=broadcast_log)
                wim_path = importer.find_install_wim()

                analyzer = WIMAnalyzer(wim_path)
                summary = analyzer.get_summary_components()
                self._set_headers()
                self.wfile.write(json.dumps({"success": True, "analysis": summary}).encode('utf-8'))
            except Exception as e:
                self._set_headers(status=500)
                self.wfile.write(json.dumps({"error": str(e)}).encode('utf-8'))

        elif path == "/api/start-build":
            spec_data = data.get("spec", {})
            iso_path = data.get("iso_path", "")
            edition_index = int(data.get("edition_index", 1))

            def worker():
                try:
                    spec = WinAlterSpec(**spec_data)
                    engine = WinAlterBuildEngine(workspace_root="project_workspace", output_dir="dist")
                    output_iso = engine.execute_build(spec, iso_path, edition_index, log_callback=broadcast_log)
                    broadcast_log(f"BUILD_SUCCESS:{output_iso}")
                except Exception as e:
                    broadcast_log(f"BUILD_ERROR:{str(e)}")

            threading.Thread(target=worker, daemon=True).start()
            self._set_headers()
            self.wfile.write(json.dumps({"success": True, "message": "WinAlter Build Pipeline launched."}).encode('utf-8'))

        else:
            self.send_error(404, "Endpoint Not Found")

def run_server(port=5100):
    server_address = ('', port)
    httpd = ThreadingHTTPServer(server_address, StudioRequestHandler)
    print(f"\n=======================================================")
    print(f" WinAlter Visual OS Studio Live at:")
    print(f" http://localhost:{port}")
    print(f"=======================================================\n")
    httpd.serve_forever()

if __name__ == "__main__":
    run_server()
