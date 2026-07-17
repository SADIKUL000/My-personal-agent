import os
import threading
from datetime import datetime, timedelta
import telebot
from groq import Groq
from flask import Flask

app = Flask(__name__)

@app.route('/')
def home():
    return "Footwear AI OS Engine is Live!"

def run_flask():
    port = int(os.environ.get("PORT", 8080))
    app.run(host="0.0.0.0", port=port)

TELEGRAM_TOKEN = os.environ.get('TELEGRAM_TOKEN')
GROQ_API_KEY = os.environ.get('GROQ_API_KEY')

bot = telebot.TeleBot(TELEGRAM_TOKEN)
client = Groq(api_key=GROQ_API_KEY)

# --- 🎯 ১. স্পেশালাইজড এজেন্ট: REAL FOOTWEAR BACKWARD PLANNER ENGINE ---
# স্ক্রিনশট অনুযায়ী ফিক্সড ডে-র মাস্টার ডিকশনারি (ক্যালকুলেশন সিকোয়েন্স ঠিক রাখার জন্য)
TASK_LEAD_TIMES = [
    ("Go ship", 0), # Base XF Date
    ("Go prod", -27),
    ("Go Indus: Passed", -29),
    ("Go Indus: Start", -50),
    ("CFM Sample: Validation", -50),
    ("CFM Sample: ETD", -64),
    ("CFM Sample: Start", -72),
    ("F&R sample:Validation", -72),
    ("F&R sample: End", -93),
    ("F&R sample: Start", -100),
    ("F&R Mold: Validation", -100),
    ("F&R Mold: ETA", -107),
    ("F&R Mold: Order", -177),
    ("Proto: Validation", -177),
    ("Proto: End", -184),
    ("Proto: Start", -191),
    ("Bulk Material: ETA", -198),
    ("Bulk Material: Order", -288),
    ("BOM: DKT Validation", -295),
    ("Sample Mold: Validation", -295),
    ("Sample Mold: ETA", -302),
    ("Sample Mold: Order", -344),
    ("Sample Received: Raw Materials", -351),
    ("Sample Order: Raw Materials", -381),
    ("Consumption, CBD (sharing)", -381),
    ("Project Initiation", -381)
]

def generate_exact_backward_plan(project_name, xf_date_str):
    try:
        # ডেট ফরম্যাট চেকিং (YYYY-MM-DD)
        base_date = datetime.strptime(xf_date_str.strip(), "%Y-%m-%d")
    except ValueError:
        return "⚠️ ডেট ফরম্যাট সঠিক নয়! দয়া করে এভাবে লিখুন: `YYYY-MM-DD` (যেমন: `2027-04-22`)"

    table_rows = []
    table_rows.append(f"### 📊 Backward Plan for: **{project_name.upper()}**")
    table_rows.append(f"📅 **Base XF Date:** {xf_date_str}\n")
    table_rows.append("| SL | Task Name | Target Date | WK No | Status |")
    table_rows.append("|---|---|---|---|---|")

    for idx, (task, days) in enumerate(TASK_LEAD_TIMES, start=1):
        target_date = base_date + timedelta(days=days)
        date_str = target_date.strftime("%m/%d/%Y")
        week_num = target_date.isocalendar()[1]
        table_rows.append(f"| {idx} | {task} | {date_str} | {week_num} | Pending 🕒 |")

    # হাই-লেভেল প্ল্যানিং সামারি দেওয়ার জন্য Llama 3.1 কে কল করা
    raw_table = "\n".join(table_rows)
    try:
        summary_completion = client.chat.completions.create(
            model="llama-3.1-8b-instant",
            messages=[
                {"role": "system", "content": "You are a Footwear Production Planner. Analyze the provided timeline table and highlight 3 critical paths (like Mold Order or Bulk Material Order Deadlines) with quick actionable tips. Keep it extremely brief and professional."},
                {"role": "user", "content": raw_table}
            ],
            temperature=0.3,
            max_tokens=500
        )
        ai_summary = summary_completion.choices[0].message.content
    except:
        ai_summary = "*(Summary could not be generated, but your chart is ready below)*"

    return f"{raw_table}\n\n### 🧠 Planner Agent 80/20 Insights:\n{ai_summary}"


# --- 🧠 ২. মাস্টার এজেন্টের প্রম্পট (Router Logic) ---
MASTER_ROUTER_PROMPT = """
You are the "Master AI OS Router". Your only job is to classify the user's input into exactly ONE category:
1. PLANNER (If they mention 'new project', 'new article', 'backward plan', 'XF Date', 'style plan', or want to calculate a timeline schedule).
2. WORKPLACE_EXECUTION (If they want to audit a raw BOM sheet text, check material consumption formulas, or write code).
3. KNOWLEDGE_BASE (If they ask for Decathlon SOP manuals, file reference, or company rules).

CRITICAL: Output ONLY the word 'PLANNER', 'WORKPLACE_EXECUTION', or 'KNOWLEDGE_BASE'. Do not add any punctuation or intro.
"""

# --- 🚀 ৩. মূল মেসেজ হ্যান্ডলার ---
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
        
        # ১. প্ল্যানার এজেন্ট এক্টিভেশন লজিক
        if "PLANNER" in decision:
            # ইউজার ইনপুট থেকে সহজ উপায়ে প্রজেক্ট নাম এবং ডেট আলাদা করার প্রম্পট
            extraction_prompt = (
                f"Extract the Project/Article Name and the XF Date (in YYYY-MM-DD format) from this text: '{user_input}'. "
                "Respond in exactly this format: Name | YYYY-MM-DD. Nothing else."
            )
            ext_completion = client.chat.completions.create(
                model="llama-3.1-8b-instant",
                messages=[{"role": "user", "content": extraction_prompt}],
                temperature=0.0
            )
            
            extracted_data = ext_completion.choices[0].message.content.strip()
            
            if "|" in extracted_data:
                proj_name, xf_date = extracted_data.split("|")
                response_text = generate_exact_backward_plan(proj_name.strip(), xf_date.strip())
            else:
                response_text = "⚠️ আমি প্রজেক্টের নাম বা XF Date সঠিকভাবে বুঝতে পারছি না। দয়া করে এভাবে লিখুন:\n`New Project: Sneaker-01, XF Date: 2027-04-22`"
            
        elif "WORKPLACE_EXECUTION" in decision:
            response_text = "🤖 **Master Router:** [Workplace Execution Agent] এর কাজ পরবর্তী ধাপে ডেভেলপ করা হবে।"
            
        elif "KNOWLEDGE_BASE" in decision:
            response_text = "🤖 **Master Router:** [Knowledge Base Agent] এর কাজ পরবর্তী ধাপে ডেভেলপ করা হবে।"
            
        else:
            response_text = "⚠️ মাস্টার এজেন্ট কাজটি ক্যাটাগরাইজ করতে পারেনি। অনুগ্রহ করে স্পষ্ট করে লিখুন।"

        bot.reply_to(message, response_text, parse_mode="Markdown")

    except Exception as e:
        bot.reply_to(message, f"⚠️ রাউটিং এরর: `{str(e)}`", parse_mode="Markdown")

if __name__ == "__main__":
    threading.Thread(target=run_flask, daemon=True).start()
    bot.infinity_polling()
