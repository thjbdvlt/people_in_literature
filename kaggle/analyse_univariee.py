# import pandas as pd
# import matplotlib.pyplot as plt
# import numpy as np
# import seaborn as sns
import calendar
from collections import Counter

# fonction pour csv -> liste de liste
def csv_from_file(fp, delimiter:str=','):
    with open(fp) as f:
        c = f.readlines()
    a = [i.replace('\n', '').split(delimiter) for i in c]
    return a

# ouvrir le csv, mettre le contenu dans une variable
fp = './Hotel Reservations.csv'
c = csv_from_file(fp)
c[:2] # observer les noms de colonnes et une ligne

# premier regard sur les données: les années d'arrivée, qui nous montre que toutes les réservations sont réparties dans seulement deux années: 2017 et 2018
c[0][9] # id / arrival_year
a = [(i[0],i[9]) for i in c]
Counter([i[1] for i in a])

# Question qui nous permettra peut-etre d'en apprendre davantage sur le type d'établissement: les saisons de réservations.
d = Counter([i[10] for i in c[1:]])
e = [int(i) for i in d]
e.sort()
f = [(i, d[str(i)]) for i in e]
f

# faire un "plot" simple, qui nous permet de voir le mois avec le plus d'arrivées: octobre
print('Répartition des réservations dans les mois de l\'année:')
for i in f:
    j = '|' * int(i[1] / 100)
    print(calendar.month_name[i[0]][:3], j, i[1])

# required_car_parking_space: les valeurs sont 0 / 1
# on peut voir que la plupart des personnes ne reservent pas de place de parking.
p = Counter([i[6] for i in c])
p
q = [i for i in p if i.isdigit()]
print('Combien de personnes réservent une place de parking pour voiture?')
for i in q:
    if int(i) == 0:
        k = 'non'
    else: 
        k = 'oui'
    j = '|' * int(p[i] / 1000)
    print(k, j, p[i])

# les personnes qui reservent, à quel moment de l'année viennent-elles?
g = Counter([i[10] for i in c if i[6] == '1'])
print('Quand viennent les personnes qui souhaitent avoir une place de parking?')
for i in g:
    j = '|' * int(int(g[i]) / 10)
    print(calendar.month_name[int(i)][:3], j, g[i])
