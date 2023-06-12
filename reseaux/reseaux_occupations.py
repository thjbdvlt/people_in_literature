"""
Observation des réseaux de relations entre les différentes occupations des écrivain-es. Continuation nocturne du carnet "reseaux_occupations".
"""

from SPARQLWrapper import SPARQLWrapper, JSON
from collections import Counter
import networkx as nx
import matplotlib.pyplot as plt
import re

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
groups = ["Novelist", "Poet", "Playwright"]
for i in groups:
    q = SPARQLWrapper("http://dbpedia.org/sparql")
    q.setReturnFormat(JSON)
    q.setQuery(
        "PREFIX dbo: <http://dbpedia.org/ontology/>\n"
        "PREFIX dbr: <http://dbpedia.org/resource/>\n"
        "\n"
        "SELECT DISTINCT ?person ?occupation\n"
        "WHERE {\n"
        f"    ?person ?a dbr:{i} ;\n"
        "            dbo:occupation ?occupation .\n"
        "}\n"
    )
    res = sparql.queryAndConvert()
    p = [
        (i["person"]["value"], i["occupation"]["value"])
        for i in res["results"]["bindings"]
    ]
    pairs.extend(p)


# J'enlève le début des URI, pour ne garder que les noms et les occupations.
clean_pairs = [
    (
        i.replace("http://dbpedia.org/resource/", ""),
        # Je passe les occupations en lowercase pour faciliter
        # les recherches de caractères.
        j.replace("http://dbpedia.org/resource/", "").lower(),
    )
    for i, j in pairs
]
clean_pairs[:3]

# Certaines paires me sont inutiles, celles qui ont comme occupation "[nom de la personne]_PersonFunction".
[i for i in clean_pairs if "personfunction" in i[1]][:5]

# Je construis donc une nouvelle liste sans ces paires.
non_trivial_pairs = [
    i for i in clean_pairs if "personfunction" not in i[1]
]
len(non_trivial_pairs)

# Il y a des répétitions de paires, puisque les Novelist, les Poets, etc., sont souvent aussi catégorisé-es comme Writer. En fait, l'ajout des nouveaux groupes n'a peut-être pas été si utile. [À faire, peut-être: ajouter des occupations liées à la littérature mais plutôt, par exemple, du côté des éditeurices, des bibliothécaires, des critiques. Ou, à l'inverse, des artistes, des musicien-nes, pour voir si les activités annexes sont du même type, s'il y a des recoupements, etc.]
uniqpairs = list(set(non_trivial_pairs))
len(uniqpairs)

# Je vais aussi éliminer les occupations pour lesquelles il y a une seule occurrence.
occupations = [j for i, j in uniqpairs]
notuniqocc = []
count = Counter(occupations)
for i, j in count.items():
    if j > 1:
        notuniqocc.append(i)
uniqpairs = [(i, j) for i, j in uniqpairs if j in notuniqocc]
uniqpairs[:3]

# Puisque ce sont les interactions entre occupations qui m'intéresse, je ne vais garder que les données qui concernent les personnes avec au moins deux entrées. Je commence par faire une liste des noms.
names = [i for i, j in uniqpairs]
names[:3]

# Le nombre total d'occurences de noms.
len(names)

# Le nombre d'occurences de noms qui apparaissent plusieurs fois.
names_repeated = [i for i in names if names.count(i) > 1]
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
len([i for i, j in list(d.items()) if "writer" not in j])

# Mais la question se pose, tout de même, de l'intérêt ici de l'occupation "Writer" (qui est aussi, dans DBPedia, une méta-occupation). Je préfère la retirer, étant donné que les poète-sses, les romancier-ères, les dramaturges, sont aussi des écrivain-es. Puisque les réseaux que je vais construire sont des réseaux d'occupations annexes à l'écriture, il est inutile que tous les points du réseaux soient reliés à un point central "écriture": c'est leur intégration au graphe qui constitue cette relation commune.
data_to_pop = [
    i for i in list(d.keys()) if len(d[i]) < 3 and "writer" in d[i]
]
len(data_to_pop)
for i in data_to_pop:
    d.pop(i)

# Enlever également des entrées restantes l'item 'writer'.
for i, j in d.items():
    if "writer" in j:
        d[i].pop(d[i].index("writer"))

# Le nombre d'entrées restantes dans le dictionnaires.
len(d)

