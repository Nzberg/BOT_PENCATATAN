import os
from telegram import Update, ReplyKeyboardMarkup
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes
from openpyxl import Workbook
from datetime import datetime
import json

TOKEN = os.getenv("8581211049:AAFXckqJMwdSKiSofvLQXr_9DW4KOSbh1M8")

# Load lokasi dari file
def load_locations():
    try:
        with open("locations.json", "r") as f:
            return json.load(f)
    except:
        return ["Matrix"]

def save_locations(data):
    with open("locations.json", "w") as f:
        json.dump(data, f)

locations = load_locations()
user_state = {}

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    keyboard = [["📊 Buat Data Baru"], ["📍 Check Lokasi"], ["➕ Tambah Lokasi"]]
    await update.message.reply_text("Pilih menu:", reply_markup=ReplyKeyboardMarkup(keyboard, resize_keyboard=True))

async def handle(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global locations

    user_id = update.message.from_user.id
    text = update.message.text

    if user_id not in user_state:
        user_state[user_id] = {}

    state = user_state[user_id]

    if text == "📊 Buat Data Baru":
        state["mode"] = "input"
        state["index"] = 0
        state["step"] = "input1"
        state["data"] = []
        await update.message.reply_text(f"Lokasi: {locations[0]}\nInput 1:")
        return

    elif text == "📍 Check Lokasi":
        await update.message.reply_text("\n".join(locations))
        return

    elif text == "➕ Tambah Lokasi":
        state["mode"] = "add"
        await update.message.reply_text("Masukkan lokasi baru:")
        return

    if state.get("mode") == "add":
        locations.append(text)
        save_locations(locations)
        await update.message.reply_text("✅ Lokasi ditambahkan")
        state["mode"] = None
        return

    if state.get("mode") == "input":
        idx = state["index"]

        if state["step"] == "input1":
            state["temp"] = int(text)
            state["step"] = "input2"
            await update.message.reply_text("Input 2:")
            return

        elif state["step"] == "input2":
            state["data"].append({
                "lokasi": locations[idx],
                "input1": state["temp"],
                "input2": int(text)
            })

            state["index"] += 1

            if state["index"] >= len(locations):
                file = create_excel(state["data"])
                await update.message.reply_document(document=open(file, "rb"))
                state["mode"] = None
            else:
                state["step"] = "input1"
                await update.message.reply_text(f"Lokasi: {locations[state['index']]}\nInput 1:")

def create_excel(data):
    wb = Workbook()
    ws = wb.active

    ws.append(["Lokasi", "Input 1", "Input 2"])

    total1 = 0
    total2 = 0

    for d in data:
        ws.append([d["lokasi"], d["input1"], d["input2"]])
        total1 += d["input1"]
        total2 += d["input2"]

    ws.append(["TOTAL", total1, total2])

    filename = f"report_{datetime.now().strftime('%d-%m-%Y')}.xlsx"
    wb.save(filename)

    return filename

app = ApplicationBuilder().token(TOKEN).build()
app.add_handler(CommandHandler("start", start))
app.add_handler(MessageHandler(filters.TEXT, handle))

app.run_polling()