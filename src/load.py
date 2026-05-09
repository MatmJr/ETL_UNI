import sqlite3
from dotenv import load_dotenv
import os
from pymongo import MongoClient
from pymongo.server_api import ServerApi

load_dotenv()

DB_USER = os.getenv("DB_USER")
DB_PASSWORD = os.getenv("DB_PASSWORD")


class Load:
    """
    Classe responsável pelo carregamento (Load) dos dados extraídos em bancos de dados relacionais e NoSQL.
    """

    def __init__(self):
        pass

    def create_sqlite_table(self, universities_list, db_name, table_name):
        """
        Cria um banco de dados SQLite local, estrutura uma tabela e insere a lista de universidades.

        Args:
            universities_list (list): Lista de dicionários contendo os dados das universidades extraídos da API.
            db_name (str): Nome do arquivo de banco de dados SQLite que será criado ou conectado (sem o .db).
            table_name (str): Nome da tabela onde os dados serão armazenados.

        Returns:
            None
        """
        # Criar o banco e se concectar nele
        con = sqlite3.connect(f"{db_name}.db")
        c = con.cursor()
        c.execute(f"""
        CREATE TABLE IF NOT EXISTS {table_name}
                (
                id INTERGER PRIMARY KEY,
                name TEXT,
                country TEXT,
                state_province TEXT,
                web_pages TEXT,
                domains TEXT
                );
        """)

        for university in universities_list:
            c.execute(
                f"""INSERT INTO {table_name} (name, country, state_province, web_pages, domains) VALUES (?,?,?,?,?);""",
                (
                    university.get("name"),
                    university.get("country"),
                    university.get("state-province"),
                    ", ".join(university.get("web_pages", [])),
                    ", ".join(university.get("domains", [])),
                ),
            )

        con.commit()
        con.close()

    def insert_in_mongo(self, uni_dict, db_name, collection_name):
        """
        Conecta a um cluster MongoDB Atlas via URI e insere um ou múltiplos documentos em uma coleção.

        Args:
            uni_dict (list/dict): Dados (documentos) a serem inseridos na base de dados.
            db_name (str): Nome do banco de dados no MongoDB Atlas.
            collection_name (str): Nome da coleção onde os documentos serão inseridos.

        Returns:
            None
        """
        uri = f"mongodb+srv://{DB_USER}:{DB_PASSWORD}@cluster0.qm7hugf.mongodb.net/?appName=Cluster0"

        client = MongoClient(uri, server_api=ServerApi("1"))

        db = client[db_name]
        collection = db[collection_name]

        if uni_dict:
            collection.insert_many(uni_dict)

        print(f"Dados inseridos com sucesso na coleção '{collection_name}'!")

    def save_spark_to_sqlite_local(self, df, db_name, table_name, mode="append"):
        """
        Salva um DataFrame do PySpark em um banco SQLite local convertendo para Pandas,
        evitando a necessidade de drivers JDBC e problemas de tipos de dados nativos.

        Args:
            df (DataFrame): O DataFrame do PySpark a ser salvo.
            db_name (str): Nome do arquivo de banco de dados (sem o .db).
            table_name (str): Nome da tabela.
            mode (str): Comportamento de escrita ('append' ou 'replace').
        """
        pandas_mode = "replace" if mode == "overwrite" else mode
        pdf = df.toPandas()
        con = sqlite3.connect(f"{db_name}.db")
        pdf.to_sql(table_name, con, if_exists=pandas_mode, index=False)
        con.close()
        print(f"Dados processados pelo Spark salvos com sucesso na tabela '{table_name}' do SQLite local usando Pandas!")
