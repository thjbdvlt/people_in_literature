"""
Observation des relations entre (1) les différentes occupations et (2) des relations entre occupations et mouvements auxquels sont rattaché-es les poéte-sses et écrivain-es.
"""

# Peut-etre enlever mouvement et uniquement faire des liens entre occupations.
# Et le faire avec des recherches simples regex

import sparql_dataframe
import plotly.express as plt
import re

# Adresser la requête à DBPedia.
dbpedia = "http://dbpedia.org/sparql"

# La requête SPARQL.

query = (
    "PREFIX dbo: <http://dbpedia.org/ontology/>\n"
    "PREFIX dbp: <http://dbpedia.org/property/>\n"
    "\n"
    "SELECT ?person ?occupation ?movement\n"
    "WHERE {\n"
    "    {\n"
    "    ?person a dbo:Poet ;\n"
    "            dbo:occupation ?occupation ;\n"
    "            dbo:movement ?movement .\n"
    "    }\n"
    "    UNION\n"
    "    {\n"
    "    ?person a dbr:Novelist ;\n"
    "            dbo:occupation ?occupation ;\n"
    "            dbo:movement ?movement .\n"
    "    }\n"
    "    UNION\n"
    "    {\n"
    "    ?person a dbo:Writer ;\n"
    "            dbo:occupation ?occupation ;\n"
    "            dbo:movement ?movement .\n"
    "    }\n"
    "    UNION\n"
    "    {\n"
    "    ?person a dbo:Dramatist ;\n"
    "            dbo:occupation ?occupation ;\n"
    "            dbo:movement ?movement .\n"
    "    }\n"
    "}\n"
)

df = sparql_dataframe.get(dbpedia, query)
df.head()


df.replace(
    r"http://dbpedia\.org/(?:resource|ontology)/(.*)",
    "\\1",
    regex=True,
    inplace=True,
)

movements = [i for i in df.movement]
set(movements)
len(set(movements))

occupations = [i for i in df.occupation]
set(occupations)
len(set(occupations))

# Les nombres d'occupations et de mouvements sont beaucoup trop grand,
# respectivement (avec les données que j'utilise au moment où j'écris)
# de 324 et 470. Par ailleurs, certains movements ou occupations
# identiques apparaissent sous des noms différents. Par exemple:
[i for i in set(occupations) if i.startswith("Drama")]

# Il faut donc procéder à des regroupements. Un tri manuel serait
# beaucoup trop laborieux, et poserait problème pour répéter
# l'opération si des nouveaux résultats venaient s'ajouter. Je vais
# donc opter plutôt pour une approche plus approximative mais
# permettant d'automatiser cette opération et de l'appliquer à des
# données en nombre important. L'idée est d'utiliser, comme dans
# l'exemple ci-dessus, la correspondance de motif (pattern) pour
# sélectionner et grouper des occupations.
reli = [
    i
    for i in occupations
    if re.search(
        "([Tt]heol|[Rr]elig|[Pp]riest|[Pp]reach|[Ss]aint|[Cc]hurch|[Mm]yst)",
        i,
    )
]
len(reli)
drama = [
    i
    for i in occupations
    if re.search("([Dd]rama|[Tt]heat|[Pp]lay)", i)
]
len(drama)

poe = [i for i in occupations if re.search("[Pp]oe", i)]
len(poe)

[i for i in occupations if re.search("([Rr]adio|[Tt]ele)", i)]
[i for i in occupations if re.search("[Rr]heto", i)]
arts = [
    i
    for i in occupations
    if re.search(
        "([^a-zA-Z][Aa]rt|[Cc]omic|[Pp]aint|[Pp]hoto|[Ii]llust|[Ff]ilm|[Mm]us|[Aa]ct[ro]|[Pp]erfo)",
        i,
    )
]
len(arts)
[i for i in occupations if re.search("[Dd]ire", i)]
books = [
    i
    for i in occupations
    if re.search("([Ee]dit|[Bb]ook|[Pp]ublish|[Pp]rint|[Ll]ibr)", i)
]
len(books)

[i for i in occupations if re.search("[Tt]ele", i)]
[
    i
    for i in occupations
    if re.search(
        "([Pp]olit|[Dd]eput|[Gg]overn|[Pp]resid|[Ll]aw|[Ll]ega|[Jj]ur)",
        i,
    )
]
[i for i in occupations if re.search("[Tt]ransl", i)]
[i for i in occupations if re.search("([Nn]ovel|[Ff]ict)", i)]
[i for i in occupations if re.search("[Ss]hort.*[Ss]tory", i)]
[i for i in occupations if re.search("([Ss]creen|[Ss]cript)", i)]
[i for i in occupations if re.search("[Mm]edia", i)]
[i for i in occupations if re.search("[Pp]oet|[]", i)]
[i for i in occupations if re.search("[Ll]ite", i)]
[i for i in occupations if re.search("([Dd]eal|[Mm]erch)", i)]


press = [
    i
    for i in occupations
    if re.search("([Jj]our|[Rr]eport|[Mm]agaz|[Nn]ews|[Cc]hroni)", i)
]

intellectual = [
    i
    for i in occupations
    if re.search(
        "(gist$|[Ss]tud|[Ss]chol|[Cc]ritic|[Pp]rof|[Ll]ectur|[Uu]niv|[Ss]earch|[Ss]ocio|[Aa]nthro|[Ee]thno|[Hh]ist|[Tt]heor|[Ll]ingu|[Pp]hys|[Cc]hemis|[Bb]iol|[Mm]ath|[Mm]edic|[Ss]cien[tc]|[Pp]hilo|[Ll]exico)",
        i,
    )
]
len(intellectual)

education = [
    i
    for i in occupations
    if re.search("([Ss]chool|[Tt]each|[Pp]edag|[Ee]duc)", i)
]

#
# Milit
# Lyrics
# Libr
# Law
[i for i in occupations if re.search("[Gg]raph", i)]
[i for i in occupations if re.search("gist$", i)]
[i for i in occupations if re.search("[Ll]ite", i)]
[i for i in occupations if re.search("crat", i)]

[i for i in occupations if re.search("(olo|gist$)", i)]


len([i for i in occupations if re.search("[wW]rit", i)])
len([i for i in occupations if re.search("gist", i)])
len([i for i in occupations if re.search("[lL]ite", i)])
len([i for i in occupations if re.search("[Pp]oe", i)])
len([i for i in occupations if re.search("([Dd]rama|[Tt]heat)", i)])
len([i for i in occupations if re.search("([Nn]ovel|[Ss]hort)", i)])

