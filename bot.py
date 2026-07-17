import os
import threading
import requests
import telebot
from groq import Groq
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Personal AI OS with Footwear Backward Planner is Active!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

# এনভায়রনমেন্ট ভ্যারিয়েবল সেটআপ
TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# --- 🎯 ১. স্পেশালাইজড এজেন্ট: FOOTWEAR 80/20 PLANNER AGENT ---
PLANNER_SYSTEM_PROMPT = """
You are the "Footwear Production 80/20 Planner". Your job is to act as a highly experienced Production Planning & Control (PPC) Manager for footwear manufacturing.

You will receive lists of tasks which include Running Tasks (Today's Deadlines) and Overdue Tasks from the factory's backward planning spreadsheet. 
Your core responsibility is to apply the Pareto Principle (80/20 Rule):
1. Extract the top 20% high-impact tasks that will prevent production line stoppage or sample delivery delays (e.g., BOM Validation, Consumption checks, Sample QA, Decathlon SOP compliance).
2. De-prioritize the remaining 80% non-urgent administrative clutter.
3. Generate a bulletproof, time-blocked action plan for the user in a clean Markdown table format.

Tone: Professional, highly focused, industrial-grade, and action-oriented.
"""

def handle_80_20_planner(user_input):
    try:
        completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": PLANNER_SYSTEM_PROMPT},
                {"role": "user", "content": f"Analyze my current footwear planning status and give me the 20% core focus and daily plan: \n\n{user_input}"}
            ],
            temperature=0.3,
            max_tokens=1500
        )
        return completion.choices[0].message.content
    except Exception as e:
        return f"⚠️ Planner Agent প্রসেস করতে পারেনি। এরর: {str(e)}"

# --- ⚙️ ২. অন্য এজেন্টদের ডামি ফাংশন (ভবিষ্যতের জন্য) ---
def handle_workplace_execution(message):
    return "👟 [Workplace Execution Agent]: (BOM Creation / Consumption ক্যালকুলেশন অটোমেশনের জন্য এটি পরবর্তী ধাপে তৈরি হবে)।"

def handle_knowledge_base(message):
    return "📚 [Knowledge Base Agent]: (Decathlon SOP / Material Library এর সাথে কানেক্ট করার জন্য এটি তৈরি হবে)।"


# --- 🧠 ৩. মাস্টার এজেন্টের প্রম্পট (Router Logic) ---
MASTER_ROUTER_PROMPT = """
You are the "Master AI OS Router". Your job is to classify the incoming message into exactly ONE of the three categories:
1. PLANNER
2. WORKPLACE_EXECUTION
3. KNOWLEDGE_BASE

Guidelines:
- PLANNER: Choose this if the message contains lists of tasks, daily schedules, alerts about running/overdue tasks, updates from the Google Sheet planner, or general routine building.
- WORKPLACE_EXECUTION: Choose this if the user wants to execute specific technical footwear calculations right now (e.g., 'Validate this BOM text', 'Calculate wastage from leather sheet').
- KNOWLEDGE_BASE: Choose this if the message is asking for references, Decathlon SOP guidelines, or material standard specifications.

CRITICAL: Your response must be ONLY one word: 'PLANNER', 'WORKPLACE_EXECUTION', or 'KNOWLEDGE_BASE'. Do not add any punctuation or explanation.
"""

# --- 🚀 ৪. মূল মেসেজ হ্যান্ডলার ---
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
            temperature=0.0,
            max_tokens=10
        )
        
        decision = routing_completion.choices[0].message.content.strip().upper()
        
        # সিদ্ধান্ত অনুযায়ী সঠিক এজেন্টের ফাংশน কল করা হচ্ছে
        if "PLANNER" in decision:
            planner_output = handle_80_20_planner(user_input)
            response_text = f"📊 **[80/20 Footwear Planner Agent]**\n\n{planner_output}"
            
        elif "WORKPLACE_EXECUTION" in decision:
            agent_reply = handle_workplace_execution(user_input)
            response_text = f"🤖 **Master Router:** এই কাজটি **Workplace Execution** এর আওতাভুক্ত।\n\n{agent_reply}"
            
        elif "KNOWLEDGE_BASE" in decision:
            agent_reply = handle_knowledge_base(user_input)
            response_text = f"🤖 **Master Router:** এই কাজটি **Knowledge Base** এর আওতাভুক্ত।\n\n{agent_reply}"
            
        else:
            response_text = "⚠️ মাস্টার এজেন্ট কাজটি ক্যাটাগরাইজ করতে পারেনি। অনুগ্রহ করে স্পষ্ট করে লিখুন।"

        bot.reply_to(message, response_text, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"⚠️ রাউটিং এরর: `{str(e)}`", parse_mode="Markdown")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