# Il va désormais s'agir d'explorer les relations entre occupations en utilisant l'analyse de réseaux. Pour le début de l'exploration, je vais simplifier les données et regarder les relations d'occupations uniquement, en excluant les personnes des graphes, ou plus exactement: je vais créer un graphe avec un seul type de noeud, les occupations, et en réduisant les personnes à des nombres qui renforceront le poids des relations entre les noeuds-occupations. Plus une relation entre deux occupations (deux noeuds) sera répandue, et plus le lien entre elles sera considéré comme lourd.
# Pour créer un réseau reliant les occupations les unes aux autres, il faut d'abord créer des relations entre occupations, des nouvelles paires occupation/occupation.
occ_pairs = []
for name, occupations in d.items():
    for occ_one in occupations:
        for occ_two in occupations:
            if occ_two != occ_one:
                o = [occ_one, occ_two]
                o.sort()
                p = (o[0], o[1])
                occ_pairs.append(p)

# Certaines paires ont plusieurs occurences: quand deux occupations cohabitent chez plusieurs personnes.
[i for i in occ_pairs if "biographer" in i and "novelist" in i][:10]

# Plutôt que d'avoir ainsi des doublons, on peut représenter le nombre d'occurences comme la force de la relation. Observer les relations avec le plus d'occurences.
count = Counter(occ_pairs)
count.most_common()[:10]

def faire_un_graphe_simple_most_common(relations, nb: str):
    """
    Construit un graphe (avec visualisation) des relations les plus répandues.
    En paramètre: une liste de relations et le nombre de relations à sélectionner.
    """
    # Compter les relations.
    count = Counter(relations)
    relations_selected = [
        (i[0], i[1], j) for i, j in list(count.most_common()[:nb])
    ]
    # Construire le graphe
    g = nx.Graph()
    for relation in relations_selected:
        node1, node2 = relation[0], relation[1]
        g.add_edge(node1, node2)
    # Tracer le graphe.
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos, alpha=0.6, node_size=10)
    nx.draw_networkx_edges(g, pos, alpha=0.5, edge_color='gray')
    nx.draw_networkx_labels(g, pos, alpha=0.7, font_size=9)

    plt.figure(figsize=(20, 10))
    plt.show()


# Construction d'un graphe avec ces paires d'occupations.
faire_un_graphe_simple_most_common(occ_pairs, 10)

# Cette première visualisation nous montre déjà des choses intéressantes, quoi que relativement triviales. Le graphe est séparé en deux clusters: les écritures littéraires et le journalisme d'un côté, les activités liées au cinéma ou à la télévision de l'autre. Ce premier découpage est intéressant du fait de l'annexion de l'occupation journalistique aux écritures littéraires. Le journalisme, du point de vue de ce graphe, peut bien apparaître, d'une part, comme un métier d'appoint typique des littérateurices; et d'autre part comme un espace d'expression publique dont les littérateurices se saisissent davantage que d'autres groupes d'écrivain-es. Surtout, ce découpage en deux clusters est moins un découpage entre deux types d'activités qu'entre deux "mondes de l'art" au sens de Howard Becker. Car, d'un point de vue technique, technologique, physiologique, etc., l'écriture pour la télévision est bien plus proche de l'écriture d'une pièce de théâtre que de l'acting. À moins qu'on entende par "écriture" un ensemble large de pratiques intégrant les formes de collaboration (réécrire sous la contrainte des équipes de tournages, discuter, reprendre des parties de scripts existants, etc.), auquel cas "l'écriture" du screenwriter a en effet beaucoup à voir avec l'acting, puisqu'il s'agit essentiellement d'une activité consistant à employer les mêmes critères et à cotoyer les mêmes personnes: celles et ceux du monde du cinéma.
# Par ailleurs, on peut voir, dans le cluster lié au cinéma, que les nodes 'actor' et 'television writer' sont très éloigné, tandis que les nodes 'actor' et 'screen writer' (l'écriture pour le cinéma) sont plus rapprochés: on peut ainsi faire l'hypothèse que le monde de la télévision n'est pas structuré avec la même souplesse que le monde du cinéma, et que l'assignation à des rôles professionnels définis y est plus forte. Toutefois, il faut fortement relativiser cette hypothèse: ces résultats sont probablement liés au biais induit par la sélection des paires d'occupations les plus courantes.

