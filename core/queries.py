from SPARQLWrapper import SPARQLWrapper2

from AGRe.settings import GRAPHDB_SECRET, GRAPHDB_APIKEY, GRAPHDB_URL

query_graph = SPARQLWrapper2(GRAPHDB_URL)
query_graph.setCredentials(GRAPHDB_APIKEY, GRAPHDB_SECRET)

insert_graph = SPARQLWrapper2(GRAPHDB_URL + '/statements')
insert_graph.setCredentials(GRAPHDB_APIKEY, GRAPHDB_SECRET)

RESOURCE_DETAILS_QUERY = \
    """select ?prop ?subj ?name where {{ 
	?uri ?prop ?subj.
    
    OPTIONAL {{
           ?subj <http://xmlns.com/foaf/0.1/name> ?name .
    }}
    FILTER(?uri = <{uri}>)
    
}} limit 100 """

INSERT_QUERY = """
    INSERT DATA {{ GRAPH <http://agre.com/{graph}> {{ <{subject}> <{predicate}> <{object}>. }} }}
"""

DELETE_REVIEW_QUERY = """
DELETE {{?s ?p ?o}} WHERE {{
    ?s ?p ?o .
    <{user}> ?p <{resource}>.
}}
"""
