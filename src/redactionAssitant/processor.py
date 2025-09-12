import logging
# eliminar import prompts
import openai 
from src.redactionAssitant import builder as b
from concurrent.futures import ThreadPoolExecutor, as_completed
import re 
from openai import OpenAI  


class Processor:
    """Procesador de HUS, Test Cases y Expected Results."""

    def __init__(self, cfg, api_key):
        self.cfg     = cfg
        self.logger  = logging.getLogger(__name__)
        self.client = OpenAI(api_key= api_key, base_url="https://api.deepseek.com")
        # openai.api_key = api_key
        #self.client = openai

        self.builder = b.Builder(self.client)
        self.batch_size = 20
        #self.logger.info("Procesador inicializado con API Key: %s", api_key)

    def cps_corregidas(self, hu: str, cps:str) -> str:
        """Corrige los casos de prueba (CPS) relacionados con una historia de usuario (HU)."""
        cod_hu = self.cfg.code_hu
        self.logger.info("Corrigiendo casos de prueba para la HU: %s", cod_hu)
        
        if not hu or not cps:
            self.logger.warning("Historia de usuario o casos de prueba vacíos.")
            return "", ""
        
        # Procesar en batches
        cps_list = preprocess_exp_or_cps(cps)
        if not cps_list:
            return "", ""
        
        batches = [cps_list[i : i + self.batch_size] for i in range(0, len(cps_list), self.batch_size)]

        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            for batch_out in executor.map(lambda b: self.builder.corregir_ortografia(hu, b), batches):
                results.extend(batch_out.splitlines())
        self.logger.info("Corrección de casos de prueba completada. Procesando resultados...")
        sep_obs = "OBS"
        sep_cps = cod_hu
        
        obs   = "\n".join([l for l in results if l.startswith(sep_obs)])
        # Filtrar casos de prueba corregidos
        self.logger.info("Filtrando casos de prueba corregidos...")
        # regex extraer desde sep_cps hasta el final de la línea o hasta sep_obs
        regex_cps = f"{sep_cps}.*?(?={sep_obs}|$)"
        cps_r = [re.search(regex_cps, l).group(0) for l in results if re.search(regex_cps, l)]

        feedback = self.builder.obtener_feedback(obs)

        if len(cps_r) != len(cps_list):
            self.logger.warning("La cantidad de casos de prueba corregidos no coincide con la original.")
            self.logger.warning("número de casos de prueba originales: %d", len(cps_list))
            self.logger.warning("número de casos de prueba corregidos: %d", len(cps_r))
            self.logger.warning("CPS original: %s", cps)
            self.logger.warning("CPS corregidos: %s", "\n".join(cps_r))
            return "",""

        if not cps_r:
            self.logger.warning("No se encontraron casos de prueba corregidos.")
            return "",""
        else:
            self.logger.info("Se corrigieron %d Casos de prueba corregidos correctamente.", len(cps_r))

        return "\n".join(cps_r), feedback
    
    def exp_corregidos(self, hu: str, cps: str, exp: str) -> str:
        """Corrige los resultados esperados (EXP) relacionados con una historia de usuario (HU) y casos de prueba (CPS)."""
        cod_hu = self.cfg.code_hu
        self.logger.info("Corrigiendo resultados esperados para la HU: %s", cod_hu)
        

        safe_quit = False
        if not hu:
            self.logger.warning("Historia de usuario vacía.")
            safe_quit = True

        if not cps:
            self.logger.warning("Casos de prueba vacíos.")
            safe_quit = True

        if not exp:
            self.logger.warning("Resultados esperados vacíos.")
            safe_quit = True

        if safe_quit:
            return "", ""

        # Procesar en batches
        if len(cps.splitlines()) != len(exp.splitlines()):
            self.logger.warning("Los casos de prueba y resultados esperados no tienen la misma longitud.")
            self.logger.warning("número de casos de prueba: %d", len(cps.splitlines()))
            self.logger.warning("número de resultados esperados: %d", len(exp.splitlines()))
            self.logger.warning("CPS: %s", cps)
            self.logger.warning("EXP: %s", exp)
            return "",""
        else:
            exp_list = cps_with_exp(cps, exp)

        if not exp_list:
            return "",""
        

        batches = [exp_list[i : i + self.batch_size] for i in range(0, len(exp_list), self.batch_size)]

        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            for batch_out in executor.map(self.builder.corregir_expect_result, batches):
                results.extend(batch_out.splitlines())

        sep_obs = "OBS"
        sep_exp = "ExpRes"
        
        obs_str   = "\n".join([l.split(":",1)[-1].strip() for l in results if l.startswith(sep_obs)])
        exp_str   = "\n".join([l.split(":",1)[-1].strip() for l in results if l.startswith(sep_exp)])

        # Filtrar resultados esperados corregidos
        self.logger.info("Filtrando resultados esperados corregidos...")
        # regex extraer desde sep_exp hasta el final de la línea o hasta sep_obs
        #regex_exp = f"{sep_exp}.*?(?={sep_obs}|$)"
        #exp_r = [re.search(regex_exp, l).group(0) for l in results if re.search(regex_exp, l)]

        feedback = self.builder.obtener_feedback(obs_str)
        return exp_str, feedback


def cps_with_exp(cps: str, exp: str) -> list[str]:
    """Combina casos de prueba (CPS) y resultados esperados (EXP) en una lista."""
    if not cps or not exp:
        return []
    
    # Separar por líneas y limpiar espacios
    cps_lines = [line.strip() for line in cps.splitlines() if line.strip()]
    exp_lines = [line.strip() for line in exp.splitlines() if line.strip()]
    
    # Combinar en una lista
    combined = []
    for cp, ex in zip(cps_lines, exp_lines):
        combined.append(f"{cp} | {ex}")
    
    return combined


def preprocess_exp_or_cps(cps: str) -> list[str]:
    """Preprocesa los cps y exp para la corrección."""
    if not cps:
        return ""
    # Separar por líneas y limpiar espacios
    return [line.strip() for line in cps.splitlines() if line.strip()]
    
    