import sqlite3
import random
from datetime import datetime, timedelta

DB_FILE = "banque.db"

PRENOMS = ["Amal", "Karim", "Sana", "Youssef", "Nour", "Wassim", "Ines", "Mehdi", "Leila", "Omar"]
NOMS = ["Ben Ali", "Trabelsi", "Chourabi", "Gharbi", "Mansouri", "Jlassi", "Khelifi", "Bouazizi"]
VILLES = ["Tunis", "Sfax", "Sousse", "Nabeul", "Bizerte"]
TYPES_COMPTE = ["Compte courant", "Compte épargne", "Compte professionnel"]
TYPES_CREDIT = ["Crédit consommation", "Crédit immobilier", "Crédit auto"]
STATUTS_CREDIT = ["En cours d'étude", "Approuvé", "Refusé", "En attente de documents"]
TYPES_TRANSACTION = ["Virement reçu", "Virement envoyé", "Paiement carte", "Retrait DAB", "Prélèvement"]
LIBELLES = ["STEG", "SONEDE", "Loyer", "Salaire", "Achat Carrefour", "Virement Ami", "Abonnement Internet"]

def creer_tables(cur):
    cur.execute("""
    CREATE TABLE IF NOT EXISTS clients (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        nom_complet TEXT,
        cin TEXT UNIQUE,
        adresse TEXT,
        telephone TEXT,
        email TEXT
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS comptes (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        iban TEXT UNIQUE,
        type_compte TEXT,
        solde REAL,
        devise TEXT,
        date_ouverture TEXT,
        FOREIGN KEY (client_id) REFERENCES clients(id)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS transactions (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        compte_id INTEGER,
        date TEXT,
        type TEXT,
        montant REAL,
        libelle TEXT,
        FOREIGN KEY (compte_id) REFERENCES comptes(id)
    )""")
    cur.execute("""
    CREATE TABLE IF NOT EXISTS credits (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        client_id INTEGER,
        type_credit TEXT,
        montant_demande REAL,
        duree_mois INTEGER,
        taux_interet REAL,
        statut TEXT,
        FOREIGN KEY (client_id) REFERENCES clients(id)
    )""")

def generer_donnees(cur, nb_clients=20):
    for _ in range(nb_clients):
        prenom = random.choice(PRENOMS)
        nom = random.choice(NOMS)
        nom_complet = f"{prenom} {nom}"
        cin = str(random.randint(10000000, 99999999))
        adresse = f"{random.randint(1,150)} Rue {random.choice(['de la Liberté','Habib Bourguiba','Ibn Khaldoun'])}, {random.choice(VILLES)}"
        telephone = f"+216 {random.randint(20,99)} {random.randint(100,999)} {random.randint(100,999)}"
        email = f"{prenom.lower()}.{nom.lower().replace(' ','')}@email.com"

        cur.execute("""INSERT OR IGNORE INTO clients (nom_complet, cin, adresse, telephone, email)
                        VALUES (?, ?, ?, ?, ?)""", (nom_complet, cin, adresse, telephone, email))
        client_id = cur.lastrowid

        # Un ou deux comptes par client
        for _ in range(random.randint(1, 2)):
            iban = f"TN59 {random.randint(1000,9999)} {random.randint(1000,9999)} {random.randint(1000000000,9999999999)} {random.randint(10,99)}"
            type_compte = random.choice(TYPES_COMPTE)
            solde = round(random.uniform(50, 15000), 2)
            date_ouverture = (datetime.now() - timedelta(days=random.randint(30, 2000))).strftime("%d/%m/%Y")

            cur.execute("""INSERT INTO comptes (client_id, iban, type_compte, solde, devise, date_ouverture)
                            VALUES (?, ?, ?, ?, ?, ?)""",
                        (client_id, iban, type_compte, solde, "TND", date_ouverture))
            compte_id = cur.lastrowid

            # Quelques transactions par compte
            for _ in range(random.randint(3, 8)):
                date = (datetime.now() - timedelta(days=random.randint(0, 60))).strftime("%d/%m/%Y")
                type_t = random.choice(TYPES_TRANSACTION)
                montant = round(random.uniform(-500, 2000), 2)
                libelle = random.choice(LIBELLES)
                cur.execute("""INSERT INTO transactions (compte_id, date, type, montant, libelle)
                                VALUES (?, ?, ?, ?, ?)""", (compte_id, date, type_t, montant, libelle))

        # Certains clients ont une demande de crédit
        if random.random() < 0.4:
            type_credit = random.choice(TYPES_CREDIT)
            montant_demande = random.randint(5000, 200000)
            duree_mois = random.choice([12, 24, 36, 60, 120])
            taux = round(random.uniform(5.5, 12.5), 2)
            statut = random.choice(STATUTS_CREDIT)
            cur.execute("""INSERT INTO credits (client_id, type_credit, montant_demande, duree_mois, taux_interet, statut)
                            VALUES (?, ?, ?, ?, ?, ?)""",
                        (client_id, type_credit, montant_demande, duree_mois, taux, statut))

if __name__ == "__main__":
    conn = sqlite3.connect(DB_FILE)
    cur = conn.cursor()
    creer_tables(cur)
    generer_donnees(cur, nb_clients=20)
    conn.commit()
    conn.close()
    print(f"Base de données '{DB_FILE}' créée avec succès (20 clients, comptes, transactions, crédits).")