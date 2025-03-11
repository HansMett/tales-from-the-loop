import streamlit as st
import json
import csv
import pandas as pd
from io import StringIO, BytesIO
from fpdf import FPDF
import os

# 🔹 Sicherstellen, dass der Speicherordner existiert
SAVE_DIR = "charaktere"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Titel der App
st.title("Tales from the Loop - Heldenbogen")

# Eingabe: Name und Alter (mit `session_state`)
name = st.text_input("Name des Charakters", value=st.session_state.get("name", ""))
st.session_state.name = name

alter = st.slider("Alter", 10, 15, st.session_state.get("alter", 12))
st.session_state.alter = alter  # Stelle sicher, dass das Alter im Session State aktualisiert wird



# Falls noch nicht gesetzt, Initialisieren

if "attribute_values" not in st.session_state:
    st.session_state.attribute_values = {attr: 1 for attr in ["Körper", "Technik", "Herz", "Verstand"]}

st.subheader("Attribute")

attribute_values = {}
cols = st.columns(4)  # Nutze vier Spalten für Attribute

max_attribute_points = st.session_state.get("alter", 12)  # Die Summe der Attribute muss dem Alter entsprechen
remaining_attr_points = max_attribute_points - sum(st.session_state.attribute_values.values())

for i, attr in enumerate(["Körper", "Technik", "Herz", "Verstand"]):
    current_value = st.session_state.attribute_values.get(attr, 1)
    max_possible = 5
    
    attribute_values[attr] = cols[i % 4].slider(attr, 1, max_possible, current_value)

    # Neue Punkte berechnen nach jeder Änderung
    remaining_attr_points = max_attribute_points - sum(attribute_values.values())

st.session_state.attribute_values = attribute_values

# Verbleibende Punkte separat unter den Slidern anzeigen
st.subheader(f"Verbleibende Attributspunkte: {remaining_attr_points}")



# 🔹 Heldenklassen definieren **vor** der Nutzung
heldenklassen = {
    "Bücherwurm": ["Berechnen", "Ermitteln", "Begreifen"],
    "Computernerd": ["Berechnen", "Programmieren", "Begreifen"],
    "Bauer": ["Kraftakt", "Bewegen", "Tüfteln"],
    "Sportler": ["Kraftakt", "Bewegen", "Kontakte"],
    "Klassenliebling": ["Kontakte", "Schmeicheln", "Führen"],
    "Rocker": ["Bewegen", "Schmeicheln", "Einfühlen"],
    "Troublemaker": ["Kraftakt", "Schleichen", "Führen"],
    "Sonderling": ["Schleichen", "Ermitteln", "Einfühlen"]
}

# Standardwert setzen, falls noch nicht in session_state
if "heldenklasse" not in st.session_state:
    st.session_state.heldenklasse = "Bücherwurm"

# `selectbox` mit sicherem Index
heldenklasse = st.selectbox(
    "Heldenklasse",
    list(heldenklassen.keys()),
    index=list(heldenklassen.keys()).index(st.session_state.heldenklasse)  # Jetzt sicher!
)

# Aktualisiere `session_state`, falls der Nutzer eine neue Klasse wählt
st.session_state.heldenklasse = heldenklasse


# 🔹 Fähigkeiten definieren **vor** der Nutzung
skills = [
    "Schleichen", "Kraftakt", "Bewegen", "Tüfteln", "Programmieren", "Berechnen",
    "Kontakte", "Schmeicheln", "Führen", "Ermitteln", "Begreifen", "Einfühlen"
]

max_skill_points = 10

# Falls noch nicht gesetzt, Initialisieren
if "skill_values" not in st.session_state:
    st.session_state.skill_values = {skill: 0 for skill in skills}

st.subheader("Fähigkeiten")

skill_values = {}
cols = st.columns(6)  # Nutze mehrere Spalten für eine bessere Darstellung

for i, skill in enumerate(skills):
    max_wert = 3 if skill in heldenklassen.get(heldenklasse, []) else 1
    current_value = st.session_state.skill_values.get(skill, 0)
    remaining_points = max_skill_points - sum(skill_values.values())
    max_possible = max_wert
    
    skill_values[skill] = cols[i % 6].slider(skill, 0, max_possible, current_value)

    # Neue Punkte berechnen nach jeder Änderung
    remaining_points = max_skill_points - sum(skill_values.values())

st.session_state.skill_values = skill_values

# Verbleibende Punkte separat unter den Slidern anzeigen
st.subheader(f"Verbleibende Fähigkeitenpunkte: {remaining_points}")



# Charakterbeschreibung mit `session_state`
st.subheader("Charakterbeschreibung")
beschreibung = {
    "Antrieb": st.text_area("Antrieb", value=st.session_state.get("beschreibung", {}).get("Antrieb", "")),
    "Problem": st.text_area("Problem", value=st.session_state.get("beschreibung", {}).get("Problem", "")),
    "Stolz": st.text_area("Stolz", value=st.session_state.get("beschreibung", {}).get("Stolz", "")),
    "Anker": st.text_area("Anker", value=st.session_state.get("beschreibung", {}).get("Anker", "")),
    "Beschreibung": st.text_area("Beschreibung", value=st.session_state.get("beschreibung", {}).get("Beschreibung", "")),
    "Lieblingslied": st.text_input("Lieblingslied 🎵", value=st.session_state.get("beschreibung", {}).get("Lieblingslied", "")),
}
st.session_state.beschreibung = beschreibung

