"""
Observation des relations entre (1) les différentes occupations et (2) des relations entre occupations et mouvements auxquels sont rattaché-es les poéte-sses et écrivain-es.
"""

import sparql_dataframe
import plotly.express as plt

# Adresser la requête à DBPedia.
dbpedia = "http://dbpedia.org/sparql"

# La requête SPARQL.

query = (
    "PREFIX dbo: <http://dbpedia.org/ontology/>\n"
    "PREFIX dbp: <http://dbpedia.org/property/>\n"
    "\n"
    "SELECT ?person ?occupation ?movement\n"
    "WHERE {\n"
    "    {\n"
    "    ?person a dbo:Writer ;\n"
    "            dbo:occupation ?occupation ;\n"
    "            dbo:movement ?movement .\n"
    "    }\n"
    "    UNION\n"
    "    {\n"
    "    ?person a dbo:Poet ;\n"
    "            dbo:occupation ?occupation ;\n"
    "            dbo:movement ?movement .\n"
    "    }\n"
    "    UNION\n"
    "    {\n"
    "    ?person a dbr:Novelist ;\n"
    "            dbo:occupation ?occupation ;\n"
    "            dbo:movement ?movement .\n"
    "    }\n"
    "    UNION\n"
    "    {\n"
    "    ?person a dbo:Dramatist ;\n"
    "            dbo:occupation ?occupation ;\n"
    "            dbo:movement ?movement .\n"
    "    }\n"
    "}\n"
)

df = sparql_dataframe.get(dbpedia, query)
df.head()


df.replace(
    r"http://dbpedia\.org/(?:resource|ontology)/(.*)",
    "\\1",
    regex=True,
    inplace=True,
)
