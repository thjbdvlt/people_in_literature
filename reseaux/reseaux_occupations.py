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
uniqpairs = [(i, j) for i, j in uniqpairs if j != "writer"]

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
    plt.figure(figsize=(30, 30))
    pos = nx.spring_layout(g)
    nx.draw_networkx_nodes(g, pos, alpha=0.6, node_color="gainsboro")
    nx.draw_networkx_edges(g, pos, alpha=0.5, edge_color="gray")
    nx.draw_networkx_labels(g, pos, alpha=0.7, font_size="medium")

    fp = f"img/most_common_{nb}.svg"
    plt.savefig(fp, format="svg")
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

# Je vais maintenant construire un graphe avec toutes les données, impossible à visualiser mais que je pourrai interroger et à partir duquel réaliser des 'sous-graphe' qu'il sera possible de visualiser.
g = nx.Graph()

# Les nodes: tous les noms de personnes, toutes les occupations.
all_names = [(name, {"type": "P"}) for name, occupation in uniqpairs]
all_occs = [
    (occupation, {"type": "O"}) for name, occupation in uniqpairs
]
g.add_nodes_from(all_names + all_occs)

# Les edges sans poids: les relations person-occupation.
g.add_edges_from(uniqpairs)

# Puis les edges avec un attribut "poids" (weight): les relations occupation-occupation (le poids est égal à la fréquence de cette relation = de la coprésence de ces deux occupation chez les personnes). (Cela pourrait probablement être calculé dans le graphe, mais le faire ainsi est facile et rapide.)
count = Counter(occ_pairs).items()
for occs, nb in count:
    g.add_edges_from([(occs[0], occs[1], {"weight": nb})])

# Dans le graphe précédent, les deux activités les plus éloignées sont 'comedian' et 'translator'. Quels sont les points qui les relient le plus directement?


def relier(
    start_node: str, end_node: str, max_steps: int, mini_weight: int
):
    """
    Trouver les nodes qui relient le plus directement deux nodes.

    Comme paramètres: les deux nodes (start_node/end_node), le maximum de steps (de nodes intermédiares), et le poids minimum des edges qui permettent de relier ces deux nodes.
    """
    connecting_nodes = []
    for path in nx.all_simple_paths(
        g, source=start_node, target=end_node, cutoff=max_steps
    ):
        if all(
            g.get_edge_data(path[i], path[i + 1]).get("weight", 0)
            >= mini_weight
            for i in range(len(path) - 1)
        ):
            connecting_nodes.extend(path)
    connecting_nodes = [
        i
        for i in list(set(connecting_nodes))
        if i not in [start_node, end_node]
    ]
    return connecting_nodes


# Les trajets les plus courts entre les deux activités les plus éloignés de notre dernière visualisation.
relier("translator", "comedian", 2, 1)

# Le résultat ci-dessus est difficile à interpréter. J'augmente le poids minimum des edges pour trouver, en le diminuant progressivement, le node qui relie ces deux nodes, avec un trajets plus grand (4) et le poids le plus important possible.
n = 100
while len(relier("translator", "comedian", 2, n)) < 1:
    n = n - 1
print("poids:", n, "->", relier("translator", "comedian", 2, n))

# On a déjà vu que l'occupation journalist était en relation significative avec les occupations littéraires, et je pense qu'on peut imaginer sans trop de difficultés qu'elle est aussi en relation avec le monde du cinéma. Le journalisme pourrait ainsi être un métier d'appui, y compris pour des individus exerçant des professions non-liées à l'écrit. Trouver les noms des personnes ayant les occupations translator et comedian. Il deux personnes: la première, Robert Beauvais, est un comédien et auteur français, qui a écrit des romans ainsi que leur adaptatin au cinéma. L'article Wikipedia ne nous dit rien de son activité journalistique. La seconde personne, en revanche, Rudy Badil, s'est reconvertie dans le journalisme après avoir du abandonner une carrière dans la comédie en raison de problème d'anxiété liés au fait de monter sur scène. Dans ce cas, le journalisme apparaît moins comme un métier d'appui possible pour des non-professionnels des médias que comme une possibilité de repli.
for i in g.nodes():
    if g.nodes[i]["type"] == "P":
        if g.has_edge(i, "journalist"):
            if g.has_edge(i, "comedian"):
                print(i)

# Idem avec un trajet plus long. Le résultat représente les occupations intermédiaires entre la 'translator' et 'comedian'.
n = 100
while len(relier("translator", "comedian", 3, n)) < 1:
    n = n - 1
print("poids:", n, "->", relier("translator", "comedian", 3, n))

# Si, parmi les littérateurices, novelist semblait être l'occupation la plus connectée avec les autres activités littéraires, il se pourrait que poet soit une occupation avec une plus grande extension, qui connecte (indirectement) des pratiques ordinairement plus éloignées. (Je laisse actor de côté, très proche de comedian.)
# Je me propose pour la fin de ce carnet d'explorer cette question de la  'connectivité' des pratiques poétiques.
# Je commence par comparer les degrés de centralité de l'occupation poet et de l'occupation novelist
degree = dict([(d[0], {"degree": d[1]}) for d in nx.degree(g)])
for i in ("poet", "novelist"):
    print(f"{i}:", degree[i])


