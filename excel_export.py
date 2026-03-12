import pandas as pd
import sqlite3

conn = sqlite3.connect("finance.db")

def export_excel(user_id):

    df = pd.read_sql_query(
    f"SELECT * FROM transactions WHERE user_id={user_id}",
    conn
    )

    file = "report.xlsx"

    df.to_excel(file)

    return file