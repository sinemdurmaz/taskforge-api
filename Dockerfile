# Çok Aşamalı (Multi-Stage) Üretim Seviyesi Dockerfile
FROM python:3.12-slim AS builder

WORKDIR /app

# Sistem bağımlılıkları ve Python derleme araçları
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    && rm -rf /var/lib/apt/lists/*

# Bağımlılıkları yükle
COPY requirements.txt .
RUN pip install --no-cache-dir --user -r requirements.txt

# --- 2. Aşama: Çalışma Zamanı (Runtime) ---
FROM python:3.12-slim AS runner

WORKDIR /app

# Güvenlik için root olmayan kullanıcı oluştur
RUN useradd -m -u 1000 appuser

# Builder aşamasından bağımlılıkları kopyala
COPY --from=builder /root/.local /home/appuser/.local
ENV PATH=/home/appuser/.local/bin:$PATH

# Uygulama kodlarını kopyala
COPY --chown=appuser:appuser . .

# Kullanıcıya geç
USER appuser

EXPOSE 8000

# Sağlık kontrolü (Healthcheck)
HEALTHCHECK --interval=30s --timeout=5s --start-period=5s --retries=3 \
  CMD python -c "import urllib.request; urllib.request.urlopen('http://localhost:8000/')" || exit 1

# Uvicorn ile FastAPI sunucusunu başlat
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8000"]
