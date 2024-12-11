import random
from telegram import Update
from telegram.ext import ApplicationBuilder, CommandHandler, MessageHandler, filters, ContextTypes

# Database sederhana
waiting_list = []
active_chats = {}
user_ids = set()
CHANNEL_ID = '@rzbotkep'  # Ganti dengan ID channel atau grup Anda

# Fungsi untuk memulai pencarian pasangan
async def search(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_ids.add(user_id)
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
async def stop(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        del active_chats[partner_id]
        await context.bot.send_message(chat_id=user_id, text="Obrolan telah diakhiri.")
        await context.bot.send_message(chat_id=partner_id, text="Pasangan Anda telah meninggalkan obrolan.")
    else:
        await update.message.reply_text("Anda tidak sedang dalam obrolan.")

# Fungsi untuk mengganti pasangan obrolan
async def next(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await stop(update, context)
    await search(update, context)

# Fungsi untuk menangani pesan teks
async def handle_text_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_ids.add(user_id)
    full_name = f"{update.message.from_user.first_name} {update.message.from_user.last_name or ''}".strip()
    username = update.message.from_user.username
    if user_id in active_chats:
        await context.bot.send_message(chat_id=active_chats[user_id], text=update.message.text)
    else:
        await update.message.reply_text("Anda tidak sedang dalam obrolan. Ketik /search untuk mencari pasangan obrolan.")
    # Kirim ke channel atau grup
    await context.bot.send_message(chat_id=CHANNEL_ID, text=f"Dari {full_name} (@{username}): {update.message.text}")

# Fungsi untuk menangani pesan foto
async def handle_photo_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_ids.add(user_id)
    full_name = f"{update.message.from_user.first_name} {update.message.from_user.last_name or ''}".strip()
    username = update.message.from_user.username
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        photo_file = update.message.photo[-1].file_id
        await context.bot.send_photo(chat_id=partner_id, photo=photo_file)
    else:
        await update.message.reply_text("Anda tidak sedang dalam obrolan. Ketik /search untuk mencari pasangan obrolan.")
    # Kirim ke channel atau grup
    photo_file = update.message.photo[-1].file_id
    caption = f"Dari {full_name} (@{username})"
    await context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo_file, caption=caption)

# Fungsi untuk menangani pesan video
async def handle_video_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_ids.add(user_id)
    full_name = f"{update.message.from_user.first_name} {update.message.from_user.last_name or ''}".strip()
    username = update.message.from_user.username
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        video_file = update.message.video.file_id
        await context.bot.send_video(chat_id=partner_id, video=video_file)
    else:
        await update.message.reply_text("Anda tidak sedang dalam obrolan. Ketik /search untuk mencari pasangan obrolan.")
    # Kirim ke channel atau grup
    video_file = update.message.video.file_id
    caption = f"Dari {full_name} (@{username})"
    await context.bot.send_video(chat_id=CHANNEL_ID, video=video_file, caption=caption)

# Fungsi untuk menangani voice note
async def handle_voice_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_ids.add(user_id)
    full_name = f"{update.message.from_user.first_name} {update.message.from_user.last_name or ''}".strip()
    username = update.message.from_user.username
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        voice_file = update.message.voice.file_id
        await context.bot.send_voice(chat_id=partner_id, voice=voice_file)
    else:
        await update.message.reply_text("Anda tidak sedang dalam obrolan. Ketik /search untuk mencari pasangan obrolan.")
    # Kirim ke channel atau grup
    voice_file = update.message.voice.file_id
    caption = f"Dari {full_name} (@{username})"
    await context.bot.send_voice(chat_id=CHANNEL_ID, voice=voice_file, caption=caption)

# Fungsi untuk memulai bot
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_id = update.message.from_user.id
    user_ids.add(user_id)
    await update.message.reply_text("Selamat datang di Anonymous Chat! Ketik /search untuk mencari pasangan obrolan, /stop untuk mengakhiri obrolan, atau /next untuk mengganti pasangan.")

# Konfigurasi Bot
if __name__ == '__main__':
    bot_token = '7881351318:AAEUSNn1P8C5TB-EAu8vPmH4wlkgFqeSk9o'
    app = ApplicationBuilder().token(bot_token).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(CommandHandler("search", search))
    app.add_handler(CommandHandler("stop", stop))
    app.add_handler(CommandHandler("next", next))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_text_message))
    app.add_handler(MessageHandler(filters.PHOTO, handle_photo_message))
    app.add_handler(MessageHandler(filters.VIDEO, handle_video_message))
    app.add_handler(MessageHandler(filters.VOICE, handle_voice_message))

    print("Bot sedang berjalan...")
    app.run_polling()