# Inventar mit `session_state`
st.subheader("Inventar")
# Stelle sicher, dass die Liste genau 3 Elemente hat
session_inventar = st.session_state.get("inventar", ["", "", ""])  # Standardwert mit 3 leeren Strings
session_inventar += [""] * (3 - len(session_inventar))  # Falls zu kurz, auffüllen

# Inventar-Eingabefelder
inventar = [st.text_input(f"Gegenstand {i+1}", value=session_inventar[i]) for i in range(3)]
st.session_state.inventar = inventar


# Versteck & Notizen mit `session_state`
versteck = st.text_area("Versteck", value=st.session_state.get("versteck", ""))
st.session_state.versteck = versteck

notizen = st.text_area("Zusätzliche Notizen", value=st.session_state.get("notizen", ""))
st.session_state.notizen = notizen


# 🔹 Glückspunkte berechnen (falls nicht vorhanden)
glueckspunkte = 15 - alter



#Warnung, falls nicht genau 10 Skill-Punkte verteilt wurden
gesamt_skills = sum(skill_values.values())
if gesamt_skills != 10:
    st.warning(f"⚠️ Es müssen genau 10 Punkte auf die Fähigkeiten verteilt werden! (Derzeit: {gesamt_skills})")

# Warnung, falls Attributpunkte nicht dem Alter entsprechen
gesamt_attributpunkte = sum(attribute_values.values())
if gesamt_attributpunkte != alter:
    st.warning(f"⚠️ Die Summe der Attributpunkte muss genau {alter} betragen! (Derzeit: {gesamt_attributpunkte})")


# 🔹 **Download der CSV-Datei**
def download_csv():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Feld", "Wert"])
    writer.writerow(["Name", name])
    writer.writerow(["Alter", alter])
    writer.writerow(["Heldenklasse", heldenklasse])
    writer.writerow(["Glückspunkte", st.session_state.get("glueckspunkte", 15 - alter)])
    writer.writerow(["Attribute", json.dumps(st.session_state.get("attribute_values", {
        "Körper": 1,
        "Technik": 1,
        "Herz": 1,
        "Verstand": 1
    }))])
    writer.writerow(["Fähigkeiten", json.dumps(st.session_state.get("skill_values", {}))])
    writer.writerow(["Beschreibung", json.dumps(st.session_state.get("beschreibung", {}))])
    writer.writerow(["Inventar", ", ".join(st.session_state.get("inventar", ["", "", ""]))])
    writer.writerow(["Versteck", st.session_state.get("versteck", "")])
    writer.writerow(["Notizen", st.session_state.get("notizen", "")])
    return output.getvalue()



st.download_button(
    label="📥 CSV herunterladen",
    data=download_csv(),
    file_name=f"{name}_{heldenklasse}.csv",
    mime="text/csv"
)

# 🔹 **Upload einer CSV-Datei**
uploaded_file = st.file_uploader("Lade eine CSV-Datei hoch", type="csv")
if uploaded_file:
    try:
        # Datei in einen lesbaren Stream umwandeln
        bytes_data = uploaded_file.getvalue()
        stringio = StringIO(bytes_data.decode("utf-8"))
        
        # CSV-Datei mit Pandas einlesen
        df = pd.read_csv(stringio)

        # Prüfen, ob die Datei die erwarteten Spalten hat
        required_columns = ["Feld", "Wert"]
        if not all(col in df.columns for col in required_columns):
            st.error("⚠️ Fehler: Die hochgeladene Datei hat nicht die richtigen Spalten!")
        else:
            # Werte aus der CSV-Datei extrahieren und in `session_state` speichern
            st.session_state.name = df[df["Feld"] == "Name"]["Wert"].values[0]
            st.session_state.alter = int(df[df["Feld"] == "Alter"]["Wert"].values[0])
            st.session_state.heldenklasse = df[df["Feld"] == "Heldenklasse"]["Wert"].values[0]
            st.session_state.glueckspunkte = int(df[df["Feld"] == "Glückspunkte"]["Wert"].values[0])
            st.session_state.attribute = json.loads(df[df["Feld"] == "Attribute"]["Wert"].values[0])
            st.session_state.skill_values = json.loads(df[df["Feld"] == "Fähigkeiten"]["Wert"].values[0])
            st.session_state.beschreibung = json.loads(df[df["Feld"] == "Beschreibung"]["Wert"].values[0])
            st.session_state.inventar = df[df["Feld"] == "Inventar"]["Wert"].values[0].split(", ")
            st.session_state.versteck = df[df["Feld"] == "Versteck"]["Wert"].values[0]
            st.session_state.notizen = df[df["Feld"] == "Notizen"]["Wert"].values[0]

            st.success(f"✅ Charakter **{st.session_state.name}** wurde erfolgreich aus der CSV geladen!")

            # Füge den "Aktualisieren"-Button hinzu
            if st.button("🔄 Aktualisieren"):
                st.rerun()  # Die gesamte App wird neu geladen

    except Exception as e:
        st.error(f"⚠️ Fehler beim Verarbeiten der Datei: {e}")





