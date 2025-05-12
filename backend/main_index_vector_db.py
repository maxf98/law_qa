import time

from langchain.embeddings.openai import OpenAIEmbeddings
from langchain.vectorstores import Qdrant
from qdrant_client import QdrantClient

from src.data.lawbook import LawBook

apiKey = ""


def create_VectorDB():
    texts = []
    law_books = LawBook.get_all_books_from_cache()
    print("Loaded law books")
    '''for i in law_books["bafög"].paragraphs.keys():
        print("ID",law_books["bafög"].paragraphs[i].id)
        print("TITLE",law_books["bafög"].paragraphs[i].title)
        print("TEXT",law_books["bafög"].paragraphs[i].section_text_all)
        print("SUB",law_books["bafög"].paragraphs[i].section_dict)'''
    for document in law_books.keys():
        for paragraph in law_books[document].paragraphs.keys():
            texts.append(
                [law_books[document].book_name,
                 law_books[document].paragraphs[paragraph].id,
                 law_books[document].paragraphs[paragraph].title,
                 law_books[document].paragraphs[paragraph].section_text_all])
    metadata = [{"book_name": text[0], "id": text[1], "title": text[2], "source": text[3]} for text in texts]

    embeddings = OpenAIEmbeddings(openai_api_key=apiKey)

    completeText = [sublist[3] for sublist in texts if len(sublist) > 1]

    QdrantClient(url="http://localhost:6333").delete_collection('Gesetze')
    time.sleep(5)

    Qdrant.from_texts(
        completeText,
        embeddings,
        url="http://localhost:6333",
        metadatas=metadata,
        collection_name="Gesetze",
    )


if __name__ == '__main__':
    create_VectorDB()
