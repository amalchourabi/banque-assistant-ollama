import sqlite3
from werkzeug.security import generate_password_hash

conn = sqlite3.connect("banque.db")
cur = conn.cursor()

# Table des identifiants de connexion, liée à chaque client
cur.execute("""
CREATE TABLE IF NOT EXISTS utilisateurs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    client_id INTEGER UNIQUE,
    identifiant TEXT UNIQUE,
    mot_de_passe_hash TEXT,
    FOREIGN KEY (client_id) REFERENCES clients(id)
)""")

# Récupère tous les clients existants et crée un compte pour chacun
cur.execute("SELECT id, cin FROM clients")
clients = cur.fetchall()

for client_id, cin in clients:
    identifiant = cin  # utilise le CIN comme identifiant de connexion
    mot_de_passe = "password123"  # mot de passe par défaut pour la démo
    hash_pwd = generate_password_hash(mot_de_passe)
    cur.execute("""INSERT OR IGNORE INTO utilisateurs (client_id, identifiant, mot_de_passe_hash)
                    VALUES (?, ?, ?)""", (client_id, identifiant, hash_pwd))

conn.commit()
conn.close()
print("Comptes utilisateurs créés. Identifiant = CIN du client, mot de passe = 'password123' pour tous (démo).")