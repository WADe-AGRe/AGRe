from SPARQLWrapper import SPARQLWrapper2

from AGRe.settings import GRAPHDB_SECRET, GRAPHDB_APIKEY, GRAPHDB_URL

sparql = SPARQLWrapper2(GRAPHDB_URL)
sparql.setCredentials(GRAPHDB_APIKEY, GRAPHDB_SECRET)

RESOURCE_DETAILS_QUERY = \
    """select ?prop ?subj ?name where {{ 
	?uri ?prop ?subj.
    
    OPTIONAL {{
           ?subj <http://xmlns.com/foaf/0.1/name> ?name .
    }}
    FILTER(?uri = <{uri}>)
    
}} limit 100 """
