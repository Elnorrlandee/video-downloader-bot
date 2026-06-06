import os
import logging
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters, ContextTypes
import yt_dlp

TOKEN = os.getenv('TOKEN')

if not TOKEN:
    raise ValueError("TOKEN غير موجود!")

logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.reply_text(
        '🎥 مرحبا!\n'
        'أرسل رابط فيديو من أي موقع.\n'
        'ملاحظة: بعض روابط X تحتاج كوكيز.'
    )

async def download_video(update: Update, context: ContextTypes.DEFAULT_TYPE):
    url = update.message.text.strip()
    if not url.startswith('http'):
        await update.message.reply_text('❌ أرسل رابط صحيح')
        return

    msg = await update.message.reply_text('⏳ جاري التحميل...')

    try:
        ydl_opts = {
            'outtmpl': '%(title)s.%(ext)s',
            'format': 'best[height<=480]/best',
            'noplaylist': True,
            'cookiefile': 'cookies.txt',   # ← دعم الكوكيز
            'extractor_args': {
                'youtube': {'player_client': ['ios', 'web', 'android']},
                'twitter': {'skip': ['dash']},
            },
            'http_headers': {
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
            },
        }

        with yt_dlp.YoutubeDL(ydl_opts) as ydl:
            info = ydl.extract_info(url, download=True)
            filename = ydl.prepare_filename(info)

        if os.path.exists(filename):
            await msg.edit_text('📤 جاري الرفع...')
            with open(filename, 'rb') as video:
                await update.message.reply_video(video=video, caption=f"✅ {info.get('title', 'فيديو')}")
            os.remove(filename)
            await msg.delete()
        else:
            await msg.edit_text('❌ فشل التحميل')

    except Exception as e:
        await msg.edit_text(f'❌ خطأ: {str(e)[:200]}')

def main():
    app = Application.builder().token(TOKEN).build()
    app.add_handler(CommandHandler("start", start))
    app.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, download_video))
    print("✅ البوت شغال...")
    app.run_polling()

if __name__ == '__main__':
    main()