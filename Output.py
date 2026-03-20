import mysql.connector
import pandas as pd
import matplotlib.pyplot as plt
import seaborn as sns

# -------------------------------
# 1️⃣ Verbindung zur Datenbank
# -------------------------------
conn = mysql.connector.connect(
    host="stardrop-saloon.de",
    user="root",
    password="alohomoraberlin",
    database="WebscrapingDB",
    port=3306,
)

cursor = conn.cursor(dictionary=True)

# -------------------------------
# 2️⃣ Daten abfragen
# -------------------------------
query = """
SELECT 
    a.Buchtitel,
    g.Genre_Name,
    m.Medientyp,
    a.Preis,
    a.Groesse_Beschreibung,
    a.Daten_menge_thumbnail,
    a.UPC
FROM Artikel a
LEFT JOIN Genre g ON a.Genre_ID = g.Genre_ID
LEFT JOIN Medientypen m ON a.Medientyp_ID = m.Medientyp_ID;
"""

cursor.execute(query)
data = cursor.fetchall()

# In DataFrame umwandeln
df = pd.DataFrame(data)

# Verbindung schließen
cursor.close()
conn.close()

# -------------------------------
# 3️⃣ Grundlegende Kennzahlen
# -------------------------------
anzahl = len(df)
preis_min = df['Preis'].min()
preis_max = df['Preis'].max()
preis_mittel = df['Preis'].mean()
thumb_mittel = df['Daten_menge_thumbnail'].mean()
einzigartige_upc = df['UPC'].nunique()

# Annahme: Groesse_Beschreibung = Anzahl der Wörter
df['Anzahl_Woerter'] = df['Groesse_Beschreibung']

print(f"Anzahl Einträge: {anzahl}")
print(f"Preis - Min: {preis_min}, Max: {preis_max}, Mittelwert: {preis_mittel:.2f}")
print(f"Durchschnittliche Thumbnail-Größe: {thumb_mittel:.2f}")
print(f"Einzigartige UPC-Nummern: {einzigartige_upc}")

# -------------------------------
# 4️⃣ Grafische Auswertungen
# -------------------------------

sns.set_style("whitegrid")

# Buchtitel-Häufigkeit
plt.figure(figsize=(10,6))
sns.countplot(y='Buchtitel', data=df, order=df['Buchtitel'].value_counts().index)
plt.title("Häufigkeit der Buchtitel")
plt.xlabel("Anzahl")
plt.ylabel("Buchtitel")
plt.tight_layout()
plt.show()

# Preisverteilung
plt.figure(figsize=(8,5))
sns.histplot(df['Preis'], bins=10, kde=True)
plt.title("Preisverteilung")
plt.xlabel("Preis")
plt.ylabel("Anzahl")
plt.tight_layout()
plt.show()

# Durchschnittlicher Preis pro Genre
plt.figure(figsize=(8,5))
sns.barplot(x='Preis', y='Genre_Name', data=df, estimator=lambda x: sum(x)/len(x))
plt.title("Durchschnittlicher Preis pro Genre")
plt.xlabel("Durchschnittlicher Preis")
plt.ylabel("Genre")
plt.tight_layout()
plt.show()

# Durchschnittliche Thumbnail-Größe pro Medientyp
plt.figure(figsize=(8,5))
sns.barplot(x='Daten_menge_thumbnail', y='Medientyp', data=df, estimator=lambda x: sum(x)/len(x))
plt.title("Durchschnittliche Thumbnail-Größe pro Medientyp")
plt.xlabel("Durchschnittliche Thumbnail-Größe")
plt.ylabel("Medientyp")
plt.tight_layout()
plt.show()