import argparse

from src.data.lawbook import LawBook
from src.law_lookup.referenced import ReferencedLookUp

parser = argparse.ArgumentParser()
parser.add_argument('--input')

if __name__ == '__main__':
    args = parser.parse_args()

    law_books = LawBook.get_all_books_from_cache()

    with open(args.input) as f:
        example_text = f.read()

    ref = ReferencedLookUp(law_books)
    print(ref.find_references(example_text))
