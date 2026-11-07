import json
import pandas as pd
from difflib import get_close_matches

def load_company_metadata(path):
    """
    Loads company metadata from a JSON file into a pandas DataFrame 
    and standardizes the primary company identifier column name.
    """
    try:
        with open(path, "r", encoding="utf-8") as f:
            data = json.load(f)
        df_meta = pd.DataFrame(data)
        
        # Standardize company name column to 'company_name' if named differently in the JSON
        for possible_col in ["company_name", "company", "name", "organization"]:
            if possible_col in df_meta.columns and possible_col != "company_name":
                df_meta.rename(columns={possible_col: "company_name"}, inplace=True)
                break
                
        return df_meta
    except Exception as e:
        print(f"Error loading company metadata: {e}")
        return pd.DataFrame()

def clean_company_name(name):
    """
    Normalizes a company name string by converting it to lowercase, 
    stripping whitespace, and removing common corporate suffixes/punctuation.
    """
    if pd.isna(name): 
        return ""
    c = str(name).strip().lower()
    for s in [",", ".", "inc", "llc", "corp"]: 
        c = c.replace(s, "")
    return c.strip()

def enrich_articles_with_company_data(df_art, df_meta):
    """
    Enriches the article DataFrame by matching company references against 
    metadata using exact and fuzzy matching algorithms, calculating company age,
    and categorizing company size.
    """
    if df_meta.empty or "company_name" not in df_meta.columns:
        df_art["resolved_company_name"] = df_art["company_name"] if "company_name" in df_art.columns else "Unknown"
        df_art["company_age"] = None
        df_art["company_size_category"] = "Unknown"
        return df_art
        
    valid = df_meta["company_name"].dropna().unique().tolist()
    c_to_orig = {clean_company_name(x): x for x in valid}
    matched = []
    
    # Identify the appropriate company column in the articles DataFrame
    news_company_col = "company_name" if "company_name" in df_art.columns else df_art.columns[0]
    
    # Perform fuzzy and exact matching to link article companies with metadata records
    for raw in df_art[news_company_col]:
        if pd.isna(raw) or not str(raw).strip(): 
            matched.append(None)
            continue
            
        ex = get_close_matches(str(raw), valid, n=1, cutoff=0.9)
        if ex: 
            matched.append(ex[0])
        else:
            fz = get_close_matches(clean_company_name(raw), list(c_to_orig.keys()), n=1, cutoff=0.7)
            matched.append(c_to_orig[fz[0]] if fz else None)
            
    df_art["resolved_company_name"] = matched
    
    # Merge articles with company metadata based on the resolved name
    df_m = df_art.merge(df_meta, left_on="resolved_company_name", right_on="company_name", how="left", suffixes=("", "_meta"))
    
    if "company_name_meta" in df_m.columns: 
        df_m.drop(columns=["company_name_meta"], inplace=True)
        
    # Calculate company age based on article publication year and company founding year
    if "founded_year" in df_m.columns and "year" in df_m.columns:
        df_m["company_age"] = df_m["year"] - pd.to_numeric(df_m["founded_year"], errors="coerce")
    else: 
        df_m["company_age"] = None
    
    # Helper function to categorize companies by employee headcount
    def cat_size(cnt):
        if pd.isna(cnt): 
            return "Unknown"
        try:
            val = int(cnt)
            if val < 10000: 
                return "Small"
            elif val <= 30000: 
                return "Medium"
            else: 
                return "Large"
        except ValueError: 
            return "Unknown"
        
    emp_col = "employee_count" if "employee_count" in df_m.columns else "employees"
    if emp_col in df_m.columns:
        df_m["company_size_category"] = df_m[emp_col].apply(cat_size)
    else:
        df_m["company_size_category"] = "Unknown"
        
    return df_m