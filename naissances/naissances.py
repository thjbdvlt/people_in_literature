"""
Observation de la distribution des naissances de la population.
"""

import sparql_dataframe

# import pandas
# import plotly.express as plt

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
df = df.drop(df[df["birthDate"].str.len() > 4].index)

# Regarder s'il y a des valeurs qui, au contraire, ont moins que 4 caractères.
df[df["birthDate"].str.len() < 4]

# Comme il n'y en a pas, regarder s'il y en a qui commencent par "0".
df[df["birthDate"].str.startswith("0")]

# Les années qui ont le plus de naissances, et celles qui en ont le moins.
a = df.birthDate.value_counts()
a

# Une visualisation du nombres de naissances par années.
df["birthDate"].value_counts().sort_index().plot(kind="bar")

# Mais cette représentation est inappropriée, car les années sans naissances ne sont pas représentées -- la représentation du temps est donc déformée --, alors que nous voudrions les voir représentées avec la valeur 0.
years = [(int(i), j) for i, j in df.birthDate.value_counts().items()]
years[:10]

years_a = [i[0] for i in years]
years_a.sort()


year_start = years_a[0]
year_end = years_a[-1]

# Construire, pour les besoin de la visualisation, la liste de toutes les années, y compris celles sans naissances, en faisant une liste
years_all = [i for i in range(int(year_start), int(year_end) + 1, 1)]

y = []
for i in years_all:
    if i in dict(years):
        y.append((i, dict(years)[i]))
    else:
        y.append((i, 0))
