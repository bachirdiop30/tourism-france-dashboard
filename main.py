# main.py
import streamlit as st
from src.utils.load_cleaned_data import load_cleaned_data  # notre fonction corrigée

# -----------------------------
# Chargement des données nettoyées
# -----------------------------
@st.cache_data
def load_data():
    return load_cleaned_data()

df_dict = load_data()  # df_dict contient les 3 fichiers nettoyés

# -----------------------------
# Navigation multi-pages
# -----------------------------
st.sidebar.title("Navigation")
page = st.sidebar.radio("Aller à :", ["Accueil", "Régions", "International", "Économie"])

if page == "Accueil":
    from src.pages.home import show_home
    show_home(df_dict)
elif page == "Régions":
    from src.pages.regional import show_regional
    show_regional(df_dict)
elif page == "International":
    from src.pages.international import show_international
    show_international(df_dict)
elif page == "Économie":
    from src.pages.economic import show_economic
    show_economic(df_dict)
