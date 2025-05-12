import openai
from PIL import Image
import os
import base64
import requests
from io import BytesIO

# Configuration de la clé API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ou remplace par ta clé directement (non recommandé en prod)




def preparer_contexte_reflexion(personnage, theme):
    prompt_system = (
        "Tu es un expert en analyse littéraire et philosophique."
        " Ton objectif est de préparer un cadre de réflexion originale."
    )
    prompt_user = (
        f"Le personnage suivant va réfléchir à ce thème : « {theme} ».\n"
        f"Personnage : {personnage}\n\nRédige une note d'intention phylosophique"
        # "1. Analyse le style d'expression du personnage (ton, vocabulaire, références, rythme, etc.).\n"
        # "2. Décris sa manière de penser (logique, métaphores, structure d'argumentation, etc.).\n"
        # "3. Propose 3 axes de réflexion que ce personnage pourrait développer sur le thème.\n"
        # "4. Donne quelques références ou images qu’il pourrait utiliser pour enrichir sa pensée.\n"
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user}
        ],
        temperature=0.7,
        max_tokens=2000
    )
    return response.choices[0].message.content.strip()

def generer_reflexion_ia(personnage, theme, elements_preparatoires, img_path):
    prompt = (
        f"Personnage : {personnage}\n"
        f"Thème : {theme}\n"
        f"Contexte préparatoire :\n{elements_preparatoires}\n\n"
        "{personnage} est dans une situation quotidienne, discute avec David , un ami quand, soudaint\n" 
        "il découvre {theme}.\n\n"
        f"Rédige en markdown avec l'image suivante : image.png comme référence visuelle au début.\n\n"
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es {personnage}. Tu rédiges un dialogue doncs le lexique et l'élocance' sont ceux de {personnage}."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=2000
    )
    return response.choices[0].message.content.strip()

# Étape 2 : Générer une image illustrant le personnage face à l’IA
def generer_image_ia(personnage,prompt):
    dalle_prompt = (
        f"Un avatar de {personnage}, placé dans son contexte, "
        f"utilise les style graphique' de l'époque de {personnage}.\n"
        f"confronté' a cette idée: '{prompt.strip()[:80]}...', "
        f"en utilisant des éléments visuels qui évoquent son univers.\n"
        "L'image ne doit pas contenir de texte."
   
    )

    response = openai.Image.create(
        model="dall-e-3",
        prompt=dalle_prompt,
        n=1,
        size="1024x1024"
    )
    
    image_url = response['data'][0]['url']
    return image_url

def charger_personnages(fichier):
    with open(fichier, "r", encoding="utf-8") as f:
        return [ligne.strip() for ligne in f if ligne.strip()]


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

if __name__ == "__main__":
    # Cration d'un fichier texte avec une liste de personnages
    theme = "Les technologies  et le progrets"
    generer_liste_personnage(theme, "personnage.txt")
    personnages = charger_personnages("personnage.txt")
    
    print("Liste des personnages disponibles :")
    
    for p in personnages:
        #p = p.replace(" ", "_")
        p = p.replace("é", "e")
        p = p.replace("è", "e")
        p = p.replace("ê", "e")
        p = p.replace("ô", "o")
        p = p.replace("ç", "c")
        p = p.replace("à", "a")
        print(f"- {p}")
    
        personnage,description = p.split(" - ")
        # On remplace les espaces par des underscores pour le nom du personnage
        personnage = personnage.replace(" ", "_")

        prompt = """l'intelligence artificielle"""

        #cree un dossier pour le stockage des fichiers du personnage
        os.makedirs(personnage, exist_ok=True)
        
        image_path = os.path.join(personnage, "image.png")
        contexte_path = os.path.join(personnage, "contexte.txt")
        reflexion_path = os.path.join(personnage, "reflexion.md")


        print("\n--- RÉFLEXION GÉNÉRÉE ---\n")
        contexte = preparer_contexte_reflexion(personnage, prompt)
        #Ecrit le contexte dans un fichier texte
        with open(contexte_path, "w", encoding="utf-8") as f:
            f.write(contexte)

        print("\n--- GÉNÉRATION DE TEXTE EN COURS ---\n")
        reflexion = generer_reflexion_ia(personnage, prompt, contexte, image_path)

        with open(reflexion_path, "w", encoding="utf-8") as f:
            f.write(reflexion)

        print("\n--- GÉNÉRATION D'IMAGE EN COURS ---\n")
        try:
            image_url = generer_image_ia(personnage, prompt)
            image_response = requests.get(image_url)

            # Ouvrir l'image avec PIL
            img = Image.open(BytesIO(image_response.content))

            # Calculer les nouvelles dimensions (2x plus petit en largeur et hauteur)
            new_size = (img.width // 4, img.height // 4)
            img_resized = img.resize(new_size)

            # Enregistrer l'image redimensionnée
            img_resized.save(image_path)
            print(f"Image enregistrée sous : {image_path}")
            print(f"Image générée : {image_url}")
        except Exception as e:
            print(f"Erreur lors de la génération de l'image : {e}")
            print("L'URL de l'image n'est pas valide ou l'image n'a pas pu être téléchargée.")
