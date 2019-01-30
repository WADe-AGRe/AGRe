from rdflib import Namespace

SCHEMA_NS = Namespace("https://schema.org/")

LIKES_URI = SCHEMA_NS.likes
DISLIKES_URI = SCHEMA_NS.dislikes
RATING_URI = SCHEMA_NS.rating

ONTOLOGY_BASE_URL = "https://agre.herokuapp.com/ontology/"

USER_NS = Namespace(ONTOLOGY_BASE_URL + "user/")
BOOK_NS = Namespace(ONTOLOGY_BASE_URL + "book/")
AUTHOR_NS = Namespace(ONTOLOGY_BASE_URL + "author/")
TAGS_NS = Namespace(ONTOLOGY_BASE_URL + "tags/")
CATEGORIES_NS = Namespace(ONTOLOGY_BASE_URL + "categories/")
PUBLISHER_NS = Namespace(ONTOLOGY_BASE_URL + "publisher/")
ARTICLE_NS = Namespace(ONTOLOGY_BASE_URL + "article/")


class ThingONT:
    TYPE = NotImplemented
    NAME = SCHEMA_NS.name


class ResourceONT(ThingONT):
    TYPE = SCHEMA_NS.CreativeWork
    URL = SCHEMA_NS.url
    PUBLISHER = SCHEMA_NS.publisher
    CATEGORY = SCHEMA_NS.category
    TAGS = SCHEMA_NS.keywords
    DESCRIPTION = SCHEMA_NS.description
    AUTHOR = SCHEMA_NS.author


class ArticleONT(ResourceONT):
    ISSN = SCHEMA_NS.issn
    PUBLICATION = SCHEMA_NS.publication


class BookONT(ResourceONT):
    ID = SCHEMA_NS.identifier


class PersonONT(ThingONT):
    TYPE = SCHEMA_NS.Person


class TagONT(ThingONT):
    TYPE = SCHEMA_NS.Text


class PublisherONT(ThingONT):
    TYPE = SCHEMA_NS.Organization
    CITY = SCHEMA_NS.city
    COUNTRY = SCHEMA_NS.country


class CategoryONT(ThingONT):
    TYPE = SCHEMA_NS.Category
