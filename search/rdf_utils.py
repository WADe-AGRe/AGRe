from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SKOS, FOAF
from rdflib.plugins.stores import sparqlstore

api_key   = 's4reml553j6d'
api_secret = 'ngpcvnoi4p9l5hc'

# Identify a named graph where we will be adding our instances.
course_graph = URIRef('http://agre.com/courses')
book_graph = URIRef('https://agre.herokuapp.com/ontology/books')
article_graph = URIRef('https://agre.herokuapp.com/ontology/articles')

# Define the Stardog update store
update_endpoint = 'https://rdf.ontotext.com/4234582382/agre-graphdb/repositories/agre/statements'
update_store = sparqlstore.SPARQLUpdateStore()
update_store.open((update_endpoint, update_endpoint))

query_endpoint = 'https://rdf.ontotext.com/4234582382/agre-graphdb/repositories/agre'
query_store = sparqlstore.SPARQLUpdateStore()
query_store.open((query_endpoint, query_endpoint))

course_g = Graph(query_store, identifier=course_graph)
course_g.store.setCredentials(api_key, api_secret)

book_g = Graph(query_store, identifier=book_graph)
book_g.store.setCredentials(api_key, api_secret)

article_g = Graph(query_store, identifier=article_graph)
article_g.store.setCredentials(api_key, api_secret)

s_person = URIRef('http://schema.org/Person')
s_action = URIRef('http://schema.org/Action')
s_creative_work1 = URIRef('http://schema.org/CreativeWork')
s_organization = URIRef('http://schema.org/Organization')
s_book = URIRef('http://schema.org/Book')
s_book_format_type = URIRef('http://schema.org/BookFormatType')
s_course = URIRef('http://schema.org/Course')
s_instructor = URIRef('http://schema.org/instructor')
s_name = URIRef('http://schema.org/name')
s_about = URIRef('http://schema.org/about')
s_provider = URIRef('http://schema.org/provider')
s_offeredBy = URIRef('http://schema.org/offeredBy')
s_location = URIRef('http://schema.org/location')
s_description = URIRef('http://schema.org/description')
s_rating = URIRef('http://schema.org/aggregateRating')
s_inLanguage = URIRef('http://schema.org/inLanguage')

s_name2 = URIRef('https://schema.org/name')
s_description2 = URIRef('https://schema.org/description')
s_url = URIRef('https://schema.org/url')
s_author = URIRef('https://schema.org/author')
s_category = URIRef('https://schema.org/category')
s_publisher = URIRef('https://schema.org/publisher')
s_keywords = URIRef('https://schema.org/keywords')
s_identifier = URIRef('https://schema.org/identifier')
s_creative_work = URIRef('https://schema.org/CreativeWork')

s_publication = URIRef('https://schema.org/publication')
s_issn = URIRef('https://schema.org/issn')


class Generic:
    def __init__(self, type='', link='', name='', description=''):
        self.type = type
        self.link = link
        self.name = name
        self.description = description

class Course:
    def __init__(self, link='', name='', university=None, provider='', instructors=None, language='',
                 country='', description='', rating=0, categories=None, reviews=None, provider_url=''):
        self.type = "course"
        self.link = link
        self.name = name

        if description.startswith('STARTS'):
            description = description[7:]

        self.description = description
        self.university = university
        self.provider = provider
        self.provider_url = provider_url
        self.instructors = instructors
        self.language = language
        self.country = country
        self.rating = rating
        self.categories = categories
        self.reviews = reviews

class Book:
    def __init__(self, link='', name='', authors=None, description='',
                 rating=0, categories=None, reviews=None, publisher='', keywords=''):
        self.type = "book"
        self.link = link
        self.name = name
        self.description = description
        self.authors = authors
        self.rating = rating
        self.categories = categories
        self.reviews = reviews
        self.publisher = publisher
        self.keywords = keywords

class Article:
    def __init__(self, link='', name='',  publication='', authors=None, description='',
                 rating=0, categories=None, reviews=None, publisher='', keywords='', issn=''):
        self.type = "article"
        self.link = link
        self.name = name
        self.description = description
        self.publication = publication
        self.authors = authors
        self.rating = rating
        self.categories = categories
        self.reviews = reviews
        self.publisher = publisher
        self.keywords = keywords
        self.issn = issn

