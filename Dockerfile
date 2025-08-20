FROM python:3.11-slim

# Variável de ambiente para evitar prompts interativos
ENV DEBIAN_FRONTEND=noninteractive

# Instala dependências de sistema
RUN apt-get update && apt-get install -y \
    build-essential \
    cmake \
    libboost-all-dev \
    libopenblas-dev \
    liblapack-dev \
    libx11-dev \
    libgtk-3-dev \
    python3-dev \
    && apt-get clean && rm -rf /var/lib/apt/lists/*

# Define diretório de trabalho
WORKDIR /app

# Copia os arquivos para dentro do container
COPY . .

# Instala as dependências do Python
RUN pip install --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# Expõe a porta
EXPOSE 5000

# Comando padrão
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--timeout", "120", "app:app"]
