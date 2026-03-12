from telegram import ReplyKeyboardMarkup,Update
from telegram.ext import ApplicationBuilder,MessageHandler,CommandHandler,filters,ContextTypes
from datetime import datetime

from config import TOKEN,ALLOWED_USERS
from database import add_transaction,get_balance,get_last_transactions
from stats import generate_stats
from excel_export import export_excel


menu=ReplyKeyboardMarkup([
["💰 Доход","💸 Расход"],
["🏺 Банки","🤝 Долги"],
["💳 Рассрочка","📊 Статистика"],
["📁 Excel","💳 Баланс"],
["📜 История"]
],resize_keyboard=True)


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

    user_id=update.effective_user.id

    if not allowed(user_id):
        return

    text=update.message.text


    if text=="💳 Баланс":
        await balance(update,context)
        return

    if text=="📜 История":
        await history(update,context)
        return

    if text=="📊 Статистика":
        await stats(update,context)
        return

    if text=="📁 Excel":
        await excel(update,context)
        return


    parts=text.split()

    if len(parts)==2:

        try:

            if parts[0].isdigit():

                amount=float(parts[0])
                category=parts[1]

            else:

                category=parts[0]
                amount=float(parts[1])


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

app.run_polling()