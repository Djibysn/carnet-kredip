import streamlit as st
import pandas as pd
import urllib.parse
import os

# Configuration de la page
st.set_page_config(page_title="Carnet Kredip", page_icon="📖", layout="centered")

st.title("📖 Carnet Kredip")
st.caption("Le cahier de crédit digital & relances clients")

# Base de données locale
DATA_FILE = "credits.csv"

if os.path.exists(DATA_FILE):
    df = pd.read_csv(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Nom Client", "Téléphone", "Montant (FCFA)", "Article / Note", "Statut"])

# --- FORMULAIRE D'AJOUT ---
st.subheader("➕ Enregistrer un crédit")
with st.form("add_credit_form", clear_on_submit=True):
    nom = st.text_input("Nom du client")
    telephone = st.text_input("Numéro de téléphone (ex: 221770000000)")
    montant = st.number_input("Montant dû (FCFA)", min_value=100, step=500)
    note = st.text_input("Article acheté / Motif")
    submitted = st.form_submit_button("Enregistrer")

    if submitted:
        if nom and telephone and montant:
            new_row = pd.DataFrame([{
                "Nom Client": nom,
                "Téléphone": telephone,
                "Montant (FCFA)": montant,
                "Article / Note": note,
                "Statut": "Non payé"
            }])
            df = pd.concat([df, new_row], ignore_index=True)
            df.to_csv(DATA_FILE, index=False)
            st.success(f"Crédit enregistré pour {nom} !")
            st.rerun()
        else:
            st.error("Veuillez remplir le nom, le téléphone et le montant.")

st.divider()

# --- LISTE DES CRÉDITS EN COURS ---
st.subheader("📋 Crédits en cours")

if not df.empty:
    total_du = df[df["Statut"] == "Non payé"]["Montant (FCFA)"].sum()
    st.metric(label="Total restant à recouvrer", value=f"{total_du:,} FCFA")

    for index, row in df.iterrows():
        if row["Statut"] == "Non payé":
            with st.expander(f"🔴 {row['Nom Client']} — {row['Montant (FCFA)']} FCFA"):
                st.write(f"**Téléphone :** {row['Téléphone']}")
                st.write(f"**Motif :** {row['Article / Note']}")
                
                langue = st.radio("Langue du message", ["Wolof", "Français"], key=f"lang_{index}", horizontal=True)
                
                if langue == "Wolof":
                    message = f"Na nga def {row['Nom Client']}, gnn ngi lay fattali krédi {row['Montant (FCFA)']} FCFA bi ngi amoon ci boutique bi ({row['Article / Note']}). Jerejef !"
                else:
                    message = f"Bonjour {row['Nom Client']}, nous vous rappelons amicalement le règlement de votre crédit de {row['Montant (FCFA)']} FCFA concernant : {row['Article / Note']}. Merci !"
                
                phone_clean = str(row['Téléphone']).replace(" ", "").replace("+", "")
                encoded_msg = urllib.parse.quote(message)
                wa_url = f"https://wa.me/{phone_clean}?text={encoded_msg}"
                
                col1, col2 = st.columns(2)
                with col1:
                    st.link_button("📲 Relancer sur WhatsApp", wa_url)
                with col2:
                    if st.button("✅ Marquer Payé", key=f"pay_{index}"):
                        df.at[index, "Statut"] = "Payé"
                        df.to_csv(DATA_FILE, index=False)
                        st.success("Crédit archivé !")
                        st.rerun()
else:
    st.info("Aucun crédit en cours.")