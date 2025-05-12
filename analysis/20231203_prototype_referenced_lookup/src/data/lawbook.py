import os.path
import re
import pickle

import requests
from bs4 import BeautifulSoup

# IMPORTANT! When adding a new book, check that the structure of the HTML page is supported
# Add a new book in the following format `short_title: (long_title, url_for_all_of_the_text)
supported_books = {
    'BGB': (
        'Bürgerliches Gesetzbuch',
        'https://www.gesetze-im-internet.de/bgb/BJNR001950896.html'
    ),
    'BAföG': (
        'Bundesgesetz über individuelle Förderung der Ausbildung',
        'https://www.gesetze-im-internet.de/baf_g/BJNR014090971.html'
    ),
    'GG': (
        'Grundgesetz für die Bundesrepublik Deutschland',
        'https://www.gesetze-im-internet.de/gg/BJNR000010949.html'
    ),
    'BABG': (
        'Gesetz über die vermögensrechtlichen Verhältnisse der '
        'Bundesautobahnen und sonstigen Bundesstraßen des Fernverkehrs',
        'https://www.gesetze-im-internet.de/babg/BJNR001570951.html'
    ),
    'StGB': (
        'Strafgesetzbuch',
        'https://www.gesetze-im-internet.de/stgb/BJNR001270871.html'
    ),
    'HGB': (
        'Handelsgesetzbuch',
        'https://www.gesetze-im-internet.de/hgb/BJNR002190897.html'
    ),
    'ZPO': (
        'Zivilprozessordnung',
        'https://www.gesetze-im-internet.de/zpo/BJNR005330950.html'
    ),
    'VwVfG': (
        'Verwaltungsverfahrensgesetz',
        'https://www.gesetze-im-internet.de/vwvfg/BJNR012530976.html'
    ),
    'EnWG':(
        'Gesetz über die Elektrizitäts- und Gasversorgung',
        'https://www.gesetze-im-internet.de/enwg_2005/BJNR197010005.html'
    ),
    'GWB':(
        'Gesetz gegen Wettbewerbsbeschränkungen',
        'https://www.gesetze-im-internet.de/gwb/BJNR252110998.html'
    )
}


class LawBook:
    class Paragraph:
        def __init__(self, id_: str, title: str, section_text_all: str, section_dict: dict[str, str]):
            self.id: str = id_
            self.title: str = title  # The title of the paragraph
            self.section_text_all: str = section_text_all  # The text inside the paragraph
            self.section_dict: dict[str, str] = section_dict  # The subparagraphs by their id
            # section_dict may be empty if the subparagraphs are not numbered

    def __init__(self, book_name, paragraph_dict):
        self.paragraphs = paragraph_dict
        self.book_name = book_name

    def save_cache(self, filename=None):
        filename = os.path.join('data', f"{self.book_name}.pkl") if not filename else filename
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    # Use this method one the cache is saved, much faster and reliable than the from_website
    @classmethod
    def init_from_cache(cls, book_name, filename=None):
        if book_name not in supported_books.keys():
            raise ValueError('Not supported book specified')

        filename = os.path.join('data', f"{book_name}.pkl") if not filename else filename
        with open(filename, 'rb') as f:
            return pickle.load(f)

    @classmethod
    def init_from_website(cls, book_name):
        try:
            url = supported_books[book_name][1]
        except KeyError:
            raise ValueError('Not supported book specified')

        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError:
            raise RuntimeError('Law book HTML page unreachable')

        soup = BeautifulSoup(response.content, 'html.parser')

        paragraph_divs = soup.find('div', id='paddingLR12').find_all('div', class_='jnnorm')

        paragraph_dict = {}

        for paragraph_div in paragraph_divs:
            paragraph_id = paragraph_div.find('span', class_='jnenbez')
            if not paragraph_id:
                continue
            paragraph_id = paragraph_id.text.replace('§', '').strip()

            paragraph_title = paragraph_div.find('span', class_='jnentitel')
            if paragraph_title and 'weggefallen'.lower() in paragraph_title.text.lower():
                continue
            paragraph_title = paragraph_title.text if paragraph_title else None

            subparagraphs = paragraph_div.find('div', class_='jnhtml')
            if not subparagraphs:
                continue
            subparagraphs = subparagraphs.find_all('div', class_='jurAbsatz')
            if not subparagraphs:
                continue
            subparagraphs = list(map(lambda a: a.text.strip(), subparagraphs))

            subparagraphs_all = '/n'.join(subparagraphs)

            pattern = re.compile(r'\((.*?)\)')
            subparagraphs_dict = {pattern.match(text).group(1): text[pattern.match(text).end():].strip() for text in
                                  subparagraphs if pattern.match(text)}

            paragraph_dict[paragraph_id] = cls.Paragraph(paragraph_id, paragraph_title, subparagraphs_all,
                                                         subparagraphs_dict)

        return cls(book_name, paragraph_dict)
