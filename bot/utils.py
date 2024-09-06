import gspread
import re
from gspread.exceptions import WorksheetNotFound, GSpreadException
from config.settings import settings
from oauth2client.service_account import ServiceAccountCredentials

# تنظیم دسترسی به Google Sheets با استفاده از متغیرهای محیطی
scope = ["https://spreadsheets.google.com/feeds", "https://www.googleapis.com/auth/drive"]
if settings.DEBUG:
    creds = ServiceAccountCredentials.from_json_keyfile_name(settings.GSPREAD_CREDENTIALS, scope)
else:
    creds = ServiceAccountCredentials.from_json_keyfile_dict(settings.GSPREAD_CREDENTIALS, scope)
client = gspread.authorize(creds)

async def get_price_by_code(code):
    # بررسی فرمت کد ورودی
    if not re.match(r'^[A-Z]\d{3}$', code):
        return "فرمت ورودی درست نیست. لطفاً کدی با فرمت صحیح وارد کنید (یک کاراکتر حرف بزرگ انگلیسی + سه عدد)."
    
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
        return f"دسته بندی مربوط به کد '{sheet_prefix}' یافت نشد."

    try:
        sheet = client.open("PriceList").worksheet(matching_sheet_name)
        
        # پیدا کردن ایندکس ستون قیمت کانال
        header_row = sheet.row_values(1)
        try:
            price_column_index = header_row.index("قیمت کانال")
        except ValueError:
            return "ستون 'قیمت کانال' در شیت یافت نشد."
        
        # جستجوی کد در شیت
        try:
            cell = sheet.find(code)
            if cell is None:
                return f"کد {code} در دسته بندی '{matching_sheet_name[2:]}' یافت نشد."
            row = sheet.row_values(cell.row)
            price = row[price_column_index]  # استفاده از ایندکس ستون قیمت

            if not price or price == "$0":
                return f"جهت استعلام قیمت برای کد {code} ، لطفاً با ادمین تماس بگیرید."
            else:
                return f"قیمت برای کد {code}: {price}"
        except GSpreadException as e:
            return f"خطا در جستجوی کد {code} در دسته بندی '{matching_sheet_name}'. خطا: {str(e)}"

    except WorksheetNotFound:
        return f"دسته بندی '{matching_sheet_name}' یافت نشد."
    except GSpreadException as e:
        return f"خطا در ارتباط با Google Sheets: {str(e)}"
    except Exception as e:
        return f"خطای ناشناخته: {str(e)}"
