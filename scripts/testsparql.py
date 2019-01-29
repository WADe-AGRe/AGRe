from rdflib.namespace import FOAF

from AGRe.settings import GRAPHDB_SECRET, GRAPHDB_APIKEY, GRAPHDB_URL
from SPARQLWrapper import SPARQLWrapper2
import simplejson as json

sparql = SPARQLWrapper2(GRAPHDB_URL)
sparql.setCredentials(GRAPHDB_APIKEY, GRAPHDB_SECRET)

# query = """select ?prop ?subj ?name where {
# 	?uri ?prop ?subj.
#
#     OPTIONAL {
#            ?subj <http://xmlns.com/foaf/0.1/name> ?name .
#     }
#     FILTER(?uri = <http://agre.org/article/85059441988>)
#
# } limit 100 """
#
# sparql.setQuery(query)
#
# ret = sparql.queryAndConvert()
# print(ret.variables)
# for binding in ret.bindings:
#     # each binding is a dictionary. Let us just print the results
#     print("%s: %s (of type %s)" % ("p", binding["prop"].value, binding["prop"].type))
#     print("%s: %s (of type %s)" % ("s", binding[u"subj"].value, binding[u"subj"].type))
#     # print("%s: %s (of type %s)" % ("s", binding["name"].value, binding["name"].type))
#     # print('-------')
#     print(binding.get('name'))


insert_query = """
    INSERT DATA {{ GRAPH <http://agre.com/likes> {{ <{subject}> <{predicate}> <{object}>. }} }}
""".format(subject=FOAF.test, predicate=FOAF.lala, object=FOAF.blabal)

sparql.setQuery(insert_query)
sparql.setMethod('POST')
sparql.query()
