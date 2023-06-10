"""
Exploration d'une jeu de données de réservations d'hôtel issu du site Kaggle.
"""


from collections import Counter
import calendar


# Je lis le contenu du csv.
csvpath = "./hotel_reservations.csv"
with open(csvpath, "r") as f:
    csv = f.readlines()

# Je transforme chaque ligne en une liste. L'ensemble est donc une liste de listes.
csv = [line.split(",") for line in csv]
csv[:1]

# Pour pouvoir plus facilement travailler, je transforme la liste de listes en dictionnaires de dictionnaires (nested dicts). L'ensemble est un dictionnaire, et chaque ligne du csv (= chaque réservation) va constituer un sous-dictionnaire, dont les clés correspondront aux entêtes du csv (les intitulés des colonnes)
c = {}
for line in csv[1:]:
    no_reservation = line[0]
    c[no_reservation] = {}
    colonnes = [i for i in range(1, len(line))]
    for no in colonnes:
        c[no_reservation][csv[0][no]] = line[no]


# Combien d'années différentes sont concernées par ces réservations?
years = [c[i]["arrival_year"] for i in c.keys()]
Counter(years)

# Y a-t-il des réservations pour tous les mois de l'années?
months = [c[i]["arrival_month"] for i in c.keys()]
Counter(months)


# Je crée quelques fonctions simples pour explorer quelques aspects de ces données.


# Fonction qui retourne une liste de tuples: l'id de la réservation et la valeur d'une colonne à choix, entrée comme paramètre.
def query_id_col(col: str):
    a = [(i, c[i][col]) for i in c.keys()]
    return a


# Fonction qui retourne un dictionnaire associant (clé) l'id de la réservation à (valeur) la valeur attribuée à la colonne choisie pour cette réservation.
def query_id_dict(col: str):
    di = {}
    for i in c.keys():
        di[i] = c[i][col]
    return di


# Fonction qui retourne pour une colonne, un dictionnaire qui associe (clé) les valeurs existantes pour cette colonnes au (valeur) nombre de réservation avec cette valeur dans cette colonne.
def query_valeur_nb(col: str):
    a = [(i, c[i][col]) for i in c.keys()]
    values = {}
    for i in a:
        if i[1] not in values.keys():
            values[i[1]] = 0
        else:
            values[i[1]] = values[i[1]] + 1
    return values


# Fonction qui retourne, pour une colonne, un dictionnaire associant (clé) les valeurs existantes pour cette colonne à (valeur) une liste des ids des réservations ayant cette valeur.
def query_valeur_id(col: str):
    a = [(i, c[i][col]) for i in c.keys()]
    values = {}
    for i in a:
        if i[1] not in values.keys():
            values[i[1]] = []
        else:
            values[i[1]].append(i[0])
    return values


# Question qui nous permettra peut-etre d'en apprendre davantage sur le type d'établissement: les saisons de réservations.
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

# Vraisemblablement, il ne s'agit pas d'un hôtel dont le public-cible est constitué de skieureuses. Les mois d'hivers et du début du printemps sont ceux pour lesquels il y a le moins de réservations.

# La colonne "required_car_parking_space".
query_valeur_nb("required_car_parking_space")

# Le champ "required_car_parking_space" me semble être intéressant à croiser avec d'autres champs. Par exemple, y a-t-il un rapport entre le mois de la réservation et le fait d'avoir besoin d'une place de parking? Peut-être qu'en été les gens viennent à pieds dans cet hôtel.

# Pour chaque mois, le nombre de réservation avec une place de parking, et le nombre de réservation sans place de parking.
# months_id = query_id_dict("required_car_parking_space")
# parking = query_valeur_id("required_car_parking_space")
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

# Calculer l'écart.
proportions = [a[i]["proportion"] for i in a.keys()]
proportions.sort()
print(
    proportions[0],
    "/",
    proportions[-1],
    "=",
    round(proportions[-1] / proportions[0], 1),
)

# Print les mois par la valeur "proportion".
p = [
    (a[i]["proportion"], calendar.month_name[int(i)][:3])
    for i in a.keys()
]
p.sort()
p.reverse()

for n, m in p:
    print(m, ":", n)

# Une hypothèse que je formule à partir de ces résultats: les réservations de place de parking sont corrélées avec le nombre d'enfants. Des vacances d'été (s'il y en a dans le pays dans lequel se trouve cet hôtel, où dans les pays dans lesquels vivent ses clients) dans une période (disons) standardisée pour l'ensemble d'une population pourrait être une explication pour ces disparités. Je commence par faire la même opération mais avec la colonne "no_of_children".
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

# On peut voir des différences importantes dans les proportions de réservations avec voitures: de 0.018 par réservation en octobre à 0.058 en Aout.
for i in b.keys():
    print(calendar.month_name[int(i)][:3], b[i])

# Calculer l'écart
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

for n, m in q:
    print(m, ":", n)

# Maintenant, essayer de voir si les familles avec enfant sont aussi les familles avec parking.
months = query_valeur_id("arrival_month")
parking = query_id_dict("required_car_parking_space")
children = query_id_dict("no_of_children")
c = {}
for i in months.keys():
    c[i] = {}
    c[i]["np_nc"] = 0
    c[i]["p_c"] = 0
    c[i]["np_c"] = 0
    c[i]["p_nc"] = 0
    for r in months[i]:
        if parking[r] == "0":
            if children[r] == "0":
                c[i]["np_nc"] = c[i]["np_nc"] + 1
            elif int(children[r]) > 0:
                c[i]["np_c"] = c[i]["np_c"] + 1
        elif parking[r] != "0":
            if children[r] == "0":
                c[i]["p_nc"] = c[i]["p_nc"] + 1
            elif int(children[r]) > 0:
                c[i]["p_c"] = c[i]["p_c"] + 1
    # a[i]["total"] = a[i]["0"] + a[i]["1"]
    # a[i]["proportion"] = round(a[i]["1"] / a[i]["total"], 3)

for i in c.keys():
    print(calendar.month_name[int(i)][:3], c[i])
