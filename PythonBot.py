import os
import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters
from config.settings import settings


# تنظیمات لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# توکن ربات تلگرام خود را اینجا قرار دهید
TOKEN = settings.TELEGRAM_BOT_TOKEN

# تنظیم دسترسی به Google Sheets با استفاده از متغیرهای محیطی

#creds_dict = {
#    "type": "service_account",
#    "project_id": "pgpractice",
#    "private_key_id": "adce347384eb4a8b244e5b68411dcd0fd2e021c8",
#    "private_key": os.getenv("GSPREAD_PRIVATE_KEY").replace("\\n", "\n"),
#    "client_email": os.getenv("GSPREAD_CLIENT_EMAIL"),
#    "client_id": "103004925027424587941",
#    "auth_uri": "https://accounts.google.com/o/oauth2/auth",
#    "token_uri": "https://oauth2.googleapis.com/token",
#    "auth_provider_x509_cert_url": "https://www.googleapis.com/oauth2/v1/certs",
#    "client_x509_cert_url": "https://www.googleapis.com/robot/v1/metadata/x509/pgpractice%40pgpractice.iam.gserviceaccount.com",
#    "universe_domain": "googleapis.com"
#}
#creds = ServiceAccountCredentials.from_json_keyfile_dict(creds_dict, scope)
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
if settings.DEBUG:
    # حالت دیباگ: استفاده از فایل JSON
    creds = ServiceAccountCredentials.from_json_keyfile_name(settings.GSPREAD_CREDENTIALS, scope)
else:
    # حالت ریلیز: استفاده از دیکشنری JSON
    creds = ServiceAccountCredentials.from_json_keyfile_dict(settings.GSPREAD_CREDENTIALS, scope)
client = gspread.authorize(creds)

# تنظیم دسترسی به Google Sheets
#scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
#creds = ServiceAccountCredentials.from_json_keyfile_name('pgpractice-df6083d215fd.json', scope)
#client = gspread.authorize(creds)

async def get_price_by_code(code):
    sheet_prefix = code[0].upper()
    sheet_names = [
        "A فلش", "B لوازم جانبی کامپیوتر", "C گیمینگ", 
        "D تجهیزات صوتی و تصویر", "E هندزفری", "F شارژر", 
        "G کابل شارژ", "H هولدر", "I هدست", "J اسپیکر", "K ساعت",
        "L کیبورد", "M ماوس", "N جانبی موبایل", "O دانگل و اتصالات", 
        "P پاوربانک"
    ]
    
    matching_sheet_name = None
    for name in sheet_names:
        if name.startswith(sheet_prefix):
            matching_sheet_name = name
            break

    if matching_sheet_name is None:
        return f"شیت مربوط به کد '{sheet_prefix}' یافت نشد."

    try:
        sheet = client.open("PriceList").worksheet(matching_sheet_name)
        cell = sheet.find(code)
        row = sheet.row_values(cell.row)
        price = row[8]  # ستون قیمت، ایندکس 7 برای ستون هشتم
        
        if not price or price == "0":
            return f"قیمت برای کد {code} موجود نیست یا صفر است، لطفاً با ادمین تماس بگیرید."
        
        return f"قیمت برای کد {code}: {price}"

    except WorksheetNotFound:
        return f"شیت '{matching_sheet_name}' یافت نشد."
    except CellNotFound:
        return f"کد {code} در شیت '{matching_sheet_name}' یافت نشد."

async def start(update: Update, context):
    await update.message.reply_text('سلام! کد کالا را برای من ارسال کنید تا قیمت آن را به شما بگویم.')

async def handle_message(update: Update, context):
    code = update.message.text.strip()  # حذف فضاهای اضافی
    response = await get_price_by_code(code)
    await update.message.reply_text(response)

def main():
    # ایجاد شیء Application با توکن ربات
    application = Application.builder().token(TOKEN).build()

    # اضافه کردن هندلرها
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", start))  # یا می‌توانید یک تابع کمک جداگانه اضافه کنید
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_message))  # تنها متن و نه دستورات

    # شروع و نگهداری از ربات
    application.run_polling()

if __name__ == '__main__':
    main()