import logging
import gspread
from oauth2client.service_account import ServiceAccountCredentials
from telegram import Update
from telegram.ext import Application, CommandHandler, MessageHandler, filters


# توکن ربات تلگرام خود را اینجا قرار دهید
TOKEN = "7309813282:AAFeJzOMokJdwE3IV3383GASYuB_FA7PWdI"

# تنظیمات لاگ
logging.basicConfig(format='%(asctime)s - %(name)s - %(levelname)s - %(message)s', level=logging.INFO)
logger = logging.getLogger(__name__)

# تنظیم دسترسی به Google Sheets
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
creds = ServiceAccountCredentials.from_json_keyfile_name('pgpractice-df6083d215fd.json', scope)
client = gspread.authorize(creds)

def get_price_by_code(code):
    sheet_code = code[0].upper()
    try:
        sheet = client.open("PriceList").sheet1
        cell = sheet.find(code)
        row = sheet.row_values(cell.row)
        price = row[8]  # ستون قیمت
        if price:
            return f"قیمت برای کد {code}: {price}"
        else:
            return f"قیمت برای کد {code} موجود نیست، لطفاً با ادمین تماس بگیرید."
    except gspread.exceptions.WorksheetNotFound:
        return "شیت مربوط به این کد یافت نشد."
    except gspread.exceptions.CellNotFound:
        return "کد مورد نظر در این شیت یافت نشد."

async def start(update: Update, context):
    await update.message.reply_text('سلام! کد کالا را برای من ارسال کنید تا قیمت آن را به شما بگویم.')

async def handle_message(update: Update, context):
    code = update.message.text.strip()  # حذف فضاهای اضافی
    response = get_price_by_code(code)
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
