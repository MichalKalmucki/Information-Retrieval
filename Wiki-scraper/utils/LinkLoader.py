from io import open

class LinkLoader:
    def __init__(self, file):
        self.file = file

    def load(self):
        links = []
        with open(self.file, encoding='utf-8') as f:
            for line in f:
                links.append(line.strip())

        return links
    
if __name__ == '__main__':
    loader = LinkLoader('utils/links.txt')
    links = loader.load()
    print(links)