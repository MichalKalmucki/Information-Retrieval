import pandas as pd
from Scraper import WikiScraper
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cosine


class DocumentRanker():
    def __init__(self) -> None:
        self.documents_df = None
        self.dfTFIDF = None
        self.tfidf = TfidfVectorizer(use_idf=True, smooth_idf=False, sublinear_tf=True)

    def create_tfidf(self):
        scraped = pd.read_csv('data.csv')

        self.dfTFIDF = pd.DataFrame(self.tfidf.fit_transform(scraped['tokens']).toarray(), index=scraped['url'], columns=self.tfidf.get_feature_names_out())

    def get_similar(self, query):
        if self.dfTFIDF is None:
            self.create_tfidf()
        query = self.tfidf.transform([query]).toarray()[0]
        rank = 1-self.dfTFIDF.apply(lambda x: cosine(x, query), axis=1).sort_values()

        return rank.head(10)


if __name__ == '__main__':
    ranker = DocumentRanker()
    scraper = WikiScraper()
    content = scraper.get_content('https://en.wikipedia.org/wiki/')
    tokens = scraper.tokenize_text(content)
    content = ' '.join(tokens)
    print(ranker.get_similar(content))