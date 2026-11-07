import re
import pandas as pd

def clean_revenue(row_value):
    """
    Cleans raw revenue strings, handles range midpoints (e.g., '$50M-$100M'),
    converts international currencies to USD, and returns an integer in USD.
    """
    if pd.isna(row_value) or str(row_value).strip() in ["", "N/A", "Not disclosed", "None", "nan"]:
        return None
    
    val_str = str(row_value).strip()
    
    # Handle revenue ranges by calculating the average midpoint
    if "-" in val_str and not val_str.startswith("-"):
        parts = val_str.split("-")
        if len(parts) == 2:
            v1 = _parse_single_revenue(parts[0].strip())
            v2 = _parse_single_revenue(parts[1].strip())
            if v1 is not None and v2 is not None:
                return int((v1 + v2) / 2)
                
    return _parse_single_revenue(val_str)

def _parse_single_revenue(val_str):
    """
    Helper function to parse a single monetary string, apply currency conversion rates,
    and scale multipliers (Billions, Millions, Thousands).
    """
    if not val_str:
        return None
        
    curr = "USD"
    if "€" in val_str or "EUR" in val_str.upper(): 
        curr = "EUR"
    elif "£" in val_str or "GBP" in val_str.upper(): 
        curr = "GBP"
    elif "¥" in val_str or "JPY" in val_str.upper(): 
        curr = "JPY"
        
    # Keep only digits, decimal points, scale letters, and spaces
    cleaned = re.sub(r"[^\d\.bBmMiIlLmMkK\s]", "", val_str).strip()
    
    # Extract numeric value and scale modifier (e.g., million, billion, k)
    match = re.search(r"([\d\.]+)\s*([bBmM]?(?:illion)?|[bBmMkK]?)", cleaned)
    if not match: 
        return None
        
    try: 
        num = float(match.group(1))
    except ValueError: 
        return None
        
    mult_str = match.group(2).lower()
    mult = 1
    
    if "b" in mult_str or "billion" in val_str.lower(): 
        mult = 1_000_000_000
    elif "m" in mult_str or "million" in val_str.lower(): 
        mult = 1_000_000
    elif "k" in mult_str: 
        mult = 1_000
        
    base = num * mult
    
    # Apply approximate currency exchange rates to USD
    if curr == "EUR": 
        final = base * 1.1
    elif curr == "GBP": 
        final = base * 1.27
    elif curr == "JPY": 
        final = base / 150.0
    else: 
        final = base
        
    return int(round(final))

def clean_dates(series):
    """
    Normalizes a date series into standard datetime objects and extracts 
    analytical time dimensions (Year, Quarter, Month) robustly.
    """
    # Coerce invalid dates into NaT and handle mixed formats safely
    parsed = pd.to_datetime(series, errors="coerce")
    
    # Fallback loop row-by-row if standard batch parsing fails completely
    if parsed.isna().all():
        parsed = pd.Series([pd.NaT] * len(series))
        for idx, val in enumerate(series):
            try:
                parsed.iloc[idx] = pd.to_datetime(str(val), errors="coerce")
            except Exception:
                pass

    df = pd.DataFrame()
    df["published_date"] = parsed
    df["year"] = parsed.dt.year.fillna(0).astype(int)
    
    # Format period quarters (e.g., '2023Q1') and handle missing slots
    df["quarter"] = parsed.dt.to_period("Q").astype(str)
    df["quarter"] = df["quarter"].replace("NaT", "Unknown")
    df["month"] = parsed.dt.month.fillna(0).astype(int)
    
    return df

def standardize_category(cat):
    """
    Standardizes disparate category labels into a clean, unified business taxonomy.
    """
    if pd.isna(cat): 
        return "Uncategorized"
        
    c = str(cat).strip().lower()
    
    if any(t in c for t in ["ai", "artificial intelligence", "machine learning", "ml"]): 
        return "AI_ML"
    elif "cloud" in c: 
        return "Cloud Computing"
    elif "cyber" in c or "security" in c: 
        return "Cybersecurity"
    elif "data" in c or "analytics" in c: 
        return "Data and Analytics"
        
    return str(cat).strip().title()