
import pandas as pd
import pytest

from src.pipeline import extract as extract_module
from src.pipeline import transform as transform_module


@pytest.fixture
def pipeline_files(tmp_path, monkeypatch):
    """Prépare des chemins temporaires pour isoler les tests."""
    raw_dir = tmp_path / "raw"
    processed_dir = tmp_path / "processed"

    raw_file = raw_dir / "sales_raw.csv"
    clean_file = processed_dir / "sales_clean.csv"
    rejected_file = processed_dir / "sales_rejected.csv"

    monkeypatch.setattr(extract_module, "RAW_DIR", raw_dir)
    monkeypatch.setattr(extract_module, "OUTPUT_FILE", raw_file)

    monkeypatch.setattr(transform_module, "RAW_FILE", raw_file)
    monkeypatch.setattr(
        transform_module, "PROCESSED_DIR", processed_dir
    )
    monkeypatch.setattr(transform_module, "CLEAN_FILE", clean_file)
    monkeypatch.setattr(
        transform_module, "REJECTED_FILE", rejected_file
    )

    return {
        "raw": raw_file,
        "clean": clean_file,
        "rejected": rejected_file,
    }


def test_extract_creates_raw_file(pipeline_files):
    """Vérifie que l'extraction produit les données attendues."""
    extract_module.extract()

    assert pipeline_files["raw"].exists()

    df = pd.read_csv(pipeline_files["raw"])

    assert df.shape == (12, 7)
    assert df["order_id"].notna().all()


def test_transform_separates_valid_and_rejected_rows(pipeline_files):
    """Vérifie la séparation entre données valides et rejets."""
    extract_module.extract()
    transform_module.transform()

    clean = pd.read_csv(pipeline_files["clean"])
    rejected = pd.read_csv(pipeline_files["rejected"])

    assert len(clean) == 7
    assert len(rejected) == 5
    assert len(clean) + len(rejected) == 12


def test_clean_data_respects_quality_rules(pipeline_files):
    """Vérifie les principales règles de qualité."""
    extract_module.extract()
    transform_module.transform()

    clean = pd.read_csv(pipeline_files["clean"])

    assert clean["order_id"].is_unique
    assert clean["customer_id"].notna().all()
    assert clean["order_date"].notna().all()
    assert (clean["quantity"] > 0).all()
    assert (clean["unit_price"] >= 0).all()


def test_rejected_rows_have_explanations(pipeline_files):
    """Vérifie que chaque rejet possède un motif."""
    extract_module.extract()
    transform_module.transform()

    rejected = pd.read_csv(pipeline_files["rejected"])

    assert rejected["rejection_reason"].notna().all()
    assert rejected["rejection_reason"].str.len().gt(0).all()

    reasons = "; ".join(rejected["rejection_reason"])

    assert "client manquant" in reasons
    assert "quantité non positive" in reasons
    assert "prix négatif" in reasons
    assert "commande dupliquée" in reasons
    assert "date invalide" in reasons
