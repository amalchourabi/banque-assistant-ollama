import sqlite3
import requests

DB_FILE = "banque.db"

def rechercher_client(nom_ou_cin):
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    cur.execute("""SELECT * FROM clients WHERE nom_complet LIKE ? OR cin = ?""",
                (f"%{nom_ou_cin}%", nom_ou_cin))
    client = cur.fetchone()
    if not client:
        conn.close()
        return None

    client_id = client[0]
    cur.execute("SELECT * FROM comptes WHERE client_id = ?", (client_id,))
    comptes = cur.fetchall()

    cur.execute("SELECT * FROM credits WHERE client_id = ?", (client_id,))
    credits = cur.fetchall()

    conn.close()
    return {"client": client, "comptes": comptes, "credits": credits}

def construire_contexte(donnees):
    if not donnees:
        return "Aucune information trouvée pour ce client."

    client = donnees["client"]
    contexte = f"Client : {client[1]}, CIN : {client[2]}, Email : {client[5]}\n\n"

    contexte += "Comptes :\n"
    for c in donnees["comptes"]:
        contexte += f"- IBAN {c[2]}, {c[3]}, Solde : {c[4]} {c[5]}, ouvert le {c[6]}\n"

    if donnees["credits"]:
        contexte += "\nCrédits :\n"
        for cr in donnees["credits"]:
            contexte += f"- {cr[2]}, Montant demandé : {cr[3]} TND, Durée : {cr[4]} mois, Statut : {cr[6]}\n"

    return contexte

def interroger_assistant(question, contexte):
    prompt_complet = f"""Voici les informations du client concerné :
{contexte}

Question du client : {question}"""

    response = requests.post(
        'http://localhost:11434/api/generate',
        json={
            "model": "banque-assistant-texte",
            "prompt": prompt_complet,
            "stream": False
        },
        timeout=300
    )
    response.raise_for_status()
    return response.json()["response"]

if __name__ == "__main__":
    print("=== Assistant Bancaire RAG (connecté à la base de données) ===\n")
    nom_recherche = input("Nom ou CIN du client à rechercher : ").strip()
    donnees = rechercher_client(nom_recherche)

    if not donnees:
        print("Client introuvable dans la base.")
    else:
        contexte = construire_contexte(donnees)
        print("\n--- Contexte trouvé ---")
        print(contexte)

        while True:
            question = input("\nTa question (ou /bye pour quitter) : ").strip()
            if question.lower() == "/bye":
                break
            reponse = interroger_assistant(question, contexte)
            print("\nRéponse de l'assistant :\n")
            print(reponse)