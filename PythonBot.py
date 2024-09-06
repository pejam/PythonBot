import logging
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config.settings import settings
from bot.handlers import start, handle_message

# تنظیمات لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن ربات تلگرام
TOKEN = settings.TELEGRAM_BOT_TOKEN

def main():
    # ایجاد شیء Application با توکن ربات
    application = Application.builder().token(TOKEN).build()

    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # تنها متن و نه دستورات

    # شروع و نگهداری از ربات
    application.run_polling()

if __name__ == '__main__':
    main()
