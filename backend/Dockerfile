FROM python:3.11-slim AS build
LABEL authors="bennef"

# Installiere locales und Chromium sowie andere notwendige Pakete
RUN apt-get update && apt-get install -y --no-install-recommends \
    locales \
    wget \
    ca-certificates \
    fonts-liberation \
    libasound2 \
    libatk-bridge2.0-0 \
    libatk1.0-0 \
    libcups2 \
    libdbus-1-3 \
    libdrm2 \
    libgbm1 \
    libnspr4 \
    libnss3 \
    libxcomposite1 \
    libxdamage1 \
    libxrandr2 \
    xdg-utils \
    vim \
    tesseract-ocr \
    tesseract-ocr-deu \
    chromium \
    poppler-utils \
    gcc \
    g++ \
    python3-dev \
    make && \
    rm -rf /var/lib/apt/lists/*

# Generiert und konfiguriert die deutsche Locale (de_DE.UTF-8)
RUN sed -i '/de_DE.UTF-8/s/^# //g' /etc/locale.gen && \
    locale-gen de_DE.UTF-8 && \
    update-locale LANG=de_DE.UTF-8

# Setze Umgebungsvariablen für die Locale
ENV LANG=de_DE.UTF-8 \
    LC_ALL=de_DE.UTF-8 \
    LANGUAGE=de_DE.UTF-8

# Setze den Pfad für Pyppeteer, damit es das systemweite Chromium verwendet. Muss Puppeteer sein nicht Pyppeteer.
ENV PUPPETEER_EXECUTABLE_PATH=/usr/bin/chromium

WORKDIR /app
ENV PYTHONPATH=/app

COPY pyproject.toml uv.lock README.md ./
# Installiere die Python-Abhängigkeiten
RUN pip install --upgrade pip && \
    pip install --no-cache-dir uv
RUN uv sync --no-dev --frozen
EXPOSE 8000

COPY app/ ./app/
# Kopiere den restlichen Code
COPY src/ ./src/

# Überprüfe, ob das Argument 'scope' gesetzt ist
ARG scope
RUN test -n "${scope}" || (echo "scope missing" && false)
ENV SCOPE=${scope}

# Setze Umgebungsvariablen für die Python-Umgebung und Zeitzone
ENV PYTHON_ENV=production \
    TZ=Europe/Berlin

# Definiere den Einstiegspunkt für das Container-Image
CMD ["sh", "-c", "uv run app/run_services.py --scope ${SCOPE}"]