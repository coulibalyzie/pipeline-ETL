# Data Pipeline & Quality Platform

**A Python-based data engineering pipeline for extracting, validating, transforming, and loading sales data into PostgreSQL.**

## Overview

This project implements an end-to-end data pipeline designed to demonstrate core Data Engineering practices: data extraction, transformation, quality validation, automated testing, and database loading.

The pipeline processes a synthetic sales dataset containing deliberately introduced data quality issues. It separates valid records from rejected ones and loads the cleaned dataset into a PostgreSQL database.

## Architecture

```text
Synthetic Sales Data
        |
        v
    Extraction
        |
        v
  Raw CSV Dataset
        |
        v
Transformation & Data Quality Checks
        |
        +----------------------+
        |                      |
        v                      v
 Clean Sales Data       Rejected Records
        |
        v
  PostgreSQL Database
        |
        v
 Data Validation & SQL Queries
```

## Key Features

- **Data extraction:** generate a reproducible synthetic sales dataset.
- **Data transformation:** normalize data types and validate business rules.
- **Data quality checks:** detect missing customer identifiers, invalid dates, non-positive quantities, negative prices, and duplicate order identifiers.
- **Rejected-record management:** preserve invalid records with explicit rejection reasons.
- **Relational data storage:** load validated records into PostgreSQL.
- **Automated testing:** use `pytest` to verify extraction, transformation, and quality rules.
- **Containerized database:** run PostgreSQL using Docker Compose.

## Technology Stack

| Technology | Purpose |
|---|---|
| Python | Pipeline implementation |
| Pandas | Data processing and transformation |
| PostgreSQL | Relational data storage |
| SQLAlchemy | Database connectivity and loading |
| Psycopg | PostgreSQL driver |
| Docker Compose | Database containerization |
| pytest | Automated testing |
| SQL | Schema definition and data validation |

## Project Structure

```text
sales-data-pipeline/
├── data/
│   ├── raw/
│   │   └── sales_raw.csv
│   └── processed/
│       ├── sales_clean.csv
│       └── sales_rejected.csv
├── src/
│   └── pipeline/
│       ├── extract.py
│       ├── transform.py
│       └── load.py
├── sql/
│   └── schema.sql
├── tests/
│   └── test_pipeline.py
├── .env.example
├── .gitignore
├── docker-compose.yml
├── requirements.txt
└── README.md
```

*The generated CSV files are pipeline outputs and may not be committed to the repository, depending on the project's `.gitignore` configuration.*

## Data Quality Rules

The transformation stage checks the following conditions:

| Rule | Expected behavior |
|---|---|
| Missing customer identifier | Reject the record |
| Invalid order date | Reject the record |
| Invalid or non-positive quantity | Reject the record |
| Invalid or negative unit price | Reject the record |
| Duplicate order identifier | Keep the first occurrence and reject subsequent duplicates |

Rejected records are written to `data/processed/sales_rejected.csv` with their corresponding rejection reasons.

## Getting Started

### Prerequisites

- Python 3.10 or later
- Docker Desktop with Docker Compose
- Git

### 1. Clone the repository

```bash
git clone https://github.com/coulibalyzie/sales-data-pipeline.git
cd sales-data-pipeline
```

Replace `YOUR_USERNAME` with your GitHub username and adjust the repository URL if necessary.

### 2. Create and activate a virtual environment

On Windows PowerShell:

```powershell
python -m venv .venv
.\.venv\Scripts\Activate.ps1
```

On macOS or Linux:

```bash
python -m venv .venv
source .venv/bin/activate
```

### 3. Install dependencies

```bash
python -m pip install -r requirements.txt
```

### 4. Configure environment variables

Create a local `.env` file at the project root:

```dotenv
POSTGRES_DB=sales_dw
POSTGRES_USER=pipeline_user
POSTGRES_PASSWORD=replace_with_a_local_password
```

Ensure `.env` is excluded from Git. Never commit real credentials.

The password in `.env` must match the password configured for the PostgreSQL role in the running database.

### 5. Start PostgreSQL

```bash
docker compose up -d
```

Check the database status:

```bash
docker compose ps
```

The Compose configuration must publish the database on a port available on your machine. If port `5432` is already used by another project, a mapping such as `127.0.0.1:5433:5432` can be used.

Ensure `src/pipeline/load.py` connects to the corresponding host port.

### 6. Run the pipeline

Execute the stages in order:

```bash
python -m src.pipeline.extract
python -m src.pipeline.transform
python -m src.pipeline.load
```

The pipeline generates the raw dataset, transforms and separates valid and rejected records, then loads the clean records into PostgreSQL.

### 7. Run the tests

```bash
python -m pytest -v
```

The current test suite contains four tests covering extraction, transformation, quality rules, and rejection reasons.

## Results

The current synthetic dataset contains 12 records.

| Metric | Result |
|---|---:|
| Raw records | 12 |
| Valid records loaded | 7 |
| Rejected records | 5 |
| Automated tests | 4 passing |

These results reflect the current demonstration dataset and its deliberately introduced quality issues.

## Example SQL Queries

Count the loaded records:

```sql
SELECT COUNT(*) AS total_sales
FROM sales;
```

Calculate revenue by product:

```sql
SELECT
    product,
    SUM(quantity * unit_price) AS revenue
FROM sales
GROUP BY product
ORDER BY revenue DESC;
```

Calculate total revenue:

```sql
SELECT SUM(quantity * unit_price) AS total_revenue
FROM sales;
```

## Engineering Practices Demonstrated

- Separation of pipeline stages into dedicated modules
- Explicit data validation and rejection reasons
- Database constraints for data integrity
- Environment-based configuration
- Automated tests with isolated temporary files
- Reproducible local development using Docker Compose

## Limitations and Future Improvements

Potential extensions include:

- Structured logging and pipeline execution reports
- Persistent quality metrics and rejection statistics
- Incremental loading and upsert strategies
- Data lineage and execution metadata
- CI/CD with GitHub Actions
- Monitoring and visualization of data quality metrics

## Author

**Zie Coulibaly**

Engineering graduate from IMT Nord Europe, pursuing further specialization in data science and information systems at
University of Paris 1 : Pantheon Sorbonne.

**Areas of interest:** Data Engineering, databases, data quality, analytics, and information systems.
