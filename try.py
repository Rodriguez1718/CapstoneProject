import pyodbc

try:
    conn = pyodbc.connect(
        "DRIVER={SQL Server};"
        "SERVER=WARLUT-VIRTILAR\\SQLEXPRESS04;"
        "DATABASE=FUREVERFAMILY;"
        "Trusted_Connection=yes;"
    )
    print(" Connected to SQL Server successfully!")
except Exception as e:
    print(" Connection failed:", e)
