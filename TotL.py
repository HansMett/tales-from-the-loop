import streamlit as st
import json
import csv
from io import StringIO, BytesIO
from fpdf import FPDF
import os

# 🔹 Sicherstellen, dass der Speicherordner existiert
SAVE_DIR = "charaktere"
if not os.path.exists(SAVE_DIR):
    os.makedirs(SAVE_DIR)

# Titel der App
st.title("Tales from the Loop - Heldenbogen")

# Eingabe: Name und Alter
name = st.text_input("Name des Charakters")
alter = st.slider("Alter", 10, 15, 12)  # Min, Max, Standardwert

# Glückspunkte (15 - Alter)
st.text("Glückspunkte")
glueckspunkte = 15 - alter
cols = st.columns(glueckspunkte)
glueck_checkboxes = [cols[i].checkbox("", key=f"glueck_{i}") for i in range(glueckspunkte)]

# Heldenklassen mit Kernfähigkeiten
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
heldenklasse = st.selectbox("Heldenklasse", list(heldenklassen.keys()))
kernfähigkeiten = heldenklassen[heldenklasse]

# Attribute mit Slidern
st.subheader("Attribute")
attribute = {
    "Körper": st.slider("Körper", 1, 5, 1),
    "Technik": st.slider("Technik", 1, 5, 1),
    "Herz": st.slider("Herz", 1, 5, 1),
    "Verstand": st.slider("Verstand", 1, 5, 1),
}

# Warnung, falls Attributpunkte nicht dem Alter entsprechen
gesamt_attributpunkte = sum(attribute.values())
if gesamt_attributpunkte != alter:
    st.warning(f"⚠️ Die Summe der Attributpunkte muss genau {alter} betragen! (Derzeit: {gesamt_attributpunkte})")

# Fähigkeiten (2 Spalten)
st.subheader("Fähigkeiten")
skills = [
    "Schleichen", "Kraftakt", "Bewegen", "Tüfteln", "Programmieren", "Berechnen",
    "Kontakte", "Schmeicheln", "Führen", "Ermitteln", "Begreifen", "Einfühlen"
]
skill_values = {}
cols = st.columns(6)
for i, skill in enumerate(skills):
    max_wert = 3 if skill in kernfähigkeiten else 1
    skill_values[skill] = cols[i % 6].slider(f"{skill}", 0, max_wert, 0)

# Warnung, falls nicht genau 10 Skill-Punkte verteilt wurden
gesamt_skills = sum(skill_values.values())
if gesamt_skills != 10:
    st.warning(f"⚠️ Es müssen genau 10 Punkte auf die Fähigkeiten verteilt werden! (Derzeit: {gesamt_skills})")

# Charakterbeschreibung
st.subheader("Charakterbeschreibung")
beschreibung = {
    "Antrieb": st.text_area("Antrieb"),
    "Problem": st.text_area("Problem"),
    "Stolz": st.text_area("Stolz"),
    "Beschreibung": st.text_area("Beschreibung"),
    "Lieblingslied": st.text_input("Lieblingslied 🎵"),
}

# Inventar & Notizen
st.subheader("Inventar")
inventar = [st.text_input(f"Gegenstand {i+1}") for i in range(3)]
versteck = st.text_area("Versteck")
notizen = st.text_area("Zusätzliche Notizen")

# 🔹 **Download der CSV-Datei**
def download_csv():
    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(["Feld", "Wert"])
    writer.writerow(["Name", name])
    writer.writerow(["Alter", alter])
    writer.writerow(["Heldenklasse", heldenklasse])
    writer.writerow(["Glückspunkte", glueckspunkte])
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
            # Werte aus der CSV-Datei extrahieren
            name = df[df["Feld"] == "Name"]["Wert"].values[0]
            alter = int(df[df["Feld"] == "Alter"]["Wert"].values[0])
            heldenklasse = df[df["Feld"] == "Heldenklasse"]["Wert"].values[0]
            glueckspunkte = int(df[df["Feld"] == "Glückspunkte"]["Wert"].values[0])
            attribute = json.loads(df[df["Feld"] == "Attribute"]["Wert"].values[0])
            skill_values = json.loads(df[df["Feld"] == "Fähigkeiten"]["Wert"].values[0])
            beschreibung = json.loads(df[df["Feld"] == "Beschreibung"]["Wert"].values[0])
            inventar = df[df["Feld"] == "Inventar"]["Wert"].values[0].split(", ")
            versteck = df[df["Feld"] == "Versteck"]["Wert"].values[0]
            notizen = df[df["Feld"] == "Notizen"]["Wert"].values[0]

            st.success(f"✅ Charakter **{name}** wurde erfolgreich aus der CSV geladen!")

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
        self.multi_cell(190, 6, content, border=1)
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

