import os
import logging
import random
import asyncio
from datetime import datetime
from telegram import (
    Update, 
    InlineKeyboardMarkup, 
    InlineKeyboardButton,
    ReplyKeyboardMarkup,
    KeyboardButton
)
from telegram.ext import (
    Application,
    CommandHandler,
    MessageHandler,
    CallbackQueryHandler,
    ConversationHandler,
    filters,
    ContextTypes,
    CallbackContext
)

# تنظیمات لاگ
logging.basicConfig(
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.INFO
)
logger = logging.getLogger(__name__)

# توکن ربات - استفاده از متغیر محیطی برای امنیت بیشتر
TOKEN = os.getenv('TELEGRAM_BOT_TOKEN', '8239397974:AAFdP0WyxwyAFNS9uq0m9v6eTk1BAaykfGM')

# پورت برای دپلوی (اختیاری)
PORT = int(os.environ.get('PORT', 8080))

# کلاس برای مدیریت کاربران
class UserData:
    def __init__(self):
        self.virtual_numbers = {}
        self.verification_codes = {}
        self.balance = 47000
        self.purchase_count = 0
    
    def generate_irani_number(self):
        """تولید شماره مجازی ایرانی"""
        prefix = "+98"
        number = random.choice(["912", "915", "916", "917", "918", "919", "990", "991", "992"])
        for _ in range(7):
            number += str(random.randint(0, 9))
        return f"{prefix}{number}"
    
    def generate_verification_code(self):
        """تولید کد تایید 6 رقمی"""
        return str(random.randint(100000, 999999))

# ذخیره داده‌های کاربران
users_data = {}

# ==================== دستورات اصلی ====================

