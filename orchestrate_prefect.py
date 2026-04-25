from prefect import flow, task, get_run_logger
from dotenv import load_dotenv
from src.extract import Extract
from src.load import Load

load_dotenv()

@task(retries=3, retry_delay_seconds=10)
def extract(country: str) -> list[dict]:
    logger = get_run_logger()
    extractor = Extract()
    data = extractor.extract_country(country)
    logger.info(f"{len(data)} registros extraídos de {country}")
    return data

@task
def load_data(universities, db_name: str, collection_name: str):
    logger = get_run_logger()
    loader = Load()
    loader.create_sqlite_table(universities, db_name, collection_name)
    logger.info(f"{len(universities)} registros inseridos em {db_name}.{collection_name}")

@flow(name="ETL Universities Prefect", log_prints=True)
def etl_universities_flow(countries: list[str] = ["Brazil", "Italy", "Japan"]):
    for country in countries:
        data = extract(country)
        load_data(data, "universidades", f"universidades_{country.lower()}")

@flow(name="ETL Universities Prefect2", log_prints=True)
def etl_universities_flow_2(countries: list[str] = ["Chile", "Argentina"]):
    for country in countries:
        data = extract(country)
        load_data(data, "universidades", f"universidades_{country.lower()}")

if __name__ == "__main__":
    etl_universities_flow()
    etl_universities_flow_2()
