import os
import threading
import telebot
from groq import Groq
from flask import Flask

# Flask সেটআপ (Render-এর জন্য)
app = Flask(__name__)

@app.route('/')
def home():
    return "Master AI OS Router is Active!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# টোকেন ও এপিআই কি সেটআপ
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# --- ১. স্পেশালাইজড এজেন্টদের ডামি ফাংশন (পরবর্তীতে এখানে আসল কোড বসবে) ---
def handle_personal_task(message):
    return "🎯 [Personal Agent]: আমি আপনার ক্যালেন্ডার, টু-ডু বা পার্সোনাল ফাইন্যান্স ম্যানেজ করতে পারি। (এই এজেন্টটি এখনো ডেভলপমেন্টে আছে)"

def handle_workplace_task(message):
    return "👟 [Workplace Agent]: আমি আপনার জুতো তৈরির Consumption, BOM Validation এবং Sample QA দেখতে পারি। (এই এজেন্টটি এখনো ডেভলপমেন্টে আছে)"

def handle_knowledge_base(message):
    return "📚 [Knowledge Base Agent]: আমি Decathlon SOP, কোম্পানির নিয়ম এবং ম্যাটেরিয়াল লাইব্রেরি চেক করতে পারি। (এই এজেন্টটি এখনো ডেভলপমেন্টে আছে)"


# --- ২. মাস্টার এজেন্টের প্রম্পট (Router Logic) ---
MASTER_ROUTER_PROMPT = """
You are the "Master AI OS Router" for a Personal AI Operating System. 
Your only job is to analyze the user's input and classify it into exactly ONE of the three categories:
1. PERSONAL
2. WORKPLACE
3. KNOWLEDGE_BASE

Guidelines for classification:
- PERSONAL: Use this if the user talks about daily routines, personal reminders, personal finance, scheduling, personal notes, or private emails.
- WORKPLACE: Use this if the user mentions operational footwear tasks like: BOM making, BOM validation, consumption calculation, leather yield, sample validation check, fit reports, or manufacturing tasks.
- KNOWLEDGE_BASE: Use this if the user asks about specific guidelines, documentations, or references like: Decathlon SOPs, company rules, material library specifications, or templates.

CRITICAL: Your response must contain ONLY one word from these three options: 'PERSONAL', 'WORKPLACE', or 'KNOWLEDGE_BASE'. Do not add any punctuation, intro, or explanation.
"""

# --- ৩. মূল মেসেজ হ্যান্ডলার ---
@bot.message_handler(func=lambda message: True)
def master_routing_agent(message):
    user_input = message.text
    
    try:
        # মাস্টার এজেন্ট সিদ্ধান্ত নিচ্ছে কোন ক্যাটাগরিতে পড়বে
        routing_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": MASTER_ROUTER_PROMPT},
                {"role": "user", "content": user_input}
            ],
            temperature=0.0, # তাপমাত্রা ০ রাখা হয়েছে যাতে রাউটিং নিখুঁত হয় এবং উল্টোপাল্টা উত্তর না দেয়
            max_tokens=10
        )
        
        decision = routing_completion.choices[0].message.content.strip().upper()
        
        # সিদ্ধান্ত অনুযায়ী সঠিক এজেন্টের ফাংশন কল করা হচ্ছে
        if "PERSONAL" in decision:
            agent_reply = handle_personal_task(user_input)
            response_text = f"🤖 **Master Agent Router:** এই কাজটি **Personal Tasks** এর আওতাভুক্ত।\n\n{agent_reply}"
            
        elif "WORKPLACE" in decision:
            agent_reply = handle_workplace_task(user_input)
            response_text = f"🤖 **Master Agent Router:** এই কাজটি **Workplace Tasks** এর আওতাভুক্ত।\n\n{agent_reply}"
            
        elif "KNOWLEDGE_BASE" in decision:
            agent_reply = handle_knowledge_base(user_input)
            response_text = f"🤖 **Master Agent Router:** এই কাজটি **Knowledge Base** এর আওতাভুক্ত।\n\n{agent_reply}"
            
        else:
            response_text = "⚠️ মাস্টার এজেন্ট কাজটি ক্যাটাগরাইজ করতে পারেনি। অনুগ্রহ করে স্পষ্ট করে লিখুন।"

        bot.reply_to(message, response_text, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"⚠️ রাউটিং এরর: `{str(e)}`", parse_mode="Markdown")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
