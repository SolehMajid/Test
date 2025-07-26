import asyncio
from telegram import Bot, Update
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    filters,
    ConversationHandler,
    ContextTypes,
)

# Token dan chat ID
TOKEN = '8022486289:AAHiGZ253Q-ObwwpGQCJKOWAhn_JPJ_GYto'
CHAT_ID = 5819407687

# Variabel tagihan
tagihan = 0

# State untuk ConversationHandler
TAMBAH = range(1)

# Start command
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Bot aktif! Tagihan akan terus bertambah.")

# Handler untuk 'ya'
async def handle_ya(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global tagihan
    tagihan -= 100000
    await update.message.reply_text(f"✅ Sisa tagihanmu: Rp {tagihan:,}")

# Handler ketika user ketik "tambah"
async def tambah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Masukkan nominal yang ingin ditambahkan:")
    return TAMBAH  # pindah ke state TAMBAH

# Handler untuk menerima angka setelah "tambah"
async def proses_tambah(update: Update, context: ContextTypes.DEFAULT_TYPE):
    global tagihan
    pesan = update.message.text

    if pesan.isdigit():
        jumlah = int(pesan)
        tagihan += jumlah
        await update.message.reply_text(f"✅ Sisa tagihanmu: Rp {tagihan:,}")
    else:
        await update.message.reply_text("Harap masukkan angka yang valid.")

    return ConversationHandler.END  # kembali ke state awal

# Handler jika input tidak sesuai
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text("Ketik 'ya' untuk bayar 100.000 atau 'tambah' untuk menambah tagihan.")

# Fungsi kirim tagihan rutin
async def kirim_tagihan(bot: Bot):
    global tagihan
    while True:
        tagihan += 100000
        await bot.send_message(chat_id=CHAT_ID, text=f"💸 Tagihanmu sekarang: Rp {tagihan:,}")
        await asyncio.sleep(10)  # ubah ke 86400 untuk setiap hari

# Fungsi utama
async def main():
    app = Application.builder().token(TOKEN).build()

    # Command start
    app.add_handler(CommandHandler("start", start))

    # Handler percakapan tambah
    conv_handler = ConversationHandler(
        entry_points=[MessageHandler(filters.TEXT & filters.Regex(r'(?i)^tambah$'), tambah)],
        states={
            TAMBAH: [MessageHandler(filters.TEXT & ~filters.COMMAND, proses_tambah)],
        },
        fallbacks=[],
    )

    # Handler untuk "ya"
    app.add_handler(MessageHandler(filters.TEXT & filters.Regex(r'(?i)^ya$'), handle_ya))

    # Tambahkan semua handler
    app.add_handler(conv_handler)
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))

    # Jalankan pengiriman tagihan otomatis
    asyncio.create_task(kirim_tagihan(app.bot))

    await app.initialize()
    await app.start()
    await app.updater.start_polling()
    print("✅ Bot berjalan...")

    await asyncio.Event().wait()

# Jalankan program
asyncio.run(main())
