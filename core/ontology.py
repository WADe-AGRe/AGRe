from rdflib.namespace import FOAF


class BaseONT:
    TYPE = NotImplemented
    NAME = FOAF.name


class ArticleONT(BaseONT):
    TYPE = FOAF.Article
    ISSN = FOAF.hasISSN
    AUTHOR = FOAF.hasCreator
    URL = FOAF.hasURL
    PUBLICATION = FOAF.hasPublication
    SUBJECT = FOAF.hasSubject
    AFFILIATION = FOAF.hasAffiliation


class PersonONT(BaseONT):
    TYPE = FOAF.Person


class TagONT(BaseONT):
    TYPE = FOAF.Tag


class AffiliationONT(BaseONT):
    TYPE = FOAF.Affiliation
    CITY = FOAF.hasCity
    COUNTRY = FOAF.hasCountry
