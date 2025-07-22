# Dockerfile
FROM python:3.11-slim

WORKDIR /app

# Instala as dependências do sistema necessárias para compilar dlib, face-recognition etc
RUN apt-get update && apt-get install -y --no-install-recommends \
    build-essential \
    cmake \
    libboost-all-dev \
    libglib2.0-0 \
    libsm6 \
    libxext6 \
    libxrender-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Copia requirements e instala tudo de uma vez só
COPY requirements.txt .

RUN pip install --no-cache-dir -r requirements.txt

# Copia o restante do código da aplicação
COPY . .

# Expõe a porta que o Gunicorn usará
EXPOSE 5000

# Comando para iniciar o servidor Gunicorn
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "app:app"]
