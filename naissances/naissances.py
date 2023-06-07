"""
Observation de la distribution des naissances de la population.
"""

import pandas
import sparql_dataframe

dbp = "http://dbpedia.org/sparql"
query = """
PREFIX dbo: <http://dbpedia.org/ontology/>
PREFIX dbr: <http://dbpedia.org/resource/>

SELECT DISTINCT ?person ?birthDate
WHERE {
  {
  ?person ?p dbr:Novelist ;
            dbo:birthDate ?birthDate .
  }
  UNION
  {
  ?person ?p dbo:Poet ;
            dbo:birthDate ?birthDate .
  }
  UNION
  {
    ?person ?p dbo:Poet ;
            dbo:birthDate ?birthDate .
  }
  UNION
  {
    ?person ?p dbo:Dramatist ;
            dbo:birthDate ?birthDate .
  }
  UNION
  {
    ?person ?p dbo:Translator ;
            dbo:birthDate ?birthDate .
  }
  UNION
  {
    ?person ?p dbo:Librarian ;
            dbo:birthDate ?birthDate .
  }
  UNION
  {
    ?person ?p dbo:Editor ;
            dbo:birthDate ?birthDate .
  }
  UNION
  {
    ?person ?p dbo:Critic ;
            dbo:birthDate ?birthDate .
  }
  UNION
  {
  ?person ?p dbo:Anthologist ;
            dbo:birthDate ?yearOfBirth .
  }
  UNION
  {
    ?person ?p dbo:Writer ;
            dbo:birthDate ?birthDate .
  }
}
"""

dataframe = sparql_dataframe.get(dbp, query)

dataframe.head
