import pandas as pd
from sklearn.feature_extraction.text import TfidfVectorizer
from scipy.spatial.distance import cosine


class DocumentRanker():
    def __init__(self) -> None:
        self.documents_df = None
        self.dfTFIDF_sublinear_true = None
        self.dfTFIDF_sublinear_false = None

        self.tfidf_sublinear_true = TfidfVectorizer(use_idf=True, smooth_idf=False, sublinear_tf=True)
        self.tfidf_sublinear_false = TfidfVectorizer(use_idf=True, smooth_idf=False, sublinear_tf=False)

    def create_tfidf(self):
        scraped = pd.read_csv('data.csv')

        self.dfTFIDF_sublinear_true = pd.DataFrame(self.tfidf_sublinear_true.fit_transform(scraped['tokens']).toarray(),
                                                    index=scraped['url'], columns=self.tfidf_sublinear_true.get_feature_names_out())

        self.dfTFIDF_sublinear_false = pd.DataFrame(self.tfidf_sublinear_false.fit_transform(scraped['tokens']).toarray(),
                                                     index=scraped['url'], columns=self.tfidf_sublinear_false.get_feature_names_out())

    def get_similar(self, query):
        if self.dfTFIDF_sublinear_true is None or self.dfTFIDF_sublinear_false is None:
            self.create_tfidf()

        query_vector_sublinear_true = self.tfidf_sublinear_true.transform([query]).toarray()[0]
        query_vector_sublinear_false = self.tfidf_sublinear_false.transform([query]).toarray()[0]

        rank_sublinear_true = 1 - self.dfTFIDF_sublinear_true.apply(lambda x: cosine(x, query_vector_sublinear_true), axis=1)
        rank_sublinear_false = 1 - self.dfTFIDF_sublinear_false.apply(lambda x: cosine(x, query_vector_sublinear_false), axis=1)

        rank_average = (rank_sublinear_true + rank_sublinear_false) / 2
        rank_average = rank_average.sort_values(ascending=False)
        return rank_average.head(10)