# ── Stage: runtime ────────────────────────────────────────────────────────────
FROM python:3.12-slim

# Metadata
LABEL maintainer="TecArt CTF"
LABEL description="Web Challenge #2 — Cookie Manipulation (Base64)"

# Don't write .pyc files, don't buffer stdout/stderr
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1

WORKDIR /app

# Install dependencies first (layer cache-friendly)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy application source
COPY app.py .
COPY templates/ templates/
COPY static/    static/

# Run as non-root user for basic hardening
RUN adduser --disabled-password --gecos "" ctfuser
USER ctfuser

EXPOSE 8082

# Use gunicorn for production-grade serving
CMD ["gunicorn", "--bind", "0.0.0.0:8082", "--workers", "2", "--timeout", "60", "app:app"]
