"""
Observation des relations entre les différentes occupations des writers.
"""

import sparql_dataframe
import pandas
import re

# import plotly.express as plt

# Adresser la requête à DBPedia.
dbpedia = "http://dbpedia.org/sparql"

# Les requêtes SPARQL. Je sépare en plusieurs requêtes afin de pouvoir avoir plus que 10'000 résultats. Les requêtes portent sur les occupations des personnes ayant une des occupations suivantes: Novelist, Poet, Dramatist, Writers.
queries = {}
dataframe = {}
writing_classes = ["Writer", "Novelist", "Poet", "Dramatist"]
for i in writing_classes:
    queries[i] = (
        "PREFIX dbo: <http://dbpedia.org/ontology/>\n"
        "PREFIX dbr: <http://dbpedia.org/resource/>\n"
        "\n"
        "SELECT DISTINCT ?person ?occupation\n"
        "WHERE {\n"
        f"    ?person ?a dbr:{i} ;\n"
        "            dbo:occupation ?occupation .\n"
        "}\n"
    )
    dataframe[i] = sparql_dataframe.get(dbpedia, queries[i])
    dataframe[i]["Group"] = i
    print(len(dataframe[i]))

# Assembler (concaténer) les dataframes en un seul dataframe.
df = pandas.concat(dataframe.values())
df.info()

# Je simplifie les URIs en noms (en enlevant le début).
df.replace(
    r"http://dbpedia\.org/(?:resource|ontology)/(.*)",
    "\\1",
    regex=True,
    inplace=True,
)
len(df)

# Comme on peut le voir en observant le début du tableau, une ligne ne correspond pas à une personne, mais à une occupation. Puisque ce qui va m'intéresser ici consiste dans la multiplication des activités, (par exemple poet + translater + musician) je ne vais chercher à réduire ces lignes à des personnes, et travaillerai sur des relations occupation-occupation.
df.head()

# Le tableau contient de nombreuses lignes dont la valeur de la colonne "occupation" est en fait le nom de la personne associé à la mention "PersonFunction".
df[df["occupation"].str.contains("PersonFunction")]

# Ces lignes ne sont pas utiles pour moi. Je les retire donc.
df = df[~df["occupation"].str.contains("PersonFunction")]
len(df)

# Les nombres d'occupations est très elevé.
len(set(df.occupation))

# Et certaines occupations identiques apparaissent sous des noms différents.
[i for i in set(df.occupation) if i.startswith("Drama")]

# Il faut donc procéder à des regroupements. Un tri manuel serait beaucoup trop laborieux, et poserait problème pour répéter l'opération si des nouveaux résultats venaient s'ajouter. Je vais donc opter plutôt pour une approche plus approximative mais permettant d'automatiser cette opération et de l'appliquer à des données en nombre important. L'idée est d'utiliser, comme dans l'exemple ci-dessus, la correspondance de motifs (patterns) pour sélectionner et grouper des occupations. On peut par exemple grouper un certains nombres d'occupations qui se terminent en "gist", et qui, généralement, désignent des activités intellectuelles spécialisées et institutionalisées dans un cadre académique. Cette manière de faire est approximative et les résultats obtenus contiennent des erreurs (ex. Suffragist, Collagist), mais ça permet de travailler rapidement et avec une certaine souplesse dans l'éventualité où les données changeraient.
[i for i in set(df.occupation) if re.search("gist$", i)]

# Pour la suite de l'exploration de ces données, l'objectif est d'observer les différences dans les activités annexes à l'activité de création littéraire entre les sous-groupes que constituent les "poets", les "dramatists" et les "novelists" qui constituent les trois genres dominants de la production littéraire occidentale moderne. Je n'intègre pas l'essai ni l'autobiographie, qui représentent des cas à part et sont difficiles à distinguer de pratiques non-littéraires en raison de leur caractère non-fictionnel (ex. les autobiographie de star, ou les essais de développement personnel). L'idée est de voir si certaines activités annexes sont sur- ou sous-représentrées dans certains de ces sous-groupes. Par exemple, trouve-t-on davantages de personnes exerçant des activités religieuses ou mystiques chez les poètes-ses que chez les dramaturges? À l'inverse, les dramaturges ont-iels en revanche plus tendance que les poète-sses à écrire pour le cinéma, et les romancier-ères pour la presse écrite? Les poètes font-iels plus de musique, les romancier-ères plus de peinture?

