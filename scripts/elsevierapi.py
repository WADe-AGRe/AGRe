import requests
import json
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import RDF

from scripts.add_resource_to_db import add_resource
from core.models import Resource
from core.ontology import ArticleONT, PersonONT, TagONT, AffiliationONT

subjects = ['networking', 'data+structures', 'machine+learning', 'programming', 'artificial+intelligence', 'database',
            'neural+networks', 'semantic+web', 'web+technologies', 'algorithms', 'c', 'data+mining', 'big+data', 'html',
            'django', 'linear', 'svm', 'sparql']

key = '&apiKey=7f59af901d2d86f78a1fd60c1bf9426a'
url = 'https://api.elsevier.com/content/search/scopus?query=all({subject})' + key
g = Graph()

article_ns = Namespace("http://agre.org/article/")
author_ns = Namespace("http://agre.org/author/")
affiliation_ns = Namespace("http://agre.org/affiliation/")
tags_ns = Namespace("http://agre.org/tags/")


def getJsonFromRequest(url):
    response = requests.get(url)
    return json.loads(response.text)


def addToGraph(entry, tagName):
    article_url = entry['link'][2]['@href']
    creator_name = entry['dc:creator']
    article_issn = entry.get('prism:issn', entry.get('prism:eIssn'))
    if article_issn is None:
        return
    article_uri = entry["dc:identifier"].split(':')[1]

    article = article_ns[article_uri]
    creator = author_ns[creator_name.replace(' ', '')]
    tag = tags_ns[tagName]

    add_resource(resource_uri=article.toPython(), resource_type=Resource.ARTICLE)

    g.add((article, RDF.type, ArticleONT.TYPE))
    g.add((article, ArticleONT.NAME, Literal(entry['dc:title'])))
    g.add((article, ArticleONT.ISSN, Literal(article_issn)))
    g.add((article, ArticleONT.URL, Literal(article_url)))
    g.add((article, ArticleONT.PUBLICATION, Literal(entry['prism:publicationName'])))
    g.add((article, ArticleONT.SUBJECT, tag))
    g.add((article, ArticleONT.AUTHOR, creator))

    g.add((creator, RDF.type, PersonONT.TYPE))
    g.add((creator, PersonONT.NAME, Literal(creator_name)))

    g.add((tag, RDF.type, TagONT.TYPE))
    g.add((tag, TagONT.NAME, Literal(tagName)))

    for aff in entry.get('affiliation', []):
        aff_name = aff['affilname']
        aff_city = aff['affiliation-city']
        aff_country = aff['affiliation-country']

        affiliation = affiliation_ns[
            '{}-{}-{}'.format(aff_name, aff_city, aff_country).replace(' ', '')]

        g.add((affiliation, RDF.type, AffiliationONT.TYPE))
        g.add((affiliation, AffiliationONT.NAME, Literal(aff_name)))
        g.add((affiliation, AffiliationONT.CITY, Literal(aff_city)))
        g.add((affiliation, AffiliationONT.COUNTRY, Literal(aff_country)))
        g.add((article, ArticleONT.AFFILIATION, affiliation))


def main():
    for s in subjects:
        print(s)
        js = getJsonFromRequest(url.format(subject=s))
        results = js['search-results']['entry']

        # create rdf objects
        for entry in results:
            addToGraph(entry, s)

    g.serialize(destination='articles.rdf')


__name__ == '__main__' and main()
