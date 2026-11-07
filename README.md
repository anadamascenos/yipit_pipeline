# YipitData | Local Python Data Pipeline & Semantic Search

A modular, production-grade local Python data pipeline built to ingest messy technology-news articles, parse and normalize inconsistent revenue fields (treating valid figures as ARR observations), enrich them with company metadata using exact and fuzzy matching, store them in a local DuckDB data warehouse, and generate a vector search index for semantic querying.

---

## Architecture & Features

- **Robust Revenue & ARR Parsing**: Cleans raw monetary strings, handles range midpoints (e.g., `$50M - $100M`), standardizes international currencies (EUR, GBP, JPY to USD), and extracts numerical integers while maintaining source lineage.
- **Flexible Date Normalization**: Parses multi-format dates and extracts analytical dimensions (`year`, `quarter`, `month`).
- **Fuzzy Company Matching**: Resolves inconsistent corporate naming variations against metadata registries using Python's `difflib`.
- **Data Warehouse Storage**: Materializes clean dimension and fact tables, persisting them locally via CSV exports and an embedded DuckDB database (`yipit_warehouse.db`).
- **Semantic Vector Search**: Generates dense text embeddings using `sentence-transformers` (`all-MiniLM-L6-v2`) and computes cosine similarity scores to identify top-3 similar articles.
- **Targeted Downstream Export**: Generates `ai_articles_enriched.csv` filtering strictly for AI/ML categories/industries, publication years 2022–2024, and ARR greater than $50M.

---

## Project Structure

```text
yipit_pipeline/
│
├── data/
│   ├── raw/                  # Source datasets (tech_news.csv, company_metadata.json)
│   ├── processed/            # Modeled warehouse CSVs (dim_companies, fct_arr_observations)
│   ├── exports/              # Final downstream filter (ai_articles_enriched.csv)
│   └── yipit_warehouse.db    # Embedded DuckDB analytical store
│
├── src/
│   ├── cleaning.py           # Revenue, date cleaning & category standardization
│   ├── enrichment.py         # Metadata integration & fuzzy name matching
│   ├── embeddings.py         # Sentence-transformer embeddings & cosine similarity
│   ├── pipeline.py           # Main orchestration script
│   └── validate_export.py    # Automated dataset validation script
│
├── requirements.txt          # Project dependencies
├── ARCHITECTURE.md           # Data Architecture Document
└── README.md                 # Project documentation