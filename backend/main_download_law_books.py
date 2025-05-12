import json
import os.path

import requests
from bs4 import BeautifulSoup
from tqdm import tqdm

from src.data.lawbook import LawBook


def main():
    print('Scraping alphabet links')
    letter_links = get_alphabet_links()

    print('Scraping book info')
    books = [book for letter_link in tqdm(letter_links) for book in get_all_books_info(letter_link)]

    print('Exporting book info')
    with open(os.path.join('data', 'book_infos.json'), 'w', encoding='UTF-8') as f:
        json.dump(books, f, ensure_ascii=False, indent=2)

    print('Saving book contents')
    for book_info in tqdm(books):
        book = LawBook.init_from_website(book_info[0], book_info[1], book_info[2])
        if len(book.paragraphs) > 0:
            book.save_cache()


def get_alphabet_links():
    letter_links = get_website_soup("https://www.gesetze-im-internet.de/aktuell.html").find_all('a', class_="alphabet")
    letter_links = [f"https://www.gesetze-im-internet.de/{e['href'].split('/', 1)[1]}" for e in letter_links]
    return letter_links


def get_all_books_info(letter_link):
    books = get_website_soup(letter_link).find('div', id='content_2022')
    books = books.find('div', id='container').find('div', id='paddingLR12').find_all('p')
    books = [(book.find('abbr').text.strip(),
              book.find('abbr')['title'].strip(),
              get_full_book_link(f"https://www.gesetze-im-internet.de/{book.find('a')['href'].split('/', 1)[1]}")
              ) for book in books]

    assert all('PDF' != book[0] and 'html' in book[2] for book in books)

    return books


def get_full_book_link(book_index_link):
    full_link = get_website_soup(book_index_link) \
        .find('div', id='content_2022').find('div', id='container').find_all('a')
    full_link = list(filter(lambda a: a.text == 'HTML', full_link))
    assert len(full_link) == 1
    return f"{book_index_link.replace('index.html', '')}{full_link[0]['href']}"


def get_website_soup(url):
    try:
        response = requests.get(url)
        response.raise_for_status()
    except requests.exceptions.HTTPError:
        raise RuntimeError(f'{url} is unreachable')

    return BeautifulSoup(response.content, 'html.parser')


if __name__ == '__main__':
    main()
