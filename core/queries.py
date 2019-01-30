from SPARQLWrapper import SPARQLWrapper2

from AGRe.settings import GRAPHDB_SECRET, GRAPHDB_APIKEY, GRAPHDB_URL

query_graph = SPARQLWrapper2(GRAPHDB_URL)
query_graph.setCredentials(GRAPHDB_APIKEY, GRAPHDB_SECRET)

insert_graph = SPARQLWrapper2(GRAPHDB_URL + '/statements')
insert_graph.setCredentials(GRAPHDB_APIKEY, GRAPHDB_SECRET)
from core.ontology import ThingONT, ONTOLOGY_BASE_URL

RESOURCE_DETAILS_QUERY = """
    select ?prop ?subj ?name where {{ 
        ?uri ?prop ?subj.
        
        OPTIONAL {{
               ?subj <""" + ThingONT.NAME.toPython() + """> ?name .
        }}
        FILTER(?uri = <{uri}>)
        
    }} limit 100 """

INSERT_QUERY = """
    INSERT DATA {{ GRAPH <""" + ONTOLOGY_BASE_URL + """{graph}> {{ <{subject}> <{predicate}> <{object}>. }} }}
"""

DELETE_REVIEW_QUERY = """
DELETE WHERE {{
    <{user}> ?p <{resource}>.
}}
"""

UPDATE_REVIEW_QUERY = """
    WITH <"""+ ONTOLOGY_BASE_URL + """{graph}>
    DELETE {{ ?s ?p ?o }}
    INSERT {{ ?s ?p {value} }}
    WHERE
      {{ ?s ?p ?o . 
             FILTER (?s = <{subject}> && ?p = <{predicate}>) 
  }}
"""
