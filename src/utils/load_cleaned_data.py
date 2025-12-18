# src/utils/load_data.py
import pandas as pd
import os

CLEANED_DIR = "data/cleaned/"

def load_cleaned_data():
    files = {
        "frequentation_hoteliere": "frequentation_hoteliere_cleaned.csv",
        "frequentation_mensuelle": "frequentation_mensuelle_cleaned.csv",
        "frequentation_region": "frequentation_region_cleaned.csv",
    }

    dfs = {}
    for key, filename in files.items():
        path = os.path.join(CLEANED_DIR, filename)
        
        print(f"Chargement de {filename}...")
        
        # Lecture simple avec virgule
        df = pd.read_csv(path, sep=",", encoding="utf-8")
        
        print(f"  Colonnes: {df.columns.tolist()}")
        print(f"  Shape: {df.shape}")
        
        # Conversion des colonnes numériques si nécessaire
        num_cols = ["Nombre de touristes", "Nombre de croisièristes", 
                   "Nuitées touristiques", "Durée de séjour moyenne"]
        for col in num_cols:
            if col in df.columns:
                # Si déjà numérique, on skip
                if df[col].dtype in ['int64', 'float64']:
                    continue
                df[col] = pd.to_numeric(
                    df[col].astype(str).str.replace(",", "."), 
                    errors="coerce"
                )

        dfs[key] = df
        print(f"  ✓ Chargé avec succès\n")

    return dfs


if __name__ == "__main__":
    data = load_cleaned_data()
    for k, df in data.items():
        print(f"\n=== {k} ===")
        print(f"Shape: {df.shape}")
        print(f"Colonnes: {df.columns.tolist()}")
        print(df.head())