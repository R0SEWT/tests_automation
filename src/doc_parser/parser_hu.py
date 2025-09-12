import os
import pandas
from bs4 import BeautifulSoup
import xmltodict

        ##################################### LOGICA   #####################################

def get_xml_files(path='.'):
    xml_files = []
    for root, dirs, files in os.walk(path):
        for file in files:
            if file.endswith('.xml'):
                xml_files.append(os.path.join(root, file))
    return xml_files

def get_xml_content(xml_file):
    with open(xml_file) as f:
        return f.read()
    
def get_xml_soup(xml_content):
    return BeautifulSoup(xml_content, 'xml')

def get_xml_dict(xml_soup):
    return xmltodict.parse(str(xml_soup))

def get_xml_df(xml_dict):
    return pandas.json_normalize(xml_dict)

def get_hu_dict_from_xml_file(xml_file):
    xml_content = get_xml_content(xml_file)
    xml_soup = get_xml_soup(xml_content)
    xml_dict = get_xml_dict(xml_soup)
    raw_hu_dict = xml_dict["rss"]["channel"]["item"]
    return raw_hu_dict

def get_description_from_raw_hu_dict(raw_hu_dict):
    return raw_hu_dict["description"]

def get_clean_hu_dict(raw_hu_dict):
    clean_hu_dict = {
            "title": raw_hu_dict["title"],
            "link": raw_hu_dict["link"],
            "description": get_description_from_raw_hu_dict(raw_hu_dict),
        }
    return clean_hu_dict

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