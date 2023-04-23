# ---
# jupyter:
#   jupytext:
#     text_representation:
#       extension: .py
#       format_name: light
#       format_version: '1.5'
#       jupytext_version: 1.14.5
#   kernelspec:
#     display_name: py310_data_analysis
#     language: python
#     name: py310_data_analysis
# ---

import pandas as pd
import plotly.express as px

from itables import init_notebook_mode, show
import scipy.stats as stats
import numpy as np
import csv

init_notebook_mode(all_interactive=False)

### Construire un CSV commun à partir des CSV birthdate / occupations

def file_to_list(fp):
    a = []
    with open(fp) as f:
        c = f.readlines()
        for i in c:
            a.append(i.replace('"', '').replace('\n', '').replace('http://dbpedia.org/resource/', ''))
    return(a)

# ouvrir les csv
fp_a = '../data/dbpedia/dbpedia_poets_birthdate.csv'
fp_b = '../data/dbpedia/poets_occupations.csv'
c_a = file_to_list(fp_a)
c_b = file_to_list(fp_b)

# faire un dictionnaire avec les données du premier csv (birthdate)
tmp_c = {} # dict vide
# iterate les birthdate
for i in c_a[1:]: # enlever la premiere ligne (titres des colonnes)
    j = i.split(',') # faire une liste
    tmp_c[j[0]] = {} # chaque individu donne lieu à une dictionnaire
    tmp_c[j[0]]['birthdate'] = j[1][:4] # dans chaque dict-individu, une entrée "birthdate"

# iterate les birthplace
for i in c_b[1:]:
    j = i.split(',')
    if j[0] in tmp_c.keys(): # check si la clé de l'individu existe
        if not j[1].endswith("PersonFunction__1"):
            tmp_c[j[0]]['occupation'] = j[1] # ajouter une clé "occupation" et l'occupation comme valeur

# enlever les individus incomplets
c = {} # le dictionnaire des individus avec bd + bp
for i in tmp_c.keys(): # iterate sur les keys
    if len(tmp_c[i]) == 2: # si pas deux entrées (birthplace + birthdate)...
        c[i] = tmp_c[i] # création d'un nouveau dictionnaire

# sous forme de liste
a = [['name', 'birthdate', 'occupation']] # la premiere ligne = noms des columns
for i in c.keys():
    j = [i, c[i]['birthdate'], c[i]['occupation']]
    a.append(j)

# exporter vers un nouveau csv
fp = '../data/birthdate_occupation.csv'
b = [','.join(y) for y in a] # les sous-listes en str
with open(fp, 'w') as f:
    f.write('\n'.join(b)) # fabriquer les lignes

# construire un ensemble des occupations
all_occ = [i[2] for i in a if i[2] and type(i[2]) == str] # enlever une sous-liste problématique
all_occ = set(all_occ) # faire un ensemble
fp = '../data/set_occapation.csv'
with open(fp, 'w') as f:
    f.write('\n'.join(all_occ)) # fabriquer les lignes

