"""
Observation de la distribution des naissances de la population.
"""

import sparql_dataframe
import plotly.express as plt

# L'adresse de DBPedia, où la requête sera adressée.
dbpedia = "http://dbpedia.org/sparql"

# La requête SPARQL.
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
    ?person ?p dbo:Writer ;
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
}
"""

# Faire la requête et stocker ses résultats dans un DataFrame Pandas
df = sparql_dataframe.get(dbpedia, query)
df.head()

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

# Observer les valeurs extrêmes, pour éviter les problèmes futurs et pour pouvoir s'assurer d'une homogénéité des données (et de leur type). On voit qu'une personne, Virgile, a une date dont le format est différent. Puisqu'il s'agit de la seule valeur négative, je l'enlève des données.
df.birthDate.sort_values()

# L'opération que j'utilise pour homogénéiser les valeur consiste à enlever les rows dans lequelles la valeur de birthDate est plus grande que 4 caractères. De cette façon, si les données se trouvaient modifiées pour une raison quelconque, l'opération continuerait à être efficace (contrairement à si j'enlevais la row à partir de son index).
df = df.drop(df[df["birthDate"].str.len() > 4].index)

# Regarder s'il y a des valeurs qui, au contraire, ont moins que 4 caractères.
df[df["birthDate"].str.len() < 4]

# Comme il n'y en a pas, regarder s'il y en a qui commencent par "0".
df[df["birthDate"].str.startswith("0")]

# Une première représentation, des années qui ont le plus de naissances et de celles qui en ont le moins. Quoique cette représentation ne soit pas vraiment appropriée, elle nous permet déjà de voir que les naissances augmentent à mesure qu'on se rapproche de nous dans le temps: l'axe des x a un air approximativement décroissant.
plot = plt.bar(df.birthDate.value_counts())
plot.show()

# Une visualisation du nombres de naissances par années, classées dans l'ordre du temps, qui confirme que la population se situe très largement majoritairement dans les 20e et 19e siècle.
plot = plt.bar(df.birthDate.value_counts().sort_index())
plot.show()

# Mais cette représentation est inappropriée, car les années sans naissances ne sont pas représentées, la représentation du temps est donc déformée, alors que nous voudrions les voir représentées avec la valeur 0. Pour ça, je vais utiliser la fonction "range()" qui permet de créer une séquence de nombre. Il me faut préalablement convertir les éléments de ma liste, qui sont des chaînes de caractères (str) en entier (int).
years = [(int(i), j) for i, j in df.birthDate.value_counts().items()]
years[:10]

# Méthode .sort() pour mettre les années dans l'ordre chronologique (et non pas dans l'ordre de leur valeur -- "j"  dans la liste telle que décrite ci-dessus).
years.sort()

# Le début et la fin de la séquences.
year_start = years[0][0]
year_end = years[-1][0]

# Construire, pour les besoin de la visualisation, la liste de toutes les années, y compris celles sans naissances, en faisant une liste
years_all = [i for i in range(int(year_start), int(year_end) + 1, 1)]

# Déclaration d'une nouvelle liste. Je la remplis en prenant une à une toutes les années de la séquences des années (years_all), et en récupérant le nombre des naissances dans la variable 'years' qui contient les années associées aux nombres de naissances -- variable convertie en dictionnaire (dict()) pour utiliser l'année comme clé permettant de récupérer la valeur associée. Si l'année ne se trouve pas dans la variable 'years', c'est que le nombre de naissances est de 0.
y = []
for i in years_all:
    if i in dict(years):
        y.append((i, dict(years)[i]))
    else:
        y.append((i, 0))

# Print le début et la fin de la liste.
y[:10]
y[-10:]

# Une nouvelle visualisation avec les années vides (0 naissances). Cette visualisation est peu lisible, mais montre avec une évidence extrême la concentration de la population dans les 19e et 20e siècles.
plot = plt.bar(x=[i[0] for i in y], y=[i[1] for i in y])
plot.show()

# Je vais resserrer un peu, et ne me concentrer que sur la période moderniste, que je vais faire commencer en 1860, entre la publication par Baudelaire des 'Fleurs du mal' (1857) et de 'Un peintre de la vie moderne' (1863), deux textes fondamentaux pour la notion de modernité en littérature. On peut voir que les pics de naissances des individus répertoriés de la population se trouvent vers le milieu du siècle, entre les années 40 et les années 60. On peut expliquer cela par au moins deux choses: le fait que Wikipedia présente de façon générale davantage d'informations sur des personnes proches de nous dans le temps; et le fait que la reconnaissance par le champ littéraire, qui est un préalable à la recension d'un individu en tant que "Writer" ou "Poète" est un processus qui s'accomplit avec un certain délai: il est donc assez naturel que les personnes nées depuis les années 1990 soient en nombre aussi faible. À cela on peut encore ajouter deux choses: le fait que l'entrée dans le champ littéraire puisse être tardive dans la vie d'un individu; et le fait que la recherche en littératures à l'université se concentrait jusqu'à récemment sur des auteurices décédées, sur lesquel-les un recul plus important pouvait être pris.
plot = plt.bar(
    x=[i[0] for i in y if i[0] > 1860],
    y=[i[1] for i in y if i[0] > 1860],
)
plot.show()

# Une dernière représentation, par tranche de 10 ans. Pour la construire, je rassemble les années en écartant leur dernier nombre et en le remplaçant par 0 et en additionnant les valeurs des années ainsi regroupées.
w = dict([[i, 0] for i in range(1860, 2001, 10)])
for i in y:
    if i[0] > 1859:
        j = int(f"{str(i[0])[:3]}0")
        w[j] = w[j] + i[1]
plot = plt.bar(x=w.keys(), y=w.values())
plot.show()

# Quoi que fabriquer une 'moyenne' sur la base d'années puisse sembler une opération vide de sens (puisque un année de naissances n'est pas une propriété quantitative) du moins assez artificielle, je vais quand même le faire car il s'agit d'une manière simple de voir, une fois encore, vers où tendent à être né-es les membres de la population. Afin de m'assurer que cela n'est pas complétement absurde, je vais réaliser d'abord un petit test, lequel test montre bien que faire la moyenne des années permet de connaitre le point central autour duquel s'organise les naissances. Par ailleurs, il est toujours possible de reformuler l'année de naissance de façon à en faire une valeur quantitative, par exemple en tant qu'écart entre l'année de naissance de la personne et aujourd'hui ("1920" deviendrait "83 ans d'écart", "1955" deviendrait "78 ans d'écart") -- propriété quantitative puisque contrairement à une année de naissance, il est courant de dire qu'un écart est plus grand ou plus petit qu'un autre.
test_a = [0, 0, 0, 2000]
test_b = [1800, 2000, 0, 0]
test_c = [1900, 1910, 1920, 2000]
for i in test_a, test_b, test_c:
    a = sum(i) / len(i)
    print(a)

# Exécuter la même opération sur mes données. Le résultat obtenu montre encore une fois que la population est largement issue des derniers siècles.
sum([int(i) for i in df.birthDate]) / len(df.birthDate)
