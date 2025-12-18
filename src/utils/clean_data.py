# src/utils/clean_data.py
import pandas as pd
from pathlib import Path

PROJECT_ROOT = Path(__file__).parent.parent.parent
RAW_DIR = PROJECT_ROOT / "data" / "raw"
CLEANED_DIR = PROJECT_ROOT / "data" / "cleaned"

CLEANED_DIR.mkdir(parents=True, exist_ok=True)

FILES = {
    "frequentation_mensuelle.csv": "frequentation_mensuelle_cleaned.csv",
    "frequentation_region.csv": "frequentation_region_cleaned.csv",
    "frequentation_hoteliere.csv": "frequentation_hoteliere_cleaned.csv"
}

def clean_tourism_data():
    cleaned_dfs = {}
    for raw_file, cleaned_file in FILES.items():
        path = RAW_DIR / raw_file
        print(f"Nettoyage de {raw_file}...")
        
        if not path.exists():
            print(f"   {path} n'existe pas !")
            continue
        
        # Lecture avec le bon séparateur
        df = pd.read_csv(path, sep=",", encoding='utf-8')
        
        print(f"  Colonnes: {df.columns.tolist()}")
        print(f"  Shape avant: {df.shape}")
        
        # Suppression des doublons
        df = df.drop_duplicates()
        print(f"  Shape après dédoublonnage: {df.shape}")
        
        # Conversion des colonnes numériques
        numeric_cols = ["Nombre de touristes", "Nombre de croisièristes", 
                       "Nuitées touristiques", "Durée de séjor moyenne"]
        
        for col in numeric_cols:
            if col in df.columns:
                # Convertir en string, gérer les virgules décimales
                df[col] = (df[col]
                          .astype(str)
                          .str.replace(',', '.')  # Virgule → point
                          .str.strip()            # Enlever espaces
                          .str.replace('"', ''))  # Enlever guillemets si présents
                
                # Convertir en numérique
                df[col] = pd.to_numeric(df[col], errors="coerce")
                
                # Afficher le nombre de valeurs manquantes
                n_missing = df[col].isna().sum()
                if n_missing > 0:
                    print(f"    {col}: {n_missing} valeurs manquantes")
        
        cleaned_dfs[raw_file] = df
        
        # Sauvegarde propre
        cleaned_path = CLEANED_DIR / cleaned_file
        df.to_csv(
            cleaned_path, 
            index=False, 
            sep=",",
            encoding="utf-8"
        )
        print(f"  ✓ Sauvegardé: {cleaned_path}\n")
    
    return cleaned_dfs

if __name__ == "__main__":
    print(f"RAW_DIR: {RAW_DIR}")
    print(f"CLEANED_DIR: {CLEANED_DIR}\n")
    clean_tourism_data()
    print(" Nettoyage terminé !")