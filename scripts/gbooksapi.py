import requests
import json
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF

from scripts.add_resource_to_db import add_resource
from core.models import Resource
from core.ontology import BOOK_NS, AUTHOR_NS, TAGS_NS, CATEGORIES_NS, BookONT, TagONT, CategoryONT, PersonONT

subjects = ['vpn', 'ip', 'cryptography', 'networking', 'data+structures', 'machine+learning', 'programming',
            'artificial+intelligence', 'database', 'neural+networks', 'semantic+web', 'web+technologies', 'algorithms',
            'c', 'data+mining', 'big+data', 'html', 'django', 'linear', 'svm', 'sparql']

key = '&key=AIzaSyC34kV2e0JxiXxth3a67SCRO-4D7Swh1XY'
url = 'https://www.googleapis.com/books/v1/volumes?q={subject}' + key
g = Graph()


def getJsonFromRequest(url):
    response = requests.get(url)
    return json.loads(response.text)


def addToGraph(entry, tagName):
    book_url = entry['accessInfo']['webReaderLink']
    book_id = entry['id']
    book_description = entry['volumeInfo'].get('description', '')
    book_publisher = entry['volumeInfo'].get('publisher', '').replace(' ', '')

    book = BOOK_NS[book_id]
    tag = TAGS_NS[tagName]

    add_resource(resource_uri=book.toPython(), resource_type=Resource.BOOK)

    g.add((book, RDF.type, BookONT.TYPE))
    g.add((book, BookONT.NAME, Literal(entry['volumeInfo']['title'])))
    g.add((book, BookONT.ID, Literal(book_id)))
    g.add((book, BookONT.URL, Literal(book_url)))
    g.add((book, BookONT.PUBLISHER, Literal(book_publisher)))
    g.add((book, BookONT.TAGS, tag))
    g.add((book, BookONT.DESCRIPTION, Literal(book_description)))

    g.add((tag, RDF.type, TagONT.TYPE))
    g.add((tag, TagONT.NAME, Literal(tagName)))

    volInfo = entry['volumeInfo']
    for cat in volInfo.get('categories', []):
        cat_name = cat.replace(' ', '-').lower()
        category = CATEGORIES_NS[cat_name]

        g.add((category, RDF.type, CategoryONT.TYPE))
        g.add((category, CategoryONT.NAME, Literal(cat_name)))
        g.add((book, BookONT.CATEGORY, category))

    for author in volInfo.get('authors', []):
        author_name = author.replace(' ', '')
        author = AUTHOR_NS[author_name]

        g.add((author, RDF.type, PersonONT.TYPE))
        g.add((author, PersonONT.NAME, Literal(author_name)))
        g.add((book, BookONT.AUTHOR, author))


def main():
    for s in subjects:
        print(s)
        js = getJsonFromRequest(url.format(subject=s))
        results = js['items']

        # create rdf objects
        for entry in results:
            addToGraph(entry, s)

    g.serialize(destination='books.rdf')


__name__ == '__main__' and main()
