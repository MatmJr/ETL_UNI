from src.extract import Extract
from src.load import Load
from pyspark.sql import SparkSession
from pyspark.sql.functions import col, to_date, round
from pyspark.sql.types import DoubleType

extract = Extract()
load = Load()

# Extração
meios_pag = extract.extract_meios_pagamentos(trimestre="20191", n_retornos=100)
dados = meios_pag.get("value", [])

if dados:
    # 1. Inicializar sessão do Spark
    spark = SparkSession.builder \
        .appName("ProcessamentoMeiosPagamento") \
        .master("local[*]") \
        .getOrCreate()

    # 2. Criar DataFrame a partir dos dados da API
    df = spark.createDataFrame(dados)

    # 3. Transformações de Data e Limpeza
    # Converter a string 'datatrimestre' para o tipo Date real do Spark
    df_transformado = df.withColumn("data_trimestre", to_date(col("datatrimestre"), "yyyy-MM-dd")) \
                        .drop("datatrimestre")

    # 4. Ajustar as escalas (Valores estão em Milhões, Quantidades em Milhares)
    colunas_valor = [c for c in df.columns if c.startswith('valor')]
    colunas_qtd = [c for c in df.columns if c.startswith('quantidade')]

    for c in colunas_valor:
        # Transforma o valor na unidade absoluta (Multiplica por 1 Milhão)
        df_transformado = df_transformado.withColumn(c, round(col(c).cast(DoubleType()) * 1000000, 2))

    for c in colunas_qtd:
        # Transforma a quantidade na unidade absoluta (Multiplica por 1 Mil)
        df_transformado = df_transformado.withColumn(c, round(col(c).cast(DoubleType()) * 1000, 2))

    # Exibir schema e os dados processados para validação
    print("\n--- Schema do DataFrame Processado ---")
    df_transformado.printSchema()
    
    print("\n--- Amostra dos Dados Processados ---")
    df_transformado.show(truncate=False)

    # 5. Load: Salvar no banco de dados SQLite local usando a biblioteca nativa do Python
    load.save_spark_to_sqlite_local(
        df=df_transformado,
        db_name="meios_pagamento", 
        table_name="meios_pagamento_trimestral"
    )

    # Pausa o script para manter o servidor Spark UI aberto
    input("\n[Servidor Spark UI Aberto] Acesse http://localhost:4040 no navegador. Pressione ENTER aqui no terminal para encerrar...")

    spark.stop()
else:
    print("A API não retornou dados para o trimestre informado.")