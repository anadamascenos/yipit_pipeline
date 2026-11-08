import pandas as pd
import os

def validate_dataset():
    file_path = "data/exports/ai_articles_enriched.csv"
    
    if not os.path.exists(file_path):
        print(f"❌ Error: Export file not found at {file_path}")
        return
        
    df = pd.read_csv(file_path)
    print(f"=== VALIDATING DATASET: {file_path} ===")
    print(f"Total rows in export: {len(df)}")
    
    if len(df) == 0:
        print("⚠️ Warning: The export file is empty!")
        return

    # Check 1: Category Filtering (Strictly AI/ML)
    if "category" in df.columns:
        invalid_categories = df[~df["category"].str.contains("AI", case=False, na=False)]
        if len(invalid_categories) > 0:
            print(f"Validation Failed: Found {len(invalid_categories)} rows not related to AI/ML.")
        else:
            print("Check 1 Passed: All rows belong to the AI_ML category taxonomy.")
    else:
        print("Warning: 'category' column missing from export.")

    # Check 2: Year Filtering (2022-2024)
    if "year" in df.columns:
        invalid_years = df[~df["year"].isin([2022, 2023, 2024])]
        if len(invalid_years) > 0:
            print(f"Validation Failed: Found {len(invalid_years)} rows outside years 2022-2024. Years found: {df['year'].unique()}")
        else:
            print("Check 2 Passed: All publication years are strictly within 2022-2024.")
    else:
        print("Warning: 'year' column missing from export.")

    # Check 3: ARR Threshold (> )
    if "arr_usd" in df.columns:
        invalid_arr = df[df["arr_usd"] <= 50_000_000]
        min_arr = df["arr_usd"].min()
        max_arr = df["arr_usd"].max()
        print(f"ℹ️ ARR Stats -> Minimum:  | Maximum: ")
        
        if len(invalid_arr) > 0:
            print(f"Validation Failed: Found {len(invalid_arr)} rows with ARR <= ,000,000.")
        else:
            print("Check 3 Passed: All rows have an ARR strictly greater than ,000,000.")
    else:
        print("Warning: 'arr_usd' column missing from export.")

    print("\n--- SAMPLE DATA PREVIEW ---")
    preview_cols = [c for c in ["article_id", "title", "company_name", "year", "arr_usd", "category"] if c in df.columns]
    print(df[preview_cols].head(3).to_string(index=False))
    print("=== VALIDATION COMPLETED ===")

if __name__ == "__main__":
    validate_dataset()