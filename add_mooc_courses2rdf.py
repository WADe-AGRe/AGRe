from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SKOS, FOAF
from rdflib.plugins.stores import sparqlstore
import tqdm

s_person = URIRef('http://schema.org/Person')
s_action = URIRef('http://schema.org/Action')
s_creative_work = URIRef('http://schema.org/CreativeWork')
s_organization = URIRef('http://schema.org/Organization')
s_book = URIRef('http://schema.org/Book')
s_book_format_type = URIRef('http://schema.org/BookFormatType')
s_course = URIRef('http://schema.org/Course')

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

print(SKOS.Concept)
course = URIRef('https://www.coursera.org/learn/regression-modeling-practice')

# update_g.add( (course, RDF.type, s_course) )

# print(query_g.serialize(format='turtle').decode())

{"link": "https://www.mooc-list.com/course/logic-and-paradoxes-unav", "title": "Logic and Paradoxes (UNAV)", "description": "", "tags": [{"tag": "Humanities", "url": "https://www.mooc-list.com/categories/humanities"}]}

def add_course(g, course):
    uri = URIRef(course['link'])

    g.add((uri, RDF.type, s_course))

    if 'title' in course:
        name = URIRef('http://schema.org/name')
        g.add((uri, name, Literal(course['title'])))

    if 'instructors' in course:
        author = URIRef('http://schema.org/author')
        for instructor in course['instructors']:
            g.add((uri, author, URIRef(instructor['url'])))
            
    if 'language' in course:
        inLanguage = URIRef('http://schema.org/inLanguage')
        g.add((uri, inLanguage, Literal(course['language']['text'])))

    if 'provider' in course:
        provider = URIRef('http://schema.org/provider')
        g.add((uri, provider, URIRef(course['provider']['url'])))

    if 'university' in course:
        university = URIRef('http://schema.org/location')
        g.add((uri, university, URIRef(course['university']['url'])))

    if 'country' in course:
        location = URIRef('http://schema.org/location')
        g.add((uri, location, URIRef(course['country']['url'])))

    if 'duration' in course:
        duration = URIRef('http://schema.org/duration')
        g.add((uri, duration, URIRef(course['duration']['url'])))

    if 'frequency' in course:
        frequency = URIRef('http://schema.org/repeatFrequency')
        g.add((uri, frequency, URIRef(course['frequency']['url'])))

    # if 'exam' in course:
    #     exam = Literal('exam')
    #     g.add((uri, exam, URIRef(course['exam']['url'])))

    if 'certificate' in course:
        certificate = URIRef('http://schema.org/educationalCredentialAwarded')
        g.add((uri, certificate, URIRef(course['certificate']['url'])))

    if 'category' in course:
        category = URIRef('http://schema.org/about')
        g.add((uri, category, URIRef(course['category']['url'])))

    if 'description' in course:
        description = URIRef('http://schema.org/description')
        g.add((uri, description, Literal(course['description'])))

def add_enteties_from_courses(g, courses):
    instructors = dict()
    universities = set()
    providers = set()
    worksFor = URIRef('http://schema.org/worksFor')

    for course in tqdm.tqdm(courses):
        if 'university' in course:
            uni_url = course['university']['url']
            uni_ref = URIRef(uni_url)
            if uni_url not in universities:
                g.add((uni_ref, RDF.type, s_organization))
                universities.add(uni_url)

        if 'provider' in course:
            provider_url = course['provider']['url']
            provider_ref = URIRef(provider_url)
            if uni_url not in universities:
                g.add((provider_ref, RDF.type, s_organization))
                providers.add(provider_url)

        if 'instructors' in course:
            for instructor in course['instructors']:
                if instructor['url'] not in instructors:
                    instructor_ref = URIRef(instructor['url'])
                    g.add(( instructor_ref, RDF.type, s_person))
                    instructors[instructor['url']] = set()

                if 'university' in course:
                    if uni_url not in instructors[instructor['url']]:
                        g.add((instructor_ref, worksFor, uni_ref))
                        instructors[instructor['url']].add(uni_url)



if __name__ == "__main__":
    import json

    with open('data/mooc_list_courses_detailed.json', 'r') as f:
        courses = json.load(f)

    add_enteties_from_courses(update_g, courses)
    for course in tqdm.tqdm(courses):
        add_course(update_g, course)