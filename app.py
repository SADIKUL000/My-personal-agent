import streamlit as st
import os
from datetime import datetime, timedelta
from groq import Groq

# পেজ কনফিগারেশন (মোবাইল ও পিসির স্ক্রিনে পারফেক্টলি ফিট হওয়ার জন্য)
st.set_page_config(page_title="Footwear AI OS", layout="wide")

# Groq ক্লায়েন্ট সেটআপ
GROQ_API_KEY = os.environ.get('GROQ_API_KEY', '')
if GROQ_API_KEY:
    client = Groq(api_key=GROQ_API_KEY)
else:
    st.error("⚠️ GROQ_API_KEY খুঁজে পাওয়া যায়নি! অনুগ্রহ করে সেটিংস চেক করুন।")

# স্ক্রিনশট অনুযায়ী ফিক্সড ডে-র ব্যাকওয়ার্ড প্ল্যানিং ডেটা
TASK_LEAD_TIMES = [
    ("Go ship", 0),
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

# --- UI ডিজাইন ---
st.title("👟 Footwear Personal AI Operating System")
st.write("আপনার পার্সোনাল এবং ওয়ার্কপ্লেস অটোমেশন হাব।")

# সাইডবার মেনু (এজেন্ট সিলেক্টর)
st.sidebar.title("🤖 Master AI Router")
selected_agent = st.sidebar.radio(
    "কোন এজেন্ট ব্যবহার করতে চান?",
    ["📊 80/20 Planner Agent", "⚙️ Workplace Execution", "📚 Knowledge Base"]
)

# --- ১. প্ল্যানার এজেন্ট ইন্টারফেস ---
if selected_agent == "📊 80/20 Planner Agent":
    st.header("📋 Backward Planning Engine")
    
    # ইনপুট ফিল্ডস
    col1, col2 = st.columns(2)
    with col1:
        project_name = st.text_input("Article / Style Name:", placeholder="e.g., Decathlon-Sneaker-X")
    with col2:
        xf_date = st.date_input("Proposed XF Date (Shipment Date):", datetime.now() + timedelta(days=180))
        
    if st.button("Generate Backward Plan 🚀"):
        if project_name:
            # ডেট ও টেবিল ক্যালকুলেশন
            base_date = datetime.combine(xf_date, datetime.min.time())
            plan_data = []
            
            for idx, (task, days) in enumerate(TASK_LEAD_TIMES, start=1):
                target_date = base_date + timedelta(days=days)
                plan_data.append({
                    "SL": idx,
                    "Task Name": task,
                    "Target Date": target_date.strftime("%m/%d/%Y"),
                    "WK No": target_date.isocalendar()[1],
                    "Status": "Pending 🕒"
                })
            
            # টেবিল ডিসপ্লে (স্ক্রিনশটের মতো নিখুঁত ভিউ)
            st.subheader(f"📊 Plan for: {project_name.upper()}")
            st.dataframe(plan_data, use_container_width=True) # use_container_width রেসপনসিভ করে দেয়
            
            # AI Insights
            st.subheader("🧠 Planner Agent 80/20 Insights")
            with st.spinner("AI অ্যানালাইসিস করছে..."):
                try:
                    summary_completion = client.chat.completions.create(
                        model="llama-3.1-8b-instant",
                        messages=[
                            {"role": "system", "content": "You are a Footwear Production Planner. Highlight 3 critical deadlines from the calculated steps with brief actionable factory advice."},
                            {"role": "user", "content": str(plan_data)}
                        ],
                        temperature=0.3
                    )
                    st.info(summary_completion.choices[0].message.content)
                except Exception as e:
                    st.error(f"AI ইনসাইট জেনারেট করা যায়নি। এরর: {e}")
        else:
            st.warning("⚠️ দয়া করে আর্টিকেলের নাম লিখুন।")

# --- ২. ওয়ার্কপ্লেস এবং ৩. নলেজ বেস (ভবিষ্যতের জন্য ফাকা রাখা হলো) ---
elif selected_agent == "⚙️ Workplace Execution":
    st.header("⚙️ Workplace Execution Agent")
    st.info("এখানে পরবর্তী ধাপে আপনার BOM Validation এবং Leather Consumption ক্যালকুলেটর যুক্ত হবে।")
    
elif selected_agent == "📚 Knowledge Base":
    st.header("📚 Knowledge Base Agent")
    st.info("এখানে আপনার Decathlon SOP এবং ফ্যাক্টরি রুলস আপলোড করার অপশন থাকবে।")
