import os
import telebot
import google.generativeai as genai

# টোকেন ও এপিআই কি সেটআপ (যা ক্লাউড এনভায়রনমেন্ট থেকে আসবে)
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GEMINI_API_KEY = os.environ.get('GEMINI_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
genai.configure(api_key=GEMINI_API_KEY)
model = genai.GenerativeModel('gemini-pro')

@bot.message_handler(func=lambda message: True)
def reply_to_user(message):
    try:
        # ব্যবহারকারীর মেসেজ Gemini এআই-এর কাছে পাঠানো
        response = model.generate_content(message.text)
        bot.reply_to(message, response.text)
    except Exception as e:
        bot.reply_to(message, "দুঃখিত, একটু সমস্যা হয়েছে। আবার চেষ্টা করুন।")

# বট লাইভ রাখা
bot.infinity_polling()
