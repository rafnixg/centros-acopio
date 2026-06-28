# ============================================================
# Dockerfile — Centros de Acopio Venezuela
# Python 3.12 slim · FastAPI + Uvicorn
# ============================================================

FROM python:3.12-slim

WORKDIR /app

# Variables de entorno
ENV PYTHONDONTWRITEBYTECODE=1 \
    PYTHONUNBUFFERED=1 \
    ADMIN_TOKEN=admin123 \
    DATABASE_URL=sqlite:////data/centros_acopio.db

# Crear directorio para la base de datos persistente
RUN mkdir -p /data

# Instalar dependencias del sistema
RUN apt-get update && apt-get install -y --no-install-recommends \
    gcc \
    && rm -rf /var/lib/apt/lists/*

# Copiar e instalar dependencias Python
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copiar el código fuente
COPY . .

# Puerto
EXPOSE 8000

# Volumen para datos persistentes (base de datos SQLite)
VOLUME ["/data"]

# Comando de inicio
CMD ["uvicorn", "backend.main:app", "--host", "0.0.0.0", "--port", "8000"]