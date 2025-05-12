from __future__ import annotations

import os.path
import re
import pickle

import requests
from bs4 import BeautifulSoup
from langchain.text_splitter import RecursiveCharacterTextSplitter


class Paragraph:
    def __init__(self, id_: str, title: str, section_text_all: str, section_dict: dict[str, str]):
        self.id: str = id_
        self.title: str = title  # The title of the paragraph
        self.section_text_all: str = section_text_all  # The text inside the paragraph
        self.section_dict: dict[str, str] = section_dict  # The subparagraphs by their id
        # section_dict may be empty if the subparagraphs are not numbered
    
    def split_into_smaller_paragraphs(self,text_splitter):
        smaller_texts = text_splitter.create_documents([self.section_text_all])
        return [Paragraph(self.id, self.title, part.page_content, self.section_dict) for part in smaller_texts]

class LawBook:
    def __init__(self, book_name, book_title, paragraph_dict):
        self.paragraphs: dict[str, Paragraph] = paragraph_dict
        self.book_name: str = book_name
        self.book_title: str = book_title

    def save_cache(self):
        illegal_characters = r'[<>:"/\\|?*\x00-\x1F]'
        filename = re.sub(illegal_characters, "_", self.book_name)
        filename = os.path.join('data', 'law_books', f"{filename}.pkl")
        with open(filename, 'wb') as f:
            pickle.dump(self, f)

    # Use this method one the cache is saved, much faster and reliable than the from_website
    @classmethod
    def init_from_cache(cls, filepath):
        with open(filepath, 'rb') as f:
            return pickle.load(f)

    @classmethod
    def init_from_website(cls, book_name, book_title, book_url):
        try:
            response = requests.get(book_url)
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

            paragraph_dict[paragraph_id] = Paragraph(paragraph_id, paragraph_title, subparagraphs_all,
                                                     subparagraphs_dict)
        new_paragraph_dict = {}
        text_splitter = RecursiveCharacterTextSplitter(
            chunk_size=3000,
            chunk_overlap=20,
            length_function=len,
            is_separator_regex=False,
        )
        for paragraph_id, paragraph in paragraph_dict.items():
            smaller_paragraphs = paragraph.split_into_smaller_paragraphs(text_splitter)
            for i, small_paragraph in enumerate(smaller_paragraphs):
                new_paragraph_id = f"{paragraph_id}_part{i+1}" if i!=0 else paragraph_id
                new_paragraph_dict[new_paragraph_id] = small_paragraph
        return cls(book_name, book_title, new_paragraph_dict)

    @staticmethod
    def get_all_books_from_cache():
        books = [os.path.join('data', 'law_books', f) for f in os.listdir(os.path.join('data', 'law_books'))]
        books = [LawBook.init_from_cache(law_book) for law_book in books]
        books = {book.book_name.lower().strip(): book for book in books}
        return books