# Je compare maintenant le nombre d'arêtes qui relie 'poet' et 'novelist' aux autres nodes. Si les poètes ont une plus grande connectivité à d'autres activités (que ce soit par esprit d'avant-garde ou par précarité), la proportion de nodes 'occupations' devrait être plus élevé que celle de nodes 'person' parmi les edges de 'poet' que de 'novelist'. Quoi que la différence soit légère, le résultat de la boucle suivante va dans ce sens: les poète-sses ont un plus grand nombre d'occupations annexes (une plus grande variété), non seulement proportionnellement mais également en nombre absolu (la population de poète est plus basse, mais le nombre d'occupations annexes est plus haut).
def proportion(valeur: int, total: int, arrondi: int = 2):
    """
    Fonction pour print une valeur, un total, et le rapport entre les deux.
    """
    print(f"{valeur}/{total} ({round(valeur / total, 2)})")


for o in ["poet", "novelist"]:
    t = degree[o]["degree"]
    a = len([i for i in g[o] if g.nodes[i]["type"] == "O"])
    print(o)
    proportion(a, t)

# Je place les mêmes données, pour chaque occupations, dans un dictionnaire.
c = {}
for o in [i for i in g.nodes() if g.nodes[i]["type"] == "O"]:
    c[o] = {}
    c[o]["T"] = degree[o]["degree"]
    c[o]["O"] = len([i for i in g[o] if g.nodes[i]["type"] == "O"])
    c[o]["P"] = c[o]["T"] - c[o]["O"]

# Je crée, pour chaque node, une nouvelle entrée dans le dictionnaire, à laquelle j'attribue, comme valeur, la somme des edges connectant les nodes occupations (auxquels le node est lié) à d'autres nodes.
for o in c.keys():
    c[o]["X"] = 0
    for node in g[o]:
        if g.nodes[node]["type"] == "O":
            if g.has_edge(o, node):
                c[o]["X"] += c[node]["O"]

# Les occupations avec le plus de connections directe (lenght=1) avec d'autres occupations.
a = [(c[i]["X"], i) for i in c.keys() if c[i]["X"] != 0]
a.sort()
a.reverse()
a[:10]

# Les occupations avec le plus de connections indirecte (lenght=2) avec d'autres occupations.
b = [(c[i]["O"], i) for i in c.keys() if c[i]["O"] != 0]
b.sort()
b.reverse()
b[:10]


def deuxcolonnes(a: list, b: list, n: int):
    """
    Présente le haut de deux liste côte à côte.
    """
    # for L in (a, b):
    #     all.extend([j for i, j in L[:10]])
    all = [j for i, j in a[:10]] + [j for i, j in b[:10]]
    all = []
    for L in (a, b):
        all.extend([j for i, j in L[:10]])
    max = 0
    for e in all:
        if len(e) > max:
            max = len(e)
    max
    for i in range(0, 10):
        print(a[i][1], (max - len(a[i][1])) * " ", b[i][1])


# Si l'on compare les occupations les plus connectés directement et les plus connectées indirectement, on peut voir que la position de novelist et de poet s'inverse. L'occupation poète est donce connectée à des occupations elles-mêmes assez connectées. Ce résultat vient très probablement de la forte connexion entre poet et journalist.
deuxcolonnes(a, b, 10)

# Prendre en compte l'ampleur de chaque connection: si A est connecté à B par 10 personnes, et que B est connecté à 20 occupations, alors j'attribue à A une valeur de 200 (10 * 20) provenant de B. Le résultat obtenu est une connectivité absolu (non relative au nombre de personnes qui ont A comme occupation). L'occupation poète a à nouveau une place un peu plus importante. L'occupation screenwriter, qu'on a déjà vu être au croisement des deux clusters littérature / cinéma-tv, se trouve également avoir un score assez haut de connectivité. Mais c'est film_director qui apparait comme le plus connecté indirectement.
for o in c.keys():
    c[o]["XP"] = 0
    total_personnes = c[o]["P"]
    for node in g[o]:
        if g.nodes[node]["type"] == "O":
            if g.has_edge(o, node):
                c[o]["XP"] += c[node]["O"] * g[o][node]["weight"]
xp = [(c[i]["XP"], i) for i in c.keys() if c[i]["XP"] != 0]
xp.sort()
xp.reverse()
xp[:10]


for o in c.keys():
    c[o]["XP"] = 0
    total_personnes = c[o]["P"]
    for node in g[o]:
        if g.nodes[node]["type"] == "O":
            if g.has_edge(o, node):
                c[o]["XP"] += c[node]["O"] * g[o][node]["weight"]

# Construction d'un sous-graphe à partir de ces nouvelles données, qui permet de visualiser les choses mises en évidence au début de l'analyse.
node_w = {o: c[o]['XP'] for o in c.keys()}
nx.set_node_attributes(g, node_w, "weight")
xp = [(c[i]["XP"], o) for o in c.keys() if c[o]["XP"] != 0]
nodes = [node[1] for node in xp if c[node[1]]['O'] > 10]
subgraph = g.subgraph(nodes)
plt.figure(figsize=(30, 30))
pos = nx.spring_layout(subgraph)
node_sizes = [
    (subgraph.nodes[node]["weight"] / 10) for node in subgraph.nodes()
]
nx.draw_networkx_nodes(
    subgraph, pos, node_color="burlywood", node_size=node_sizes
)
nx.draw_networkx_edges(subgraph, pos, alpha=0.5, edge_color="gainsboro")
nx.draw_networkx_labels(subgraph, pos, alpha=0.7, font_size="medium")
plt.axis("off")
plt.show()
