# Data Architecture Document: YipitData Pipeline

## 1. Executive Summary
This document outlines the architectural design, schema modeling, lineage tracking, and scaling strategy for the local Python data pipeline built for the YipitData engineering challenge. The system transforms unstructured text and semi-structured company records into queryable analytical tables and vector-indexed datasets.

## 2. Data Modeling Strategy (Dimensional Modeling)
- **Dimension Table (dim_companies)**: One row per unique canonical company, storing master attributes like industry, employee count, headquarters, and public status.
- **Fact Table (ct_arr_observations)**: One row per article publication representing a reported ARR observation over time, maintaining lineage by preserving raw revenue strings alongside normalized USD values.

## 3. Pipeline Lifecycle & Ingestion
1. **Cleaning**: Normalizes multi-format dates, handles revenue ranges via midpoints, and converts international currencies (EUR, GBP, JPY) to USD.
2. **Enrichment**: Standardizes categories (AI_ML) and resolves company names using exact and fuzzy matching (difflib).
3. **Embeddings & Vector Search**: Generates sentence embeddings using sentence-transformers and computes top-3 similar articles via cosine similarity.
4. **Materialization**: Exports modeled tables as CSVs and loads them into an embedded DuckDB database (yipit_warehouse.db).

## 4. Scaling & Production Roadmap
To transition this local pipeline to production, it can be integrated with **Apache Airflow** for orchestration, scaled using **PySpark/Databricks** for distributed compute, and migrated to a dedicated vector database (like Qdrant or Pinecone) for high-scale semantic retrieval.