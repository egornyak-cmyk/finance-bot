import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

conn = sqlite3.connect("finance.db")


# КРУГОВАЯ СТАТИСТИКА
def generate_stats(user_id):

    df = pd.read_sql_query(
        f"SELECT * FROM transactions WHERE user_id={user_id}",
        conn
    )

    if df.empty:
        return None

    exp = df[df["type"] == "expense"]

    stats = exp.groupby("category")["amount"].sum()

    plt.figure()

    stats.plot(kind="pie", autopct='%1.1f%%')

    plt.title("Расходы")

    plt.savefig("stats.png")

    plt.close()

    return "stats.png"


# 📊 РАСХОДЫ ПО МЕСЯЦАМ
def monthly_stats(user_id):

    df = pd.read_sql_query(
        f"SELECT * FROM transactions WHERE user_id={user_id}",
        conn
    )

    if df.empty:
        return None

    df["date"] = pd.to_datetime(df["date"])

    df["month"] = df["date"].dt.to_period("M")

    exp = df[df["type"] == "expense"]

    stats = exp.groupby("month")["amount"].sum()

    plt.figure()

    stats.plot(kind="bar")

    plt.title("Расходы по месяцам")

    plt.ylabel("Сумма")

    plt.savefig("months.png")

    plt.close()

    return "months.png"


# 📈 ДОХОД VS РАСХОД
def income_vs_expense(user_id):

    df = pd.read_sql_query(
        f"SELECT * FROM transactions WHERE user_id={user_id}",
        conn
    )

    if df.empty:
        return None

    df["date"] = pd.to_datetime(df["date"])

    df["month"] = df["date"].dt.to_period("M")

    income = df[df["type"] == "income"].groupby("month")["amount"].sum()

    expense = df[df["type"] == "expense"].groupby("month")["amount"].sum()

    data = pd.DataFrame({
        "income": income,
        "expense": expense
    }).fillna(0)

    plt.figure()

    data.plot(kind="bar")

    plt.title("Доходы vs Расходы")

    plt.ylabel("Сумма")

    plt.savefig("income_vs_expense.png")

    plt.close()

    return "income_vs_expense.png"


# 🏆 ТОП КАТЕГОРИЙ
def top_categories(user_id):

    df = pd.read_sql_query(
        f"SELECT * FROM transactions WHERE user_id={user_id}",
        conn
    )

    if df.empty:
        return None

    exp = df[df["type"] == "expense"]

    stats = exp.groupby("category")["amount"].sum().sort_values(ascending=False)

    text = "🏆 Топ расходов:\n\n"

    for i, (cat, amount) in enumerate(stats.items(), 1):

        text += f"{i}. {cat} — {round(amount,2)}\n"

    return text