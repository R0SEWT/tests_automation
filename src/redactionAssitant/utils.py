import logging
from itertools import islice
from typing import Callable, Iterable, List, TypeVar
from pathlib import Path

logger = logging.getLogger(__name__)

def _read_text(path: Path) -> str:
    """Lee y limpia el contenido de un archivo UTF-8."""
    text = path.read_text(encoding="utf-8").strip()
    logger.debug("Leídos %d caracteres de %s", len(text), path.name)
    return text


def get_data(cfg):
    """Carga HUS, Test Cases y Expected Results."""
    paths = {
        "HUS": Path(cfg.input_path("hus")),
        "CPS": Path(cfg.input_path("cps")),
        "EXP": Path(cfg.input_path("exp")),
    }
    logger.debug("Rutas de datos: %s", paths)

    # Validar existencia
    for label, p in paths.items():
        if not p.exists():
            raise FileNotFoundError(f"Archivo {label} no encontrado: {p}")

    # Leer contenido
    hus = _read_text(paths["HUS"])
    cps = _read_text(paths["CPS"])
    exp = _read_text(paths["EXP"])

    if not hus:
        logger.warning("El archivo de HUS está vacío.")
    if not cps:
        logger.warning("El archivo de CPS está vacío.")
    if not exp:
        logger.warning("El archivo de EXP está vacío.")

    return hus, cps, exp

"""Guarda los datos corregidos y el feedback en archivos."""
def save_data(new_cps: str, new_exp: str, feedback: str, cps_out: str, exp_out: str, fb_out: str):
    try:
        with open(cps_out, 'w', encoding='utf-8') as f:
            f.write(new_cps)
            logger.info("Casos de prueba corregidos guardados en %s", cps_out)
            with open(exp_out, 'w', encoding='utf-8') as f:
                f.write(new_exp)
                logger.info("Expected Results corregidos guardados en %s", exp_out)

        with open(fb_out, 'w', encoding='utf-8') as f:
            f.write(feedback)
            logger.info("Feedback guardado en %s", fb_out)

    except Exception as e:
        logger.error("Error al guardar los datos: %s", e)
        raise e
        

T = TypeVar("T")

def procesar_en_batches(
    items: Iterable[T],
    procesador: Callable[[List[T]], str],
    batch_size: int = 10
) -> List[str]:
    """
    Aplica 'procesador' sobre los items en trozos de tamaño batch_size.
    'procesador' recibe la lista de items del batch y debe devolver
    un str con líneas separadas por '\n'. Devuelve la lista concatenada
    de todas esas líneas.
    """
    resultados: List[str] = []
    it = iter(items)
    logger.debug("Procesando %d ítems en batches de tamaño %d", len(items), batch_size)
    if batch_size <= 0:
        logger.error("batch_size debe ser mayor que 0, recibido: %d", batch_size)
        raise ValueError("batch_size debe ser mayor que 0")
    while True:
        batch = list(islice(it, batch_size))
        if not batch:
            break
        logger.info("Procesando batch de %d ítems", len(batch))
        try:
            salida = procesador(batch)
            resultados.extend(salida.splitlines())
        except Exception as e:
            logger.error("Error procesando batch %s: %s", batch, e)
            logger.debug("Detalles del error: %s", e, exc_info=True)
            raise
    logger.info("Procesados %d ítems en total", len(resultados))

    return resultados