def occupation_group(occupation):
    a = {}
    if 'poet' in occupation or 'Poet' in occupation:
        generic_occupation = 'poetry'
    else:
        d_a = {
            'poetry': [
                    'Spoken_word',
                    'Spoken_word_artist'
                    ],
            'edition_and_books': [
                    'Librarian_of_Congress',
                    'Typographer',
                    'Publisher',
                    'Printer',
                    'Print_maker',
                    'Printmaker',
                    'Copy_editing'
                    ],
            'writing_for_press': [
                    'Columnist',
                    'Opinion_journalism',
                    'Publicist',
                    'Copyist',
                    'Editor-in-chief',
                    'Journalist'
                    ],
            'translating': [
                    'Translation',
                    'Translator'
                ],
            'critic_academic': [
                    'History',
                    'Literary_magazine',
                    'Theatrologist',
                    'History_of_philosophy_in_Polans',
                    'Philologist',
                    'Art_critic',
                    'Literary_critic',
                    'Poetry_(magazine)',
                    'Emeritus',
                    'Psychoanalist',
                    'Historian',
                    'Scholar',
                    'Art_historian',
                    'Parapsychology',
                    'Professor',
                    'University_of_Massachusetts_Amherst',
                    'History_of_literature',
                    'Theologian',
                    'Essayist'
                    ],
            'creative_writing': [
                    'Writer',
                    'Travel_writer',
                    'Short_story',
                    'Short_story_writer',
                    'Satirist',
                    'Philosopher',
                    'Memoirist',
                    'Surrealist',
                    'Literature_of_Hungary',
                    'Author',
                    'Prose',
                    'Novelist'
                    ],
            'writing_for_non_written_media': [
                    'Playwright',
                    'Radio_drama',
                    'Screenwriter',
                    'Songwriter',
                    'Hymnodist',
                    'Dramatist'
                    ],
            'non_written_art': [
                    'Musician',
                    'Composer',
                    'Humorist',
                    'Vermont_College_of_Fine_Arts',
                    'Cartoonist',
                    'Game_designer',
                    'Illustrator',
                    'Sculptor',
                    'Graphic_designer',
                    'Vocalist'
                    ],
            # catégorie fourre-tout, que je ne vais pas intégrer dans l'analyse
            'religion_and_social_institutions': [
                    'Reformed_Church_in_Hungary',
                    'Oratory_of_St._Philip_Neri',
                    'Mysticism',
                    'Priesthood_in_the_Catholic_Church',
                    'Liberation_theologian',
                    'Primate_of_Poland',
                    'Congregational_church',
                    'Reform_movement',
                    'Head_teacher',
                    'Teacher',
                    'Educator',
                    'Governess',
                    'Sheriff-Depute',
                    'Politician',
                    'Archimandrite'
                    ],
            'other': [
                    'Dog_sled',
                    'Bueno_Aires',
                    'Soldier',
                    'Pharmacist',
                    'Rilingas',
                    'Tramp',
                    'Social_security',
                    'Shepherd',
                    'Solicitor',
                    'Forgery',
                    'Civil_rights_activist',
                    'Revolutionary',
                    'Political_activist',
                    'Abolitionism_in_the_United_States',
                    '_Lord_Tennyson'
                    ]
        }
        d_b = {}
        for i in d_a.keys():
            for j in d_a[i]:
                # if i in ['religion_and_public_institutions', 'other']:
                #     d_b[j] = 'other'
                # else:
                d_b[j] = i
        generic_occupation = d_b[occupation]
    return(generic_occupation)

# créer une nouvelle liste pour la remplir avec les nouvelles occupations
grouped = [] # initialiser la liste 
for i in b[1:]: # ne pas inclure l'entete 
    j = i.split(',') # transformer la ligne en liste
    try:
        g_o = occupation_group(j[2]) # la fonction qui attribue une occupation plus générique
    except KeyError: # pour les exceptions (ex. occupation nominale "Lord truc")
        g_o = 'other' # qui sont à placer dans la catégorie "autre"
    # k = [j[0], j[1], j[2], g_o] # la nouvelle ligne
    try:
        k = [j[0], str(int(j[1])), j[2], g_o] # la nouvelle ligne
    except ValueError:
        print(i)
    grouped.append(','.join(k)) # ajouter à la liste
grouped[0] = f'{b[0]},occupation_class'

# écrire le nouveau fichier
fp_group = '../data/birthdate_occupation_group.csv'
b_group = [','.join(y) for y in a]
with open(fp_group, 'w') as f:
    f.write('\n'.join(grouped)) 

# ouvrir avec pandas
df = pd.read_csv(fp_group)# Ouverture du nouveau CSV
print(df.shape, df.head(3), '\n\n-----\n', df.tail(3))# Inspecter les dimensions et les 3 premières et dernières lignes
df.info()# inspecter les colonnes
show(df)# Afficher les données
occupation = df.groupby(by='occupation').size().sort_values(ascending=False)# Grouper par champ d'activité
occupation = occupation.reset_index()
occupation.head()
occupation = occupation.rename(columns={'field':'occupation', 0: 'effectif'})# Renommer et inspecter les colonnes
occupation.info()
len(occupation), occupation.describe()# Inspecter le nombre de valeurs et leur distribution

### Distribution des champs d'intérêt ou occupations
fig = px.bar(occupation, x='occupation', y='effectif') # les occupations sans classes
fig.show() 
# ce que montre la figure, c'est que la catégorie "poetry" est démesurée par rapport aux autres.
# c'est attendu, étant donné qu'il s'agit d'une liste de poètes
# la question à laquelle ces classes essaient de toute manière de répondre est celle des métiers annexes (y compris écriture créative de genre plus rémunérateurs)
# => on enleve les lignes "poetry"
grouped_no_poetry = [y for y in grouped if 'poetry' not in y]
len(grouped)
len(grouped_no_poetry)

