import json
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import unquote, urlparse

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
ROOT = Path(__file__).resolve().parent
CHAR_DIR = ROOT / "assets" / "characters"
ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


class AppHandler(SimpleHTTPRequestHandler):
    def _send_json(self, payload: dict) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(200)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _list_character_paths(self) -> list[str]:
        if not CHAR_DIR.exists() or not CHAR_DIR.is_dir():
            return []

        files = [
            p for p in CHAR_DIR.iterdir()
            if p.is_file() and p.suffix.lower() in ALLOWED_EXTS
        ]
        files.sort(key=lambda p: p.name.lower())

        result = []
        for file_path in files:
            rel = file_path.relative_to(ROOT).as_posix()
            result.append(rel)
        return result

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/api/characters":
            self._send_json({"characters": self._list_character_paths()})
            return

        super().do_GET()


def main() -> None:
    os.chdir(ROOT)
    server = ThreadingHTTPServer((HOST, PORT), AppHandler)
    print(f"Serving on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
