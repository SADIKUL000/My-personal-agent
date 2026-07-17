import os
import threading
import telebot
from google import genai
from flask import Flask

# Flask সেটআপ
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

# Gemini Client সেটআপ
client = genai.Client(api_key=GEMINI_API_KEY)

@bot.message_handler(func=lambda message: True)
def reply_to_user(message):
    try:
        # কোনো স্পেসিফিক ভার্সন ছাড়াই নতুনদের জন্য গুগলের ডিফল্ট ফ্রি মডেল কল করা
        response = client.models.generate_content(
            model='gemini-2.5-flash', 
            contents=message.text,
        )
        bot.reply_to(message, response.text)
    except Exception as e:
        # যদি ওপরের মডেলে তাও সমস্যা করে, তবে এটি অটোমেটিক ব্যাকআপ ২.০ মডেলে ট্রাই করবে
        try:
            response = client.models.generate_content(
                model='gemini-2.0-flash',
                contents=message.text,
            )
            bot.reply_to(message, response.text)
        except Exception as backup_error:
            error_message = f"⚠️ দুঃখিত, জেমিনি এপিআই-তে সমস্যা হয়েছে।\n\nআসল এররটি হলো:\n`{str(backup_error)}`"
            bot.reply_to(message, error_message, parse_mode="Markdown")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