# nouveau fichier sans poetry + correction d'une erreur
fp_no_poetry = '../data/birthdate_occupation_group_no_poetry.csv'
b_group = [','.join(y) for y in a]
with open(fp_no_poetry, 'w') as f:
    f.write('\n'.join(grouped_no_poetry)) 

# on refait sans la catégorie "poetry"
df = pd.read_csv(fp_no_poetry) # lire le fichier
# df.info()# inspecter les colonnes
# show(df)# Afficher les données
occupation = df.groupby(by='occupation').size().sort_values(ascending=False)# Grouper par champ d'activité
occupation = occupation.reset_index()
occupation.head()
occupation = occupation.rename(columns={'field':'occupation', 0: 'effectif'})# Renommer et inspecter les colonnes
# occupation.info()
# len(occupation), occupation.describe()# Inspecter le nombre de valeurs et leur distribution
fig = px.bar(occupation, x='occupation', y='effectif')# Distribution des champs d'intérêt ou occupations
fig.show() 

occupations_w_classes = pd.read_csv('../data/birthdate_occupation_group_no_poetry.csv')
### Regrouper les données recodées par classe
classes = occupations_w_classes.groupby(by='occupation_class').size().sort_values(ascending=False)
# classes = occupations_w_classes.groupby(by='occupation_class').size().sort_values(ascending=False)
classes = classes.reset_index()
classes

### inspecter les colonnes
classes = classes.rename(columns={ 0: 'effectif'})
classes.info()

### Ajouter les fréquences par classe
classes['freq'] = classes['effectif'].apply(lambda x : x / sum(classes['effectif']))
classes.info(), show(classes)

### Représenter les effectifs
fig = px.bar(classes, x='occupation_class', y='effectif')
fig.show()

### Représenter les fréquences
classes['y'] = 0 
e = list(classes['effectif'])

## https://plotly.com/python/horizontal-bar-charts/
fig = px.bar(classes,  x='freq', y = 'y', color='occupation_class', height=1000,
            orientation = 'h', hover_data=['freq', 'effectif'])
fig.update_layout()
fig.show()

# ## Créer les périodes
df['birthdate'].min(),df['birthdate'].max()

### Ce qui suit permet ensuite d'identifier les quantiles
# dfo['qcut'] = pd.qcut(dfo['birthdate'], 6  )
# type(dfo['qcut']), dfo.head(2)
df['qcut'] = pd.qcut(df['birthdate'], 6  )
type(df['qcut']), df.head(2)

periodes = df.groupby(by='qcut').size()
periodes = periodes.reset_index()
periodes

# bins = [1000, 1200, 1400, 1600, 1800, 2000] # rien entre 1200 et 1600!!!
# bins = [1600, 1700, 1800, 1900, 2000]
bins = [1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000]

# dfo['cut'] = pd.cut(dfo['birthYear'], bins=bins, right=False  )
df['cut'] = pd.cut(df['birthdate'], bins=bins, right=False  )
df.head(2)

periodes = df.groupby(by='cut').size()
periodes = periodes.reset_index()
periodes

periodes = periodes.rename(columns={ 0: 'effectif'})
periodes.info()

## bins 'imposés'
tranches = [1600, 1650, 1700, 1750, 1800, 1850, 1900, 1950, 2000]
df['tranches'] = pd.cut(df['birthdate'], tranches, right=False)
# Inspection
df.head()

df.groupby(by='tranches').size().sort_index()

df.drop(df[['qcut']], axis=1, inplace=True) 

df['str_cut'] = df['cut'].apply(lambda x : str(int(x.left))+'-'+ str(int(x.right)-1))
df['str_cut'][:2]

df['cen'] = df['tranches'].apply(lambda x : str(int(x.left))+'-'+ str(int(x.right)-1))
df['cen'][:2]

show(df)

# ## Chi2 — cuts

# +
### La fonction pivot_table produit un tableau de contingence
## Au centre du tableau se trouvent les effectifs conjoints, 
## aux bords les effectifs marginaux qui correspondent 
## aux distributions indépendantes des variables

X = "occupation_class"  # "0"
Y = "str_cut"

df_fs = df[[Y,X]].pivot_table(index=Y,columns=X,aggfunc=len,margins=True,margins_name="Total").fillna(0).astype(int)
df_fs

