"""
Observation de la distribution des naissances de la population.
"""

import pandas
import sparql_dataframe

# L'adresse de DBPedia, où la requête sera adressée
dbpedia = "http://dbpedia.org/sparql"

# La requête SPARQL
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
            dbo:birthDate ?birthDate .
  }
  UNION
  {
    ?person ?p dbo:Writer ;
            dbo:birthDate ?birthDate .
  }
}
"""

# Stocker les résultat de la requête dans un DataFrame Pandas
df = sparql_dataframe.get(dbpedia, query)

# Enlever le début des URI pour n'avoir que les noms.
df.replace(
    r"http://dbpedia\.org/resource/(.*)",
    "\\1",
    regex=True,
    inplace=True,
)

# Enlever les jours et les mois pour ne garder que les années.
df["birthDate"].replace(
    r"^([0-9]{4})-[0-9]{2}-[0-9]{2}", "\\1", regex=True, inplace=True
)

# Observer les valeurs extrêmes, pour éviter les problèmes futurs et pour pouvoir s'assurer d'une homogénéité des données (et de leur type).
# On voit qu'une personne, Virgile, a une date dont le format est différent. Puisqu'il s'agit de la seule valeur négative, je l'enlève des données.
df.birthDate.sort_values()

# L'opération que j'utilise pour homogénéiser les valeur consiste à enlever les rows dans lequelles la valeur de birthDate est plus grande que 4 caractères.
new_df = df.drop(df[df['birthDate'].str.len() > 4].index)

# Regarder s'il y a des valeurs qui, au contraire, ont moins que 4 caractères.
df[df['birthDate'].str.len() < 4]

# Comme il n'y en a pas, regarder s'il y en a qui commencent par "0".
df[df['birthDate'].str.startswith('0')]

