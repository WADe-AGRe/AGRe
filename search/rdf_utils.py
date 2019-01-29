from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SKOS, FOAF
from rdflib.plugins.stores import sparqlstore

api_key   = 's4reml553j6d'
api_secret = 'ngpcvnoi4p9l5hc'

# Identify a named graph where we will be adding our instances.
course_graph = URIRef('http://agre.com/courses')
book_graph = URIRef('http://agre.com/books')
article_graph = URIRef('http://agre.com/articles')

# Define the Stardog update store
update_endpoint = 'https://rdf.ontotext.com/4234582382/agre-graphdb/repositories/agre/statements'
update_store = sparqlstore.SPARQLUpdateStore()
update_store.open((update_endpoint, update_endpoint))

query_endpoint = 'https://rdf.ontotext.com/4234582382/agre-graphdb/repositories/agre'
query_store = sparqlstore.SPARQLUpdateStore()
query_store.open((query_endpoint, query_endpoint))

course_g = Graph(query_store, identifier=course_graph)
course_g.store.setCredentials(api_key, api_secret)

book_g = Graph(query_store, identifier=course_graph)
book_g.store.setCredentials(api_key, api_secret)

article_g = Graph(query_store, identifier=course_graph)
article_g.store.setCredentials(api_key, api_secret)

s_person = URIRef('http://schema.org/Person')
s_action = URIRef('http://schema.org/Action')
s_creative_work = URIRef('http://schema.org/CreativeWork')
s_organization = URIRef('http://schema.org/Organization')
s_book = URIRef('http://schema.org/Book')
s_book_format_type = URIRef('http://schema.org/BookFormatType')
s_course = URIRef('http://schema.org/Course')
s_instructor = URIRef('http://schema.org/instructor')
s_name = URIRef('http://schema.org/name')
s_category = URIRef('http://schema.org/about')
s_provider = URIRef('http://schema.org/provider')
s_offeredBy = URIRef('http://schema.org/offeredBy')
s_location = URIRef('http://schema.org/location')
s_description = URIRef('http://schema.org/description')
s_rating = URIRef('http://schema.org/aggregateRating')
s_inLanguage = URIRef('http://schema.org/inLanguage')

class Generic:
    def __init__(self, type='', link='', name='', description=''):
        self.type = type
        self.link = link
        self.name = name
        self.description = description

class Course:
    def __init__(self, link='', name='', university=None, provider='', instructors=None, language='',
                 country='', description='', rating=0, categories=None, reviews=None):
        self.type = "course"
        self.link = link
        self.name = name
        self.description = description
        self.university = university
        self.provider = provider
        self.instructors = instructors
        self.language = language
        self.country = country
        self.rating = rating
        self.categories = categories
        self.reviews = reviews

class Book:
    def __init__(self, link='', name='',  provider='', authors=None, description='',
                 rating=0, categories=None, reviews=None, publisher='', subject=''):
        self.type = "course"
        self.link = link
        self.name = name
        self.description = description
        self.provider = provider
        self.authors = authors
        self.rating = rating
        self.categories = categories
        self.reviews = reviews
        self.publisher = publisher
        self.subject = subject

