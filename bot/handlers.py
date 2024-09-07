from telegram import ReplyKeyboardMarkup, KeyboardButton, Update
from telegram.ext import ContextTypes
from bot.utils import get_price_by_code

# ایجاد منو
async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    # بررسی اگر کدی از طریق deep link ارسال شده باشد
    if context.args:
        code = context.args[0]  # دریافت کد کالا از لینک
        response = await get_price_by_code(code)
        await update.message.reply_text(response)
    else:
        # ایجاد دکمه‌های منو
        keyboard = [
            [KeyboardButton("استعلام قیمت")],
            [KeyboardButton("مقایسه قیمت")]
        ]
        reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)

        # ارسال پیام با منو
        await update.message.reply_text(
            "سلام! لطفاً یکی از گزینه‌های زیر را انتخاب کنید:",
            reply_markup=reply_markup
        )

# هندلر پیام‌ها برای مدیریت دکمه‌های منو
async def handle_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    user_message = update.message.text.strip()

    # بررسی انتخاب کاربر از منو
    if user_message == "استعلام قیمت":
        await update.message.reply_text("لطفاً کد کالا را وارد کنید.")
        context.user_data['operation'] = 'price_check'  # ذخیره عملیات فعلی
    elif user_message == "مقایسه قیمت":
        await update.message.reply_text("لطفاً کد کالای اول را وارد کنید.")
        context.user_data['operation'] = 'compare'  # ذخیره عملیات فعلی
        context.user_data['compare'] = {}  # ذخیره کد کالاهای مقایسه
    else:
        # بررسی عملیات انتخاب‌شده توسط کاربر
        operation = context.user_data.get('operation')

        if operation == 'price_check':
            response = await get_price_by_code(user_message)
            await update.message.reply_text(response)

        elif operation == 'compare':
            compare_data = context.user_data['compare']
            if 'first_code' not in compare_data:
                compare_data['first_code'] = user_message
                await update.message.reply_text("لطفاً کد کالای دوم را وارد کنید.")
            elif 'second_code' not in compare_data:
                compare_data['second_code'] = user_message
                await compare_prices(update, context, compare_data['first_code'], compare_data['second_code'])
                del context.user_data['compare']  # حذف داده‌های مقایسه پس از انجام عملیات

        else:
            await update.message.reply_text("دستور نامعتبر است. لطفاً از منو یک گزینه انتخاب کنید.")
    
# مقایسه قیمت‌ها
async def compare_prices(update: Update, context: ContextTypes.DEFAULT_TYPE, code1: str, code2: str):
    price1 = await get_price_by_code(code1)
    price2 = await get_price_by_code(code2)
    
    if "قیمت" in price1 and "قیمت" in price2:
        await update.message.reply_text(f"قیمت {code1}: {price1}\nقیمت {code2}: {price2}")
    else:
        await update.message.reply_text(f"خطایی در مقایسه کدها:\n{price1}\n{price2}")