def find_courses(search_terms=None, limit=10, offset=0, search_tags=None):
    global course_g

    query_s = '''SELECT DISTINCT ?course ?name ?location ?provider ?description ?rating ?language ?provider_url
        WHERE {
         ?course rdf:type ?c . 
         ?course ?n ?name . 
         ?course ?desc ?description . 
        ?course ?loc ?location_url .
        ?location_url ?n ?location .
        ?course ?offerBy ?provider_url .
        ?provider_url ?n ?provider .

        optional {
            ?course ?rate ?rating .
            ?course ?inLang ?language .
        }
        '''

    if search_terms:
        query_s += 'filter contains(lcase(str(?name)),"%s")\n' % (search_terms.lower())

    query_s += '}\nORDER BY ASC(?name)\n'

    query_s += 'LIMIT %d\n' % (limit)
    if offset > 0:
        query_s += 'OFFSET  %d\n' % (offset)

    qres = course_g.query(query_s, initBindings={'c': s_course, 'n': s_name, 'i': s_instructor,
                                            'prov': s_provider, 'loc': s_location, 'offerBy':s_offeredBy,
                                            'desc':s_description, 'rate':s_rating, 'cat':s_about, 'inLang':s_inLanguage}, )

    course2data = dict()
    for (course , name, location ,provider ,description ,rating ,language, provider_url) in qres:
        if rating:
            rating = float(rating) / 2

        if course not in course2data:
            course2data[course] = {
                'name':str(name),
                'unis':set(),
                'instructors':set(),
                'location':str(location),
                'provider':str(provider),
                'provider_url':str(provider_url),
                'description':str(description),
                'rating':rating,
                'categories':set(),
                'language':str(language),
            }


    course_set = list(set([str(course) for course in course2data.keys()]))
    set_str = '( <' + '> , <'.join(course_set) + '> )'

    if len(course_set) > 0:

        query_s = '''SELECT DISTINCT ?course ?category
        WHERE {
         ?course rdf:type ?c . 
        ?course ?cat ?category_url .
        ?category_url ?n ?category .
        filter(?course IN %s)
         }''' % (set_str)

        cat_qres = course_g.query(query_s, initBindings={'c': s_course, 'n': s_name, 'i': s_instructor,
                                                     'prov': s_provider, 'loc': s_location, 'offerBy': s_offeredBy,
                                                     'desc': s_description, 'rate': s_rating, 'cat': s_about,
                                                     'inLang': s_inLanguage}, )

        for (course, category) in cat_qres:
            course2data[course]['categories'].add(str(category))

        query_s = '''SELECT DISTINCT ?course ?instructor
        WHERE {
         ?course rdf:type ?c . 
        ?course ?i ?instructor_url .
        ?instructor_url ?n ?instructor .
        filter(?course IN %s)
         }''' % (set_str)

        instructor_qres = course_g.query(query_s, initBindings={'c': s_course, 'n': s_name, 'i': s_instructor,
                                                     'prov': s_provider, 'loc': s_location, 'offerBy': s_offeredBy,
                                                     'desc': s_description, 'rate': s_rating, 'cat': s_about,
                                                     'inLang': s_inLanguage}, )

        for (course, instructor) in instructor_qres:
            course2data[course]['instructors'].add(str(instructor))

        query_s = '''SELECT DISTINCT ?course ?uni ?uni_url 
        WHERE {
         ?course rdf:type ?c . 
        ?course ?prov ?uni_url .
        ?uni_url ?n ?uni .
        filter(?course IN %s)
         }''' % (set_str)

        uni_qres = course_g.query(query_s, initBindings={'c': s_course, 'n': s_name, 'i': s_instructor,
                                                     'prov': s_provider, 'loc': s_location, 'offerBy': s_offeredBy,
                                                     'desc': s_description, 'rate': s_rating, 'cat': s_about,
                                                     'inLang': s_inLanguage}, )

        for (course, uni, uni_url ) in uni_qres:
            university = (str(uni), str(uni_url))
            course2data[course]['unis'].add(university)

    res_courses = []
    for course_url in course2data:
        course = course2data[course_url]
        instructors = [Generic(name=name) for name in course['instructors']]
        universities = [Generic(name=name, link=url) for (name,url) in course['unis']]
        c = Course(link=course_url, name=course['name'], instructors=instructors, university=universities, categories=course['categories'],
                   rating=course['rating'], language=course['language'], description=course['description'], provider=course['provider'],
                   country=course['location'])
        res_courses.append(c)
    return res_courses

