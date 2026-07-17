import os
import threading
import telebot
import google.generativeai as genai
from flask import Flask

# Flask সেটআপ (যাতে Render একটি অ্যাক্টিভ পোর্ট পায়)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    # Render নিজে থেকেই একটি PORT এনভায়রনমেন্ট ভেরিয়েবল পাঠায়
    # পোর্ট না পেলে ডিফোল্ট হিসেবে 8080 ব্যবহার করবে
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
        print(f"Error: {e}")
        bot.reply_to(message, "দুঃখিত, একটু সমস্যা হয়েছে। আবার চেষ্টা করুন।")

if __name__ == "__main__":
    # Flask সার্ভারটি আলাদা থ্রেডে ব্যাকগ্রাউন্ডে স্টার্ট করা হচ্ছে
    threading.Thread(target=run_flask, daemon=True).start()
    
    # টেলিগ্রাম বট স্টার্ট করা হচ্ছে
    bot.infinity_polling()
