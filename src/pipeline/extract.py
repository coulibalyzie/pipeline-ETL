
from pathlib import Path

import pandas as pd


# Chemins du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
RAW_DIR = PROJECT_ROOT / "data" / "raw"
OUTPUT_FILE = RAW_DIR / "sales_raw.csv"


def extract() -> Path:
    """
    Simule l'extraction de données commerciales
    et les enregistre dans un fichier CSV brut.
    """
    RAW_DIR.mkdir(parents=True, exist_ok=True)

    # Données de ventes avec quelques anomalies volontaires
    rows = [
        (1001, "2026-10-01", "C001", "Laptop", 2, 850.00, "France"),
        (1002, "2026-10-01", "C002", "Mouse", 5, 20.00, "France"),
        (1003, "2026-10-02", "C003", "Keyboard", 3, 45.00, "Belgium"),
        (1004, "2026-10-02", "C004", "Monitor", 1, 220.00, "France"),
        (1005, "2026-10-03", "C005", "Laptop", 1, 850.00, "Germany"),
        (1006, "2026-10-03", None, "Mouse", 4, 20.00, "France"),
        (1007, "2026-10-04", "C007", "Keyboard", 0, 45.00, "Belgium"),
        (1008, "2026-10-04", "C008", "Monitor", 2, -220.00, "France"),
        (1009, "2026-10-05", "C009", "Mouse", 10, 20.00, "Germany"),
        (1010, "2026-10-05", "C010", "Laptop", 1, 850.00, "France"),
        (1010, "2026-10-05", "C010", "Laptop", 1, 850.00, "France"),
        (1011, "date_invalide", "C011", "Monitor", 2, 220.00, "France"),
    ]

    columns = [
        "order_id",
        "order_date",
        "customer_id",
        "product",
        "quantity",
        "unit_price",
        "country",
    ]

    df = pd.DataFrame(rows, columns=columns)

    # Sauvegarde des données brutes, sans correction
    df.to_csv(OUTPUT_FILE, index=False)

    print(f"Extraction terminée : {len(df)} lignes.")
    print(f"Fichier généré : {OUTPUT_FILE}")

    return OUTPUT_FILE


if __name__ == "__main__":
    extract()
