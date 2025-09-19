from openai import OpenAI  
import logging
from typing import List, Union

class Builder:
    """Constructor de casos de prueba, expect results y correcciones ortográficas."""

    def __init__(self, client: OpenAI, provider: str = "deepseek"):
        self.client = client
        if provider == "deepseek":
            self.model = "deepseek-chat"
        elif provider == "openai":
            self.model = "gpt-4"  # or whatever default OpenAI model
        else:
            raise ValueError(f"Unsupported provider: {provider}")
        self.logger = logging.getLogger(__name__)

    def corregir_ortografia(self, hu, cps: List[str]) -> str:
        if not hu or not cps:
            self.logger.warning("Historia de usuario o casos de prueba vacíos.")

        prompt = (
            "Eres un experto en QA.\n\n"
            "Objetivos:\n"
            " - Corregir *solo* errores ortográficos y gramaticales leves.\n"
            " - Mantener numeración y significado funcional.\n"
            " - **Para cada caso de prueba recibido, devuelve exactamente una línea de salida.**\n"
            "   Si un caso no necesita corrección, repítelo tal cual.\n\n"
            "Formato de salida:\n"
            " OBS[n]: <descripción del cambio, “sin cambios” o duplicado>, CP: <caso corregido o original>\n\n"
            f"Historia de Usuario:\n{hu}\n\n"
            "Casos de prueba:\n"
            + "\n".join(cps) +
            "\n\nFin de instrucción."
        )
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en pruebas de software."},
                    {"role": "user", "content": prompt},
                ],
                stream=False
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error("Error al llamar a la API: %s", e)
            return f"Error al corregir ortografía: {str(e)}"

    def obtener_feedback(self, obs_for_cps: str):
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en pruebas de software. Tu tarea es proporcionar un feedback claro y conciso sobre las correcciones realizadas."},
                    {"role": "user", "content": f"Aquí tienes las observaciones de corrección:\n{obs_for_cps}\n\nDevuelve únicamente el feedback en texto plano, sin formato adicional."}
                ],
                stream=False
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error("Error al obtener feedback: %s", e)
            return f"Error: {str(e)}"

    def corregir_expect_result(self, cps_with_expectResult: Union[str, List[str]]):
        if isinstance(cps_with_expectResult, list):
            # Sanitize each element to remove embedded newlines
            sanitized_elements = [elem.replace('\n', ' ') if isinstance(elem, str) else str(elem) for elem in cps_with_expectResult]
            cps_with_expectResult = "\n".join(sanitized_elements)
        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "Eres un experto en pruebas de software. Tu tarea es corregir la ortografía y mejorar la redacción de los Expected Results, manteniendo el sentido original y usando tiempo presente."},
                    {"role": "user", "content": f"Aquí tienes los pares Caso de Prueba + Expected Result:\n{cps_with_expectResult}"},
                    {"role": "user", "content": (
                        "Devuelve únicamente los Expected Results corregidos en tiempo presente, mejora la redacción y corrige la ortografía, usa mayúscula inicial. "
                        "En texto plano y con este formato:\n"
                        "ExpRes1: <texto corregido 1>\n"
                        "ExpRes2: <texto corregido 2>\n"
                        "...\n\n"
                        "Al final, incluye un listado de observaciones de corrección con este formato:\n"
                        "OBS: <observación 1>\n"
                        "OBS: <observación 2>\n"
                        "No uses comillas ni ningún otro formato adicional."
                    )}
                ],
                stream=False
            )
            return response.choices[0].message.content.strip()
        except Exception as e:
            self.logger.error("Error al corregir expected results: %s", e)
            return f"Error: {str(e)}"
