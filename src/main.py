from src.extract import executar_extracao
from src.transform import executar_transformacao
from src.load import executar_carga

def executar_pipeline() -> None:
    print("Iniciando pipeline EPTC (Bronze -> Silver)")
    executar_extracao()
    executar_transformacao()
    executar_carga()
    print("Pipeline concluído com sucesso")

if __name__ == "__main__":
    executar_pipeline()