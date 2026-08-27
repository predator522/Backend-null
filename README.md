# NULLSEC KIT — Defensive Security & Reconnaissance Toolkit Backend

**NULLSEC KIT** is a defensive security research, authorized-assessment, and laboratory analysis toolkit built with Python 3.12+, FastAPI, Uvicorn, dnspython, MongoDB, and Redis.

## Phase Status

- **PHASE 1 — FOUNDATION**: Completed (`/api/v1/health`, centralized error handling, SSRF target validator, sliding token-bucket rate limiter, security headers, modular database client managers).
- **PHASE 2 — DNS RECONNAISSANCE**: Completed (`POST /api/v1/dns/lookup` supporting `A`, `AAAA`, `MX`, `NS`, `TXT`, `CNAME`, `SOA` records via asynchronous `dnspython`).
- **NEXT PHASES**: Phase 3 (WHOIS, IP Intelligence, TLS, Cryptography Utilities), Phase 4 (HTTP Analysis, Headers, CORS, Cookies), Phase 5 (CVE Lookup, Reports, MongoDB/Redis integration).

## Quickstart

```bash
cd backend
python3 -m venv .venv
source .venv/bin/activate
pip install -r requirements.txt
cp .env.example .env
uvicorn app.main:app --host 0.0.0.0 --port 8000 --reload
```

## Running Tests

```bash
pytest -v
```

## Example API Request (`POST /api/v1/dns/lookup`)

```bash
curl -X POST http://localhost:8000/api/v1/dns/lookup \
  -H "Content-Type: application/json" \
  -d '{"domain": "example.com"}'
```
