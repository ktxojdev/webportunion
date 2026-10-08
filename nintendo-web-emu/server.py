import os
import sys
import socket
from http.server import HTTPServer, SimpleHTTPRequestHandler

PORT = 3000
DIRECTORY = os.path.dirname(os.path.abspath(__file__))

class NintendoEmuHandler(SimpleHTTPRequestHandler):
    def __init__(self, *args, **kwargs):
        super().__init__(*args, directory=DIRECTORY, **kwargs)

    def end_headers(self):
        # Enable Cross-Origin Isolation for SharedArrayBuffer, WebGPU, and WASM threads
        self.send_header("Cross-Origin-Opener-Policy", "same-origin")
        self.send_header("Cross-Origin-Embedder-Policy", "require-corp")
        self.send_header("Access-Control-Allow-Origin", "*")
        self.send_header("Cache-Control", "no-cache, no-store, must-revalidate")
        super().end_headers()

    def guess_type(self, path):
        if path.endswith(".wasm"):
            return "application/wasm"
        if path.endswith(".js"):
            return "application/javascript"
        return super().guess_type(path)

def is_port_in_use(port):
    with socket.socket(socket.AF_INET, socket.SOCK_STREAM) as s:
        return s.connect_ex(('127.0.0.1', port)) == 0

def run():
    global PORT
    while is_port_in_use(PORT):
        PORT += 1

    server_address = ('127.0.0.1', PORT)
    httpd = HTTPServer(server_address, NintendoEmuHandler)
    url = f"http://localhost:{PORT}"
    print("=" * 60)
    print("[THE WEBPORT UNION LOCALHOST SERVER]")
    print(f"Running at: {url}")
    print("Cross-Origin Isolation Headers: ENABLED")
    print("Press Ctrl+C to stop the server.")
    print("=" * 60)
    
    try:
        httpd.serve_forever()
    except KeyboardInterrupt:
        print("\nStopping server.")
        httpd.server_close()

if __name__ == "__main__":
    run()
