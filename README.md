# ETL Meios de Pagamento — Banco Central + IA

Projeto educacional que extrai dados de Meios de Pagamento da API do Banco Central, processa com **PySpark**, persiste em **SQLite/MongoDB** e expõe os dados para consulta em linguagem natural via **Streamlit + OpenAI + MCP**.

---

## Arquitetura

```
API Banco Central (OLINDA)
        │
   ┌────┴────────────────────┐
   │                         │
   ▼                         ▼
src/extract.py          src/extract.py
   │                         │
   ▼                         ▼
spark_processing.py     mcp_server.py
   │                    (FastMCP server)
   ▼                         │
src/load.py                  ▼
   │                       app.py
   ▼                  (Streamlit + OpenAI)
meios_pagamento.db
```

---

## Estrutura do Projeto

```
ETL_UNI/
├── src/
│   ├── extract.py          # Classe Extract — consulta API do Banco Central
│   └── load.py             # Classe Load — salva em SQLite ou MongoDB
├── app.py                  # Interface web (Streamlit) com chat via OpenAI
├── mcp_server.py           # Servidor MCP que expõe ferramentas de consulta
├── spark_processing.py     # Pipeline ETL principal com PySpark
├── main.py                 # Script legado (referência)
├── Dockerfile              # Imagem com Python 3.10 + Java (para PySpark)
├── requirements.txt        # Dependências Python
├── .env.example            # Template de variáveis de ambiente
└── meios_pagamento.db      # Banco SQLite gerado após execução do ETL
```

---

## Pré-requisitos

- Python 3.10+
- [Docker](https://www.docker.com/products/docker-desktop/) (para rodar o PySpark em contêiner)
- Conta OpenAI com chave de API (para o chat com IA)
- MongoDB Atlas (opcional, para carga em nuvem)

---

## Configuração

Copie `.env.example` para `.env` e preencha as variáveis:

```env
DB_USER=seu_usuario_mongodb
DB_PASSWORD=sua_senha_mongodb
OPENAI_API_KEY=sk-...
```

---

## 1. Pipeline ETL (PySpark via Docker)

### Construir a imagem

```powershell
docker build -t etl-pyspark .
```

### Executar o processamento

**PowerShell:**
```powershell
docker run --rm -it -p 4040:4040 -v "${PWD}:/app" etl-pyspark
```

**CMD:**
```cmd
docker run --rm -it -p 4040:4040 -v "%cd%:/app" etl-pyspark
```

Após a execução, acesse `http://localhost:4040` para visualizar o Spark UI. Pressione `ENTER` no terminal para encerrar o contêiner.

O script `spark_processing.py` realiza as seguintes etapas:
1. Extrai dados trimestrais a partir do 1º trimestre de 2019
2. Converte a coluna de data para o tipo `DateType` do Spark
3. Escala os valores monetários (x 1.000.000) e quantidades (x 1.000)
4. Salva o resultado em `meios_pagamento.db`

### Shell interativo do PySpark (opcional)

```bash
docker run --rm -it etl-pyspark pyspark
```

---

## 2. Servidor MCP

O `mcp_server.py` expõe uma ferramenta `buscar_meios_pagamento` via protocolo MCP, permitindo que agentes de IA consultem os dados do Banco Central por trimestre.

```bash
python mcp_server.py
```

---

## 3. Interface de Chat com IA (Streamlit)

O `app.py` é uma interface conversacional que permite consultar os dados de meios de pagamento em linguagem natural, usando o modelo GPT-4o-mini da OpenAI com integração ao servidor MCP.

```bash
streamlit run app.py
```

Acesse `http://localhost:8501` no navegador. Exemplos de perguntas:

- *"Qual o volume de transações Pix no 1º trimestre de 2024?"*
- *"Compare os meios de pagamento do 3T2023 com o 3T2022."*

---

## Dependências

```
requests
python-dotenv
pymongo
pyspark
pandas
streamlit
openai
fastmcp
```

Instalar localmente:

```bash
pip install -r requirements.txt
```

---

## Fonte dos Dados

API pública do Banco Central do Brasil — [OLINDA](https://olinda.bcb.gov.br/olinda/servico/MPV_DadosAbertos/versao/v1/odata/MeiosDePagamentosPorPeriodo)
