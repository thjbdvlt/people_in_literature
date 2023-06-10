"""
Exploration d'une jeu de données de réservations d'hôtel issu du site Kaggle.
"""

import calendar

# Je place le contenu du csv dans un fichier, en tant que liste (liste de lignes: chaque ligne est une réservation.)
csvpath = "./hotel_reservations.csv"
with open(csvpath, "r") as f:
    csv = f.readlines()

# Je transforme chaque ligne en une liste. L'ensemble est donc une liste de listes. Chaque ligne est une liste de valeurs.
csv = [line.split(",") for line in csv]
for i in csv[:3]:
    print(i)

# Pour pouvoir plus facilement travailler, je transforme la liste de listes en dictionnaires de dictionnaires. L'ensemble est un dictionnaire, et chaque ligne du csv (chaque réservation) va constituer un sous-dictionnaire, dont les clés correspondront aux entêtes du csv (les intitulés des colonnes)
data = {}
for line in csv[1:]:
    no_reservation = line[0]
    data[no_reservation] = {}
    colonnes = [i for i in range(1, len(line))]
    for no in colonnes:
        data[no_reservation][csv[0][no]] = line[no]

# Aperçu de la structure, deux entrées:
for j in [i for i in data.items()][:2]:
    print(j)

# Plus lisible:
for k in [data[i] for i in data.keys()][1].keys():
    print(k, ":", [data[i] for i in data.keys()][1][k])


# Je crée quelques fonctions simples pour explorer quelques aspects de ces données.
# Une fonction qui retourne une liste de tuples: l'id de la réservation et la valeur d'une colonne à choix, entrée comme paramètre.
def query_id_col(col: str):
    a = [(i, data[i][col]) for i in data.keys()]
    return a


# Fonction qui retourne un dictionnaire associant (clé) l'id de la réservation à (valeur) la valeur attribuée à la colonne choisie pour cette réservation.
def query_id_dict(col: str):
    di = {}
    for i in data.keys():
        di[i] = data[i][col]
    return di


# Fonction qui retourne pour une colonne, un dictionnaire qui associe (clé) les valeurs existantes pour cette colonnes au (valeur) nombre de réservation avec cette valeur dans cette colonne.
def query_valeur_nb(col: str):
    a = [(i, data[i][col]) for i in data.keys()]
    values = {}
    for i in a:
        if i[1] not in values.keys():
            values[i[1]] = 1
        else:
            values[i[1]] = values[i[1]] + 1
    return values


# Fonction qui retourne, pour une colonne, un dictionnaire associant (clé) les valeurs existantes pour cette colonne à (valeur) une liste des ids des réservations ayant cette valeur.
def query_valeur_id(col: str):
    a = [(i, data[i][col]) for i in data.keys()]
    values = {}
    for i in a:
        if i[1] not in values.keys():
            values[i[1]] = []
        else:
            values[i[1]].append(i[0])
    return values


# Combien d'années différentes sont concernées par ces réservations?
query_valeur_nb("arrival_year")

# Y a-t-il des réservations pour tous les mois de l'années?
query_valeur_nb("arrival_month")

# Question qui nous permettra peut-etre d'en apprendre davantage sur le type d'établissement: la distribution des réservations dans l'année.
months = query_valeur_nb("arrival_month")
for m in months.keys():
    j = "|" * int(months[m] / 100)
    print(calendar.month_name[int(m)][:3], j, months[m])

# Pour y voir un peu mieux, mettre les mois dans l'ordre, et répéter l'opération.
months_sorted = [(int(m), months[m]) for m in months.keys()]
months_sorted.sort()
months_sorted
for m in months_sorted:
    j = "|" * int(m[1] / 100)
    print(calendar.month_name[m[0]][:3], j, m[1])

# Vraisemblablement, il ne s'agit pas (par exemple) d'un hôtel dont le public-cible est constitué de skieureuses. Les mois d'hivers et du début du printemps sont ceux pour lesquels il y a le moins de réservations.

