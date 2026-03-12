import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

conn = sqlite3.connect("finance.db")

def generate_stats(user_id):

    df = pd.read_sql_query(
    f"SELECT * FROM transactions WHERE user_id={user_id}",
    conn
    )

    if df.empty:
        return None

    exp = df[df["type"]=="expense"]

    stats = exp.groupby("category")["amount"].sum()

    plt.figure()

    stats.plot(kind="pie",autopct='%1.1f%%')

    plt.title("Расходы")

    plt.savefig("stats.png")

    return "stats.png"