import csv
import json
from collections import Counter
import pprint
import plotly.express as px
from collections import Counter

# Carnet destiné à inspecter la répartition des naissances de la populations des poètes-ses.

# Indiquer le lien vers le CSV, le lire et stocker son contenu dans une liste.
csv_file = '../data/dbpedia/dbpedia_poets_birthdate.csv'
csv_content = []
with open(csv_file) as f:
    rdr = csv.reader(f,delimiter=',')
    for i in rdr:
        csv_content.append(i)

# Print les résultats.
# Puis, print le premier nom sans l'URI: c'est ainsi que sont récupérés les noms.
csv_content[:3]
csv_content[1][0].replace('http://dbpedia.org/resource/', '')

# Nouvelle liste composée des URIs, des années de naissances et des noms, i.e. des URI raccourcies selon l'exemple ci-dessus.
csv_noms = [(
    i[0], 
    i[0].replace('http://dbpedia.org/resource/', '').replace('_', ' '), 
    int(i[1][:4])
    ) for i in csv_content[1:]]

# Liste des années uniquement.
annees = [e[2] for e in csv_noms]

# Les premières et les dernières années.
annees[:3], annees[-3:]

# Compter l'effectif de chaque année (= le nombre de personnes qui ont cette année comme propriété en tant qu'année de naissance).
freq_annees = Counter(annees)
freq_annees.most_common()[:7] # print les 7 premieres de la liste

# Ouvrir un fichier et y mettre le dictionnaire en format JSON.
with open('../data/birth_years_grouped.json', 'w') as f:
    json.dump(freq_annees, f)

# Faire une liste des années qui inclut les années avec un effectif de 0.
annees_toutes = list(
        range(
            min(annees),
            max(annees) + 1, 
            1 # le "step" entre chaque item est de "1" (une année)
            )
        )

# Montrer le début et la fin de la nouvelle liste.
annees_toutes[:4], annees_toutes[-4:]

# Faire une liste de tuples: les années, les effectifs, les noms des personnes.
annees_noms = []
for i in annees_toutes:
    noms = [] # réinitialiser la liste
    if i in freq_annees.keys():
        effectif = freq_annees[i]
    else:
        effectif = 0
    for j in csv_noms:
        if j[2] == i:
            noms.append(j[1])
    annees_noms.append((
                        i, # l'année
                        effectif, # l'effectif
                        ', '.join(noms) # les noms
                        ))

# Observer le début de la liste.
pprint.pprint(annees_noms[:5]) 

# Fabriquer les axes du graphique à partir des valeurs.
a_x = [i[0] for i in annees_noms]
a_y = [i[1] for i in annees_noms]

# et les noms lors du survol à la souris.
hover = [i[2] for i in annees_noms]

# Construire le plot.
fig = px.bar(
        x=a_x, y=a_y, labels={'x':'Year','y':'Effectifs'}, 
        hover_name=hover
        )

# Visualiser.
fig.show()
