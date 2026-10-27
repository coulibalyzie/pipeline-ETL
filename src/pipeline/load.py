
from pathlib import Path
import os

import pandas as pd
from dotenv import load_dotenv
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL


# Chemins du projet
PROJECT_ROOT = Path(__file__).resolve().parents[2]
CLEAN_FILE = PROJECT_ROOT / "data" / "processed" / "sales_clean.csv"
SCHEMA_FILE = PROJECT_ROOT / "sql" / "schema.sql"

# Chargement de la configuration locale
load_dotenv(PROJECT_ROOT / ".env")


def get_engine():
    """Crée une connexion SQLAlchemy vers PostgreSQL."""
    required_vars = [
        "POSTGRES_DB",
        "POSTGRES_USER",
        "POSTGRES_PASSWORD",
    ]

    missing = [
        name for name in required_vars
        if not os.getenv(name)
    ]

    if missing:
        raise RuntimeError(
            f"Variables manquantes dans .env : {', '.join(missing)}"
        )

    database_url = URL.create(
        drivername="postgresql+psycopg",
        username=os.environ["POSTGRES_USER"],
        password=os.environ["POSTGRES_PASSWORD"],
        host="localhost",
        port=5433,
        database=os.environ["POSTGRES_DB"],
    )

    return create_engine(database_url, pool_pre_ping=True)


def load() -> int:
    """
    Charge les ventes valides dans PostgreSQL.

    Le chargement remplace le contenu précédent de la table
    dans une transaction, afin de pouvoir relancer le pipeline.
    """
    if not CLEAN_FILE.exists():
        raise FileNotFoundError(
            f"Fichier introuvable : {CLEAN_FILE}. "
            "Exécute d'abord l'extraction et la transformation."
        )

    if not SCHEMA_FILE.exists():
        raise FileNotFoundError(
            f"Schéma SQL introuvable : {SCHEMA_FILE}"
        )

    df = pd.read_csv(CLEAN_FILE, parse_dates=["order_date"])

    if df.empty:
        raise ValueError(
            "Le fichier des ventes valides est vide. "
            "Chargement annulé."
        )

    if df["order_id"].duplicated().any():
        raise ValueError(
            "Le fichier contient des identifiants de commande dupliqués."
        )

    engine = get_engine()

    try:
        with engine.begin() as connection:
            # Création de la table si nécessaire
            schema_sql = SCHEMA_FILE.read_text(encoding="utf-8")
            connection.exec_driver_sql(schema_sql)

            # Remplacement transactionnel des données
            connection.execute(text("TRUNCATE TABLE sales"))

            df.to_sql(
                name="sales",
                con=connection,
                if_exists="append",
                index=False,
                method="multi",
                chunksize=1000,
            )

            count = connection.execute(
                text("SELECT COUNT(*) FROM sales")
            ).scalar_one()

        print("Chargement terminé.")
        print(f"Lignes chargées : {count}")
        print(f"Base de données : {os.environ['POSTGRES_DB']}")
        print("Table : sales")

        return count

    finally:
        engine.dispose()


if __name__ == "__main__":
    load()
