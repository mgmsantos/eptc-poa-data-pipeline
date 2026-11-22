from pathlib import Path
import requests
from src.config import BRONZE_DIR, URL_ACIDENTES, URL_VITIMAS

def baixar_csv(url: str, destino: Path) -> Path:
    """Baixa um arquivo csv da API e salva no caminho especificado"""
    destino.parent.mkdir(parents = True, exist_ok = True)
    print(f"Baixando {destino.name}...")
    resposta = requests.get(url, timeout = 300)
    resposta.raise_for_status()
    destino.write_bytes(resposta.content)
    print(f"Salvo com sucesso em {destino}")
    return destino

def executar_extracao() -> None:
    baixar_csv(URL_ACIDENTES, BRONZE_DIR / "cat_acidentes.csv")
    baixar_csv(URL_VITIMAS, BRONZE_DIR  / "cat_vitimas.csv")

if __name__ == "__main__":
    executar_extracao()