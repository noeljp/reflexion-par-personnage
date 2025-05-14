

import os
import requests
import openai
import random

def generer_liste_personnage(theme,fichier):
    # a partir du theme, on va generer une liste de personnage
    prompt = (f"Voici le thème : {theme}\n"
              "Génère une liste de personnages qui pourraient réfléchir à ce thème.\n"
              "Donne-moi une liste de 10 personnages avec leur nom et une courte description.\n"
              "Format : Nom - Description\n")
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es un expert en littérature et en philosophie."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    personnages = response.choices[0].message.content.strip().split("\n")
    with open(fichier, "w", encoding="utf-8") as f:
        for personnage in personnages:
            f.write(personnage + "\n")
    print(f"Liste de personnages générée et enregistrée dans {fichier}.")

def charger_personnages(fichier):
    with open(fichier, "r", encoding="utf-8") as f:
        return [ligne.strip() for ligne in f if ligne.strip()]

def generer_image(theme, personnage, description):
    # On remplace les espaces par des underscores pour le nom du personnage
    personnage = personnage.replace(" ", "_")
    # On génère une image à partir du thème et du personnage
    dalle_prompt = (f"Voici le thème : {theme}\n"
                   f"Voici le personnage : {personnage}\n"
                   f"Voici la description : {description}\n"
                   "Génère une image qui représente ce personnage en lien avec le thème.\n"
                   "L'image doit être de haute qualité et artistique.\n")
    
    response = openai.Image.create(
        model="dall-e-3",
        prompt=dalle_prompt,
        n=1,
        size="1024x1024"
    )
    
    image_url = response['data'][0]['url']
    return image_url

def telecharger_image(url, nom_fichier):
    response = requests.get(url)
    if response.status_code == 200:
        with open(nom_fichier, 'wb') as f:
            f.write(response.content)
        print(f"Image téléchargée : {nom_fichier}")
    else:
        print("Erreur lors du téléchargement de l'image.")

def generer_interview(personnage, theme):
    prompt_system = """Tu es un écrivain créatif et historien spécialiste de la vulgarisation.
Tu sais adopter le style, le ton et les références d’un personnage célèbre, quel que soit son époque ou son domaine.
Ton objectif : rédiger une interview fictive mais crédible entre un·e journaliste et un personnage célèbre.
L’interview doit être courte et structurée (titre, introduction, 5 questions-réponses).
Chaque réponse doit refléter la personnalité, l’époque, les idées et le ton du personnage. Elles doivent être courtes, percutantes et pertinentes.
Le style doit être vivant, fluide et légèrement teinté d’humour ou d’esprit, selon le personnage.
Si le personnage est décédé ou ancien, ses brève réponses doivent s’appuyer sur des anachronismes pertinents ou amusants mais toujours brièvement.
Si tu détectes que le personnage n’a aucun lien crédible avec le thème, précise-le dans l’introduction de manière élégante et joue-en dans les réponses."""

    prompt = f"""Objectif : Rédige une interview fictive d’un personnage célèbre en lien avec le thème suivant : {theme}.
Personnage choisi : {personnage}
L’interview doit respecter la structure suivante :
🔹 Titre accrocheur
Trouve un titre original en lien avec le personnage, son époque ou une phrase marquante qu’il ou elle aurait pu dire.
🔹 Introduction
Présente brièvement le personnage et explique pourquoi il/elle est pertinent·e pour aborder ce thème aujourd’hui.
🔹 Questions / Réponses
Voici les 5 questions à poser, auxquelles le personnage doit répondre avec sa personnalité, son époque, son style :
Vous voilà face à une IA : curieux, effrayé ou inspiré ?
→ Réponse ancrée dans ses références historiques ou personnelles.
Quel usage de l’IA vous aurait fait gagner du temps à votre époque ?
→ Cherche une réponse drôle, inattendue ou ingénieuse.
Comment imaginez-vous l’avenir avec l’IA (ou dans l’espace) ?
→ Laisse place à une vision poétique, exagérée ou utopique.
Quel conseil donneriez-vous à un·e collaborateur·rice de Thales aujourd’hui ?
→ Une leçon, une maxime ou une formule pleine de sens.
Quelle IA rêveriez-vous d’avoir à vos côtés ?
→ Ce peut être une invention fictive, un objet parlant ou un allié imaginaire.
Soigne le style pour qu’on sente bien le ton et les convictions du personnage."""

    
    response = openai.ChatCompletion.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=1000
    )
    return response.choices[0].message.content.strip()
# description du prompt pour simuler une Interview avec un personnage   

if __name__ == "__main__":
    theme = "L'IA et l'espace"
    fichier_personnages = "personnages.txt"
    
    # Étape 1 : Générer la liste de personnages
    generer_liste_personnage(theme,fichier_personnages)
    
    # Étape 2 : Charger les personnages depuis le fichier
    personnages = charger_personnages(fichier_personnages)
    
    for i, personnage in enumerate(personnages):
        print(f"{i + 1}. {personnage}")

    
    # # Étape 4 : Générer l'image du personnage
    # description = "Un personnage célèbre en lien avec le thème de l'IA et de l'espace."
    # image_url = generer_image(theme, personnage_choisi, description)
    
    # # Étape 5 : Télécharger l'image
    # nom_fichier_image = f"{personnage_choisi.replace(' ', '_')}.png"
    # telecharger_image(image_url, nom_fichier_image)
    
    # Étape 6 : Générer l'interview
        interview = generer_interview(personnage, theme)
    
    # Afficher l'interview
        print(interview)
        # # Étape 7 : Enregistrer l'interview dans un fichier texte
        nom_fichier_interview = f"interview_{personnage.replace(' ', '_')}.txt"
        #cree le dossier interview s'il n'existe pas
        dossier_interview = "interviews"
        if not os.path.exists(dossier_interview):
            os.makedirs(dossier_interview)
        with open(os.path.join(dossier_interview, nom_fichier_interview), "w", encoding="utf-8") as f:
            f.write(interview)
        print(f"Interview enregistrée dans {nom_fichier_interview}.")