# -

### Total général, dernière cellule de la dernière ligne
df_fs.iat[-1,-1]

# +
tx = df_fs.loc[:,["Total"]]
ty = df_fs.loc[["Total"],:]
n = df_fs.iat[-1,-1] 

### Compute the matrix multiplication between the columns.
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.dot.html
indep = tx.dot(ty) / n
#pd.options.display.float_format = '{0:3.5}'.format

# Non arrondi
show(indep.round(3))

# Arrondi : effectifs théoriques
show(indep.round(0).astype(int))

# -

### Différence en effectifs entre le théorique et l'observé
#  Valeurs arrondies
### Doc. :
#   Bennani, p.30
#  https://openclassrooms.com/fr/courses/4525266-decrivez-et-nettoyez-votre-jeu-de-donnees/4775616-analysez-deux-variables-qualitatives-avec-le-chi-2
ecarts = (df_fs-indep).iloc[:-1,:-1]
## Attention : arrondi aux entiers dans l'affichage
print(ecarts.round(0).astype(int))

df_fs.iloc[:-1,:-1]

### Ecarts positifs et pondérés par les effectifs: contribution au Chi2
### Doc. :
#   Bennani, p.31
#  https://openclassrooms.com/fr/courses/4525266-decrivez-et-nettoyez-votre-jeu-de-donnees/4775616-analysez-deux-variables-qualitatives-avec-le-chi-2
ecarts_ponderes = round((df_fs-indep)**2/indep,2)
ecarts_ponderes.iloc[:-1,:-1]

chi_2 = ecarts_ponderes.sum().sum()
print(round(chi_2, 2))

chi2 = stats.chi2_contingency(df_fs.iloc[:-1,:-1])

### https://www.statology.org/chi-square-test-of-independence-python/
chi2.statistic, chi2.pvalue

# P-value: 0.001683 à 40 degrés d'indépendace (cf. https://www.statology.org/chi-square-p-value-calculator/)

### Écart pondérés: afficher
tableau = ecarts_ponderes.iloc[:-1,:-1]
fig = px.imshow(tableau, text_auto=True, aspect='auto')
fig.show()


fig = px.imshow(ecarts.round(1), text_auto=True, aspect='auto')
fig.show()

### Degrés d'indépendance
(len(ecarts_ponderes)-2) * (len(ecarts_ponderes.columns)-2), len(ecarts_ponderes)-1,len(ecarts_ponderes.columns)-1

# v = 40, 0.05 = 55.76, X2 = 71.32

# +
### Tables des proportions de contributions au chi-2
# cf. Benani, p.35

table = ecarts_ponderes/chi_2
table['total'] = table.sum(axis=1)
table.loc['total'] = table.sum(axis=0)
table

# +


### % plus lisibles
round(table*100,2)

# -

# * https://www.statology.org/cramers-v-in-python/
# * https://www.statology.org/chi-square-test-of-independence-python/
# * https://www.statology.org/chi-square-goodness-of-fit-test-python/

df_fs.iloc[:-1,:-1]
# df_fs.iloc[-1:,-1:].to

# +
### Coéfficient de Cramer
## https://en.wikipedia.org/wiki/Cramer’s_V
# https://www.geeksforgeeks.org/how-to-calculate-cramers-v-in-python/

X2 = chi2.statistic
N = np.sum(np.array(df_fs.iloc[:-1,:-1]))
minimum_dimension = min(df_fs.shape)-1
N, X2, minimum_dimension

# +
  
# Calculate Cramer's V
result = np.sqrt((X2/N) / (minimum_dimension-1) )
  
# Print the result
print(result)

# +
### Coéfficient de Cramer
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.contingency.association.html

## Le résultat montre un certain lien entre les variables, mais plutôt faible
# Noter aussi que les effectifs de certaines paries de valeurs 
# sont probablement insuffisant pour que ces tests soient valides
stats.contingency.association(df_fs.iloc[:-1,:-1], method='cramer')
# -

# https://en.wikipedia.org/wiki/Cramer’s_V

# ## Chi2 — générations

# +
### La fonction pivot_table produit un tableau de contingence
## Au centre du tableau se trouvent les effectifs conjoints, 
## aux bords les effectifs marginaux qui correspondent 
## aux distributions indépendantes des variables

X = "occupation_class"  # "0"
Y = "cen"

