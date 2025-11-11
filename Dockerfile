# Dockerfile para aplicación Bibliometry
# Uso: docker build -t bibliometry .
#      docker run -p 8501:8501 bibliometry

# Base: Python 3.10 slim (ligera y estable)
FROM python:3.10-slim

# Metadata
LABEL maintainer="bibliometry-team"
LABEL description="Sistema de análisis bibliométrico con IA Generativa"
LABEL version="1.0"

# Variables de entorno
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_NO_CACHE_DIR=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# Directorio de trabajo
WORKDIR /app

# Instalar dependencias del sistema necesarias para algunas librerías Python
# - build-essential, gcc: compiladores para paquetes que requieren compilación
# - libgomp1: OpenMP para NumPy/SciPy
# - libglib2.0-0, libnss3, libx11-6, etc.: dependencias de Playwright
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    gcc \
    g++ \
    libgomp1 \
    git \
    wget \
    curl \
    ca-certificates \
    # Dependencias para Playwright/Chromium
    libnss3 \
    libnspr4 \
    libatk1.0-0 \
    libatk-bridge2.0-0 \
    libcups2 \
    libdrm2 \
    libdbus-1-3 \
    libxkbcommon0 \
    libatspi2.0-0 \
    libxcomposite1 \
    libxdamage1 \
    libxfixes3 \
    libxrandr2 \
    libgbm1 \
    libpango-1.0-0 \
    libcairo2 \
    libasound2 \
    && rm -rf /var/lib/apt/lists/*

# Copiar archivos de requisitos
COPY requirements.txt ./

# Instalar dependencias de Python
# Usar --extra-index-url para PyTorch CPU-only (reduce tamaño de imagen)
RUN pip install --upgrade pip setuptools wheel && \
    pip install -r requirements.txt \
    --extra-index-url https://download.pytorch.org/whl/cpu \
    -c constraints.txt

# Instalar navegadores de Playwright (solo Chromium para reducir tamaño)
RUN playwright install chromium && \
    playwright install-deps chromium

# Copiar código fuente
COPY . .

# Crear directorios necesarios si no existen
RUN mkdir -p data/raw/IEEE data/raw/SemanticScholar \
    data/processed data/analysis data/logs \
    clustering

# Puerto de Streamlit (configurable para diferentes plataformas)
ENV PORT=8501
EXPOSE $PORT

# Healthcheck para verificar que la aplicación está respondiendo
HEALTHCHECK --interval=30s --timeout=10s --start-period=5s --retries=3 \
    CMD curl --fail http://localhost:${PORT}/_stcore/health || exit 1

# Comando por defecto: ejecutar dashboard de Streamlit
# Usa $PORT de Railway/Cloud Run, fallback a 8501
CMD streamlit run app.py \
    --server.port=${PORT:-8501} \
    --server.address=0.0.0.0 \
    --server.headless=true \
    --browser.gatherUsageStats=false
