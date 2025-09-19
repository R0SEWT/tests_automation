import logging
from src.redactionAssitant import builder as b
from concurrent.futures import ThreadPoolExecutor
import re 
from openai import OpenAI  


class Processor:
    """
    Procesador inteligente de Historias de Usuario, Casos de Prueba y Resultados Esperados.
    
    Esta clase es el núcleo del sistema de corrección automática. Utiliza IA (DeepSeek) 
    para procesar y mejorar la calidad de la documentación de QA mediante:
    
    - Corrección ortográfica y gramatical
    - Mejora de redacción manteniendo el contexto técnico
    - Procesamiento en lotes para eficiencia
    - Validación de integridad de datos
    - Generación de feedback detallado
    
    Attributes:
        cfg: Objeto de configuración con rutas y parámetros del sistema
        logger: Logger para trazabilidad del proceso
        client: Cliente OpenAI configurado para DeepSeek API
        builder: Constructor de prompts especializados para IA
        batch_size: Tamaño de lote para procesamiento concurrente (default: 20)
    
    Example:
        >>> config = Config()
        >>> processor = Processor(config, "api_key_here")
        >>> cps_corregidos, feedback = processor.cps_corregidas(hu_text, cps_text)
    """

    def __init__(self, cfg, api_key):
        self.cfg = cfg
        self.logger = logging.getLogger(__name__)
        
        if not api_key:
            raise ValueError("API key is required")
            
        try:
            if cfg.provider == "deepseek":
                self.client = OpenAI(api_key=api_key, base_url="https://api.deepseek.com")
            else:  # openai
                self.client = OpenAI(api_key=api_key)
        except Exception as e:
            self.logger.error("Failed to initialize OpenAI client: %s", e)
            raise
            
        self.builder = b.Builder(self.client, cfg.provider)
        self.batch_size = cfg.batch_size
        self.logger.info("Processor initialized successfully with batch_size=%d", self.batch_size)

    def cps_corregidas(self, hu: str, cps: str) -> tuple[str, str]:
        """
        Corrige casos de prueba utilizando IA, manteniendo el contexto de la historia de usuario.
        
        Procesa los casos de prueba en lotes concurrentes para optimizar el rendimiento,
        aplicando correcciones ortográficas y de redacción mientras preserva el significado
        técnico y la estructura original.
        
        Args:
            hu (str): Historia de usuario que proporciona contexto para las correcciones
            cps (str): Casos de prueba separados por líneas, en formato texto plano
            
        Returns:
            tuple[str, str]: Tupla con (casos_corregidos, feedback_detallado)
                - casos_corregidos: Casos de prueba con correcciones aplicadas
                - feedback_detallado: Resumen de cambios realizados por la IA
                
        Raises:
            ValueError: Si la cantidad de casos corregidos no coincide con los originales
            
        Example:
            >>> hu = "Como usuario quiero poder login al sistema"
            >>> cps = "USRNM001 Validar login con credenciales validas"
            >>> corregidos, feedback = processor.cps_corregidas(hu, cps)
        """
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
    
    def exp_corregidos(self, hu: str, cps: str, exp: str) -> tuple[str, str]:
        """
        Corrige resultados esperados utilizando IA y contexto de HU y casos de prueba.
        
        Procesa los resultados esperados en lotes, aplicando correcciones ortográficas,
        mejorando la redacción y asegurando que estén en tiempo presente. Mantiene
        la correspondencia 1:1 con los casos de prueba.
        
        Args:
            hu (str): Historia de usuario para contexto
            cps (str): Casos de prueba corregidos como referencia
            exp (str): Resultados esperados originales a corregir
            
        Returns:
            tuple[str, str]: Tupla con (resultados_corregidos, feedback_detallado)
                - resultados_corregidos: Expected Results mejorados
                - feedback_detallado: Resumen de cambios realizados
                
        Raises:
            ValueError: Si no hay correspondencia entre CPS y EXP
            
        Example:
            >>> exp_corregidos, feedback = processor.exp_corregidos(hu, cps, exp)
        """
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

        cps_list = preprocess_exp_or_cps(cps)
        exp_list = preprocess_exp_or_cps(exp)

        # Procesar en batches
        if len(cps_list) != len(exp_list):
            self.logger.warning("Los casos de prueba y resultados esperados no tienen la misma longitud.")
            self.logger.warning("número de casos de prueba: %d", len(cps_list))
            self.logger.warning("número de resultados esperados: %d", len(exp_list))
            self.logger.warning("CPS: %s", cps)
            self.logger.warning("EXP: %s", exp)
            return "",""

        if not cps_list:
            return "",""

        clean_pairs = [f"{cp} | {ex}" for cp, ex in zip(cps_list, exp_list)]

        batches = [clean_pairs[i : i + self.batch_size] for i in range(0, len(clean_pairs), self.batch_size)]

        results = []
        with ThreadPoolExecutor(max_workers=4) as executor:
            for batch_out in executor.map(lambda batch: self.builder.corregir_expect_result("\n".join(batch)), batches):
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
    """
    Combina casos de prueba con sus resultados esperados correspondientes.
    
    Esta función crea pares CPS-EXP manteniendo la correspondencia línea por línea,
    lo cual es esencial para que la IA pueda procesar ambos elementos en contexto
    y mantener la coherencia entre el caso de prueba y su resultado esperado.
    
    Args:
        cps (str): Casos de prueba separados por líneas
        exp (str): Resultados esperados separados por líneas
        
    Returns:
        list[str]: Lista de strings con formato "caso_prueba | resultado_esperado"
        
    Example:
        >>> cps = "USRNM001 Validar login\\nUSRNM002 Validar logout"
        >>> exp = "Sistema permite acceso\\nSistema cierra sesion"
        >>> result = cps_with_exp(cps, exp)
        >>> print(result[0])  # "USRNM001 Validar login | Sistema permite acceso"
    """
    if not cps or not exp:
        return []
    
    # Separar por líneas y limpiar espacios
    cps_lines = [line.strip() for line in cps.splitlines() if line.strip()]
    exp_lines = [line.strip() for line in exp.splitlines() if line.strip()]
    
    # Combinar en una lista usando list comprehension para mejor rendimiento
    return [f"{cp} | {ex}" for cp, ex in zip(cps_lines, exp_lines)]


def preprocess_exp_or_cps(cps: str) -> list[str]:
    """
    Preprocesa casos de prueba o resultados esperados para corrección por IA.
    
    Limpia y estructura el texto de entrada separándolo por líneas y removiendo
    espacios innecesarios. Es un paso esencial antes del procesamiento por lotes.
    
    Args:
        cps (str): Texto con casos de prueba o resultados esperados
        
    Returns:
        list[str]: Lista de líneas limpias listas para procesamiento
        
    Example:
        >>> text = "  USRNM001 Caso 1  \\n\\n  USRNM002 Caso 2  \\n"
        >>> result = preprocess_exp_or_cps(text)
        >>> print(result)  # ["USRNM001 Caso 1", "USRNM002 Caso 2"]
    """
    if not cps:
        return []
    # Separar por líneas y limpiar espacios
    return [line.strip() for line in cps.splitlines() if line.strip()]
    
    