def find_books(search_terms=None, limit=10, offset=0):
    global book_g

    query_s = '''SELECT DISTINCT ?book ?name ?description ?link ?keywords ?publisher
            WHERE {
             ?book rdf:type ?b . 
             ?book ?n ?name . 
             ?book ?desc ?description . 
             ?book ?url ?link . 
             ?book ?pub ?publisher .
             ?book ?key ?keywords_url . 
             ?keywords_url ?n ?keywords . 
            '''

    if search_terms:
        query_s += 'filter contains(lcase(str(?name)),"%s")\n' % (search_terms.lower())

    query_s += '}\nORDER BY ASC(?name)\n'

    query_s += 'LIMIT %d\n' % (limit)
    if offset > 0:
        query_s += 'OFFSET  %d\n' % (offset)


    # qres = book_g.query(query_s, initBindings={'b': FOAF.Book, 'n': FOAF.name, 'url': FOAF.hasURL,
    #                                  'sub': FOAF.hasSubject, 'pub': FOAF.hasPublisher,'desc': FOAF.hasDescription,}, )

    qres = book_g.query(query_s, initBindings={'b': s_creative_work, 'n': s_name2, 'url': s_url,
                                            'pub': s_publisher, 'desc': s_description2, 'key': s_category }, )

    book2data = dict()
    for (book, name, description, link, keywords, publisher) in qres:
        if book not in book2data:
            book2data[book] = {
                'name': str(name),
                'link': str(link),
                'publisher': str(publisher),
                'authors': set(),
                'description': str(description),
                'categories': set(),
                'keywords': str(keywords),
                'rating': 0,
            }

    book_set = list([str(book) for book in book2data.keys()])
    set_str = '( <' + '> , <'.join(book_set) + '> )'

    if len(book_set) > 0:
        query_s = '''SELECT DISTINCT ?book ?category
                WHERE {
                 ?book rdf:type ?b . 
                 ?book ?hasCat ?category_url . 
                 ?category_url ?n ?category . 
                 filter(?book IN %s)
                 }
                ''' % (set_str)

        cat_qres = book_g.query(query_s, initBindings={ 'b': s_creative_work, 'hasCat': s_category, 'n': s_name2 })

        for (book, category) in cat_qres:
            book2data[book]['categories'].add(category)


        query_s = '''SELECT DISTINCT ?book ?author_
                WHERE {
                 ?book rdf:type ?b . 
                 ?book ?auth ?author_url . 
                 ?author_url ?n ?author_ . 
                 filter(?book IN %s)
                 }
                ''' % (set_str)

        author_qres = book_g.query(query_s, initBindings={ 'b': s_creative_work, 'auth':s_author, 'n': s_name2})

        for (book, author) in author_qres:
            book2data[book]['authors'].add(author)

        # query_s = '''SELECT DISTINCT ?book ?keywords
        #         WHERE {
        #          ?book rdf:type ?b .
        #          ?book ?key ?keywords_url .
        #          ?keywords_url ?n ?keywords .
        #          filter(?book IN %s)
        #          }
        #         ''' % (set_str)
        #
        # keywords_qres = book_g.query(query_s, initBindings={ 'b': s_creative_work, 'key': s_category, 'n': s_name2})
        #
        # for (book, keywords) in keywords_qres:
        #     book2data[book]['keywords'].add(keywords)

    res_books = []
    for book_url in book2data:
        book = book2data[book_url]
        b = Book(link=book['link'], name=book['name'], authors=list(book['authors']),
                   categories=list(book['categories']), keywords=book['keywords'],
                   rating=book['rating'], description=book['description'])
        res_books.append(b)
    return res_books