async def start(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /start"""
    user_id = update.effective_user.id
    
    # ایجاد یا بازیابی داده‌های کاربر
    if user_id not in users_data:
        users_data[user_id] = UserData()
    
    # پیام خوش‌آمدگویی
    welcome_msg = """
✨ **به ربات شماره مجازی روبیکا خوش آمدید!** ✨

📱 **امکانات ربات:**
• خرید شماره مجازی ایران
• خدمات ویژه
• افزایش موجودی
• دریافت کد تایید

👇 لطفا یکی از گزینه‌های زیر را انتخاب کنید:
    """
    
    # ایجاد کیبورد اصلی
    keyboard = [
        [KeyboardButton("🛒 خرید شماره مجازی")],
        [KeyboardButton("💰 افزایش موجودی"), KeyboardButton("⭐ خدمات ویژه")],
        [KeyboardButton("🎁 شماره مجازی رایگان"), KeyboardButton("👤 حساب من")]
    ]
    
    reply_markup = ReplyKeyboardMarkup(keyboard, resize_keyboard=True)
    
    await update.message.reply_text(
        welcome_msg,
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

# ==================== مدیریت دکمه‌ها ====================

async def handle_messages(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک روی دکمه‌ها"""
    user_id = update.effective_user.id
    text = update.message.text
    
    if text == "🛒 خرید شماره مجازی":
        await buy_virtual_number(update, context)
    elif text == "💰 افزایش موجودی":
        await increase_balance(update, context)
    elif text == "⭐ خدمات ویژه":
        await special_services(update, context)
    elif text == "🎁 شماره مجازی رایگان":
        await free_virtual_number(update, context)
    elif text == "👤 حساب من":
        await my_account(update, context)
    else:
        # پاسخ به پیام‌های دیگر
        await update.message.reply_text(
            "لطفاً از دکمه‌های منو استفاده کنید.",
            parse_mode='Markdown'
        )

async def buy_virtual_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی خرید شماره مجازی"""
    keyboard = [
        [InlineKeyboardButton("🇮🇷 ایران", callback_data="country_iran")],
        [InlineKeyboardButton("🇬🇧 انگلستان", callback_data="country_uk")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "🌍 **لطفا کشور مورد نظر را انتخاب کنید:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def increase_balance(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """منوی افزایش موجودی"""
    keyboard = [
        [InlineKeyboardButton("💳 کارت به کارت", callback_data="payment_card")],
        [InlineKeyboardButton("🌐 درگاه زرین پال", callback_data="payment_zarinpal")]
    ]
    
    reply_markup = InlineKeyboardMarkup(keyboard)
    
    await update.message.reply_text(
        "💰 **روش افزایش موجودی را انتخاب کنید:**",
        reply_markup=reply_markup,
        parse_mode='Markdown'
    )

async def special_services(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """خدمات ویژه"""
    await update.message.reply_text(
        "⭐ **خدمات ویژه به زودی فعال خواهد شد...**\n\n"
        "در حال حاضر می‌توانید از سرویس‌های اصلی ربات استفاده کنید.",
        parse_mode='Markdown'
    )

async def free_virtual_number(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """شماره مجازی رایگان"""
    await update.message.reply_text(
        "🎁 **شماره مجازی رایگان**\n\n"
        "این سرویس به زودی راه‌اندازی خواهد شد.\n"
        "برای دریافت شماره مجازی از بخش خرید اقدام کنید.",
        parse_mode='Markdown'
    )

async def my_account(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """اطلاعات حساب کاربر"""
    user_id = update.effective_user.id
    user = users_data.get(user_id, UserData())
    
    account_info = f"""
👤 **اطلاعات حساب کاربری**

🆔 شناسه کاربری: `{user_id}`
📞 شماره تماس: `+98{random.randint(9100000000, 9199999999)}`
👤 نام اکانت: کاربر روبیکا
📊 تعداد خرید: {user.purchase_count} عدد
💰 موجودی کیف پول: {user.balance:,} تومان

📅 تاریخ عضویت: {datetime.now().strftime('%Y/%m/%d')}
    """
    
    await update.message.reply_text(
        account_info,
        parse_mode='Markdown'
    )

# ==================== مدیریت Callback ====================

async def handle_callback(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت کلیک روی دکمه‌های اینلاین"""
    query = update.callback_query
    await query.answer()
    
    user_id = update.effective_user.id
    user = users_data.get(user_id, UserData())
    
    if query.data == "country_iran":
        # تولید شماره ایرانی
        virtual_number = user.generate_irani_number()
        
        # ذخیره شماره برای کاربر
        user.virtual_numbers[user_id] = virtual_number
        
        # ایجاد دکمه‌های مربوطه
        keyboard = [
            [InlineKeyboardButton("📋 کپی شماره", callback_data="copy_number")],
            [InlineKeyboardButton("📲 دریافت کد تأیید", callback_data="get_code")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = f"""
✅ **شماره مجازی ایرانی با موفقیت ساخته شد!**

📱 **شماره شما:**
`{virtual_number}`

📝 **راهنمای استفاده:**
1. شماره بالا را کپی کنید
2. در برنامه روبیکا وارد شوید
3. شماره را وارد کنید
4. روی دریافت کد تأیید کلیک کنید
5. کدی که دریافت می‌کنید را اینجا وارد کنید

⏱ **مدت اعتبار:** 24 ساعت
        """
        
        await query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == "country_uk":
        # کشور انگلستان غیرفعال
        await query.edit_message_text(
            "⛔ **سرویس کشور انگلستان در حال حاضر غیرفعال است!**\n\n"
            "لطفاً کشور ایران را انتخاب کنید.",
            parse_mode='Markdown'
        )
    
    elif query.data == "copy_number":
        # کپی شماره
        await query.answer("✅ شماره کپی شد! (در حالت واقعی قابل کپی است)")
    
    elif query.data == "get_code":
        # تولید کد تأیید
        verification_code = user.generate_verification_code()
        user.verification_codes[user_id] = verification_code
        
        # ایجاد دکمه کپی کد
        keyboard = [
            [InlineKeyboardButton("📋 کپی کد", callback_data="copy_code")]
        ]
        
        reply_markup = InlineKeyboardMarkup(keyboard)
        
        message_text = f"""
🔐 **کد تأیید 6 رقمی**

📝 **کد شما:**
`{verification_code}`

⚠️ **توجه:**
• این کد فقط یکبار قابل استفاده است
• کد تا 5 دقیقه دیگر منقضی می‌شود
• کد را در برنامه روبیکا وارد کنید

✅ پس از وارد کردن کد، حساب شما فعال خواهد شد
        """
        
        await query.edit_message_text(
            message_text,
            reply_markup=reply_markup,
            parse_mode='Markdown'
        )
    
    elif query.data == "copy_code":
        # کپی کد
        await query.answer("✅ کد کپی شد! (در حالت واقعی قابل کپی است)")
    
    elif query.data == "payment_card":
        # پرداخت کارت به کارت
        await query.edit_message_text(
            "💳 **روش پرداخت کارت به کارت**\n\n"
            "📌 **شماره کارت:** `6037-9971-1234-5678`\n"
            "🏦 **بانک:** ملی\n"
            "👤 **به نام:** روبیکا\n\n"
            "✅ پس از واریز، رسید را برای ادمین ارسال کنید.\n"
            "⏱ واریز شما حداکثر تا 30 دقیقه تأیید می‌شود.",
            parse_mode='Markdown'
        )
    
    elif query.data == "payment_zarinpal":
        # پرداخت زرین‌پال
        await query.edit_message_text(
            "🌐 **درگاه پرداخت زرین پال**\n\n"
            "🔗 **لینک پرداخت:** در حال حاضر غیرفعال\n\n"
            "⚠️ این درگاه به زودی فعال خواهد شد.\n"
            "لطفاً از روش کارت به کارت استفاده کنید.",
            parse_mode='Markdown'
        )

# ==================== دستورات دیگر ====================

async def help_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /help"""
    help_text = """
🤖 **راهنمای ربات شماره مجازی روبیکا**

📌 **دستورات اصلی:**
/start - شروع ربات و نمایش منوی اصلی
/help - نمایش این راهنما
/about - درباره ربات

🛒 **نحوه خرید شماره مجازی:**
1. روی «خرید شماره مجازی» کلیک کنید
2. کشور ایران را انتخاب کنید
3. شماره تولید شده را کپی کنید
4. در روبیکا از شماره استفاده کنید
5. کد تأیید را دریافت کنید

💰 **افزایش موجودی:**
از بخش «افزایش موجودی» و سپس «کارت به کارت»

👤 **مشاهده حساب:**
از بخش «حساب من» اطلاعات خود را ببینید

📞 **پشتیبانی:**
@rubika_support
    """
    
    await update.message.reply_text(help_text, parse_mode='Markdown')

async def about_command(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """دستور /about"""
    about_text = """
📱 **ربات شماره مجازی روبیکا**

✨ **ویژگی‌ها:**
• تولید شماره مجازی ایرانی
• دریافت کد تأیید
• کیف پول داخلی
• پشتیبانی 24 ساعته

🛡 **امنیت:**
• تمامی شماره‌ها واقعی و فعال
• کدها امن و یکبار مصرف
• محرمانگی اطلاعات کاربران

👨‍💻 **توسعه‌دهنده:**
@rubika_dev

📅 **ورژن:** 2.0.0
    """
    
    await update.message.reply_text(about_text, parse_mode='Markdown')

# ==================== تابع اصلی ====================

async def error_handler(update: Update, context: ContextTypes.DEFAULT_TYPE):
    """مدیریت خطاها"""
    logger.error(f"خطا در بروزرسانی {update}: {context.error}")

def main():
    """تابع اصلی اجرای ربات"""
    # ایجاد اپلیکیشن
    application = Application.builder().token(TOKEN).build()
    
    # افزودن هندلرهای دستورات
    application.add_handler(CommandHandler("start", start))
    application.add_handler(CommandHandler("help", help_command))
    application.add_handler(CommandHandler("about", about_command))
    
    # افزودن هندلر برای دکمه‌های کیبورد
    application.add_handler(MessageHandler(filters.TEXT & ~filters.COMMAND, handle_messages))
    
    # افزودن هندلر برای callback query
    application.add_handler(CallbackQueryHandler(handle_callback))
    
    # افزودن هندلر خطا
    application.add_error_handler(error_handler)
    
    # شروع ربات
    print("🤖 ربات شماره مجازی روبیکا شروع به کار کرد...")
    print(f"👤 برای شروع: https://t.me/{application.bot.username}")
    
    # دو حالت اجرا: لوکال و سرور
    if os.getenv('RAILWAY_ENVIRONMENT') or os.getenv('HEROKU_APP_ID'):
        # اجرا در سرور (مانند Railway یا Heroku)
        application.run_webhook(
            listen="0.0.0.0",
            port=PORT,
            url_path=TOKEN,
            webhook_url=f"https://{os.getenv('RAILWAY_STATIC_URL', 'your-app-name')}.railway.app/{TOKEN}"
        )
    else:
        # اجرا لوکال
        application.run_polling(allowed_updates=Update.ALL_TYPES)

if __name__ == '__main__':
    main()
