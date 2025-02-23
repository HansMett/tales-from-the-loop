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
alter = st.slider("Alter", 10, 15, st.session_state.get("alter", 12))

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

# 🔹 Fähigkeiten mit `session_state`
st.subheader("Fähigkeiten")
skill_values = {}
cols = st.columns(6)
for i, skill in enumerate(skills):
    max_wert = 3 if skill in heldenklassen.get(heldenklasse, []) else 1
    skill_values[skill] = cols[i % 6].slider(
        f"{skill}",
        0,
        max_wert,
        st.session_state.get("skill_values", {}).get(skill, 0)
    )

# Charakterbeschreibung mit `session_state`
st.subheader("Charakterbeschreibung")
beschreibung = {
    "Antrieb": st.text_area("Antrieb", value=st.session_state.get("beschreibung", {}).get("Antrieb", "")),
    "Problem": st.text_area("Problem", value=st.session_state.get("beschreibung", {}).get("Problem", "")),
    "Stolz": st.text_area("Stolz", value=st.session_state.get("beschreibung", {}).get("Stolz", "")),
    "Beschreibung": st.text_area("Beschreibung", value=st.session_state.get("beschreibung", {}).get("Beschreibung", "")),
    "Lieblingslied": st.text_input("Lieblingslied 🎵", value=st.session_state.get("beschreibung", {}).get("Lieblingslied", "")),
}

# Inventar mit `session_state`
st.subheader("Inventar")
# Stelle sicher, dass die Liste genau 3 Elemente hat
session_inventar = st.session_state.get("inventar", ["", "", ""])  # Standardwert mit 3 leeren Strings
session_inventar += [""] * (3 - len(session_inventar))  # Falls zu kurz, auffüllen

# Inventar-Eingabefelder
inventar = [st.text_input(f"Gegenstand {i+1}", value=session_inventar[i]) for i in range(3)]

# Versteck & Notizen mit `session_state`
versteck = st.text_area("Versteck", value=st.session_state.get("versteck", ""))
notizen = st.text_area("Zusätzliche Notizen", value=st.session_state.get("notizen", ""))

# 🔹 Glückspunkte berechnen (falls nicht vorhanden)
glueckspunkte = 15 - alter


# 🔹 **Download der CSV-Datei**
def download_csv():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Feld", "Wert"])
    writer.writerow(["Name", name])
    writer.writerow(["Alter", alter])
    writer.writerow(["Heldenklasse", heldenklasse])
    writer.writerow(["Glückspunkte", st.session_state.get("glueckspunkte", 15 - alter)])  # Sicherstellen, dass `glueckspunkte` existiert
    writer.writerow(["Attribute", json.dumps(attribute)])
    writer.writerow(["Fähigkeiten", json.dumps(skill_values)])
    writer.writerow(["Beschreibung", json.dumps(beschreibung)])
    writer.writerow(["Inventar", ", ".join(inventar)])
    writer.writerow(["Versteck", versteck])
    writer.writerow(["Notizen", notizen])
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

    except Exception as e:
        st.error(f"⚠️ Fehler beim Verarbeiten der Datei: {e}")




# 🔹 **PDF-Generierung**
class PDF(FPDF):
    def header(self):
        self.set_font("Arial", "B", 14)
        self.cell(190, 10, f"{name} - {heldenklasse}", border=1, ln=True, align="C")
        self.ln(5)

    def add_section(self, title, content):
        self.set_font("Arial", "B", 12)
        self.cell(190, 7, title, border=1, ln=True, align="C")
        self.set_font("Arial", size=10)
    
        # **Sicherstellen, dass content ein String ist**
        if content is None:
            content = ""  # Falls None, leeren String setzen
        elif isinstance(content, list):
            content = "\n".join(content)  # Falls Liste, umwandeln
    
        self.multi_cell(190, 6, str(content), border=1)  # In String umwandeln
        self.ln(3)


    def add_glueckspunkte(self, glueck):
        self.set_font("Arial", "B", 12)
        self.cell(190, 7, "Glückspunkte", border=1, ln=True, align="C")
        self.set_font("Arial", size=10)
        self.cell(190, 6, f"Verfügbare Glückspunkte: {glueck}", border=1, ln=True)
        self.ln(5)

    def add_attributes(self, attributes):
        self.set_font("Arial", "B", 12)
        self.cell(190, 7, "Attribute", border=1, ln=True, align="C")
        self.set_font("Arial", size=10)
        self.cell(95, 6, f"Körper: {attributes['Körper']}", border=1, ln=False)
        self.cell(95, 6, f"Technik: {attributes['Technik']}", border=1, ln=True)
        self.cell(95, 6, f"Herz: {attributes['Herz']}", border=1, ln=False)
        self.cell(95, 6, f"Verstand: {attributes['Verstand']}", border=1, ln=True)
        self.ln(5)

    def add_skills(self, skills):
        self.set_font("Arial", "B", 12)
        self.cell(190, 7, "Fähigkeiten", border=1, ln=True, align="C")
        self.set_font("Arial", size=10)
        count = 0
        for skill, value in skills.items():
            self.cell(95, 6, f"{skill}: {value}", border=1, ln=False)
            count += 1
            if count % 2 == 0:
                self.ln()
        self.ln(5)

def generate_pdf():
    pdf = PDF()
    pdf.add_page()
    pdf.add_glueckspunkte(glueckspunkte)
    pdf.add_attributes(attribute)
    pdf.add_skills(skill_values)
    for key, value in beschreibung.items():
        pdf.add_section(key, value)
    pdf.add_section("Inventar", "\n".join(filter(None, inventar)))
    pdf.add_section("Versteck", versteck)
    pdf.add_section("Notizen", notizen)
    return pdf.output(dest="S").encode("latin1")

if st.button("PDF speichern"):
    pdf_data = generate_pdf()
    st.download_button("📥 PDF herunterladen", data=pdf_data, file_name=f"{name}_{heldenklasse}.pdf", mime="application/pdf")

