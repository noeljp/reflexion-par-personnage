import openai
import os
import base64
import requests

# Configuration de la clé API OpenAI
openai.api_key = os.getenv("OPENAI_API_KEY")  # Ou remplace par ta clé directement (non recommandé en prod)




def preparer_contexte_reflexion(personnage, theme):
    prompt_system = (
        "Tu es un expert en analyse littéraire et philosophique."
        " Ton objectif est de préparer un cadre de réflexion."
    )
    prompt_user = (
        f"Le personnage suivant va réfléchir à ce thème : « {theme} ».\n"
        f"Personnage : {personnage}\n\n"
        "1. Analyse le style d'expression du personnage (ton, vocabulaire, références, rythme, etc.).\n"
        "2. Décris sa manière de penser (logique, métaphores, structure d'argumentation, etc.).\n"
        "3. Propose 3 axes de réflexion que ce personnage pourrait développer sur le thème.\n"
        "4. Donne quelques références ou images qu’il pourrait utiliser pour enrichir sa pensée.\n"
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": prompt_system},
            {"role": "user", "content": prompt_user}
        ],
        temperature=0.7,
        max_tokens=1500
    )
    return response.choices[0].message.content.strip()

def generer_reflexion_ia(personnage, theme, elements_preparatoires, img_path):
    prompt = (
        f"Personnage : {personnage}\n"
        f"Thème : {theme}\n"
        f"Contexte préparatoire :\n{elements_preparatoires}\n\n"
        "Écris une réflexion approfondie comme si elle était rédigée par ce personnage."
        " Adopte fidèlement son style, ses références, ses tournures d’esprit. "
        "Structure la réflexion avec clarté et densité, comme un texte littéraire ou philosophique."
        f"Rédige en markdown avec l'image suivante : {img_path} comme référence visuelle au début.\n\n"
    )
    
    response = openai.ChatCompletion.create(
        model="gpt-4",
        messages=[
            {"role": "system", "content": "Tu es le personnage. Tu rédiges un dialogue personnelle et stylisée."},
            {"role": "user", "content": prompt}
        ],
        temperature=0.8,
        max_tokens=4000
    )
    return response.choices[0].message.content.strip()


# Étape 2 : Générer une image illustrant le personnage face à l’IA
def generer_image_ia(personnage,prompt):
    dalle_prompt = (
        f"Un avatar de {personnage}, placé dans son contexte, "
        f"confronté a cette idée: '{prompt.strip()[:80]}...', "
        
    )

    response = openai.Image.create(
        model="dall-e-3",
        prompt=dalle_prompt,
        n=1,
        size="1024x1024"
    )
    
    image_url = response['data'][0]['url']
    return image_url


import requests

def charger_personnages(fichier):
    with open(fichier, "r", encoding="utf-8") as f:
        return [ligne.strip() for ligne in f if ligne.strip()]

if __name__ == "__main__":
    personnages = charger_personnages("personnage.txt")
    print("Liste des personnages disponibles :")
    for p in personnages:
        print(f"- {p}")
    
        personnage = p

        prompt = """Tu découvres l'intelligence artificielle et tu te demandes ce que cela signifie pour l'humanité."""
        image_path = f"{personnage}_image.png"

        print("\n--- RÉFLEXION GÉNÉRÉE ---\n")
        contexte = preparer_contexte_reflexion(personnage, prompt)
        print(contexte)

        print("\n--- GÉNÉRATION DE TEXTE EN COURS ---\n")
        reflexion = generer_reflexion_ia(personnage, prompt, contexte, image_path)

        with open(f"{personnage}_reflexion.md", "w", encoding="utf-8") as f:
            f.write(reflexion)
        print(reflexion)

        print("\n--- GÉNÉRATION D'IMAGE EN COURS ---\n")
        image_url = generer_image_ia(personnage, prompt)
        image_response = requests.get(image_url)

        with open(image_path, "wb") as img_file:
            img_file.write(image_response.content)
        print(f"Image enregistrée sous : {image_path}")
        print(f"Image générée : {image_url}")

