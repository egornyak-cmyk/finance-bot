from telegram import ReplyKeyboardMarkup, Update
from telegram.ext import ApplicationBuilder, MessageHandler, CommandHandler, filters, ContextTypes
from datetime import datetime
import sqlite3

from config import TOKEN, ALLOWED_USERS
from database import add_transaction, get_balance, get_last_transactions
from stats import generate_stats, monthly_stats, income_vs_expense, top_categories
from excel_export import export_excel
from monthly_report import generate_month_report
from apscheduler.schedulers.background import BackgroundScheduler


# --- Кнопки ---
menu = ReplyKeyboardMarkup([
["💰 Доход","💸 Расход"],
["📊 Статистика","📊 Месяцы"],
["📈 Доход vs Расход","🏆 Топ"],
["💳 Баланс","📜 История"],
["📁 Excel","🆕 Новый месяц"]
], resize_keyboard=True)


# --- Доступ ---
def allowed(user_id):
    return user_id in ALLOWED_USERS


# --- Состояние ввода (доход/расход) ---
user_state = {}


# --- Сброс месяца ---
def reset_month():
    conn = sqlite3.connect("finance.db")
    cursor = conn.cursor()
    cursor.execute("DELETE FROM transactions")
    conn.commit()
    conn.close()


# --- Команда старт ---
async def start(update:Update, context:ContextTypes.DEFAULT_TYPE):
    if not allowed(update.effective_user.id):
        return

    await update.message.reply_text(
        "Финансовый бот",
        reply_markup=menu
    )


# --- Баланс ---
async def balance(update:Update, context:ContextTypes.DEFAULT_TYPE):
    bal = get_balance(update.effective_user.id)
    await update.message.reply_text(f"Баланс: {round(bal,2)}")


# --- История ---
async def history(update:Update, context:ContextTypes.DEFAULT_TYPE):

    rows = get_last_transactions(update.effective_user.id)

    if not rows:
        await update.message.reply_text("История пустая")
        return

    text = ""

    for r in rows:
        sign = "+" if r[0] == "income" else "-"
        text += f"{sign}{r[2]} {r[1]}\n"

    await update.message.reply_text(text)


# --- Основной обработчик сообщений ---
async def text_handler(update:Update, context:ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not allowed(user_id):
        return

    text = update.message.text


    # --- Выбор режима ---
    if text == "💰 Доход":
        user_state[user_id] = "income"
        await update.message.reply_text("Введите сумму и категорию\nпример: 6894.33 зарплата")
        return


    if text == "💸 Расход":
        user_state[user_id] = "expense"
        await update.message.reply_text("Введите сумму и категорию\nпример: 120 еда")
        return


    # --- Баланс ---
    if text == "💳 Баланс":
        await balance(update,context)
        return


    # --- История ---
    if text == "📜 История":
        await history(update,context)
        return


    # --- Круговая статистика ---
    if text == "📊 Статистика":

        img = generate_stats(user_id)

        if img:
            await update.message.reply_photo(open(img,"rb"))
        else:
            await update.message.reply_text("Нет данных")

        return


    # --- Месячный график ---
    if text == "📊 Месяцы":

        img = monthly_stats(user_id)

        if img:
            await update.message.reply_photo(open(img,"rb"))
        else:
            await update.message.reply_text("Нет данных")

        return


    # --- Доход vs расход ---
    if text == "📈 Доход vs Расход":

        img = income_vs_expense(user_id)

        if img:
            await update.message.reply_photo(open(img,"rb"))
        else:
            await update.message.reply_text("Нет данных")

        return


    # --- Топ расходов ---
    if text == "🏆 Топ":

        result = top_categories(user_id)

        if result:
            await update.message.reply_text(result)

        return


    # --- Excel отчёт ---
    if text == "📁 Excel":

        file = export_excel(user_id)

        await update.message.reply_document(open(file,"rb"))

        return


    # --- Новый месяц ---
    if text == "🆕 Новый месяц":

        reset_month()

        await update.message.reply_text("База очищена. Новый месяц начат.")

        return


    # --- Добавление операции ---
    parts = text.split()

    if len(parts) == 2:

        try:

            if parts[0].replace('.', '', 1).isdigit():

                amount = float(parts[0])
                category = parts[1]

            else:

                category = parts[0]
                amount = float(parts[1])

            transaction_type = user_state.get(user_id, "expense")

            add_transaction(
                user_id,
                transaction_type,
                category,
                amount,
                str(datetime.now())
            )

            await update.message.reply_text("Добавлено")

        except:
            pass


# --- Ежемесячный отчёт ---
def monthly_job():

    for user_id in ALLOWED_USERS:

        report = generate_month_report(user_id)

        try:
            app.bot.send_message(
                chat_id=user_id,
                text=report
            )
        except:
            pass


# --- Запуск бота ---
app = ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start",start))
app.add_handler(MessageHandler(filters.TEXT,text_handler))


# --- Планировщик ---
scheduler = BackgroundScheduler()

scheduler.add_job(
    monthly_job,
    "cron",
    day=1,
    hour=10
)

scheduler.start()


print("BOT STARTED")

app.run_polling()