import sqlite3

conn = sqlite3.connect("finance.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions(
id INTEGER PRIMARY KEY AUTOINCREMENT,
type TEXT,
category TEXT,
amount REAL,
date TEXT
)
""")

conn.commit()


def add_transaction(user_id, type_, category, amount, date):

    cursor.execute(
    "INSERT INTO transactions(type,category,amount,date) VALUES(?,?,?,?)",
    (type_,category,amount,date)
    )

    conn.commit()


def get_balance(user_id):

    cursor.execute("SELECT type,amount FROM transactions")

    rows = cursor.fetchall()

    balance = 0

    for r in rows:

        if r[0] == "income":
            balance += r[1]

        elif r[0] == "expense":
            balance -= r[1]

    return balance


def get_last_transactions(user_id):

    cursor.execute(
    "SELECT type,category,amount,date FROM transactions ORDER BY id DESC LIMIT 10"
    )

    return cursor.fetchall()