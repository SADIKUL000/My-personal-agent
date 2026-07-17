import os
import sqlite3
import threading
import telebot
from groq import Groq
from flask import Flask

# ডাটাবেস সেটআপ
conn = sqlite3.connect('assistant.db', check_same_thread=False)
cursor = conn.cursor()
cursor.execute('CREATE TABLE IF NOT EXISTS memory (user_id INTEGER, role TEXT, content TEXT)')
cursor.execute('CREATE TABLE IF NOT EXISTS tasks (user_id INTEGER, task TEXT, status TEXT)')
conn.commit()

# Flask & Bot Setup
app = Flask(__name__)
bot = telebot.TeleBot(os.environ.get('TELEGRAM_TOKEN'))
client = Groq(api_key=os.environ.get('GROQ_API_KEY'))

# সিস্টেম প্রম্পট (এটি অ্যাসিস্ট্যান্টের চরিত্র ঠিক করে)
SYSTEM_PROMPT = """
You are a proactive personal assistant. You remember user tasks, help with planning, and keep track of daily goals. 
If the user asks to save a task, confirm it. Always keep a professional yet friendly tone.
"""

def get_history(user_id):
    cursor.execute('SELECT role, content FROM memory WHERE user_id = ?', (user_id,))
    return [{"role": r, "content": c} for r, c in cursor.fetchall()]

@bot.message_handler(commands=['todo'])
def add_task(message):
    task = message.text.replace('/todo', '').strip()
    if task:
        cursor.execute('INSERT INTO tasks VALUES (?, ?, ?)', (message.chat.id, task, 'pending'))
        conn.commit()
        bot.reply_to(message, f"✅ টাস্ক সেভ করা হয়েছে: {task}")
    else:
        bot.reply_to(message, "কি কাজ যোগ করতে চান? লিখুন: /todo [কাজের নাম]")

@bot.message_handler(commands=['tasks'])
def show_tasks(message):
    cursor.execute('SELECT task FROM tasks WHERE user_id = ? AND status = "pending"', (message.chat.id,))
    tasks = cursor.fetchall()
    if tasks:
        task_list = "\n".join([f"- {t[0]}" for t in tasks])
        bot.reply_to(message, f"আপনার কাজের তালিকা:\n{task_list}")
    else:
        bot.reply_to(message, "আপনার কোনো পেন্ডিং কাজ নেই!")

@bot.message_handler(func=lambda message: True)
def chat(message):
    user_id = message.chat.id
    history = get_history(user_id)
    history.append({"role": "user", "content": message.text})
    
    # Groq-এ পাঠানো
    messages = [{"role": "system", "content": SYSTEM_PROMPT}] + history
    completion = client.chat.completions.create(model="llama-3.1-8b-instant", messages=messages)
    response = completion.choices[0].message.content
    
    # স্মৃতিতে সেভ করা
    cursor.execute('INSERT INTO memory VALUES (?, ?, ?)', (user_id, "user", message.text))
    cursor.execute('INSERT INTO memory VALUES (?, ?, ?)', (user_id, "assistant", response))
    conn.commit()
    
    bot.reply_to(message, response)

# (এখানে Flask এবং polling কোড আগের মতো থাকবে)
