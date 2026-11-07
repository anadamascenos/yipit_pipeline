import os
import numpy as np
import pandas as pd
import duckdb
from cleaning import clean_revenue, clean_dates, standardize_category
from enrichment import load_company_metadata, enrich_articles_with_company_data
from embeddings import generate_embeddings, compute_top_similar_articles

def run_pipeline():
    print("=== STARTING YIPITDATA PIPELINE ===")
    os.makedirs("data/processed", exist_ok=True)
    os.makedirs("data/exports", exist_ok=True)
    
    # 1. Load data
    df_news = pd.read_csv("data/raw/tech_news.csv")
    df_meta = load_company_metadata("data/raw/company_metadata.json")
    
    # 2. Clean revenue & dates
    df_news["raw_revenue"] = df_news["revenue"]
    df_news["arr_usd"] = df_news["revenue"].apply(clean_revenue)
    
    dates = clean_dates(df_news["published_date"])
    df_news["published_date"] = dates["published_date"]
    df_news["year"] = dates["year"]
    df_news["quarter"] = dates["quarter"]
    df_news["month"] = dates["month"]
    
    df_news["category"] = df_news["category"].apply(standardize_category)
    
    # 3. Enrich with company metadata
    df_enriched = enrich_articles_with_company_data(df_news, df_meta)
    
    if "article_id" not in df_enriched.columns:
        df_enriched["article_id"] = [f"ART_{i+1:04d}" for i in range(len(df_enriched))]
        
    # 4. Generate embeddings and similarities
    embs = generate_embeddings(df_enriched)
    df_enriched["top_similar_articles"] = compute_top_similar_articles(df_enriched, embs, 3)
    df_enriched["embedding_vector"] = [e.tolist() for e in embs]
    
    # 5. Data Warehouse modeling (Dimensions & Facts)
    dim_cols = [c for c in ["company_name", "industry", "founded_year", "headquarters", "employee_count", "is_public", "stock_ticker"] if c in df_enriched.columns]
    dim_comp = df_enriched[dim_cols].drop_duplicates(subset=["company_name"]).reset_index(drop=True)
    dim_comp["company_id"] = [f"COMP_{i+1:03d}" for i in range(len(dim_comp))]
    
    fact_cols = ["article_id", "company_name", "title", "published_date", "year", "quarter", "month", "category", "raw_revenue", "arr_usd", "summary", "url", "company_age", "company_size_category", "top_similar_articles"]
    fct_obs = df_enriched[[c for c in fact_cols if c in df_enriched.columns]].copy()
    
    dim_comp.to_csv("data/processed/dim_companies.csv", index=False)
    fct_obs.to_csv("data/processed/fct_arr_observations.csv", index=False)
    
    # DuckDB load
    con = duckdb.connect("data/yipit_warehouse.db")
    con.execute("CREATE OR REPLACE TABLE dim_companies AS SELECT * FROM dim_comp")
    con.execute("CREATE OR REPLACE TABLE fct_arr_observations AS SELECT * FROM fct_obs")
    con.close()
    
    # 6. Filter and Export AI Articles Enriched dataset
    mask_ai = df_enriched.apply(lambda r: "AI" in str(r.get("category", "")).upper() or "MACHINE" in str(r.get("category", "")).upper() or "AI" in str(r.get("industry", "")).upper() or "MACHINE" in str(r.get("industry", "")).upper(), axis=1)
    mask_y = df_enriched["year"].isin([2022, 2023, 2024])
    mask_a = (df_enriched["arr_usd"].notna()) & (df_enriched["arr_usd"] > 50_000_000)
    
    df_ai = df_enriched[mask_ai & mask_y & mask_a].copy()
    
    # Ensure year column is explicitly present
    if "year" not in df_ai.columns and "published_date" in df_ai.columns:
        df_ai["year"] = pd.to_datetime(df_ai["published_date"]).dt.year
        
    req = ["article_id", "title", "company_name", "published_date", "year", "category", "arr_usd", "summary", "url", "industry", "founded_year", "headquarters", "employee_count", "is_public", "stock_ticker", "company_age", "company_size_category", "embedding_vector", "top_similar_articles"]
    
    df_ai[[c for c in req if c in df_ai.columns]].to_csv("data/exports/ai_articles_enriched.csv", index=False)
    print("=== PIPELINE COMPLETED SUCCESSFULLY ===")

if __name__ == "__main__":
    run_pipeline()