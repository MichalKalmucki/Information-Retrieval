from utils.LinkLoader import LinkLoader
from utils.Scraper import WikiScraper
from utils.Ranker import DocumentRanker
import os

def get_ranking(link, scraper, ranker):
        content = scraper.get_content(link)
        tokens = scraper.tokenize_text(content)
        content = ' '.join(tokens)

        return ranker.get_similar(content)

def main():
    scraper = WikiScraper()
    ranker = DocumentRanker()
    if not os.path.exists('data.csv'):
        print("getting links from wikipedia, this might take a while...")
        scraper.get_n_random()
        scraper.save_to_db()
    loader = LinkLoader('links.txt')
    links = loader.load()
    for link in links:
        print('-----------------------------------')
        print(link)
        print(get_ranking(link, scraper, ranker))
        print('-----------------------------------')


if __name__ == '__main__':
    main()