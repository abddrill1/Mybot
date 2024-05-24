
import requests
import json
import time
import os
import telegram
from telegram.ext import Updater, CommandHandler, MessageHandler, Filters
from telegram import InlineKeyboardButton, InlineKeyboardMarkup

# Your bot token from BotFather
BOT_TOKEN = '6701753535:AAFo4XQ-5R1yX9opT5atx8CH290v4vf6ddc'

# Define the FaucetEarner API endpoint
FAUCET_API_URL = 'https://faucetearner.org/api.php'

# Global variables to store account information
accounts = {}  # Dictionary to store accounts with their cookies
auto_claim_jobs = {}  # Dictionary to store auto-claim jobs for each account

# Function to generate a custom keyboard for the bot
def create_keyboard():
    keyboard = [
        [InlineKeyboardButton("Login", callback_data="login"), InlineKeyboardButton("Claim", callback_data="claim")],
        [InlineKeyboardButton("Add Account", callback_data="add_account"), InlineKeyboardButton("Withdraw", callback_data="withdraw")],
        [InlineKeyboardButton("Balance", callback_data="balance"), InlineKeyboardButton("Auto-Claim", callback_data="auto_claim")]
    ]
    return InlineKeyboardMarkup(keyboard)

# Function to login to FaucetEarner
def faucet_login(email, password):
    headers = {
        'authority': 'faucetearner.org',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'ar-YE,ar;q=0.9,en-YE;q=0.8,en-US;q=0.7,en;q=0.6',
        'content-type': 'application/json',
        'origin': 'https://faucetearner.org',
        'referer': 'https://faucetearner.org/login.php',
        'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        'act': 'login',
    }

    json_data = {
        'email': email,
        'password': password,
    }

    response = requests.post(FAUCET_API_URL, params=params, headers=headers, json=json_data)
    
    if "Login successful" in response.text:
        sufi = response.cookies.get_dict()
        return sufi
    else:
        return None

# Function to claim XRP from FaucetEarner
def claim_xrp(cookies):
    headers = {
        'authority': 'faucetearner.org',
        'accept': 'application/json, text/javascript, */*; q=0.01',
        'accept-language': 'ar-YE,ar;q=0.9,en-YE;q=0.8,en-US;q=0.7,en;q=0.6',
        'origin': 'https://faucetearner.org',
        'referer': 'https://faucetearner.org/faucet.php',
        'sec-ch-ua': '"Not)A;Brand";v="24", "Chromium";v="116"',
        'sec-ch-ua-mobile': '?1',
        'sec-ch-ua-platform': '"Android"',
        'sec-fetch-dest': 'empty',
        'sec-fetch-mode': 'cors',
        'sec-fetch-site': 'same-origin',
        'user-agent': 'Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36',
        'x-requested-with': 'XMLHttpRequest',
    }

    params = {
        'act': 'faucet',
    }

    response = requests.post(FAUCET_API_URL, params=params, cookies=cookies, headers=headers).text
    
    if 'Congratulations on receiving' in response.text:
        json_data = json.loads(response)
        message = json_data["message"]
        start_index = message.find(">") + 1
        end_index = message.find(" ", start_index)
        balance = message[start_index:end_index]
        return balance
    elif 'You have already claimed, please wait for the next wave!' in response.text:
        return None
    else:
        return None

# Function to handle the /start command
def start(update, context):
    update.message.reply_text(
        "أهلا بك في بوت FaucetEarner! 🎉\n"
        "استخدم الأزرار أدناه ل  بدء  جني  XRP!",
        reply_markup=create_keyboard()
    )

# Function to handle the /login command
def login(update, context):
    chat_id = update.message.chat_id
    update.message.reply_text("أدخل  اسم  المُستخدم  و  كلمة  ال  مرور  ل  حساب  FaucetEarner  (مُنفصل ب  مسافة):")
    context.user_data['state'] = 'login_input'

# Function to handle the /claim command
def claim(update, context):
    chat_id = update.message.chat_id
    if chat_id in accounts:
        cookies = accounts[chat_id]
        balance = claim_xrp(cookies)
        if balance:
            update.message.reply_text(f"نجح  ال  جني {balance}  XRP! 🎉")
        else:
            update.message.reply_text("لم  تنجح  عملية  ال  جني.  يرجى  التحقق  من  الاتصال  بال  إنترنت  و  محاولة  ال  جني  مرة  أخرى  لاحقًا.")
    else:
        update.message.reply_text("لم  تتم  عملية  ال  دخول.  يرجى  التحقق  من  اسم  المُستخدم  و  كلمة  ال  مرور  و  محاولة  ال  دخول  مرة  أخرى  لاحقًا.")

# Function to handle the /add_account command
def add_account(update, context):
    chat_id = update.message.chat_id
    update.message.reply_text("أدخل  اسم  المُستخدم  و  كلمة  ال  مرور  ل  حساب  FaucetEarner  جديد  (مُنفصل ب  مسافة):")
    context.user_data['state'] = 'add_account_input'

