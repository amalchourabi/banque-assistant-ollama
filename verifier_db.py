import sqlite3

conn = sqlite3.connect("banque.db")
cur = conn.cursor()

print("=== CLIENTS ===")
for row in cur.execute("SELECT * FROM clients LIMIT 5"):
    print(row)

print("\n=== COMPTES ===")
for row in cur.execute("SELECT * FROM comptes LIMIT 5"):
    print(row)

print("\n=== TRANSACTIONS ===")
for row in cur.execute("SELECT * FROM transactions LIMIT 5"):
    print(row)

print("\n=== CREDITS ===")
for row in cur.execute("SELECT * FROM credits LIMIT 5"):
    print(row)

conn.close()