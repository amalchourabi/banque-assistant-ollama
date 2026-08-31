import requests
import base64
import os
from tkinter import Tk, filedialog

def choisir_image():
    root = Tk()
    root.withdraw()
    root.attributes('-topmost', True)
    chemin = filedialog.askopenfilename(
        title="Choisis une image depuis ton PC",
        filetypes=[("Images", "*.png *.jpg *.jpeg *.bmp *.webp")]
    )
    root.destroy()
    return chemin

print("Une fenêtre va s'ouvrir pour choisir ton image...")
image_path = choisir_image()

if not image_path:
    print("Aucune image sélectionnée. Arrêt du programme.")
    exit()

print(f"Image sélectionnée : {image_path}")

with open(image_path, "rb") as f:
    image_data = base64.b64encode(f.read()).decode()

prompt = input("Ta question sur l'image (ou Entrée pour 'décris ce document') : ").strip()
if not prompt:
    prompt = "décris ce document"

try:
    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            "model": "banque-assistant-image",
            "prompt": prompt,
            "images": [image_data],
            "stream": False
        },
        timeout=120
    )
    response.raise_for_status()
    result = response.json()
    print("\nRéponse du modèle :\n")
    print(result["response"])

except requests.exceptions.ConnectionError:
    print("Erreur : impossible de se connecter à Ollama. Vérifie qu'il tourne bien.")
except requests.exceptions.Timeout:
    print("Erreur : le modèle a mis trop de temps à répondre.")
except requests.exceptions.RequestException as e:
    print(f"Erreur lors de la requête : {e}")