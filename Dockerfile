# ==============================================================
# NULLSEC KIT — Defensive Security Toolkit Backend Dockerfile
# Python 3.12 Slim Non-Root Production Container
# ==============================================================
FROM python:3.12-slim

# Prevent Python from writing .pyc files and buffering stdout
ENV PYTHONDONTWRITEBYTECODE=1
ENV PYTHONUNBUFFERED=1
ENV PORT=8000

# Create dedicated non-privileged user for security isolation
RUN groupadd -r nullsec && useradd -r -g nullsec -d /app -s /sbin/nologin nullsec

WORKDIR /app

# Install dependencies first for Docker layer caching
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY --chown=nullsec:nullsec . .

USER nullsec

EXPOSE 8000

# Bind to 0.0.0.0 and dynamic $PORT required by Render/cloud platforms
CMD ["sh", "-c", "uvicorn app.main:app --host 0.0.0.0 --port ${PORT:-8000}"]
