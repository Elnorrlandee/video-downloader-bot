import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv('8653368549:AAGTMq7SwcMqiHXlkAwWTRf_hLUaKP8WD4I')  # مهم: سنجعله من Railway

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text('مرحبا! أرسل رابط الفيديو وسأحمله لك 🎥')

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith('http'):
        await update.message.reply_text('الرجاء إرسال رابط صحيح!')
        return

    msg = await update.message.reply_text('جاري التحميل... ⏳')

    try:
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'format': 'best[height<=720]',
            'noplaylist': True,
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.exists(filename):
            await msg.edit_text('جاري الرفع إلى تليجرام...')
            with open(filename, 'rb') as video:
                await update.message.reply_video(video=video, caption=f"✅ {info.get('title', 'فيديو')}")
            os.remove(filename)
        else:
            await msg.edit_text('فشل في تحميل الفيديو 😔')
    except Exception as e:
        await msg.edit_text(f'خطأ: {str(e)}')

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("البوت يعمل...")
    app.run_polling()

if __name__ == '__main__':
    main()