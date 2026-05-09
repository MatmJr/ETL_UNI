# Projeto de ETL - Meios de Pagamento (API Banco Central)

Este projeto realiza a extração de dados da API do Banco Central sobre Meios de Pagamento, aplica transformações e ajustes de escala (milhões/milhares) utilizando **PySpark** (ou **Pandas**), e salva os dados processados em um banco de dados **SQLite** local.

Toda a infraestrutura necessária (Python, Java/PySpark, dependências) foi conteinerizada utilizando **Docker**, garantindo que o projeto rode em qualquer ambiente isoladamente e sem necessidade de instalações complexas na máquina do desenvolvedor.

## Pré-requisitos
- [Docker](https://www.docker.com/products/docker-desktop/) instalado e rodando.

---

## 1. Construir a Imagem Docker
Abra o terminal na raiz do projeto (onde está o arquivo `Dockerfile`) e execute o comando abaixo. Isso irá baixar o Python, instalar o Java (necessário para o motor do PySpark) e instalar todas as bibliotecas definidas.

```bash
docker build -t etl-pyspark .
```

## 2. Executar o Processamento com PySpark
Para rodar o script principal (`spark_processing.py`), mapeamos a porta `4040` (para visualizar o painel do Spark) e utilizamos um **Volume** para garantir que o banco de dados `meios_pagamento.db` gerado não seja perdido ao final do processo.

Se estiver usando **PowerShell** (padrão no VS Code / Windows moderno):
```powershell
docker run --rm -it -p 4040:4040 -v "${PWD}:/app" etl-pyspark
```

Se estiver usando o **CMD** (Prompt de Comando antigo):
```cmd
docker run --rm -it -p 4040:4040 -v "%cd%:/app" etl-pyspark
```

*Dica: Após a execução, o script ficará pausado. Você poderá acessar `http://localhost:4040` no seu navegador para explorar o Spark UI. Pressione `ENTER` no terminal quando quiser encerrar o contêiner.*

## 3. Executar o Processamento com Pandas (Alternativo)
Caso queira testar a versão do script feita utilizando a engine do Pandas (`pandas_processing.py`):

```powershell
# PowerShell
docker run --rm -it -v "${PWD}:/app" etl-pyspark python pandas_processing.py
```

## 4. Acessar o Console Interativo do PySpark (Opcional)
Se você quiser abrir o terminal (Shell) interativo do PySpark para fazer análises manuais diretamente com o motor do Spark:

```bash
docker run --rm -it etl-pyspark pyspark
```