def find_courses(search_terms=None, limit=100, offset=0):
    global course_g

    query_s = '''SELECT DISTINCT ?course ?name ?instructor ?uni ?location ?provider ?description ?rating ?category ?language
        WHERE {
         ?course rdf:type ?c . 
         ?course ?n ?name . 
         ?course ?desc ?description . 
        ?course ?loc ?location_url .
        ?location_url ?n ?location .
        ?course ?offerBy ?provider_url .
        ?provider_url ?n ?provider .
        ?course ?i ?instructor_url .
        ?instructor_url ?n ?instructor .
        ?course ?prov ?uni_url .
        ?uni_url ?n ?uni .
        ?course ?cat ?category_url .
        ?category_url ?n ?category .
        optional {
            ?course ?rate ?rating .
            ?course ?inLang ?language .
        }
        '''

    if search_terms:
        query_s += 'filter contains(lcase(str(?name)),"%s")\n' % (search_terms)

    query_s += '}\nORDER BY ASC(?name)\n'

    query_s += 'LIMIT %d\n' % (limit)
    if offset > 0:
        query_s += 'OFFSET  %d\n' % (offset)

    qres = course_g.query(query_s, initBindings={'c': s_course, 'n': s_name, 'i': s_instructor,
                                            'prov': s_provider, 'loc': s_location, 'offerBy':s_offeredBy,
                                            'desc':s_description, 'rate':s_rating, 'cat':s_category, 'inLang':s_inLanguage}, )

    course2data = dict()
    for (course ,name ,instructor ,uni ,location ,provider ,description ,rating ,category ,language) in qres:
        if rating:
            rating = float(rating)

        if course not in course2data:
            course2data[course] = {
                'name':str(name),
                'unis':set(),
                'instructors':set(),
                'location':str(location),
                'provider':str(provider),
                'description':str(description),
                'rating':rating,
                'categories':set(),
                'language':str(language),
            }
        course2data[course]['unis'].add(str(uni))
        course2data[course]['instructors'].add(str(instructor))
        course2data[course]['categories'].add(str(category))

    res_courses = []
    for course_url in course2data:
        course = course2data[course_url]
        instructors = [Generic(name=name) for name in course['instructors']]
        c = Course(link=course_url, name=course['name'], instructors=instructors, university=course['unis'], categories=course['categories'],
                   rating=course['rating'], language=course['language'], description=course['description'], provider=course['provider'],
                   country=course['location'])
        res_courses.append(c)
    return res_courses

def find_books(search_terms=None, limit=100, offset=0):
    global book_g

    query_s = '''SELECT DISTINCT ?book ?name ?description ?link ?subject ?publisher
            WHERE {
             ?book rdf:type ?b . 
             ?book ?n ?name . 
             ?book ?desc ?description . 
             ?book ?url ?link . 
             ?book ?pub ?publisher . 
             ?book ?sub ?subject_url . 
             ?subject_url ?n subject
            '''

    if search_terms:
        query_s += 'filter contains(lcase(str(?name)),"%s")\n' % (search_terms)

    query_s += '}\nORDER BY ASC(?name)\n'

    query_s += 'LIMIT %d\n' % (limit)
    if offset > 0:
        query_s += 'OFFSET  %d\n' % (offset)

    qres = book_g.query(query_s, initBindings={'b': FOAF.Book, 'n': FOAF.name, 'url': FOAF.hasURL,
                                     'sub': FOAF.hasSubject, 'pub': FOAF.hasPublisher,'desc': FOAF.hasDescription,}, )

    book2data = dict()
    for (book, name, description, link, subject, publisher) in qres:
        if book not in book2data:
            book2data[book] = {
                'name': str(name),
                'link': str(link),
                'subject': str(subject),
                'publisher': str(publisher),
                'authors': set(),
                'description': str(description),
                'categories': set(),
            }

    book_set = list(book2data.keys())

    query_s = '''SELECT DISTINCT ?book ?cat
            WHERE {
             ?book rdf:type foaf:Book . 
             ?book foaf:hasCategory ?cat . 
             filter(?book IN ?set)
             }
            '''

    cat_qres = book_g.query(query_s, initBindings={'set':book_set})

    query_s = '''SELECT DISTINCT ?book ?author
            WHERE {
             ?book rdf:type foaf:Book . 
             ?book foaf:hasAuthor ?author . 
             filter(?book IN ?set)
             }
            '''

    author_qres = book_g.query(query_s, initBindings={'set':book_set})


    res_books = []
    for book_url in book2data:
        book = book2data[book_url]
        b = Book(link=book['link'], name=book['name'], authors=book['authors'],
                   categories=book['categories'],
                   rating=book['rating'], description=book['description'])
        res_books.append(b)
    return res_books

if __name__ == "__main__":
    print(find_courses(search_terms=None))
