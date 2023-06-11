"""
Observation des réseaux de relations entre les différentes occupations des écrivain-es.
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
import networkx as nx
import matplotlib.pyplot as plt

# L'adresse de DBPedia, où la requête doit être adressée.
sparql = SPARQLWrapper("http://dbpedia.org/sparql")

# Le format du résultat de la requête. L'objet, en python, sera un dictionnaire.
sparql.setReturnFormat(JSON)

# La requête, qui trouve les Writers et leurs occupations.
sparql.setQuery(
    "PREFIX dbo: <http://dbpedia.org/ontology/>\n"
    "PREFIX dbr: <http://dbpedia.org/resource/>\n"
    "\n"
    "SELECT DISTINCT ?person ?occupation\n"
    "WHERE {\n"
    "    ?person ?a dbr:Writer ;\n"
    "            dbo:occupation ?occupation .\n"
    "}\n"
)

# Envoyer la requête.
results = sparql.queryAndConvert()

# Aperçu de la structure de l'objet retourné. Le premier niveau du dictionnaire.
results.keys()

# L'entrée "head" (en-tête), qui décrit la structure des données.
results["head"]

# L'entrée "results".
for i, j in results["results"].items():
    if type(j) == list:
        print(f'results["results"]["{i}"]:', type(j), j[:2])
    elif type(j) == dict:
        print(
            f'results["results"]["{i}"]:', type(j), list(j.keys())[:3]
        )
    else:
        print(f'results["results"]["{i}"]:', type(j), j)

# Seul ce qui se trouve dans ['results']['bindings'] m'intéresse. Je commence par construire un simple liste de tuples selon le schéma (person, occupation).
pairs = [
    (i["person"]["value"], i["occupation"]["value"])
    for i in results["results"]["bindings"]
]
pairs[:3]

# Pour augmenter le nombre de données (la raison apparaitra plus bas, mais repose sur la limitation à 10000 résultats par requête auprès de dbpedia), je fais également des requêtes avec d'autres occupations que Writers.
queries = {}
separated_results = {}
pairs_supp = {}
groups = ["Novelist", "Poet", "Playwright"]
for i in groups:
    queries[i] = SPARQLWrapper("http://dbpedia.org/sparql")
    queries[i].setReturnFormat(JSON)
    queries[i].setQuery(
        "PREFIX dbo: <http://dbpedia.org/ontology/>\n"
        "PREFIX dbr: <http://dbpedia.org/resource/>\n"
        "\n"
        "SELECT DISTINCT ?person ?occupation\n"
        "WHERE {\n"
        f"    ?person ?a dbr:{i} ;\n"
        "            dbo:occupation ?occupation .\n"
        "}\n"
    )
    separated_results[i] = sparql.queryAndConvert()
    pairs_supp[i] = [
        (i["person"]["value"], i["occupation"]["value"])
        for i in separated_results[i]["results"]["bindings"]
    ]
    pairs.extend(pairs_supp[i])


# J'enlève le début des URI, pour ne garder que les noms et les occupations.
clean_pairs = [
    (
        i.replace("http://dbpedia.org/resource/", ""),
        j.replace("http://dbpedia.org/resource/", ""),
    )
    for i, j in pairs
]
clean_pairs[:3]

# Certaines paires me sont inutiles, celles qui ont comme occupation "[nom de la personne]_PersonFunction".
[i for i in clean_pairs if "PersonFunction" in i[1]][:5]

# Je construis donc une nouvelle liste sans ces paires.
non_trivial_pairs = [
    i for i in clean_pairs if "PersonFunction" not in i[1]
]
len(non_trivial_pairs)

# Il y a des répétitions de paires, puisque les Novelist, les Poets, etc., sont souvent aussi catégorisé-es comme Writer. En fait, l'ajout des nouveaux groupes n'a peut-être pas été si utile. [À faire, peut-être: ajouter des occupations liées à la littérature mais plutôt, par exemple, du côté des éditeurices, des bibliothécaires, des critiques. Ou, à l'inverse, des artistes, des musicien-nes, pour voir si les activités annexes sont du même type, s'il y a des recoupements, etc.]
uniqpairs = list(set(non_trivial_pairs))
len(uniqpairs)

# Puisque ce sont les interactions entre occupations qui m'intéresse, je ne vais garder que les données qui concernent les personnes avec au moins deux entrées. Je commence par faire une liste des noms.
names = [i for i, j in uniqpairs]
names[:3]

names_repeated = [i for i in names if names.count(i) > 1]

# Le nombre total d'occurences de noms.
len(names)

# Le nombre d'occurences de noms qui apparaissent plusieurs fois.
len(names_repeated)

# Le nombre de noms qui apparaissent plusieurs fois. (Les données sont plus minces que ce que je pouvais espérer et il faudrait probablement opter pour une autre manière d'interroger DBPedia.)
len(set(names_repeated))

# Les premiers noms.
uniqnames = list(set(names_repeated))
uniqnames.sort()
for i in uniqnames[:5]:
    print(i)

# Puisque chaque nom est unique, je peux utiliser les noms comme clés pour un dictionnaire. La valeur qui y sera attribuée sera une liste des occupations.
d = {}
for i in uniqnames:
    d[i] = []

# Observer le dictionnaire avant d'y mettre les données.
for i in list(d.items())[:3]:
    print(i)

# Iterate sur les éléments de la variable clean_pairs qui contient les paires person/occupation, et append la liste des occupations de la personne
for name, occupation in uniqpairs:
    if name in uniqnames:
        d[name].append(occupation)

# Observer une partie du dictionnaire.
for i in list(d.items())[:3]:
    print(i)

# L'occupation "Writer" est très présente C'est pour cela que j'ai fait des requêtes supplémentaires. Cela a permis d'ajouter un certain nombre d'entrées.
len([i for i, j in list(d.items()) if "Writer" not in j])

# Mais la question se pose, tout de même, de l'intérêt ici de l'occupation "Writer" (qui est aussi, dans DBPedia, une méta-occupation). Je préfère la retirer, étant donné que les poète-sses, les romancier-ères, les dramaturges, sont aussi des écrivain-es.
data_to_pop = [
    i for i in list(d.keys()) if len(d[i]) < 3 and "Writer" in d[i]
]
len(data_to_pop)

for i in data_to_pop:
    d.pop(i)

# Le nombre d'entrées restantes dans le dictionnaires.
len(d)

# Il va désormais s'agir d'explorer les relations entre occupations en utilisant l'analyse de réseaux. Pour créer un réseau reliant les occupations les unes aux autres, il faut d'abord créer des relations entre occupations, des nouvelles paires occupation/occupation.
occ_pairs = []
for name, occupations in d.items():
    for occ_one in occupations:
        a = occupations.copy()
        a.remove(occ_one)
        for occ_two in a:
            p = (occ_one, occ_two)
            occ_pairs.append(p)

# Certaines paires ont plusieurs occurences: quand deux occupations cohabitent chez plusieurs personnes.
[i for i in occ_pairs if 'Biographer' in i][:10]

# Plutôt que d'avoir ainsi des doublons, on peut représenter le nombre d'occurences comme la force de la relation.
c = Counter(occ_pairs)
relations = [(i[0], i[1], j) for i, j in list(c.items())]
relations[:10]

# Créer un graphe avec ces relations.
G = nx.Graph()
for relation in relations:
    node1, node2, weight = relation
    G.add_edge(node1, node2, weight=weight)

G.

# Tracer le graphe
pos = nx.spring_layout(G)  # Positions des nœuds

# Récupérer les poids des arêtes
edge_weights = [relation[2] for relation in rel[:10]]

# Tracer les arêtes avec une épaisseur basée sur les poids
nx.draw_networkx_edges(G, pos, width=edge_weights, edge_color='gray')

# Tracer les nœuds et les étiquettes
nx.draw_networkx_nodes(G, pos, node_color='lightblue', node_size=800)
nx.draw_networkx_labels(G, pos, font_size=12)

# Afficher le graphe
plt.axis('off')
plt.show()
