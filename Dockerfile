# Usar a imagem oficial do Python como base
FROM python:3.10-slim

# Instalar o Java (JRE) necessário para o motor do PySpark funcionar
RUN apt-get update && \
    apt-get install -y default-jre && \
    apt-get clean && \
    rm -rf /var/lib/apt/lists/*

# Definir a pasta de trabalho dentro do container
WORKDIR /app

# Copiar o arquivo de requisitos e instalar as dependências do Python
# (Adicionamos o pyspark explicitamente caso não esteja no requirements.txt)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt pyspark pandas requests pymongo python-dotenv

# Copiar o restante do código do projeto para dentro do container
COPY . .

# Comando que será executado quando o container iniciar
CMD ["python", "spark_processing.py"]
