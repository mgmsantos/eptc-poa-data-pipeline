import pandas as pd
from sqlalchemy import create_engine, text
from src.config import DATABASE_URL, SILVER_DIR

def criar_engine():
    if not DATABASE_URL:
        raise ValueError("Variável DATABASE_URL não encontrada no arquivo .env")
    url = DATABASE_URL.replace("postgres://", "postgresql://", 1)
    return create_engine(url)

def carregar_parquet_para_postgres(engine, nome_arquivo: str, nome_tabela: str) -> None:
    caminho = SILVER_DIR / nome_arquivo
    df = pd.read_parquet(caminho)
    print(f"Carregando {len(df)} linhas em silver.{nome_tabela}")
    df.to_sql(
        name = nome_tabela,
        con = engine,
        schema = "silver",
        if_exists = "replace",
        index = False,
        chunksize = 1000,
        method = "multi"
    )
    print(f"Tabela silver.{nome_tabela} carregada com sucesso")

def executar_carga() -> None:
    engine = criar_engine()
    with engine.begin() as conn:
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS silver;"))
        conn.execute(text("CREATE SCHEMA IF NOT EXISTS gold;"))

    carregar_parquet_para_postgres(engine, "acidentes_silver.parquet", "acidentes")
    carregar_parquet_para_postgres(engine, "vitimas_silver.parquet", "vitimas")

if __name__ == "__main__":
    executar_carga()