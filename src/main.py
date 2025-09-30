from .jira_import.jira_scraper import JiraScraper
import json
import os
import asyncio
import logging
from dotenv import load_dotenv

logger = logging.getLogger(__name__)

async def main():
    logger.info("Iniciando scraper de Jira")
    # Load configuration
    load_dotenv('config/jira_config.env')
    
    # Get issue keys from environment
    issue_keys_str = os.getenv('ISSUE_KEYS', '')
    issue_keys = [key.strip() for key in issue_keys_str.split(',') if key.strip()]
    
    if not issue_keys:
        logger.warning("No issue keys found in configuration. Using default test keys.")
        issue_keys = ["VLPER-70613"]  # fallback
    
    logger.info(f"Procesando {len(issue_keys)} issues")
    
    scraper = JiraScraper()
    logger.info("Scraper creado")
    
    await scraper._setup_browser()
    logger.info("Browser configurado")
    
    try:
        hu_list = await scraper.get_multiple_issues_data(issue_keys)
        logger.info(f"Extraídos {len(hu_list)} HUs")
        
        # Crear directorio si no existe
        output_dir = os.path.join(os.path.dirname(__file__), '..', 'data', 'raw', 'hus')
        os.makedirs(output_dir, exist_ok=True)
        logger.info(f"Directorio de salida: {output_dir}")
        
        for hu in hu_list:
            # Usar el título como nombre de archivo, limpiando caracteres especiales
            filename = "".join(c for c in hu["title"] if c.isalnum() or c in (' ', '-', '_')).rstrip()
            if not filename:
                filename = "untitled"
            filepath = os.path.join(output_dir, f"{filename}.json")
            
            with open(filepath, 'w', encoding='utf-8') as f:
                json.dump(hu, f, ensure_ascii=False, indent=2)
            
            print(f"Saved HU: {hu['title']} to {filepath}")
    finally:
        # Limpiar recursos pero mantener la sesión de Chrome abierta
        try:
            await scraper.cleanup()
            logger.info("Sesión de Chrome mantenida abierta para futuras ejecuciones")
        except Exception as cleanup_exc:
            logger.error(f"Error durante la limpieza de recursos: {cleanup_exc}", exc_info=True)

if __name__ == "__main__":
    asyncio.run(main())