# Function to handle the /withdraw command
def withdraw(update, context):
    chat_id = update.message.chat_id
    if chat_id in accounts:
        update.message.reply_text("أدخل  عنوان  محفظة  XRP  ل  ال  سحب  (مُنفصل ب  مسافة):")
        context.user_data['state'] = 'withdraw_input'
    else:
        update.message.reply_text("لم  تتم  عملية  ال  دخول.  يرجى  التحقق  من  اسم  المُستخدم  و  كلمة  ال  مرور  و  محاولة  ال  دخول  مرة  أخرى  لاحقًا.")

# Function to handle the /balance command
def balance(update, context):
    chat_id = update.message.chat_id
    if chat_id in accounts:
        cookies = accounts[chat_id]
        balance = get_balance(cookies)  # Add get_balance() function to retrieve balance
        if balance:
            update.message.reply_text(f"رصيدك الحالي هو: {balance}")
        else:
            update.message.reply_text("لم  تنجح  عملية  ال  جني.  يرجى  التحقق  من  الاتصال  بال  إنترنت  و  محاولة  ال  جني  مرة  أخرى  لاحقًا.")
    else:
        update.message.reply_text("لم  تتم  عملية  ال  دخول.  يرجى  التحقق  من  اسم  المُستخدم  و  كلمة  ال  مرور  و  محاولة  ال  دخول  مرة  أخرى  لاحقًا.")

# Function to handle the /auto_claim command
def auto_claim(update, context):
    chat_id = update.message.chat_id
    if chat_id in accounts:
        cookies = accounts[chat_id]
        if chat_id not in auto_claim_jobs:
            job = context.job_queue.run_repeating(claim_xrp, interval=47, context=cookies)
            auto_claim_jobs[chat_id] = job
            update.message.reply_text("تم  تفعيل  ال  جني  التلقائي.  سأقوم  ب  جني  XRP  لك  كل  47  ثانية.")
        else:
            update.message.reply_text("تم  تفعيل  ال  جني  التلقائي  لهذا  الحساب  من  قبل.")
    else:
        update.message.reply_text("لم  تتم  عملية  ال  دخول.  يرجى  التحقق  من  اسم  المُستخدم  و  كلمة  ال  مرور  و  محاولة  ال  دخول  مرة  أخرى  لاحقًا.")

# Function to handle button clicks
def button_click(update, context):
    query = update.callback_query
    chat_id = query.message.chat_id
    if query.data == "login":
        login(update, context)
    elif query.data == "claim":
        claim(update, context)
    elif query.data == "add_account":
        add_account(update, context)
    elif query.data == "withdraw":
        withdraw(update, context)
    elif query.data == "balance":
        balance(update, context)
    elif query.data == "auto_claim":
        auto_claim(update, context)

# Function to handle text input
def handle_text(update, context):
    chat_id = update.message.chat_id
    if context.user_data['state'] == 'login_input':
        email, password = update.message.text.split(' ')
        cookies = faucet_login(email, password)
        if cookies:
            update.message.reply_text("تم  ال  دخول  بنجاح! 🎉")
            accounts[chat_id] = cookies
            context.user_data['state'] = None
        else:
            update.message.reply_text("لم  تنجح  عملية  ال  دخول.  يرجى  التحقق  من  اسم  المُستخدم  و  كلمة  ال  مرور  و  محاولة  ال  دخول  مرة  أخرى  لاحقًا.")
    elif context.user_data['state'] == 'add_account_input':
        email, password = update.message.text.split(' ')
        cookies = faucet_login(email, password)
        if cookies:
            accounts[chat_id] = cookies
            update.message.reply_text("تم  إضافة  الحساب  بنجاح! 🎉")
            context.user_data['state'] = None
        else:
            update.message.reply_text("لم  تنجح  عملية  ال  دخول.  يرجى  التحقق  من  اسم  المُستخدم  و  كلمة  ال  مرور  و  محاولة  ال  دخول  مرة  أخرى  لاحقًا.")
    elif context.user_data['state'] == 'withdraw_input':
        # Add code to handle withdrawal using cookies and the provided XRP address
        update.message.reply_text("تم  إرسال  طلب  ال  سحب.  يرجى  ال  ل  انتظار  التأكيد.")
        context.user_data['state'] = None

# Function to get the balance of an account
def get_balance(cookies):
    # Add code to retrieve balance from FaucetEarner using cookies
    return None  # Replace with actual balance retrieval logic

# Initialize the bot
updater = Updater(BOT_TOKEN, use_context=True)

# Add handlers for commands
dispatcher = updater.dispatcher
dispatcher.add_handler(CommandHandler("start", start))
dispatcher.add_handler(CommandHandler("login", login))
dispatcher.add_handler(CommandHandler("claim", claim))
dispatcher.add_handler(CommandHandler("add_account", add_account))
dispatcher.add_handler(CommandHandler("withdraw", withdraw))
dispatcher.add_handler(CommandHandler("balance", balance))
dispatcher.add_handler(CommandHandler("auto_claim", auto_claim))

# Add handler for button clicks
dispatcher.add_handler(CallbackQueryHandler(button_click))

# Add handler for text input
dispatcher.add_handler(MessageHandler(Filters.text, handle_text))

# Start the bot
updater.start_polling()

# Run the bot until you press Ctrl-C or the process receives SIGINT,
# SIGTERM or SIGABRT. This should be used most of the time, since
# start_polling() is non-blocking and will stop the bot gracefully.
updater.idle()
