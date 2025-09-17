import os
import pandas as pd
from bs4 import BeautifulSoup
import xmltodict
from pathlib import Path
from typing import List, Dict, Any
import logging

logger = logging.getLogger(__name__)

##################################### LOGIC #####################################

def get_xml_files(path: str = '.') -> List[str]:
    """Obtiene todos los archivos XML en un directorio."""
    xml_files = []
    path_obj = Path(path)
    
    if not path_obj.exists():
        logger.warning(f"El directorio {path} no existe")
        return xml_files
        
    for xml_file in path_obj.rglob('*.xml'):
        xml_files.append(str(xml_file))
    
    logger.info(f"Encontrados {len(xml_files)} archivos XML en {path}")
    return xml_files

def get_xml_content(xml_file: str) -> str:
    """Lee el contenido de un archivo XML."""
    try:
        with open(xml_file, 'r', encoding='utf-8') as f:
            return f.read()
    except Exception as e:
        logger.error(f"Error leyendo archivo {xml_file}: {e}")
        raise

def get_xml_soup(xml_content: str) -> BeautifulSoup:
    """Convierte contenido XML a BeautifulSoup."""
    return BeautifulSoup(xml_content, 'xml')

def get_xml_dict(xml_soup: BeautifulSoup) -> Dict[str, Any]:
    """Convierte BeautifulSoup a diccionario."""
    return xmltodict.parse(str(xml_soup))

def get_xml_df(xml_dict: Dict[str, Any]) -> pd.DataFrame:
    """Convierte diccionario XML a DataFrame."""
    return pd.json_normalize(xml_dict)

def get_hu_dict_from_xml_file(xml_file: str) -> Dict[str, Any]:
    """Extrae diccionario de historia de usuario desde archivo XML."""
    xml_content = get_xml_content(xml_file)
    xml_soup = get_xml_soup(xml_content)
    xml_dict = get_xml_dict(xml_soup)
    
    try:
        raw_hu_dict = xml_dict["rss"]["channel"]["item"]
        return raw_hu_dict
    except KeyError as e:
        logger.error(f"Estructura XML inesperada en {xml_file}: {e}")
        raise

def get_description_from_raw_hu_dict(raw_hu_dict: Dict[str, Any]) -> str:
    """Extrae descripción del diccionario raw de HU."""
    return raw_hu_dict.get("description", "")

def get_clean_hu_dict(raw_hu_dict: Dict[str, Any]) -> Dict[str, str]:
    """Limpia y estructura el diccionario de HU."""
    return {
        "title": raw_hu_dict.get("title", ""),
        "link": raw_hu_dict.get("link", ""),
        "description": get_description_from_raw_hu_dict(raw_hu_dict),
    }

############################ INTERFAZ ########################################

from abc import ABC, abstractmethod

class XMLParserStrategy(ABC):
    @abstractmethod
    def parse(self, xml_file):
        pass

class BasicXMLParserStrategy(XMLParserStrategy):
    def parse(self, xml_file):
        xml_content = get_xml_content(xml_file)
        xml_soup = get_xml_soup(xml_content)
        xml_dict = get_xml_dict(xml_soup)
        return xml_dict

class HURepository:
    def __init__(self, parser_strategy: XMLParserStrategy):
        self.parser_strategy = parser_strategy

    def get_all_hu(self, path='.'):
        xml_files = get_xml_files(path)
        hu_list = []
        for file in xml_files:
            raw_hu_dict = self.parser_strategy.parse(file)
            clean = get_clean_hu_dict(raw_hu_dict["rss"]["channel"]["item"])
            hu_list.append(clean)
        return hu_list

def main():
    parser = BasicXMLParserStrategy()
    repo = HURepository(parser)
    hu_list = repo.get_all_hu()
    print(hu_list)

if __name__ == '__main__':
    main()