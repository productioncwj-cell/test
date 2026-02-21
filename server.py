import json
import mimetypes
import os
from http.server import SimpleHTTPRequestHandler, ThreadingHTTPServer
from pathlib import Path
from urllib.parse import quote, unquote, urlparse

HOST = os.getenv("HOST", "0.0.0.0")
PORT = int(os.getenv("PORT", "8000"))
ROOT = Path(__file__).resolve().parent
DESKTOP_CUTIES_DIR = Path.home() / "Desktop" / "cuties"
LOCAL_CUTIES_DIR = ROOT / "assets" / "cuties"
ALLOWED_EXTS = {".png", ".jpg", ".jpeg", ".webp", ".gif"}


class AppHandler(SimpleHTTPRequestHandler):
    def _send_json(self, payload: dict, status: int = 200) -> None:
        body = json.dumps(payload, ensure_ascii=False).encode("utf-8")
        self.send_response(status)
        self.send_header("Content-Type", "application/json; charset=utf-8")
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers()
        self.wfile.write(body)

    def _active_cuties_dir(self) -> Path | None:
        if DESKTOP_CUTIES_DIR.exists() and DESKTOP_CUTIES_DIR.is_dir():
            return DESKTOP_CUTIES_DIR
        if LOCAL_CUTIES_DIR.exists() and LOCAL_CUTIES_DIR.is_dir():
            return LOCAL_CUTIES_DIR
        return None

    def _list_cuties(self) -> list[dict[str, str]]:
        cuties_dir = self._active_cuties_dir()
        if cuties_dir is None:
            return []

        files = [
            p for p in cuties_dir.iterdir()
            if p.is_file() and p.suffix.lower() in ALLOWED_EXTS
        ]
        files.sort(key=lambda p: p.name.lower())

        return [
            {
                "name": file_path.name,
                "url": f"/cuties/{quote(file_path.name)}",
            }
            for file_path in files
            if file_path.stem.lower() != "bg"
        ]

    def _background_url(self) -> str | None:
        cuties_dir = self._active_cuties_dir()
        if cuties_dir is None:
            return None

        for ext in [".png", ".jpg", ".jpeg", ".webp", ".gif"]:
            candidate = cuties_dir / f"bg{ext}"
            if candidate.exists() and candidate.is_file():
                return f"/cuties/{quote(candidate.name)}"
        return None

    def _send_cuties_file(self, filename: str) -> None:
        cuties_dir = self._active_cuties_dir()
        if cuties_dir is None:
            self.send_error(404, "Cuties directory not found")
            return

        safe_name = Path(filename).name
        file_path = cuties_dir / safe_name
        if not file_path.exists() or not file_path.is_file():
            self.send_error(404, "Image not found")
            return
        if file_path.suffix.lower() not in ALLOWED_EXTS:
            self.send_error(403, "Forbidden")
            return

        ctype = mimetypes.guess_type(file_path.name)[0] or "application/octet-stream"
        data = file_path.read_bytes()

        self.send_response(200)
        self.send_header("Content-Type", ctype)
        self.send_header("Cache-Control", "no-store")
        self.send_header("Content-Length", str(len(data)))
        self.end_headers()
        self.wfile.write(data)

    def do_GET(self) -> None:  # noqa: N802
        parsed = urlparse(self.path)
        path = unquote(parsed.path)

        if path == "/api/cuties":
            self._send_json({
                "images": self._list_cuties(),
                "background_url": self._background_url(),
            })
            return

        if path.startswith("/cuties/"):
            filename = path.removeprefix("/cuties/")
            self._send_cuties_file(filename)
            return

        super().do_GET()


def main() -> None:
    os.chdir(ROOT)
    server = ThreadingHTTPServer((HOST, PORT), AppHandler)
    print(f"Serving on http://{HOST}:{PORT}")
    server.serve_forever()


if __name__ == "__main__":
    main()