class PDF(FPDF):
    def __init__(self):
        super().__init__()
        self.background = "hintergrund_transparent.png"  # 🔹 Setze den Dateinamen deines Hintergrundbilds
        self.set_auto_page_break(auto=True, margin=15)
    
        if not hasattr(self, "fonts") or "CustomFont" not in self.fonts:
            self.add_font("CustomFont", "", "Starjedi.ttf", uni=True)
        if not hasattr(self, "fonts") or "CustomFont2" not in self.fonts:
            self.add_font("CustomFont2", "", "Orbitron-Regular.ttf", uni=True)


    def header(self):
        if os.path.exists(self.background):
            self.image(self.background, 0, 0, 210, 297)  # 🔹 Transparentes Hintergrundbild setzen
        self.set_font("CustomFont", size=16)

        self.set_text_color(0, 0, 0)  # Schwarzer Titel-Text
        self.cell(192, 10, f"Heldenbogen: {st.session_state.get('heldenklasse', 'Unbekannt')}", border=0, ln=True, align="C")
        self.ln(5)
        
        # Name, Alter und Glückspunkte
        self.set_font("CustomFont", size=12)
        self.cell(96, 6, f"Name: {st.session_state.get('name', 'Unbekannt')}", border=1, ln=False)
        self.cell(48, 6, f"Alter: {st.session_state.get('alter', 'Unbekannt')}", border=1, ln=False)
        self.cell(48, 6, f"Glückspunkte: {15 - int(st.session_state.get('alter', 12))}", border=1, ln=True)
        self.ln(5)

    def add_table(self, title, data, columns=2):
        self.set_text_color(0, 0, 0)  # Schwarzer Text
        self.set_font("CustomFont", size=12)
        self.cell(192, 7, title, border=1, ln=True, align="C")
        self.set_font("CustomFont2", size=10)

        col_width = 192 // columns
        keys = list(data.keys())
        values = list(data.values())
        
        for i in range(0, len(keys), columns):
            for j in range(columns):
                if i + j < len(keys):
                    self.cell(col_width, 6, f"{keys[i + j]}", border=1, align="C")
            self.ln()
            for j in range(columns):
                if i + j < len(values):
                    self.cell(col_width, 6, f"{values[i + j]}", border=1, align="C")
            self.ln()
        self.ln(5)

    def add_skills_table(self, skills):
        self.set_text_color(0, 0, 0)
        self.set_font("CustomFont", size=12)
        self.cell(192, 7, "Fähigkeiten", border=1, ln=True, align="C")
        self.set_font("CustomFont2", size=10)

        col_width = 192 // 4  # 4 Spalten
        attribute_names = ["Körper", "Technik", "Herz", "Verstand"]
        skill_groups = list(skills.items())

        # Kopfzeile mit Attributen
        for attr in attribute_names:
            self.cell(col_width, 6, attr, border=1, align="C")
        self.ln()

        # Fähigkeiten unter den Attributen
        for row in range(3):  # 3 Fähigkeiten pro Attribut
            for col in range(4):
                skill_index = row + col * 3
                if skill_index < len(skill_groups):
                    skill_name, skill_value = skill_groups[skill_index]
                    self.cell(col_width, 6, f"{skill_name[:10]}: {skill_value}", border=1, align="C")
            self.ln()
        self.ln(5)

    def add_section(self, title, content):
        self.set_text_color(0, 0, 0)
        self.set_font("CustomFont", size=12)
        self.cell(192, 7, title, border=1, ln=True, align="C")
        self.set_font("CustomFont2", size=10)
        self.multi_cell(192, 6, str(content), border=1)
        self.ln(3)

    def add_inventory(self, items):
        self.add_section("inventar", "\n".join(items))


def generate_pdf():
    pdf = PDF()
    pdf.add_page()
    
    pdf.add_table("Attribute", st.session_state.attribute_values, columns=4)
    pdf.add_skills_table(st.session_state.skill_values)

    for key in ["Antrieb", "Problem", "Stolz", "Anker", "Beschreibung", "Lieblingslied"]:
        value = st.session_state.get("beschreibung", {}).get(key, "(Keine Angabe)")
        pdf.add_section(key, value)
       
    
    pdf.add_inventory(st.session_state.get("inventar", ["", "", ""]))
    pdf.add_section("versteck", st.session_state.get("versteck", ""))
    pdf.add_section("Notizen", st.session_state.get("notizen", ""))
    
    return pdf.output(dest="S").encode("latin1")

if st.button("PDF speichern"):
    pdf_data = generate_pdf()
    st.download_button("📥 PDF herunterladen", data=pdf_data, file_name=f"{st.session_state.get('name', 'Charakter')}.pdf", mime="application/pdf")

