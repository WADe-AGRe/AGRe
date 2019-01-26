import requests
import json
from rdflib import Graph, Literal, Namespace
from rdflib.namespace import FOAF, RDF

subjects = ['networking']
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

    article = article_ns[entry["dc:identifier"].split(':')[1]]
    creator = author_ns[creator_name.replace(' ', '')]
    tag = tags_ns[tagName]

    g.add((article, RDF.type, FOAF.Article))
    g.add((article, FOAF.name, Literal(entry['dc:title'])))
    g.add((article, FOAF.hasISSN, Literal(article_issn)))
    g.add((article, FOAF.hasURL, Literal(article_url)))
    g.add((article, FOAF.hasPublication, Literal(entry['prism:publicationName'])))
    g.add((article, FOAF.hasSubject, tag))
    g.add((article, FOAF.hasCreator, creator))

    g.add((creator, RDF.type, FOAF.Person))
    g.add((creator, FOAF.name, Literal(creator_name)))

    g.add((tag, RDF.type, FOAF.Tag))
    g.add((tag, FOAF.name, Literal(tagName)))

    for aff in entry.get('affiliation', []):
        aff_name = aff['affilname']
        aff_city = aff['affiliation-city']
        aff_country = aff['affiliation-country']

        affiliation = affiliation_ns[
            '{}-{}-{}'.format(aff_name, aff_city, aff_country).replace(' ', '')]

        g.add((affiliation, RDF.type, FOAF.Affiliation))
        g.add((affiliation, FOAF.name, Literal(aff_name)))
        g.add((affiliation, FOAF.hasCity, Literal(aff_city)))
        g.add((affiliation, FOAF.hasCountry, Literal(aff_country)))
        g.add((article, FOAF.hasAffiliation, affiliation))


def main():
    for s in subjects:
        js = getJsonFromRequest(url.format(subject=s))
        results = js['search-results']['entry']

        # create rdf objects
        for entry in results:
            addToGraph(entry, s)

    g.serialize(destination='articles.rdf')

__name__ == '__main__' and main()