occupations_grouped = {
    # Une première catégorie assez générale concerne les activités intellectuelles et en particulier les activités de recherche universitaire. Avec deux sous-catégories: sciences sociales; sciences expérimentales.
    "intellectual": [
        "gist",
        "stud",
        "scho",
        "critic",
        "prof",
        "lectur",
        "univ",
        "search",
        "anthro",
        "socio",
        "ethno",
        "hist",
        "theor",
        "lingu",
        "philo",
        "chemis",
        "biol",
        "math",
        "scienc",
        "lexico",
    ],
    "social sciences": ["socio", "anthro", "ethno", "hist"],
    "natural sciences": ["biol", "math", "phys", "chemis"],
    # Un autre ensemble d'activité, les médias. Que je distingue en deux ensembles: médias imprimés (presse) et médias non-imprimés (télévision, radio, cinéma).
    "non-written media": [
        "radio",
        "screen",
        "cinem",
        "script",
        "film",
    ],
    "press": ["journ", "report", "magaz", "news", "chron"],
    "religion": [
        "theol",
        "relig",
        "priest",
        "preach",
        "saint",
        "church",
        "myst",
    ],
    "visual arts": [
        "comic",
        "paint",
        "photo",
        "illust",
        "draw",
        "video",
    ],
    "music": ["music", "compos"],
    "books": ["edit", "book", "publish", "print", "libr"],
    "politic": [
        "politic",
        "deput",
        "govern",
        "presid",
        "law",
        "lega",
        "juri",
    ],
    "education": ["school", "teach", "pedag", "educ"],
    # Enfin, la traduction constitue une activité à part, à laquelle s'adonne de nombreuxses écrivain-es. C'est pourquoi j'en fais une activité à part entière.
    "translation": ["transl"],
}

# Je mets en caractères minuscules les occupations, afin de pouvoir effectuer plus facilement les comparaison avec les mots déterminés ci-dessus. Je construis une nouvelle liste à double éléments: l'occupation et la "writing_class" (Novelist, Poet, Dramatist, Writer).
occupation_and_group = [(i[1].lower(), i[2]) for i in df.values]
occupation_and_group[:10]

# À travers un enchâssement de boucles, je compte, pour chaque "writing_class", combien de lignes correspondent à chacun de ces groupes d'occupations (politic, education, etc.).
count = {}
for i in writing_classes:
    count[i] = {}
    for word_group in occupations_grouped:
        count[i][word_group] = 0
        for row in [r for r in occupation_and_group if r[1] == i]:
            for word in occupations_grouped[word_group]:
                if word in row[0]:
                    count[i][word_group] = count[i][word_group] + 1
                    break
count

# Les données peuvent être remises dans un DataFrame pandas:
occount = pandas.DataFrame(count)
occount

# Un rapide regard des données donne déjà des informations intéressantes. Par exemple, l'activité de traduction, qui est une activité importante des poètes-ses modernistes et contemporain-es, apparaît nettement comme une spécificité de ce groupe. Ce n'est pas une surprise, pour plusieurs raisons: (1) la traduction de poésie s'accomplit plus rapidement et peut donc cohabiter plus facilement avec une activité d'écriture; (2) la traduction de la poésie pose des problèmes complexes qui la font souvent percevoir comme une forme de création à part entière et au premier degré, et de fait il y a des traductions célèbres de poésie (ex. Poe traduit par Baudelaire); (3) éventuellement, la recherche d'innovation linguistique, peut-être plus présente en poésie que dans l'écriture romanesque, pousserait davantage les poéte-sses à lire ce qui se fait ailleurs -- la recherche d'un écart avec le langage ordinaire (qui caractérise la poésie) peut également être une source de motivation à lire et faire circuler des textes en langue étrangère. Il s'agit également du seul groupe chez lequel le groupe d'occupation "press" est plus élevé que le groupe "non-written media". Ici encore, ce n'est pas surprenant: la poésie étant, contrairement aux écritures romanesque et dramatique, souvent non-narrative, les poètes ont naturellement moins de relation avec le cinéma (du moins le cinéma traditionnel, où leurs compétences s'exportent plus difficilement). Par ailleurs, peut-être les groupes ne sont-ils pas distribués de façon homoène dans le temps: il est possible que si les poètes-ses ont moins travaillé pour la télévision, c'est car la plupart des poètes-ses de mon jeu de données sont né-es et mort-es avant l'essor de la télévision.

# Ajouter une colonne "total" à droite afin de pouvoir plutôt travailler avec des nombres relatifs aux totaux.
occount["total"] = occount.sum(axis=1)
occount.loc["total"] = occount.sum(numeric_only=True, axis=0)
occount

# (Je raccourci le nom de la variable.)
o = occount
o

# Le nombre d'occupation-traductrice par occupation-poètesse
round(o.Poet.translation / o.Poet.total, 2)

# Le nombre d'occupation-traductrice par occupation-romancière
round(o.Novelist.translation / o.Novelist.total, 2)

# Le nombre d'occupation-traductrice par occupation-dramaturge
round(o.Dramatist.translation / o.Dramatist.total, 2)

# Le nombre d'occupation-traductrice par occupation-écrivaine
round(o.Writer.translation / o.Writer.total, 2)

# La proportion d'occupation-traduction chez les poète-sses est largement supérieure à celle qu'on trouve chez les romancier-ères et dramaturges qui sont presque identiques (0.05, 0.06). Le rapport entre la proportion chez les poète-sses et chez les dramaturges, de 1/2 est identique a rapport entre dramaturge et writers, donc il pourrait sembler peu significatif. Mais cela n'est à mon avis pas le cas. Car la proportion plus basse chez les "Writers" s'explique autrement: en effet, ce groupe est constitué d'un nombre important d'auteurices qui n'ont pas la situation économique précaire des auteurices littéraires, puisque les Writers sont aussi des neurologistes reconnu-es publiant des essais de vulgarisation, etc. Il va de soit que l'activité de traduction dans ces catégorie socioprofessionnelle est une activité très secondaire.

