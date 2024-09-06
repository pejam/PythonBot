from telegram import Update
from telegram.ext import CallbackContext
from bot.utils import get_price_by_code

async def start(update: Update, context: CallbackContext):
    await update.message.reply_text('سلام! کد کالا را برای من ارسال کنید تا قیمت آن را به شما بگویم.')

async def handle_message(update: Update, context: CallbackContext):
    code = update.message.text.strip()  # حذف فضاهای اضافی
    response = await get_price_by_code(code)
    await update.message.reply_text(response)
