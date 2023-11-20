import requests
import bs4
import re
import random
import pandas as pd
from nltk.stem import PorterStemmer
from nltk.tokenize import wordpunct_tokenize
from nltk.stem import WordNetLemmatizer
from tqdm import tqdm
from queue import LifoQueue

class WikiScraper:
    def __init__(self):
        self.porter = PorterStemmer()
        self.visited = dict()
        self.wordnet = WordNetLemmatizer()

    @staticmethod
    def is_article_link(url):
        if ':' in url:
            return False
        return True
        
    def get_content(self, link):
        response = requests.get(link)
        parsed = bs4.BeautifulSoup(response.text, features="lxml")
        return ''.join(t.getText() for t in parsed.select('p'))

    def get_n_random(self, link='https://en.wikipedia.org/wiki/Pozna%C5%84_University_of_Technology', num_documents=1500):
        queue = LifoQueue()
        pbar = tqdm(total=num_documents, desc="Downloading links", unit="link")
        response = requests.get(link)
        link = link.replace('https://en.wikipedia.org', '')

        parsed = bs4.BeautifulSoup(response.text, features="lxml")
        child_links = parsed.find_all('a', attrs={'href': re.compile(r'^/wiki')})

        self.visited[link] = ''.join(t.getText() for t in parsed.select('p'))
        
        pbar.update(1)
        random.shuffle(child_links)
        
        for child_link in child_links:
            if child_link['href'] not in self.visited and len(self.visited) < num_documents and self.is_article_link(child_link['href']):
                queue.put(child_link)
        
        while not queue.empty() and len(self.visited) < num_documents:
            child_link = queue.get()
            response = requests.get("https://en.wikipedia.org" + child_link['href'])
            parsed = bs4.BeautifulSoup(response.text, features="lxml")
            self.visited[child_link['href']] = ''.join(t.getText() for t in parsed.select('p'))

            child_links = parsed.find_all('a', attrs={'href': re.compile(r'^/wiki')})
            random.shuffle(child_links)

            for child_link in child_links:
                if (child_link['href'] not in self.visited) and (len(self.visited) < num_documents) and (self.is_article_link(child_link['href'])):
                    queue.put(child_link)
            
            pbar.update(1)


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