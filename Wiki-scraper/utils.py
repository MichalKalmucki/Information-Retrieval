import requests
import bs4
import re
import random
import pandas as pd
from nltk.stem import PorterStemmer
from nltk.tokenize import wordpunct_tokenize
from nltk.stem import WordNetLemmatizer
from tqdm import tqdm

class WikiScraper:
    def __init__(self):
        self.porter = PorterStemmer()
        self.visited = dict()
        self.wordnet = WordNetLemmatizer()


    def get_n_random(self, link='https://en.wikipedia.org/wiki/Pozna%C5%84_University_of_Technology', num_documents=200, pbar=None):
        if len(self.visited) >= num_documents:
            return self.visited

        if len(self.visited) == 0:
            response = requests.get(link)
        else:
            response = requests.get("https://en.wikipedia.org" + link['href'])
        
        parsed = bs4.BeautifulSoup(response.text)
        child_links = parsed.find_all('a', attrs={'href': re.compile(r'^/wiki')})
        random.shuffle(child_links)

        if pbar is None:
            pbar = tqdm(total=num_documents, desc="Downloading links", unit="link")

        pbar.update(1)

        for child_link in child_links:
            if child_link['href'] not in self.visited and len(self.visited) < num_documents:
                self.visited[child_link['href']] = ''.join(t.getText() for t in parsed.select('p'))
                
                self.get_n_random(child_link, num_documents, pbar)

        if pbar.total == pbar.n:
            pbar.close()  # Close the progress bar when it's done

    def tokenize_text(self, text):
        tokens = wordpunct_tokenize(text)
        filtered_tokens = []

        for token in tokens:
            if len(token) >= 3:
                filtered_tokens.append(token)

        return [self.porter.stem(self.wordnet.lemmatize(token, pos="v")) for token in filtered_tokens]
    
    def save_to_db(self, db = 23):
        assert self.visited is not None
        data = []
        pbar = tqdm(total=len(self.visited), desc="Processing tokens", unit="link")

        for key, value in self.visited.items():
            data.append((key, self.tokenize_text(value)))
            pbar.update(1)
        
        df = pd.DataFrame(data, columns=['url', 'tokens'])
        df.to_csv('data.csv', index=False)
        pbar.close()

if __name__ == '__main__':
    scraper = WikiScraper()
    scraper.get_n_random()
    visited = scraper.visited
    random_key = random.choice(list(visited.keys()))
    random_value = visited[random_key]
    scraper.save_to_db()
        