def find_articles(search_terms=None, limit=10, offset=0):
    global article_g

    query_s = '''SELECT DISTINCT ?article ?name ?link ?keywords ?publisher ?publication
            WHERE {
             ?article rdf:type ?b . 
             ?article ?n ?name . 
             ?article ?url ?link . 
        optional {
             ?article ?published ?publisher_url .
             ?publisher_url ?n ?publisher .
             ?article ?publicat ?publication .
        }
            '''

    if search_terms:
        query_s += 'filter contains(lcase(str(?name)),"%s")\n' % (search_terms.lower())

    query_s += '}\nORDER BY ASC(?name)\n'

    query_s += 'LIMIT %d\n' % (limit)
    if offset > 0:
        query_s += 'OFFSET  %d\n' % (offset)

    qres = article_g.query(query_s, initBindings={'b': s_creative_work, 'n': s_name2, 'url': s_url, 'publicat':s_publication,
                                            'published': s_publisher, 'desc': s_description2, 'key': s_category }, )

    article2data = dict()
    for (article, name, link, keywords, publisher, publication) in qres:
        print((article, name, link, keywords, publisher, publication))
        if article not in article2data:
            article2data[article] = {
                'name': str(name),
                'link': str(link),
                'publisher': str(publisher),
                'publication': str(publication),
                'authors': set(),
                'categories': set(),
                'keywords': set(),
                'rating': 0,
            }

    article_set = list(set([str(article) for article in article2data.keys()]))
    set_str = '( <' + '> , <'.join(article_set) + '> )'

    if len(article_set) > 0:
        query_s = '''SELECT DISTINCT ?article ?keywords
                        WHERE {
                         ?article rdf:type ?b . 
                         ?article ?key ?keywords_url . 
                         ?keywords_url ?n ?keywords . 
                         filter(?article IN %s)
                         }
                        ''' % (set_str)

        key_qres = article_g.query(query_s, initBindings={'b': s_creative_work, 'hasCat': s_category, 'n': s_name2})

        for (article, keywords) in key_qres:
            article2data[article]['keywords'].add(keywords)

        query_s = '''SELECT DISTINCT ?article ?category
                WHERE {
                 ?article rdf:type ?b . 
                 ?article ?hasCat ?category_url . 
                 ?category_url ?n ?category . 
                 filter(?article IN %s)
                 }
                ''' % (set_str)

        cat_qres = article_g.query(query_s, initBindings={ 'b': s_creative_work, 'hasCat': s_category, 'n': s_name2 })

        for (article, category) in cat_qres:
            article2data[article]['categories'].add(category)

        query_s = '''SELECT DISTINCT ?article ?author_
                WHERE {
                 ?article rdf:type ?b . 
                 ?article ?auth ?author_url . 
                 ?author_url ?n ?author_ . 
                 filter(?article IN %s)
                 }
                ''' % (set_str)

        author_qres = article_g.query(query_s, initBindings={ 'b': s_creative_work, 'auth':s_author, 'n': s_name2})

        for (article, author) in author_qres:
            article2data[article]['authors'].add(author)

    res_articles = []
    for article_url in article2data:
        article = article2data[article_url]
        b = Article(link=article['link'], name=article['name'], authors=list(article['authors']),
                   categories=list(article['categories']), keywords=", ".join(list(article['keywords'])), publication=article['publication'],
                   rating=article['rating'])
        res_articles.append(b)
    return res_articles

if __name__ == "__main__":
    for row in book_g:
        # if str(row[0]) == 'https://agre.herokuapp.com/ontology/book/ZO-bPER2658C':
            print(row)

    # for row in article_g:
    #    if str(row[0]) == 'https://agre.herokuapp.com/ontology/article/85059828028':
    #        print(row)
    #
    # query_s = '''SELECT DISTINCT ?book ?category
    #         WHERE {
    #          ?book ?hasCat ?category .
    #          filter(?book in ( <https://agre.herokuapp.com/ontology/book/xxty8aDLAkoC> , <https://agre.herokuapp.com/ontology/book/xxty8aDLAkoC> ))
    #          }
    #         '''
    #
    #
    # print(URIRef('https://agre.herokuapp.com/ontology/book/xxty8aDLAkoC').n3())
    # cat_qres = book_g.query(query_s, initBindings={'hasCat': s_category, 'book_url':     URIRef('https://agre.herokuapp.com/ontology/book/xxty8aDLAkoC')})
    # for row in cat_qres:
    #     print(row)
    #
    # query_s = '''SELECT DISTINCT ?book ?name ?description ?link ?subject ?publisher
    #         WHERE {
    #          ?book ?n ?name .
    #          ?book ?desc ?description .
    #          ?book ?url ?link .
    #          ?book ?pub ?publisher
    #         }
    # LIMIT 100'''

    # qres = book_g.query(query_s, initBindings={'b': s_creative_work, 'n': s_name2, 'url': s_url,
    #                                         'pub': s_publisher, 'desc': s_description2, }, )
    #
    # for row in qres:
    #     print(row)

    print(find_articles())

    #
    # size = 12
    # offset = 0
    # query = ''
    #
    # course_results  = find_courses(query, limit=size//3, offset=offset )
    # article_results = find_articles(query, limit=size//3, offset=offset )
    # book_results    = find_books(query, limit=size-(2*(size//3)), offset=offset )
    # search_results = course_results + article_results + book_results
    # search_results.sort(key=lambda res: res.name)
    # print(len(search_results))
    # print(size//3)
    # print(article_results)
    # print(book_results)
    #
    #