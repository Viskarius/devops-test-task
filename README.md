# Local Web-App Stack (Docker Compose)

| Service    | Role                           | Port |
|------------|--------------------------------|------|
| Nginx      | Reverse proxy, TLS termination | 443  |
| Backend    | Python HTTP app                | 8080 |
| PostgreSQL | Relational DB v15              | 5432 |
| Redis      | Session / cache store          | 6379 |

## Quick Start (3-5 commands)

```bash
bash gen-certs.sh
cp .env.example .env
docker compose up -d --build
docker compose ps
curl -k https://localhost/healthz
curl -k https://localhost/
```

Stop and remove everything:
```bash
docker compose down -v
```

## Project Layout

- docker-compose.yml — orchestration
- .env / .env.example — secrets (not hardcoded in compose)
- gen-certs.sh — openssl self-signed cert generator
- certs/ — created by gen-certs.sh (git-ignored)
- nginx/nginx.conf — rate limit 10 r/s/IP, body <= 10 MB, TLS
- backend/ — Dockerfile, app.py (/, /healthz)
- postgres/init.sql — runs on first DB start

## Key Design Decisions

- Nginx: limit_req_zone 10 req/s per IP (burst 5, nodelay); client_max_body_size 10m;
  sets X-Forwarded-For/Proto/Host + X-Real-IP; TLS 1.2/1.3 only.
- Healthchecks: postgres (pg_isready), redis (redis-cli ping), backend (curl /healthz),
  nginx (HTTPS /healthz). Startup order via condition: service_healthy.
- Secrets: all passwords in .env, injected via env_file/environment.
- Backend /healthz: returns JSON with postgres and redis booleans.

## Verification

```bash
curl -k https://localhost/healthz
curl -k https://localhost/
seq 1 30 | xargs -P30 -I{} curl -k -o /dev/null -s -w "%{http_code} " https://localhost/
dd if=/dev/zero of=/tmp/big.bin bs=1M count=11
curl -k -o /dev/null -s -w "%{http_code}" -X POST --data-binary @/tmp/big.bin https://localhost/
```
