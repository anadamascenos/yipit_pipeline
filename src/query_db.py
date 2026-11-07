import duckdb

con = duckdb.connect("data/yipit_warehouse.db")
result = con.execute("""
    SELECT company_name, published_date, arr_usd, title 
    FROM fct_arr_observations 
    WHERE company_name = 'NVIDIA' 
    ORDER BY published_date DESC;
""").fetchdf()

print(result)
con.close()