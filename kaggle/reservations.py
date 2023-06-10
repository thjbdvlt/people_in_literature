"""
Exploration d'une jeu de données de réservations d'hôtel issu du site Kaggle.
"""


from collections import Counter


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
def query_nb_dict(col: str):
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


query_id_dict("arrival_year")
query_id_col("arrival_year")[:5]
query_nb_dict("arrival_year")
query_nb_dict("arrival_year")
