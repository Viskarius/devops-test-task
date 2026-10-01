import json, os, socket
from http.server import BaseHTTPRequestHandler, HTTPServer
import psycopg2, redis

PG_DSN = os.environ.get("DATABASE_URL",
    "dbname=appdb user=appuser password=secret host=postgres port=5432")
REDIS_URL = os.environ.get("REDIS_URL", "redis://redis:6379/0")
r = redis.from_url(REDIS_URL, decode_responses=True, socket_connect_timeout=3)

def pg_ping():
    try:
        with psycopg2.connect(PG_DSN, connect_timeout=3) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT 1"); return cur.fetchone()[0] == 1
    except Exception as e:
        print(f"[pg] {e}"); return False

class H(BaseHTTPRequestHandler):
    def _json(self, code, data):
        body = json.dumps(data, indent=2).encode()
        self.send_response(code)
        self.send_header("Content-Type", "application/json")
        self.send_header("Content-Length", str(len(body)))
        self.end_headers(); self.wfile.write(body)

    def do_GET(self):
        if self.path == "/healthz":
            pg, rd = pg_ping(), False
            try: rd = r.ping()
            except Exception: pass
            self._json(200 if pg and rd else 503,
                       {"status": "ok" if pg and rd else "degraded",
                        "postgres": pg, "redis": rd})
            return
        try: hits = r.incr("request_counter")
        except Exception: hits = -1
        self._json(200, {
            "message": "Hello from backend",
            "hostname": socket.gethostname(),
            "request_counter": hits,
            "forwarded_headers": {
                "X-Forwarded-For":   self.headers.get("X-Forwarded-For"),
                "X-Forwarded-Proto": self.headers.get("X-Forwarded-Proto"),
                "X-Forwarded-Host":  self.headers.get("X-Forwarded-Host"),
                "X-Real-IP":         self.headers.get("X-Real-IP")}})

if __name__ == "__main__":
    port = int(os.environ.get("BACKEND_PORT", 8080))
    print(f"Backend on :{port}")
    HTTPServer(("0.0.0.0", port), H).serve_forever()