# La sociologie des Mondes de l'art de Howard Becker semble d'ailleurs particulièrement approprié ici, davantage, par exemple, que la théorie des champs de Bourdieu (qui conçoit le fonctionnement du champ littéraire comme un ensemble de positions). Becker, en effet, décrit les mondes de l'art comme des "réseaux de coopérations", et le succès de la réalisation d'une oeuvre d'art est en fait moins la conséquence des 'talents' de l'artiste que de la capacité de l'artiste à coopérer avec les autres membres du réseaux. Les artistes doivent apprendre à manier les jeux de langages et les critères des autres corps professionnels avec lesquels iels sont amené-es à collaborer. Il leur est donc naturellement plus facile de jouer elleux-mêmes ces rôles (occupations).

# Je produis une autre visualisation avec un nombre plus grand de données sélectionnées pour construire le graphe, pour observer ce qu'il se passe si l'on modifie progressivement le grain avec lequel on observe ces données. Les deux clusters sont toujours séparés. De nouveaux points apparaissent des deux côtés, et se montre particulièrement intéressant dans le cluster littéraire. Le rôle de traduction est associé aux poètes (je commenté cela dans un autre carnet), et les romancier-ères sont associé-es à deux nouveaux noeuds: (1) l'écriture de short-stories (de nouvelles), qui apparait ainsi comme une forme apparentée au roman, écrite avec les mêmes logiques; (2) l'écriture essayiste, ce qui n'est pas étonnant étant donné que certains des romans modernes les plus importants du 20e siècle sont souvent perçues sous le prisme de l'essayisme (par exemple Proust ou Musil). Tout cela montre le statut particulier du roman dans l'histoire littéraire moderne: forme hybride à la fois narrative et réflexive, forme souple et "totale" qui a la capacité d'absorber tous les autres genres littéraires (ici: novelist est le seul point qui est connecté à tous les autres points littéraires: poet, playwright, essayist, short-story).
faire_un_graphe_simple_most_common(occ_pairs, 20)

# En augmentant encore un peu le nombre de relations à intégrer dans le graphe jusqu'à relier les deux clusters, on peut voir que les occupations qui relient les deux clusters sont screenwriter et playwright, l'écriture pour le théâtre et l'écriture pour le cinéma: deux activités d'écriture qui incluent des formes de coopération avec et d'anticipation à l'égard des autres participant-es au monde de l'art concerné, par exemple au sujet de la manière dont le texte pourra être interprêté par les comédien-nes, mis en scène, produit. Les contraintes d'écritures (format, durée, etc.) relatives au monde chargé de diffuser l'oeuvre sont ainsi bien plus proches pour le théâtre et le cinéma qu'entre théâtre et roman (ni les romancier-ères ni les poète-sses n'ont à se demander si leur oeuvre pourra être matériellement fabriquée et mise en scène: cela est hors de leur écriture, mais fait intégralement partie de l'écriture des screenwriters et des playwrights).
faire_un_graphe_simple_most_common(occ_pairs, 23)

# Construire un graphe avec toutes les données. Impossible à visualiser, mais à partir duquel faire des recherches et produire des sous-graphes à visualiser.
#
# # Commencer par placer les nodes
# g = nx.Graph()
# for name, occupation in uniqpairs:
#     node_person = (name, {"node_type": "P"})
#     node_occupation = (occupation, {"node_type": "O"})
#     g.add_nodes_from([node_person])
#     g.add_nodes_from([node_occupation])
#     g.add_edge(name, occupation)
#
# # Puis les edges, avec un attribut "poids" (weight): le nombre de paires de ces occupations.
# count = Counter(occ_pairs).items()
# for occs, nb in count:
#     g.add_edges_from([(occs[0], occs[1], {"weight": nb})])
#
# start_node = "poet"
# end_node = "actor"
# a = nx.shortest_path_length(g, start_node, end_node)
# a
# #
# reachable_nodes = [
#     node
#     for node in g.nodes()
#     if nx.has_path(g, node, end_node)
#     and nx.has_path(g, start_node, node)
#     and nx.shortest_path_length(g, start_node, node) <= 2
#     and nx.shortest_path_length(g, node, end_node) <= 2
# ]
# len(reachable_nodes)
# len([i for i in g.nodes()])
