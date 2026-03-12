import sqlite3

conn = sqlite3.connect("finance.db", check_same_thread=False)
cursor = conn.cursor()

cursor.execute("""
CREATE TABLE IF NOT EXISTS transactions(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
type TEXT,
category TEXT,
amount REAL,
date TEXT
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS jars(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
name TEXT,
amount REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS debts(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
person TEXT,
amount REAL
)
""")

cursor.execute("""
CREATE TABLE IF NOT EXISTS installments(
id INTEGER PRIMARY KEY AUTOINCREMENT,
user_id INTEGER,
name TEXT,
amount REAL,
date TEXT
)
""")

conn.commit()


def add_transaction(user_id,type_,category,amount,date):

    cursor.execute(
    "INSERT INTO transactions(user_id,type,category,amount,date) VALUES(?,?,?,?,?)",
    (user_id,type_,category,amount,date)
    )

    conn.commit()


def get_balance(user_id):

    cursor.execute(
    "SELECT type,amount FROM transactions WHERE user_id=?",
    (user_id,)
    )

    rows=cursor.fetchall()

    balance=0

    for r in rows:

        if r[0]=="income":
            balance+=r[1]

        elif r[0]=="expense":
            balance-=r[1]

    return balance


def get_last_transactions(user_id):

    cursor.execute(
    "SELECT type,category,amount,date FROM transactions WHERE user_id=? ORDER BY id DESC LIMIT 10",
    (user_id,)
    )

    return cursor.fetchall()