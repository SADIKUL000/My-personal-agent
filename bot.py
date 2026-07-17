import os
import threading
import telebot
from groq import Groq
from flask import Flask

# Flask সেটআপ (Render-এর পোর্ট সচল রাখার জন্য)
app = Flask(__name__)

@app.route('/')
def home():
    return "Bot is alive and running with Groq!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# এনভায়রনমেন্ট ভ্যারিয়েবল থেকে টোকেন সংগ্রহ
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)

# Groq ক্লায়েন্ট ইনিশিয়েট করা
client = Groq(api_key=GROQ_API_KEY)

@bot.message_handler(func=lambda message: True)
def reply_to_user(message):
    try:
        # Groq API ব্যবহার করে Llama 3.1 মডেল কল করা
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {
                    "role": "user",
                    "content": message.text
                }
            ],
            temperature=0.7,
            max_tokens=1024,
        )
        
        # এআই এর উত্তর পাঠানো
        bot.reply_to(message, completion.choices[0].message.content)
        
    except Exception as e:
        error_message = f"⚠️ দুঃখিত, Groq API-তে সমস্যা হয়েছে।\n\nআসল এররটি হলো:\n`{str(e)}`"
        bot.reply_to(message, error_message, parse_mode="Markdown")

if __name__ == "__main__":
    # Flask ব্যাকগ্রাউন্ড থ্রেডে রান করা
    threading.Thread(target=run_flask, daemon=True).start()
    # টেলিগ্রাম বটের পোলিং শুরু
    bot.infinity_polling()
