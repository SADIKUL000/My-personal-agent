import os
import threading
import telebot
import google.generativeai as genai
from flask import Flask

# Render-এর পোর্ট পোর্ট বাইন্ডিং সমস্যা সমাধানের জন্য Flask সেটআপ
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is running!"

def run_flask():
    # Render নিজে থেকেই একটি PORT পরিবেশ ভেরিয়েবল দেয়, না থাকলে 8080 ব্যবহার করবে
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# টোকেন ও এপিআই কি সেটআপ
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@bot.message_handler(func=lambda message: True)
def reply_to_user(message):
    try:
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "দুঃখিত, একটু সমস্যা হয়েছে। আবার চেষ্টা করুন।")

if __name__ == "__main__":
    # Flask সার্ভারটি আলাদা থ্রেডে ব্যাকগ্রাউন্ডে চালু করা হচ্ছে
    threading.Thread(target=run_flask).start()
    
    # টেলিগ্রাম বট চালু করা হচ্ছে
    bot.infinity_polling()
