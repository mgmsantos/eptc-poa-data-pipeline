import pandas as pd
from src.config import BRONZE_DIR, SILVER_DIR


def _padronizar_base(df_input: pd.DataFrame) -> pd.DataFrame:
    """Padroniza nomes de colunas, remove espaços extras e trata campos de data/hora."""
    df = df_input.copy()

    df.columns = df.columns.str.strip().str.lower().str.replace(" ", "_")

    colunas_texto = df.select_dtypes(include=["object", "string"]).columns
    for col in colunas_texto:
        df[col] = df[col].str.strip()

    for col_data in ["data_extracao", "data"]:
        if col_data in df.columns:
            df[col_data] = pd.to_datetime(df[col_data], errors="coerce")

    if "hora" in df.columns:
        df["hora"] = pd.to_datetime(
            df["hora"], format="%H:%M:%S.%f", errors="coerce"
        ).dt.strftime("%H:%M")

    if "data" in df.columns:
        df["dia_semana"] = df["data"].dt.day_name()

    if "dia_sem" in df.columns:
        df = df.drop(columns=["dia_sem"])

    if {"latitude", "longitude"}.issubset(df.columns):
        df["valido_para_mapa"] = df["latitude"].notna() & df["longitude"].notna()

    return df


def _converter_para_int64(df: pd.DataFrame, colunas: list[str]) -> pd.DataFrame:
    """Converte colunas numéricas (mesmo com vírgula decimal) para Int64 de forma segura."""
    for col in colunas:
        if col in df.columns:
            serie = df[col].astype(str).str.replace(",", ".", regex=False)
            df[col] = pd.to_numeric(serie, errors="coerce").astype("Int64")
    return df


def _validar_qualidade(df: pd.DataFrame, nome_base: str) -> None:
    """Trava de segurança antes de gravar a camada Silver."""
    if df.empty:
        raise ValueError(f"CRÍTICO: A base '{nome_base}' ficou vazia após a limpeza.")
    if "id_acidente" not in df.columns:
        raise ValueError(f"CRÍTICO: Coluna 'id_acidente' ausente em '{nome_base}'.")
    taxa_nulos_id = df["id_acidente"].isna().mean()
    if taxa_nulos_id > 0.05:
        raise ValueError(
            f"CRÍTICO: {taxa_nulos_id:.1%} dos IDs estão nulos em '{nome_base}'."
        )


def limpar_base_acidentes(df_input: pd.DataFrame) -> pd.DataFrame:
    """Aplica as regras de limpeza para a tabela de acidentes."""
    df = _padronizar_base(df_input)

    if "idacidente" in df.columns:
        df = _converter_para_int64(df, ["idacidente"])
        coluna_id = df.pop("idacidente")
        df.insert(0, "id_acidente", coluna_id)

    df = _converter_para_int64(df, ["predial1", "queda_arr"])

    df = df.rename(
        columns={
            "auto": "carro_passeio",
            "onibus_urb": "onibus_urbano",
            "onibus_met": "onibus_metropolitano",
            "onibus_int": "onibus_interurbano",
            "outro": "outro_veiculo",
        }
    )

    if "consorcio" in df.columns:
        df["consorcio"] = df["consorcio"].fillna("NÃO SE APLICA")

    return df


def limpar_base_vitimas(df_input: pd.DataFrame) -> pd.DataFrame:
    """Aplica as regras de limpeza para a tabela de vítimas."""
    df = _padronizar_base(df_input)

    df = df.rename(
        columns={
            "id": "id_vitima",
            "idacidente": "id_acidente",
            "tipo_acid": "tipo_acidente",
            "sit_vitima": "condicao_vitima",
            "auto": "carro_passeio",
            "onibus_urb": "onibus_urbano",
            "onibus_met": "onibus_metropolitano",
            "onibus_int": "onibus_interurbano",
            "outro": "outro_veiculo",
            "fx_et": "faixa_etaria",
            "tipo_veic": "tipo_veiculo",
            "periododia": "periodo_dia",
        }
    )

    sujeiras = ["nan", "none", "nao informado", "naoinformado", "nao cadastrado"]
    colunas_sujeira = [
        "sexo",
        "condicao_vitima",
        "tipo_acidente",
        "periodo_dia",
        "tipo_veiculo",
    ]
    for col in colunas_sujeira:
        if col in df.columns:
            df[col] = (
                df[col]
                .fillna("não informado")
                .astype(str)
                .str.lower()
                .replace(sujeiras, "não informado")
            )

    col_capitalize = [
        "sexo",
        "condicao_vitima",
        "regiao",
        "tipo_acidente",
        "periodo_dia",
        "tipo_veiculo",
    ]
    for col in col_capitalize:
        if col in df.columns:
            df[col] = df[col].str.capitalize()

    df = _converter_para_int64(df, ["id_acidente", "idade", "predial1"])

    if "consorcio" in df.columns:
        df["consorcio"] = df["consorcio"].fillna("NÃO SE APLICA")

    return df


def executar_transformacao() -> None:
    """Lê os CSVs da camada Bronze, limpa e salva em Parquet na camada Silver."""
    SILVER_DIR.mkdir(parents=True, exist_ok=True)

    print("Transformando base de acidentes...")
    df_acidentes_raw = pd.read_csv(
        BRONZE_DIR / "cat_acidentes.csv", sep=";", low_memory=False
    )
    df_acidentes_silver = limpar_base_acidentes(df_acidentes_raw)
    _validar_qualidade(df_acidentes_silver, "acidentes")
    df_acidentes_silver.to_parquet(
        SILVER_DIR / "acidentes_silver.parquet", index=False
    )
    print(f"Acidentes Silver salvo: {len(df_acidentes_silver)} linhas.")

    print("Transformando base de vítimas...")
    df_vitimas_raw = pd.read_csv(
        BRONZE_DIR / "cat_vitimas.csv", sep=";", low_memory=False
    )
    df_vitimas_silver = limpar_base_vitimas(df_vitimas_raw)
    _validar_qualidade(df_vitimas_silver, "vitimas")
    df_vitimas_silver.to_parquet(
        SILVER_DIR / "vitimas_silver.parquet", index=False
    )
    print(f"Vítimas Silver salvo: {len(df_vitimas_silver)} linhas.")


if __name__ == "__main__":
    executar_transformacao()