import logging
from pathlib import Path


def configurar_logger(ruta_log: str = "logs/software_fj.log") -> logging.Logger:
    archivo = Path(ruta_log)
    archivo.parent.mkdir(parents=True, exist_ok=True)

    logger = logging.getLogger("SoftwareFJ")
    logger.setLevel(logging.INFO)

    if not logger.handlers:
        formato = logging.Formatter(
            "%(asctime)s | %(levelname)s | %(message)s",
            datefmt="%Y-%m-%d %H:%M:%S",
        )
        file_handler = logging.FileHandler(archivo, mode="a", encoding="utf-8")
        file_handler.setFormatter(formato)
        logger.addHandler(file_handler)

    return logger