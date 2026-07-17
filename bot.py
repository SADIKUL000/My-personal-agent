import os
import threading
import telebot
from google import genai
from flask import Flask

# Flask সেটআপ (Render-এর পোর্টের জন্য)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# টোকেন ও এপিআই কি সেটআপ
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# নতুন Gemini Client সেটআপ
client = genai.Client(api_key=GEMINI_API_KEY)

@bot.message_handler(func=lambda message: True)
def reply_to_user(message):
    try:
        # নতুন লাইব্রেরির নিয়ম অনুযায়ী মেসেজ পাঠানো
        response = client.models.generate_content(
            model='gemini-2.5-flash',
            contents=message.text,
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        print(f"Error: {e}")
        bot.reply_to(message, "দুঃখিত, একটু সমস্যা হয়েছে। আবার চেষ্টা করুন।")

if __name__ == "__main__":
    # Flask ব্যাকগ্রাউন্ডে চালু করা
    threading.Thread(target=run_flask, daemon=True).start()
    
    # টেলিগ্রাম বট চালু করা
    bot.infinity_polling()
