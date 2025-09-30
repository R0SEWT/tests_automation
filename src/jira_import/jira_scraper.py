import os
import asyncio
import platform
from playwright.async_api import async_playwright, Browser, BrowserContext, Page
from typing import List, Dict, Any, Optional
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

class JiraScraper:
    def __init__(self, base_url: Optional[str] = None):
        # Load configuration from environment
        load_dotenv('config/jira_config.env')

        self.base_url = base_url or os.getenv('JIRA_BASE_URL', 'https://configurar_en_el_jira_config.com')
        self.context: Optional[BrowserContext] = None
        self.page: Optional[Page] = None
        self.playwright = None

    async def __aenter__(self):
        await self._setup_browser()
        return self

    async def __aexit__(self, exc_type, exc_val, exc_tb):
        # No cerrar automáticamente el contexto persistente para mantener la sesión de Chrome abierta
        pass

    async def _setup_browser(self):
        """Configura el navegador con un contexto persistente usando el perfil de Chrome existente."""
        self.playwright = await async_playwright().start()
        
        # Usar el perfil de Chrome existente para reutilizar la sesión
        if platform.system() == "Windows":
            user_data_dir = os.path.expanduser("~/AppData/Local/Google/Chrome/User Data/Default")
        elif platform.system() == "Darwin":  # macOS
            user_data_dir = os.path.expanduser("~/Library/Application Support/Google/Chrome/Default")
        else:  # Linux and others
            user_data_dir = os.path.expanduser("~/.config/google-chrome/Default")
        
        if not os.path.exists(user_data_dir):
            raise FileNotFoundError(f"El directorio de perfil de Chrome no existe: {user_data_dir}")
        
        logger.info(f"Usando perfil de Chrome existente: {user_data_dir}")
        
        self.context = await self.playwright.chromium.launch_persistent_context(
            user_data_dir=user_data_dir,
            headless=False,  # Necesitamos ver el navegador para verificar la sesión
            args=[
                "--no-sandbox",
                "--disable-dev-shm-usage",
                "--disable-background-timer-throttling",
                "--disable-backgrounding-occluded-windows",
                "--disable-renderer-backgrounding"
            ]
        )
        
        self.page = self.context.pages[0] if self.context.pages else await self.context.new_page()
        logger.info("Sesión de Chrome cargada exitosamente")

    async def ensure_authenticated(self):
        """Verifica que la sesión de Chrome tenga acceso a Jira."""
        logger.info("Verificando autenticación en Jira usando la sesión de Chrome existente...")
        
        # Usar la página inicial del contexto
        page = self.page
        
        try:
            # Ir a la página principal de Jira
            logger.info(f"Navegando a {self.base_url}")
            await page.goto(self.base_url)
            
            # Esperar un poco para que cargue
            await asyncio.sleep(3)
            
            # Verificar si estamos en una página que indica que estamos logueados
            current_url = page.url
            logger.info(f"URL actual: {current_url}")
            
            if "login" in current_url.lower() or "auth" in current_url.lower():
                logger.warning("Parece que no estás autenticado en Jira.")
                logger.info("Por favor, inicia sesión manualmente en el navegador que se abrió.")
                logger.info("Esperando 60 segundos para que completes el login...")
                
                # Esperar más tiempo para login manual
                await asyncio.sleep(60)
                
                # Verificar nuevamente
                current_url = page.url
                logger.info(f"URL después de esperar: {current_url}")
                
                if "login" in current_url.lower() or "auth" in current_url.lower():
                    logger.error("Aún no detecto autenticación. El scraper podría fallar.")
                else:
                    logger.info("Autenticación detectada")
            else:
                logger.info("Sesión de Jira ya autenticada")
        except Exception as e:
            logger.error(f"Error durante la verificación de autenticación: {e}")
            raise

    async def get_issue_data(self, issue_key: str) -> Dict[str, str]:
        """Extrae datos de una issue directamente de la página web."""
        # Crear una nueva página para cada issue para evitar problemas de navegación
        page = await self.context.new_page()
        
        try:
            issue_url = f"{self.base_url}/browse/{issue_key}"
            await page.goto(issue_url)
            
            # Esperar a que cargue la página
            await page.wait_for_selector("#summary-val", timeout=20000)
            
            # Extraer título
            title = issue_key  # fallback
            try:
                title_element = await page.query_selector("#summary-val")
                if title_element:
                    title = await title_element.inner_text()
                    title = title.strip()
            except Exception as e:
                logger.warning(f"Could not extract title for {issue_key}: {e}")
            
            # Extraer descripción
            description = ""
            try:
                desc_element = await page.query_selector("#description-val")
                if desc_element:
                    description = await desc_element.inner_text()
                    description = description.strip()
            except Exception as e:
                logger.warning(f"Could not extract description for {issue_key}: {e}")
            
            return {
                "issue_key": issue_key,
                "title": title,
                "link": issue_url,
                "description": description
            }
        finally:
            # Cerrar la página después de usarla
            await page.close()

    async def get_multiple_issues_data(self, issue_keys: List[str]) -> List[Dict[str, str]]:
        """Extrae datos de múltiples issues."""
        await self.ensure_authenticated()
        
        hus = []
        for key in issue_keys:
            try:
                # Verificar si el contexto aún está abierto
                if not self.context:
                    logger.error(f"Browser context closed, cannot extract data for {key}")
                    hus.append({
                        "issue_key": key,
                        "title": key,
                        "link": f"{self.base_url}/browse/{key}",
                        "description": "Browser context was closed"
                    })
                    continue
                    
                hu_data = await self.get_issue_data(key)
                hus.append(hu_data)
                logger.info(f"Extracted data for {key}: {hu_data['title']}")
            except Exception as e:
                logger.error(f"Failed to extract data for {key}: {e}")
                # Agregar un placeholder
                hus.append({
                    "issue_key": key,
                    "title": key,
                    "link": f"{self.base_url}/browse/{key}",
                    "description": f"Error extracting data: {str(e)}"
                })
        return hus

    async def _close_browser(self):
        """Cierra el navegador."""
        if self.context:
            await self.context.close()
        if self.playwright:
            await self.playwright.stop()

    async def cleanup(self):
        """Limpia recursos sin cerrar el contexto persistente."""
        if self.playwright:
            await self.playwright.stop()
            self.playwright = None
