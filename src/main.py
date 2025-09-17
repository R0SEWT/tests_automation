from src.doc_parser.parser_hu import HURepository, BasicXMLParserStrategy

def main():
    parser = BasicXMLParserStrategy()
    repo = HURepository(parser)

    hu_list = repo.get_all_hu()
    for hu in hu_list:
        print(hu["title"])

if __name__ == '__main__':
    main()