# Une autre colonne, "required_car_parking_space", qui comporte deux valeurs possible: 0 ou 1, sans ou avec.
query_valeur_nb("required_car_parking_space")

# Le champ "required_car_parking_space" me semble être intéressant à croiser avec d'autres champs. Par exemple: y a-t-il un rapport entre le mois de la réservation et le fait d'avoir besoin d'une place de parking? Peut-être qu'en été les gens viennent à pieds dans cet hôtel.

# Pour chaque mois, le nombre de réservation avec une place de parking, et le nombre de réservation sans place de parking.
months = query_valeur_id("arrival_month")
parking = query_id_dict("required_car_parking_space")
a = {}
for i in months.keys():
    a[i] = {}
    a[i]["0"] = 0
    a[i]["1"] = 0
    for r in months[i]:
        if parking[r] == "0":
            a[i]["0"] = a[i]["0"] + 1
        elif parking[r] == "1":
            a[i]["1"] = a[i]["1"] + 1
        else:
            pass
    a[i]["total"] = a[i]["0"] + a[i]["1"]
    a[i]["proportion"] = round(a[i]["1"] / a[i]["total"], 3)

# On peut voir des différences importantes dans les proportions de réservations avec voitures: de 0.018 par réservation en octobre à 0.058 en Aout.
for i in a.keys():
    print(calendar.month_name[int(i)][:3], a[i])

# Calculer l'écart entre les valeurs extrêmes.
proportions = [a[i]["proportion"] for i in a.keys()]
proportions.sort()
print(
    proportions[0],
    "/",
    proportions[-1],
    "=",
    round(proportions[-1] / proportions[0], 1),
)

# Print les mois dans l'ordre allant de la plus grande proportion de réservation avec voiture à la plus faible. Octobre, qui a le nombre de reéservation le plus haut, a aussi, proportionnellement, le taux le plus faible de demande pour une place de parking.
p = [
    (a[i]["proportion"], calendar.month_name[int(i)][:3])
    for i in a.keys()
]
p.sort()
p.reverse()

for n, m in p:
    print(m, ":", n)

# Une explication possible aurait pu être un nombre de place limité de places de parking, qui plafonnerait le nombre absolu de demande pour des places de parking et réduirait donc mécaniquement la proportion de demande pour une place de parc pour les mois avec le plus de réservations. Mais on peut probablement écarter cela, puisque le nombre le plus haut de demande de réservation en un mois est de 222 et que le nombre de réservation en octobre est très largement inférieur (94). Il faudrait toutefois, si l'on voulait s'en assurer, étudier les dates de réservations et non les mois, pour voir le nombre le plus haut de réservations simultanées de places de parking. Une hypothèse que je formule à partir de ces résultats: les réservations de place de parking sont corrélées avec le nombre d'enfants. Des vacances d'été (s'il y en a dans le pays dans lequel se trouve cet hôtel, où dans les pays dans lesquels vivent ses clients) dans une période (disons) standardisée pour l'ensemble d'une population pourrait être une explication pour ces disparités. Je commence par faire la même opération mais avec la colonne "no_of_children".
months = query_valeur_id("arrival_month")
children = query_id_dict("no_of_children")
b = {}
for i in months.keys():
    b[i] = {}
    b[i]["0"] = 0
    b[i]["1"] = 0
    for r in months[i]:
        if children[r] == "0":
            b[i]["0"] = b[i]["0"] + 1
        elif int(children[r]) > 0:
            b[i]["1"] = b[i]["1"] + 1
        else:
            pass
    b[i]["total"] = b[i]["0"] + b[i]["1"]
    b[i]["proportion"] = round(b[i]["1"] / b[i]["total"], 3)

