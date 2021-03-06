from rdflib import Graph, Literal, URIRef
from rdflib.namespace import RDF, SKOS, FOAF
from rdflib.plugins.stores import sparqlstore
import tqdm

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
s_edu_org = URIRef('http://schema.org/EducationalOrganization')
s_book = URIRef('http://schema.org/Book')
s_book_format_type = URIRef('http://schema.org/BookFormatType')
s_course = URIRef('http://schema.org/Course')
s_course_instance = URIRef('http://schema.org/CourseInstance')


print(SKOS.Concept)
course = URIRef('https://www.coursera.org/learn/regression-modeling-practice')

# update_g.add( (course, RDF.type, s_course) )

# print(query_g.serialize(format='turtle').decode())

def add_course(g, course):
    uri = URIRef(course['link'])

    g.add((uri, RDF.type, s_course))
    g.add((uri, RDF.type, s_course_instance))

    if 'title' in course:
        name = URIRef('http://schema.org/name')
        g.add((uri, name, Literal(course['title'])))

    if 'instructors' in course:
        s_instructor = URIRef('http://schema.org/instructor')
        for instructor in course['instructors']:
            g.add((uri, s_instructor, URIRef(instructor['url'])))
            
    if 'language' in course:
        inLanguage = URIRef('http://schema.org/inLanguage')
        g.add((uri, inLanguage, Literal(course['language']['text'])))

    if 'provider' in course:
        s_offeredBy = URIRef('http://schema.org/offeredBy')
        g.add((uri, s_offeredBy, URIRef(course['provider']['url'])))

    if 'universities' in course:
        s_provider = URIRef('http://schema.org/provider')
        for university in course['universities']:
            g.add((uri, s_provider, URIRef(university['url'])))

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

    if 'categories' in course:
        s_category = URIRef('http://schema.org/about')
        for category in course['categories']:
            g.add((uri, s_category, URIRef(category['url'])))

    if 'description' in course:
        description = URIRef('http://schema.org/description')
        g.add((uri, description, Literal(course['description'])))

    if 'rating' in course:
        rating = URIRef('http://schema.org/aggregateRating')
        g.add((uri, rating, Literal(course['rating'])))

def add_generic(g, l, type=None):
    description = URIRef('http://schema.org/description')
    name = URIRef('http://schema.org/name')
    for thing in tqdm.tqdm(l):
        uri = URIRef(thing['link'])
        if type is not None:
            g.add((uri, RDF.type, type))
        if 'description' in thing:
            g.add((uri, description, Literal(thing['description'])))
        if 'name' in thing:
            g.add((uri, name, Literal(thing['name'])))

def add_category_names(g, courses):
    categories = set()
    name = URIRef('http://schema.org/name')

    for course in tqdm.tqdm(courses):
        if 'categories' in course:
            for category in course['categories']:
                category_url = category['url']
                if category_url not in categories:
                    categories.add(category_url)
                    g.add((URIRef(category_url), name, Literal(category['text'])))

def add_enteties_from_courses(g, courses):
    instructors = dict()
    universities = set()
    providers = set()
    countries = set()
    worksFor = URIRef('http://schema.org/worksFor')
    s_country = URIRef('http://schema.org/Country')
    name = URIRef('http://schema.org/name')

    for course in tqdm.tqdm(courses):
        if 'categories' in course:
            for category in course['categories']:
                g.add((URIRef(category['url']), name, Literal(category['text'])))

        if 'country' in course:
            country = course['country']['url']
            country_ref = URIRef(country)
            country_lit = Literal(course['country']['text'])
            if country not in countries:
                countries.add(country)
                g.add((country_ref, RDF.type, s_country))
                g.add((country_ref, name, country_lit))

        if 'universities' in course:
            for uni in course['universities']:
                uni_url = uni['url']
                uni_ref = URIRef(uni_url)
                if uni_url not in universities:
                    g.add((uni_ref, RDF.type, s_edu_org))
                    universities.add(uni_url)

        if 'provider' in course:
            provider_url = course['provider']['url']
            provider_ref = URIRef(provider_url)
            if provider_url not in universities:
                g.add((provider_ref, RDF.type, s_organization))
                providers.add(provider_url)

        if 'instructors' in course:
            for instructor in course['instructors']:
                instructor_ref = URIRef(instructor['url'])
                if instructor['url'] not in instructors:
                    g.add(( instructor_ref, RDF.type, s_person))
                    instructors[instructor['url']] = set()

                if 'universities' in course:
                    for uni in course['universities']:
                        uni_url = uni['url']
                        uni_ref = URIRef(uni_url)
                        if uni_url not in instructors[instructor['url']]:
                            g.add((instructor_ref, worksFor, uni_ref))
                            instructors[instructor['url']].add(uni_url)



if __name__ == "__main__":
    import json

    with open('data/mooc_list_courses_detailed.json', 'r') as f:
        courses = json.load(f)

    courses = courses

    add_enteties_from_courses(update_g, courses)
    for course in tqdm.tqdm(courses):
        add_course(update_g, course)

    add_category_names(update_g, courses)

    files = ['data/mooc_list_instructors.json', 'data/mooc_list_universities.json', 'data/mooc_list_providers.json', 'data/mooc_list_courses_detailed.json']
    for file in files:
        with open(file, 'r') as f:
            l = json.load(f)
        add_generic(update_g, l)
