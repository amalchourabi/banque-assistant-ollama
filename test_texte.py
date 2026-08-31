import requests
import json
import os
from datetime import datetime

LOG_FILE = "logs/historique_texte.json"

def charger_historique():
    if os.path.exists(LOG_FILE):
        with open(LOG_FILE, "r", encoding="utf-8") as f:
            return json.load(f)
    return []

def sauvegarder_historique(historique):
    os.makedirs("logs", exist_ok=True)
    with open(LOG_FILE, "w", encoding="utf-8") as f:
        json.dump(historique, f, ensure_ascii=False, indent=2)

print("=== Test Banque Assistant (Texte) ===")
print("Tape '/bye' pour quitter\n")

historique = charger_historique()

while True:
    prompt = input("Ta question : ").strip()
    
    if prompt.lower() == "/bye":
        print("Au revoir !")
        break
    
    if not prompt:
        continue
    try:
        response = requests.post(
            'http://localhost:11434/api/generate',
            json={
                "model": "banque-assistant-texte",
                "prompt": prompt,
                "stream": False
            },
            timeout=300
        )
        response.raise_for_status()
        result = response.json()
        reponse_texte = result["response"]

        print("\nRéponse du modèle :\n")
        print(reponse_texte)
        print("\n" + "-"*50 + "\n")

        historique.append({
            "date": datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
            "modele": "banque-assistant-texte",
            "question": prompt,
            "reponse": reponse_texte
        })
        sauvegarder_historique(historique)

    except requests.exceptions.ConnectionError:
        print("Erreur : impossible de se connecter à Ollama. Vérifie qu'il tourne bien (ollama serve).")
    except requests.exceptions.Timeout:
        print("Erreur : le modèle a mis trop de temps à répondre.")
    except requests.exceptions.RequestException as e:
        print(f"Erreur lors de la requête : {e}")
    except KeyError:
        print(f"Réponse inattendue du serveur : {response.text}")