# Calculer l'écart entre les valeur extrêmes.
proportions = [b[i]["proportion"] for i in b.keys()]
proportions.sort()
print(
    proportions[0],
    "/",
    proportions[-1],
    "=",
    round(proportions[-1] / proportions[0], 1),
)

q = [
    (b[i]["proportion"], calendar.month_name[int(i)][:3])
    for i in b.keys()
]
q.sort()
q.reverse()

# Print les résultats. Comme pour les places de parking, le mois avec, proportionnellement, le plus de réservation avec enfant est le mois d'aout.
for n, m in q:
    print(m, ":", n)

# Maintenant, je vais essayer de voir si les familles avec enfant sont aussi les familles avec parking.
children = query_valeur_id("no_of_children")
parking = query_id_dict("required_car_parking_space")


# Deux fonctions qui retournent "True" si les reservations contiennent une valeur supérieure à 0 pour, respectivement, la colonne "no_of_children" et la colonne "required_car_parking_space".
def with_children(key: str):
    return int(data[key]["no_of_children"]) > 0


def with_parking(key: str):
    return data[key]["required_car_parking_space"] != "0"


# Compter les réservations pour construire les quatre possibilités: sans enfant ni parking, sans enfant mais avec parking, avec enfant mais sans parking, avec enfant et avec parking. (Le code est un peu désespérant, toutes mes excuses.)
d = {}
d["children, parking"] = len(
    [i for i in data.keys() if with_children(i) and with_parking(i)]
)
d["children, no parking"] = len(
    [
        i
        for i in data.keys()
        if with_children(i) and not with_parking(i)
    ]
)
d["no children, no parking"] = len(
    [
        i
        for i in data.keys()
        if not with_children(i) and not with_parking(i)
    ]
)
d["no children, parking"] = len(
    [
        i
        for i in data.keys()
        if not with_children(i) and with_parking(i)
    ]
)
d["children"] = d["children, parking"] + d["children, no parking"]
d["no children"] = (
    d["no children, parking"] + d["no children, no parking"]
)
d["parking"] = d["children, parking"] + d["no children, parking"]
d["no parking"] = (
    d["children, no parking"] + d["no children, no parking"]
)
total = len(csv[1:])

for i in d.keys():
    print(i, ":", d[i])

# Parmi les réservations avec enfant, la proportion de réservation avec place de parking est plus importante que la proportion de réservation avec place de parc dans l'ensemble des réservations. Mais je ne saurais trop juger si cela est significatif. (Il faudrait probablement utiliser ici le test statistique du Chi-2.) L'écart est tout de même assez faible, mais il y a quand même un peu moins du double de demande de place de parking dans les réservations avec enfant. Et surtout, la différence est au moins dans la bonne direction (plus de demande de place de parking dans les réservations avec enfants). Il me semble donc pertinent de continuer à explorer cette relation.
print(round(d["children, parking"] / d["children"], 3))
print(round(d["parking"] / total, 3))

# Puisque mon hypothèse partait initialement du mois d'aout, je vais essayer de voir ce qu'il en est de cette différence pour ce mois. Je commence par stocker dans une variable les clés des réservations qui concernent le mois d'aout.
months = query_valeur_id("arrival_month")
august = months["8"]

# Je construis une autre variable (sous-groupe de la précédente), dans laquelle je stocke les id des réservations qui (1) concerne le mois d'aout ET ont des valeurs non-nulles concernant la présence d'enfant et la demande d'une place de parking.
august_and_children_and_parking = [
    i for i in august if with_children(i) and with_parking(i)
]

# La différence ici me semble beaucoup plus significative.
print(
    "enfant + parking au mois d'aout:",
    round(len(august_and_children_and_parking) / len(august), 4),
)
print(
    "enfant + parking dans l'ensemble de l'année:",
    round(d["children, parking"] / total, 4),
)
print(
    "->",
    round(
        (len(august_and_children_and_parking) / len(august)) /
        (d["children, parking"] / total), 3)
)
