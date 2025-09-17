"""
Auto-redactor de HUS y Expected Results para QA.

Flujo:
  1. Carga configuración
  2. Obtiene datos (HUS, casos, expected results)
  3. Procesa correcciones y genera feedback
  4. Guarda los resultados 
"""
import sys
import logging
from src.redactionAssitant.config import Config
from src.redactionAssitant.utils import get_data, save_data
from src.redactionAssitant.processor import Processor


def process_flow() -> None:
    """Carga datos, corrige CPS/EXP y guarda todo."""
    cfg = Config()

    # 1) Leer datos
    hus, cps, exp = get_data(cfg)

    # 2) Instanciar procesador
    proc = Processor(cfg, cfg.API_KEY)

    # 3) Corregir y obtener feedback
    new_cps, resume_fb = proc.cps_corregidas(hus, cps)
    new_exp = proc.exp_corregidos(hus, cps, exp)
    #sume_fb = proc.resume_feedback(fb_cps, fb_exp)
    new_exp, exp_fb = proc.exp_corregidos(hus, new_cps, exp)
    
    logging.info("Feedback resumido:\n%s", resume_fb)

    resume_fb += "\n\n" + exp_fb
    # 4) Guardar salidas
    cps_out, exp_out, fb_out = cfg.all_output_paths()
    save_data(new_cps, new_exp, resume_fb, cps_out, exp_out, fb_out)


def main() -> int:
    """Punto de entrada: configura logging y lanza el flujo."""
    logging.basicConfig(
        level=logging.INFO,
        format="%(asctime)s %(levelname)s %(message)s",
        datefmt="%H:%M:%S"
    )
    try:
        process_flow()
        logging.info("Proceso finalizado con éxito.")
        return 0
    except Exception:
        logging.exception("Se produjo un error en el flujo principal.")
        return 1


if __name__ == "__main__":
    sys.exit(main())