df_fs = df[[Y,X]].pivot_table(index=Y,columns=X,aggfunc=len,margins=True,margins_name="Total").fillna(0).astype(int)
df_fs


# -

### Total général, dernière cellule de la dernière ligne
df_fs.iat[-1,-1]

# +
tx = df_fs.loc[:,["Total"]]
ty = df_fs.loc[["Total"],:]
n = df_fs.iat[-1,-1] 

### Compute the matrix multiplication between the columns.
# https://pandas.pydata.org/pandas-docs/stable/reference/api/pandas.DataFrame.dot.html
indep = tx.dot(ty) / n
#pd.options.display.float_format = '{0:3.5}'.format

# Non arrondi
show(indep.round(3))

# Arrondi : effectifs théoriques
show(indep.round(0).astype(int))


# -

### Différence en effectifs entre le théorique et l'observé
#  Valeurs arrondies
### Doc. :
#   Bennani, p.30
#  https://openclassrooms.com/fr/courses/4525266-decrivez-et-nettoyez-votre-jeu-de-donnees/4775616-analysez-deux-variables-qualitatives-avec-le-chi-2
ecarts = (df_fs-indep).iloc[:-1,:-1]
## Attention : arrondi aux entiers dans l'affichage
print(ecarts.round(0).astype(int))

df_fs.iloc[:-1,:-1]

### Ecarts positifs et pondérés par les effectifs: contribution au Chi2
### Doc. :
#   Bennani, p.31
#  https://openclassrooms.com/fr/courses/4525266-decrivez-et-nettoyez-votre-jeu-de-donnees/4775616-analysez-deux-variables-qualitatives-avec-le-chi-2
ecarts_ponderes = round((df_fs-indep)**2/indep,2)
ecarts_ponderes.iloc[:-1,:-1]

chi_2 = ecarts_ponderes.sum().sum()
print(round(chi_2, 2))

chi2 = stats.chi2_contingency(df_fs.iloc[:-1,:-1])

### https://www.statology.org/chi-square-test-of-independence-python/
chi2.statistic, chi2.pvalue

### Degrés d'indépendance, valeur 'v'
sh = ecarts_ponderes.iloc[:-1,:-1].shape
print(sh)
v = (sh[0]-1) * (sh[1]-1)
v

# P-value: 0.019988 (cf. https://www.statology.org/chi-square-p-value-calculator/)

### Écart pondérés: afficher
tableau = ecarts_ponderes.iloc[:-1,:-1]
fig = px.imshow(tableau, text_auto=True, aspect='auto')
fig.show()


fig = px.imshow(ecarts.round(1), text_auto=True, aspect='auto')
fig.show()

### Degrés d'indépendance
(len(ecarts_ponderes)-2) * (len(ecarts_ponderes.columns)-2), len(ecarts_ponderes)-1,len(ecarts_ponderes.columns)-1

# +
### Tables des proportions de contributions au chi-2
# cf. Benani, p.35

table = ecarts_ponderes/chi_2
table['total'] = table.sum(axis=1)
table.loc['total'] = table.sum(axis=0)
table

# +
##
round(table*100,2)# % plus lisibles


# -

# * https://www.statology.org/cramers-v-in-python/
# * https://www.statology.org/chi-square-test-of-independence-python/
# * https://www.statology.org/chi-square-goodness-of-fit-test-python/

df_fs.iloc[:-1,:-1]

# +
### Coéfficient de Cramer
## https://en.wikipedia.org/wiki/Cramer’s_V
# https://www.geeksforgeeks.org/how-to-calculate-cramers-v-in-python/

X2 = chi2.statistic
N = np.sum(np.array(df_fs.iloc[:-1,:-1]))
minimum_dimension = min(df_fs.shape)-1
N, X2, minimum_dimension

# +
result = np.sqrt((X2/N) / (minimum_dimension-1) )# Calculate Cramer's V
print(result)# Print the result

# +
### Coéfficient de Cramer
# https://docs.scipy.org/doc/scipy/reference/generated/scipy.stats.contingency.association.html

## Le résultat montre un certain lien entre les variables, mais plutôt faible
# Noter aussi que les effectifs de certaines paries de valeurs 
# sont probablement insuffisant pour que ces tests soient valides
stats.contingency.association(df_fs.iloc[:-1,:-1], method='cramer')
# -

# https://en.wikipedia.org/wiki/Cramer’s_V

# ca fonctionne... maintenant il faut comprendre!
