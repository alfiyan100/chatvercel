import os
from flask import Flask, request
from telegram import Update, Bot
from telegram.ext import Dispatcher, CommandHandler, MessageHandler, filters

app = Flask(__name__)

bot = Bot(token=os.environ["TELEGRAM_BOT_TOKEN"])
dispatcher = Dispatcher(bot, None, workers=0)

# Fungsi untuk memulai pencarian pasangan
async def search(update: Update, context):
    user_id = update.message.from_user.id
    if user_id in active_chats:
        await update.message.reply_text("Anda sudah dalam obrolan. Ketik /stop untuk mengakhiri obrolan atau /next untuk mencari pasangan baru.")
        return
    if waiting_list:
        partner_id = waiting_list.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        await context.bot.send_message(chat_id=user_id, text="Anda terhubung dengan pasangan obrolan.")
        await context.bot.send_message(chat_id=partner_id, text="Anda terhubung dengan pasangan obrolan.")
    else:
        waiting_list.append(user_id)
        await update.message.reply_text("⌛ Menunggu pengguna lain untuk terhubung...")

# Fungsi untuk mengakhiri obrolan
async def stop(update: Update, context):
    user_id = update.message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        del active_chats[partner_id]
        await context.bot.send_message(chat_id=user_id, text="Obrolan telah diakhiri.")
        await context.bot.send_message(chat_id=partner_id, text="Pasangan Anda telah meninggalkan obrolan.")
    else:
        await update.message.reply_text("Anda tidak sedang dalam obrolan.")

# Fungsi untuk mengganti pasangan obrolan
async def next(update: Update, context):
    await stop(update, context)
    await search(update, context)

# Fungsi untuk menangani pesan teks
async def handle_text_message(update: Update, context):
    user_id = update.message.from_user.id
    if user_id in active_chats:
        await context.bot.send_message(chat_id=active_chats[user_id], text=update.message.text)
    else:
        await update.message.reply_text("Anda tidak sedang dalam obrolan. Ketik /search untuk mencari pasangan obrolan.")
    await context.bot.send_message(chat_id=CHANNEL_ID, text=f"Dari {full_name} (@{username}): {update.message.text}")

# Fungsi untuk menangani pesan foto
async def handle_photo_message(update: Update, context):
    user_id = update.message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        photo_file = update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=partner_id, photo=photo_file)
    else:
        await update.message.reply_text("Anda tidak sedang dalam obrolan. Ketik /search untuk mencari pasangan obrolan.")
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo_file, caption=caption)

# Fungsi untuk menangani pesan video
async def handle_video_message(update: Update, context):
    user_id = update.message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        video_file = update.message.video.file_id
        await context.bot.send_video(chat_id=partner_id, video=video_file)
    else:
        await update.message.reply_text("Anda tidak sedang dalam obrolan. Ketik /search untuk mencari pasangan obrolan.")
    await context.bot.send_video(chat_id=CHANNEL_ID, video=video_file, caption=caption)

# Fungsi untuk menangani voice note
async def handle_voice_message(update: Update, context):
    user_id = update.message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        voice_file = update.message.voice.file_id
        await context.bot.send_voice(chat_id=partner_id, voice=voice_file)
    else:
        await update.message.reply_text("Anda tidak sedang dalam obrolan. Ketik /search untuk mencari pasangan obrolan.")
    await context.bot.send_voice(chat_id=CHANNEL_ID, voice=voice_file, caption=caption)

# Fungsi untuk memulai bot
async def start(update: Update, context):
    user_id = update.message.from_user.id
    await update.message.reply_text("Selamat datang di Anonymous Chat! Ketik /search untuk mencari pasangan obrolan, /stop untuk mengakhiri obrolan, atau /next untuk mengganti pasangan.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("search", search))
dispatcher.add_handler(CommandHandler("stop", stop))
dispatcher.add_handler(CommandHandler("next", next))
dispatcher.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
dispatcher.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))
dispatcher.add_handler(MessageHandler(filters.VIDEO, handle_video_message))
dispatcher.add_handler(MessageHandler(filters.VOICE, handle_voice_message))

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return "OK", 200

if __name__ == "__main__":
    app.run(port=5000)
