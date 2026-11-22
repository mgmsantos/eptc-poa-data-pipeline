from pathlib import Path
import os
from dotenv import load_dotenv

load_dotenv()

BASE_DIR = Path(__file__).resolve().parent.parent
BRONZE_DIR = BASE_DIR / "data" / "bronze"
SILVER_DIR = BASE_DIR / "data" / "silver"

# URLs API
URL_ACIDENTES = "https://dadosabertos.poa.br/dataset/d6cfbe48-ee1f-450f-87f5-9426f6a09328/resource/b56f8123-716a-4893-9348-23945f1ea1b9/download/cat_acidentes.csv"
URL_VITIMAS = "https://dadosabertos.poa.br/dataset/ddc7c320-d52a-469f-831a-921b30feb48c/resource/a46aaaca-8cc1-4082-aa78-ce9f859e2df5/download/cat_vitimas.csv"

DATABASE_URL = os.getenv("DATABASE_URL")