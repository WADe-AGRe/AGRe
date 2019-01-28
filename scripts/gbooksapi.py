import requests
import json
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import FOAF, RDF

subjects = ['vpn', 'ip', 'cryptography', 'networking', 'data+structures', 'machine+learning', 'programming', 'artificial+intelligence', 'database', 'neural+networks', 'semantic+web', 'web+technologies', 'algorithms', 'c', 'data+mining', 'big+data', 'html', 'django', 'linear', 'svm', 'sparql']

key = '&key=AIzaSyC34kV2e0JxiXxth3a67SCRO-4D7Swh1XY'
url = 'https://www.googleapis.com/books/v1/volumes?q={subject}' + key
g = Graph()

book_ns = Namespace("http://agre.org/book/")
author_ns = Namespace("http://agre.org/author/")
tags_ns = Namespace("http://agre.org/tags/")
categories_ns = Namespace("http://agre.org/categories/")

def getJsonFromRequest(url):
    response = requests.get(url)
    return json.loads(response.text)


def addToGraph(entry, tagName):
    book_url = entry['accessInfo']['webReaderLink']
    book_id = entry['id']
    book_description = entry['volumeInfo'].get('description', '')
    book_publisher = entry['volumeInfo'].get('publisher', '').replace(' ', '')

    book = book_ns[book_id]
    tag = tags_ns[tagName]

    g.add((book, RDF.type, FOAF.Book))
    g.add((book, FOAF.name, Literal(entry['volumeInfo']['title'])))
    g.add((book, FOAF.hasId, Literal(book_id)))
    g.add((book, FOAF.hasURL, Literal(book_url)))
    g.add((book, FOAF.hasPublisher, Literal(book_publisher)))
    g.add((book, FOAF.hasSubject, tag))
    g.add((book, FOAF.hasDescription, Literal(book_description)))

    g.add((tag, RDF.type, FOAF.Tag))
    g.add((tag, FOAF.name, Literal(tagName)))

    volInfo = entry['volumeInfo']
    for cat in volInfo.get('categories', []):
        cat_name = cat.replace(' ', '-').lower()
        category = categories_ns[cat_name]

        g.add((category, RDF.type, FOAF.Category))
        g.add((category, FOAF.name, Literal(cat_name)))
        g.add((book, FOAF.hasCategory, category))

    for author in volInfo.get('authors', []):
        author_name = author.replace(' ', '')
        author = author_ns[author_name]

        g.add((author, RDF.type, FOAF.Person))
        g.add((author, FOAF.name, Literal(author_name)))
        g.add((book, FOAF.hasAuthor, author))


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