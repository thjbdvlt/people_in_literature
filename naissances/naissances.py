import csv
import json
from collections import Counter
import pprint
import altair as alt
import plotly.express as px
from collections import Counter
from IPython.display import SVG

# Indiquer le CSV. 
# Créer une liste vide. (Qui conviendra elle-meme des listes.)
# Ouvrir le fichier et remplir la liste.
csv_file = './data/dbpedia/dbpedia_poets_birthdate.csv'
csv_content = []
with open(csv_file) as f:
    rdr = csv.reader(f,delimiter=',')
    for r in rdr:
        csv_content.append(r)

# Print les résultats, puis le premier nom sans l'URI.
csv_content[:3]
csv_content[1][0].replace('http://dbpedia.org/resource/', '')

# remplacer, partout, les uri par
# reinitialiser la variable r
# et y mettre les noms (=URI raccourcis)
r = []
for i in csv_content[1:]:
    a = i[0].replace('http://dbpedia.org/resource/', '')
    b = a.replace('_', ' ')
    c = int(i[1][:4])
    r.append([i[0], b, c])

# list comprehension: liste à partir de tous les second éléments des tuples dans la liste "r"
la = [e[2] for e in r] ; la[:3], la[-3:] # montrer le début et la fin de la liste

# variable à l'aide de Collections.Counter: compter fréquences les années et les classer
ctr = Counter(la)
ctr_l = list(ctr.items())
ctr.most_common()[:7]  # print les 7 premieres de la liste

# list comprehension sur la liste obtenue avec Counter
# pour obtenir un dictionnaire avec des valeurs pour les keys "year" et "effectif" (nombre d'occurence de l'année)
data = [{'year': e[0], 'eff': e[1]} for e in ctr_l]; data[:3]

# ouvrir un fichier et y mettre le dictionnaire en format JSON
with open('data/birth_years_grouped.json', 'w') as f:
    json.dump(data, f)

# list comprehensions: les années
# = variable "la"
ys = [y[2] for y in r]; ys[:3], ys[-3:]

# liste d'année complète (y compris celles sans individus)
# on utilise la fonction "range" qui crée une séquence de nombres
# on donne le début (l'année minimale), la fin (l'année max + 1), et le "step" entre chaque item (1 an)
# affichage du début et de la fin
y_l = list(range(min(ys), max(ys) + 1, 1)); y_l[:4],y_l[-4:]

# nouvelle liste de liste, à l'intérieur des sous-listes: 
# [0] = l'année
# [1] = l'effectif
# [2] = les noms des individus
# pour ca on alimente une troisieme liste "y_r"
# avec comme base les années de la liste de toutes les années (y_l), associée à la liste "r"
# de cette façon, on a une liste des années possible peuplée des individus rééls
y_r = []
for a in y_l: # les années possibles
    effectif = 0 # on commence à compter à zéro
    noms =  [] # initialisation d'une liste des noms d'individus
    for v in r: # les années avec les individus
        if a == v[2]: # si année possible dans une ligne du CSV des individus
            effectif += 1 # alors on compte + 1
            noms.append(v[1]) # et on ajoute de nom
            pass
    y_r.append([a, effectif, ', '.join(noms)])

# on observe le début de la liste
pprint.pprint(y_r[:5]) 

# pour mettre en forme: on ajoute "personnes: " seulement s'il y a effectivement des personnes
# et dans tous les cas on écrit "année: ..., effectif: ..."
[f'Année: {e[0]}, effectif: {e[1]}, personnes: {e[2]}.' if len(e[2]) > 0  
 else f'Année: {e[0]}, effectif: {e[1]}.' for e in y_r][:5]

# une liste comprehension pour faire un dictionnaire
data = [{'year': e[0], 'eff': e[1], 'names': e[2]} for e in y_r]

