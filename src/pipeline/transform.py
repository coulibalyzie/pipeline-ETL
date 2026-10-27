
from pathlib import Path

import pandas as pd


# Chemins du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_FILE = PROJECT_ROOT / "data" / "raw" / "sales_raw.csv"
PROCESSED_DIR = PROJECT_ROOT / "data" / "processed"

CLEAN_FILE = PROCESSED_DIR / "sales_clean.csv"
REJECTED_FILE = PROCESSED_DIR / "sales_rejected.csv"


def transform() -> tuple[Path, Path]:
    """
    Nettoie les données de ventes et sépare
    les lignes valides des lignes rejetées.
    """
    if not RAW_FILE.exists():
        raise FileNotFoundError(
            f"Fichier source introuvable : {RAW_FILE}. "
            "Exécute d'abord l'extraction."
        )

    PROCESSED_DIR.mkdir(parents=True, exist_ok=True)

    # Chargement des données brutes
    df = pd.read_csv(RAW_FILE)

    # Conserver le numéro de ligne du fichier source
    df.insert(0, "source_row", range(2, len(df) + 2))

    # Conversion des types
    df["order_date"] = pd.to_datetime(
        df["order_date"], errors="coerce"
    )
    df["quantity"] = pd.to_numeric(
        df["quantity"], errors="coerce"
    )
    df["unit_price"] = pd.to_numeric(
        df["unit_price"], errors="coerce"
    )

    # Motifs de rejet, cumulables pour une même ligne
    reasons = pd.Series("", index=df.index, dtype="string")

    def add_reason(condition: pd.Series, message: str) -> None:
        nonlocal reasons
        reasons.loc[condition] = reasons.loc[condition].apply(
            lambda current: (
                f"{current}; {message}" if current else message
            )
        )

    # Vérification des champs obligatoires
    add_reason(
        df["customer_id"].isna()
        | df["customer_id"].astype("string").str.strip().eq(""),
        "client manquant",
    )

    add_reason(
        df["order_date"].isna(),
        "date invalide",
    )

    add_reason(
        df["quantity"].isna(),
        "quantité invalide",
    )
    add_reason(
        df["quantity"].le(0),
        "quantité non positive",
    )

    add_reason(
        df["unit_price"].isna(),
        "prix invalide",
    )
    add_reason(
        df["unit_price"].lt(0),
        "prix négatif",
    )

    # Une commande ne doit apparaître qu'une seule fois
    duplicate_order = df["order_id"].duplicated(keep="first")
    add_reason(duplicate_order, "commande dupliquée")

    # Séparation des données
    valid_mask = reasons.eq("")

    clean_df = df.loc[valid_mask].copy()
    rejected_df = df.loc[~valid_mask].copy()

    # Ajouter le motif uniquement au fichier des rejets
    rejected_df["rejection_reason"] = reasons.loc[~valid_mask]

    # Formater les dates valides au format ISO
    clean_df["order_date"] = (
        clean_df["order_date"].dt.strftime("%Y-%m-%d")
    )

    # Enregistrer les résultats
    clean_df.to_csv(CLEAN_FILE, index=False)
    rejected_df.to_csv(REJECTED_FILE, index=False)

    print("Transformation terminée.")
    print(f"Lignes sources : {len(df)}")
    print(f"Ventes valides : {len(clean_df)}")
    print(f"Lignes rejetées : {len(rejected_df)}")
    print(f"Fichier valide : {CLEAN_FILE}")
    print(f"Fichier des rejets : {REJECTED_FILE}")

    return CLEAN_FILE, REJECTED_FILE


if __name__ == "__main__":
    transform()
