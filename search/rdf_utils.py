from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SKOS, FOAF
from rdflib.plugins.stores import sparqlstore

# Define the Stardog update store
update_endpoint = 'http://localhost:5820/demo/update'
update_store = sparqlstore.SPARQLUpdateStore()
update_store.open((update_endpoint, update_endpoint))

# Identify a named graph where we will be adding our instances.
default_graph = URIRef('http://example.org/default-graph')
update_g = Graph(update_store, identifier=default_graph)
update_g.store.setCredentials('admin', 'admin')

# Define the Stardog query store
query_endpoint = 'http://localhost:5820/demo/query'
query_store = sparqlstore.SPARQLUpdateStore()
query_store.open((query_endpoint, query_endpoint))

# Identify a named graph where we will be adding our instances.
default_graph = URIRef('http://example.org/default-graph')
query_g = Graph(query_store, identifier=default_graph)
query_g.store.setCredentials('admin', 'admin')


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

class Instructor:
    def __init__(self, name=''):
        self.name = name

class Course:
    def __init__(self, name='', university=None, provider='', instructors=None, language='',
                 country='', description='', rating=0, categories=None):
        self.type = "course"
        self.name = name
        self.university = university
        self.provider = provider
        self.instructors = instructors
        self.language = language
        self.country = country
        self.description = description
        self.rating = rating
        self.categories = categories

def find_courses(search_terms=None, limit=100, offset=0):
    global query_g

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

    qres = query_g.query(query_s, initBindings={'c': s_course, 'n': s_name, 'i': s_instructor,
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
        instructors = [Instructor(name) for name in course['instructors']]
        c = Course(name=course['name'], instructors=instructors, university=course['unis'], categories=course['categories'],
                   rating=course['rating'], language=course['language'], description=course['description'], provider=course['provider'],
                   country=course['location'])
        res_courses.append(c)
    return res_courses

if __name__ == "__main__":
    print(find_courses(search_terms='data'))