### Représenter les valeurs correctement, y compris les années sans naissance
# Si on effleure les barres on découvre les noms des personnes nées en telle année
alt.Chart.from_dict({
    "data": {
    ### Choisir si on veut afficher les données de la variable 'data'
    # ou lire le fichier qui se trouve sur le serveur local jupyter (localhost:8888/files)
    "values" : data    
    # "url" : "http://localhost:8888/files/astronomers/notebooks_jupyter/dbpedia_exploration/data/birth_years_grouped_y.json"
    },
    "mark": "bar",
    # {
    #     "type":"bar",
    #     "tooltip": {"content": "data"}
    # }, 
    "encoding": {
        "x": {"field": "year", "type": "ordinal", 
              "axis": {"values": [1450, 1500, 1550, 1600, 1650, 1700 ,1750, 1800]}}, # ordinal, quantitative
         "y": {"field": "eff", "type": "quantitative"},
        "tooltip": [
      {"field": "year", "type": "quantitative", "title": "Year"},
     {"field": "names", "type": "nominal", "title": "Names"}
    ]
    },
    "width": 1000, 
    "height": 300
}

)
### Représentation graphique avec une autre technologie: 
# Plotly: graphique à barres
# https://plotly.com/python/bar-charts/

a_x = [i[0] for i in y_r]
a_y = [i[1] for i in y_r]
hover = [i[2] for i in y_r]

fig = px.bar(x=a_x, y=a_y, labels={'x':'Year','y':'Effectifs'},
             hover_name=hover
             )
# Changer l'angle des x-labels
fig.update_xaxes(tickangle=60, )
# Noter les fonctionnalités permettant d'interagir avec le graphique
fig.show()

### enregistrer au format HTML et ouvrir comme page web
fig.write_html("pictures/birth_years_grouped.html")

### enregistrer au format SVG
# remplacer suffixe: .svg,  .html, .jpg ...
fig.write_image("pictures/birth_years_grouped.svg") 
chemin = "pictures/birth_years_grouped.svg"
SVG(filename=chemin)

min(y_l), max(y_l)

# Créer des périodes 
periode = 50 # 50 ans
per_l = list(range(1000, 2000, periode)) # compter tous les 50 ans, de 1000 à 2000 => le début de la période
per_ll = [(l, l+ periode -1) for l in per_l] # et la fin de la période = le début de la période, jusqu'au début de la période suivante moins -1 (ex. 0-49)
len(per_ll),per_ll[:3],per_ll[-3:] # nombre de période, et le début et la fin de la liste de période

# on remplit une nouvelle liste
per_r = []
for a in per_ll: # on iterate sur la liste des périodes
    # créer le label de la période 
    label = f'{a[0]}_{a[1]}' # le label de la période = début et fin (élément [0] et [1] du tuple)
    effectif = 0 # on compte depuis 0
    noms =  [] # et on vide la liste de noms
    for v in r: # pour chaque item dans la liste "r"
        if v[2] >= a[0] and v[2] <= a[1]: # si l'item se trouve entre début et fin de la période...
            effectif += 1 # ...alors on compte +1
            noms.append(v[1]) # et on ajoute le nom
    per_r.append([label, effectif, noms])

# Préparer les étiquettes avec retours à la ligne
# (<br> = retour à la ligne en html)
labels = ['<br>'.join([m.strip() for m in i[2]]) for i in per_r] ; len(labels),labels[0] 

# les deux axes
a_x = [i[0] for i in per_r] 
a_y = [i[1] for i in per_r]
#labels = [[m.strip() for m in i[2]] for i in per_r]
    
# et on construit le graphique!
fig = px.bar(x=a_x, y=a_y, labels={'x':'Vingt ans','y':'Effectifs'}
        # hover_name=hover
         )
fig.update_xaxes(tickangle=60, )
fig.update_traces(
    customdata = labels,
    # textposition="top center",
    hovertemplate="<br>".join([
        "%{y} personnes:",
        "%{customdata}",
    ]))
fig.update_layout(hovermode="x unified",
        font=dict(
                family="Courier New, monospace",
                size=10,
                color="RebeccaPurple"
        )
                 )
fig.show()
fig.write_html("pictures/birth_years_period.html") 
fig.write_image("pictures/birth_years_period.svg") 
chemin = "pictures/birth_years_period.svg"
SVG(filename=chemin)
