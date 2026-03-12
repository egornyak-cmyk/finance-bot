import sqlite3
import pandas as pd
from datetime import datetime
from stats import top_categories

conn = sqlite3.connect("finance.db", check_same_thread=False)


def generate_month_report(user_id):

    df = pd.read_sql_query(
        f"SELECT * FROM transactions WHERE user_id={user_id}",
        conn
    )

    if df.empty:
        return "Нет данных"

    df["date"] = pd.to_datetime(df["date"])

    now = datetime.now()

    df = df[
        (df["date"].dt.month == now.month) &
        (df["date"].dt.year == now.year)
    ]

    income = df[df["type"] == "income"]["amount"].sum()
    expense = df[df["type"] == "expense"]["amount"].sum()

    savings = income - expense

    report = f"""
📊 Отчёт за месяц

💰 Доход: {round(income,2)}
💸 Расход: {round(expense,2)}
💵 Экономия: {round(savings,2)}

{top_categories(user_id)}
"""

    return report