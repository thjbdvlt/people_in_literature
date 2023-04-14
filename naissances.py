import csv
import json
from collections import Counter
import pprint
import altair as alt
import plotly.express as px
from collections import Counter
from IPython.display import SVG

csv_file = './data/dbpedia/dbpedia_poets_birthdate.csv'

csv_content = []

with open(csv_file) as f:
    rdr = csv.reader(f,delimiter=',')
    for r in rdr:
        csv_content.append(r)

csv_content[:3]

csv_content[1][0].replace('http://dbpedia.org/resource/', '')


r[:5]

len(r)

dt = '1457-08-02'
a = int(dt[:4]) ; a

for i in csv_content[1:]:
    a = i[0].replace('http://dbpedia.org/resource/', '')
    b = a.replace('_', ' ')
    c = int(i[1][:4])
    if not i[0] == 't':
        print(i)
        input(i)
        r.append([i[0], b, c])

# la = [e[2] for e in r]; la[:3]
la = [e[2] for e in r]
print(la)

ctr = Counter(la)
ctr_l = list(ctr.items())
ctr_l[:7]


data = [{'year': e[0], 'eff': e[1]} for e in ctr_l]

with open('data/birth_years_grouped.json', 'w') as f:
    json.dump(data, f)

# Ce graphique utilise la librairie vega-lite, disponible dans la librairie altair
# Tous les paramètres sont indiqués explicitement
# NB : noter le problème des années qui MANQUENT dans l'axe du temps !
# Toutes les années doivent être représentées dans l'axe du temps!

alt.Chart(data).from_dict({
    "data": {
    # "url" : "http://localhost:8888/files/astronomers/notebooks_jupyter/dbpedia_exploration/data/birth_years_grouped.json"
    "values": data
    },
    "mark": "bar", 
    "width": 1000,
    "height": 400,
    "encoding": {
        # Remplacer type de x par  : 'quantitative' et observer la différence
        "x": {"field": "year", "type": "ordinal", 
              ## décommenter et observer
              # "axis": {"values": [1450, 1500, 1550, 1600, 1650, 1700 ,1750, 1800]}
             }, 
         "y": {"field": "eff", "type": "quantitative"},
        

    }
}

)

ys = [y[2] for y in r]; print (ys[:3], ys[-3:])
min(ys), max(ys)

### Créer une liste d'années complète
y_l = list(range(min(ys), max(ys) + 1, 1))
print(len(y_l))
### Afficher le début et la fin de la série complète
y_l[:4],y_l[-4:]

# y_r = []
# for a in y_l:
#     effectif = 0
#     noms =  []
#     for v in r:
#         if a == v[2]:
#             effectif += 1
#             noms.append(v[1])
#             pass
#     y_r.append([a, effectif, ', '.join(noms)])  
    
# pprint.pprint(y_r[:5])
