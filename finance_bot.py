from telegram import ReplyKeyboardMarkup,Update
from telegram.ext import ApplicationBuilder,MessageHandler,CommandHandler,filters,ContextTypes
from datetime import datetime

from config import TOKEN,ALLOWED_USERS
from database import add_transaction,get_balance,get_last_transactions
from stats import generate_stats, monthly_stats, income_vs_expense, top_categories
from excel_export import export_excel

from monthly_report import generate_month_report
from apscheduler.schedulers.background import BackgroundScheduler


menu = ReplyKeyboardMarkup([
["💰 Доход","💸 Расход"],
["📊 Статистика","📊 Месяцы"],
["📈 Доход vs Расход","🏆 Топ"],
["💳 Баланс","📜 История"],
["📁 Excel"]
], resize_keyboard=True)


def allowed(user_id):
    return user_id in ALLOWED_USERS


async def start(update:Update,context:ContextTypes.DEFAULT_TYPE):

    if not allowed(update.effective_user.id):
        return

    await update.message.reply_text(
    "Финансовый бот",
    reply_markup=menu
    )


async def balance(update:Update,context:ContextTypes.DEFAULT_TYPE):

    bal=get_balance(update.effective_user.id)

    await update.message.reply_text(f"Баланс: {bal}")


async def history(update:Update,context:ContextTypes.DEFAULT_TYPE):

    rows=get_last_transactions(update.effective_user.id)

    text=""

    for r in rows:

        sign="+" if r[0]=="income" else "-"

        text+=f"{sign}{r[2]} {r[1]}\n"

    await update.message.reply_text(text)


async def stats(update:Update,context:ContextTypes.DEFAULT_TYPE):

    img=generate_stats(update.effective_user.id)

    if img:
        await update.message.reply_photo(open(img,"rb"))
    else:
        await update.message.reply_text("Нет данных")


async def excel(update:Update,context:ContextTypes.DEFAULT_TYPE):

    file=export_excel(update.effective_user.id)

    await update.message.reply_document(open(file,"rb"))


async def text_handler(update:Update,context:ContextTypes.DEFAULT_TYPE):

    user_id = update.effective_user.id

    if not allowed(user_id):
        return

    text = update.message.text


    # БАЛАНС
    if text == "💳 Баланс":
        await balance(update,context)
        return


    # ИСТОРИЯ
    if text == "📜 История":
        await history(update,context)
        return


    # КРУГОВАЯ СТАТИСТИКА
    if text == "📊 Статистика":

        img = generate_stats(user_id)

        if img:
            await update.message.reply_photo(open(img,"rb"))
        else:
            await update.message.reply_text("Нет данных")

        return


    # ГРАФИК ПО МЕСЯЦАМ
    if text == "📊 Месяцы":

        img = monthly_stats(user_id)

        if img:
            await update.message.reply_photo(open(img,"rb"))
        else:
            await update.message.reply_text("Нет данных")

        return


    # ДОХОД VS РАСХОД
    if text == "📈 Доход vs Расход":

        img = income_vs_expense(user_id)

        if img:
            await update.message.reply_photo(open(img,"rb"))
        else:
            await update.message.reply_text("Нет данных")

        return


    # ТОП КАТЕГОРИЙ
    if text == "🏆 Топ":

        result = top_categories(user_id)

        if result:
            await update.message.reply_text(result)
        else:
            await update.message.reply_text("Нет данных")

        return


    # EXCEL
    if text == "📁 Excel":

        file = export_excel(user_id)

        await update.message.reply_document(open(file,"rb"))

        return


    # ДОБАВЛЕНИЕ РАСХОДА
    parts = text.split()

    if len(parts) == 2:

        try:

            if parts[0].replace('.', '', 1).isdigit():

                amount = float(parts[0])
                category = parts[1]

            else:

                category = parts[0]
                amount = float(parts[1])

            add_transaction(
                user_id,
                "expense",
                category,
                amount,
                str(datetime.now())
            )

            await update.message.reply_text("Добавлено")

        except:
            pass


app=ApplicationBuilder().token(TOKEN).build()

app.add_handler(CommandHandler("start",start))
app.add_handler(MessageHandler(filters.TEXT,text_handler))

print("BOT STARTED")
import os
from apscheduler.schedulers.background import BackgroundScheduler

def backup_db():

    file = "finance.db"

    if os.path.exists(file):

        app.bot.send_document(
            chat_id=ALLOWED_USERS[0],
            document=open(file,"rb"),
            caption="Автобэкап базы"
        )

scheduler = BackgroundScheduler()
scheduler.add_job(backup_db,"interval",hours=24)
scheduler.start()
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


scheduler = BackgroundScheduler()

# запуск раз в месяц
scheduler.add_job(
    monthly_job,
    "cron",
    day=1,
    hour=10
)

scheduler.start()

app.run_polling()