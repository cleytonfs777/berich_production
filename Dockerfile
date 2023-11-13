FROM python:3.9-slim-buster

# Instala as ferramentas de compilação e o Git
RUN apt-get update && \
    apt-get install -y gcc g++ make git && \
    apt-get clean

# Copia os requisitos do projeto
COPY requirements.txt .

# Atualiza o pip, instala as dependências e instala o iqoptionapi a partir do GitHub
RUN pip install --upgrade pip && \
    pip install --no-cache-dir -r requirements.txt && \
    rm -rf iqoptionapi && \
    git clone https://github.com/iqoptionapi/iqoptionapi.git && \
    cd iqoptionapi && \
    pip install .
