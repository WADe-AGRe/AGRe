import json

import requests
from rdflib import Graph, Literal
from rdflib.namespace import RDF

from scripts.add_resource_to_db import add_resource

from core.models import Resource
from core.ontology import ArticleONT, PersonONT, TagONT, PublisherONT, ARTICLE_NS, PUBLISHER_NS, AUTHOR_NS, \
    TAGS_NS

from scripts.add_interests_to_db import ALL_TAGS

url = 'https://api.elsevier.com/content/search/scopus?query=all({subject})&apiKey=7f59af901d2d86f78a1fd60c1bf9426a'
g = Graph()


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

    article = ARTICLE_NS[article_uri]
    creator = AUTHOR_NS[creator_name.replace(' ', '')]
    tag = TAGS_NS[tagName]

    add_resource(resource_uri=article.toPython(), resource_type=Resource.ARTICLE)

    g.add((article, RDF.type, ArticleONT.TYPE))
    g.add((article, ArticleONT.NAME, Literal(entry['dc:title'])))
    g.add((article, ArticleONT.ISSN, Literal(article_issn)))
    g.add((article, ArticleONT.URL, Literal(article_url)))
    g.add((article, ArticleONT.PUBLICATION, Literal(entry['prism:publicationName'])))
    g.add((article, ArticleONT.CATEGORY, tag))
    g.add((article, ArticleONT.TAGS, tag))
    g.add((article, ArticleONT.AUTHOR, creator))

    g.add((creator, RDF.type, PersonONT.TYPE))
    g.add((creator, PersonONT.NAME, Literal(creator_name)))

    g.add((tag, RDF.type, TagONT.TYPE))
    g.add((tag, TagONT.NAME, Literal(tagName)))

    for aff in entry.get('affiliation', []):
        aff_name = aff['affilname']
        aff_city = aff['affiliation-city']
        aff_country = aff['affiliation-country']

        affiliation = PUBLISHER_NS[
            '{}-{}-{}'.format(aff_name, aff_city, aff_country).replace(' ', '')]

        g.add((affiliation, RDF.type, PublisherONT.TYPE))
        g.add((affiliation, PublisherONT.NAME, Literal(aff_name)))
        g.add((affiliation, PublisherONT.CITY, Literal(aff_city)))
        g.add((affiliation, PublisherONT.COUNTRY, Literal(aff_country)))
        g.add((article, ArticleONT.PUBLISHER, affiliation))


def main():
    for s in ALL_TAGS:
        print(s)
        js = getJsonFromRequest(url.format(subject=s))
        results = js['search-results']['entry']

        # create rdf objects
        for entry in results:
            try:
                addToGraph(entry, s)
            except:
                pass

    g.serialize(destination='articles.rdf')


__name__ == '__main__' and main()
