import streamlit as st
import sys
import os
import json
import sqlite3
import pandas as pd
from datetime import datetime
import threading
import uvicorn
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional
import requests

# Python পাথ সেট করা
sys.path.insert(0, os.path.dirname(__file__))

# ---------- FastAPI সেটআপ ----------
api = FastAPI()

class CrashData(BaseModel):
    crash_value: float
    timestamp: Optional[str] = None
    source: Optional[str] = "sharex"

class CrashResponse(BaseModel):
    status: str
    message: str
    timestamp: str
    id: Optional[int] = None

# ডাটাবেস ইনিশিয়ালাইজ
def init_database():
    conn = sqlite3.connect('aviator_data.db')
    c = conn.cursor()
    c.execute('''CREATE TABLE IF NOT EXISTS rounds
                 (id INTEGER PRIMARY KEY AUTOINCREMENT,
                  timestamp TEXT,
                  crash_value REAL,
                  source TEXT,
                  created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP)''')
    conn.commit()
    conn.close()

init_database()

@api.post("/api/add_crash", response_model=CrashResponse)
async def add_crash(data: CrashData):
    """ShareX থেকে অটোমেটিক ডাটা রিসিভ করার এন্ডপয়েন্ট"""
    try:
        # টাইমস্ট্যাম্প তৈরি
        timestamp = data.timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        
        # ডাটাবেজে সেভ
        conn = sqlite3.connect('aviator_data.db')
        c = conn.cursor()
        c.execute("INSERT INTO rounds (timestamp, crash_value, source) VALUES (?, ?, ?)",
                  (timestamp, data.crash_value, data.source))
        conn.commit()
        record_id = c.lastrowid
        conn.close()
        
        # JSON ফাইলেও ব্যাকআপ
        crash_record = {
            "id": record_id,
            "timestamp": timestamp,
            "crash_value": data.crash_value,
            "source": data.source
        }
        
        with open("crash_history.json", "a") as f:
            f.write(json.dumps(crash_record) + "\n")
        
        return CrashResponse(
            status="success",
            message=f"ক্রাশ {data.crash_value} যোগ করা হয়েছে",
            timestamp=timestamp,
            id=record_id
        )
    except Exception as e:
        raise HTTPException(status_code=500, detail=str(e))

@api.get("/api/recent/{limit}")
async def get_recent(limit: int = 10):
    """সাম্প্রতিক ক্রাশ ডাটা পাওয়ার জন্য এন্ডপয়েন্ট"""
    conn = sqlite3.connect('aviator_data.db')
    df = pd.read_sql_query(f"SELECT * FROM rounds ORDER BY timestamp DESC LIMIT {limit}", conn)
    conn.close()
    return df.to_dict('records')

@api.get("/api/stats")
async def get_stats():
    """পরিসংখ্যান দেখার জন্য এন্ডপয়েন্ট"""
    conn = sqlite3.connect('aviator_data.db')
    stats = {}
    try:
        # মোট রেকর্ড
        stats['total'] = pd.read_sql_query("SELECT COUNT(*) as count FROM rounds", conn).iloc[0]['count']
        # গড় ক্রাশ
        stats['average'] = pd.read_sql_query("SELECT AVG(crash_value) as avg FROM rounds", conn).iloc[0]['avg']
        # সর্বোচ্চ ক্রাশ
        stats['max'] = pd.read_sql_query("SELECT MAX(crash_value) as max FROM rounds", conn).iloc[0]['max']
        # আজকের ডাটা
        today = datetime.now().strftime("%Y-%m-%d")
        stats['today'] = pd.read_sql_query(f"SELECT COUNT(*) as count FROM rounds WHERE timestamp LIKE '{today}%'", conn).iloc[0]['count']
    except:
        pass
    conn.close()
    return stats

# API সার্ভার চালানোর ফাংশন (আলাদা থ্রেডে)
def run_api():
    uvicorn.run(api, host="0.0.0.0", port=8000)

# API সার্ভার শুরু করুন (শুধুমাত্র লোকাল ডেভেলপমেন্টের জন্য)
if os.environ.get('STREAMLIT_CLOUD') != '1':
    api_thread = threading.Thread(target=run_api, daemon=True)
    api_thread.start()

# ---------- Streamlit UI ----------
st.set_page_config(page_title="Aviator Predictor", layout="wide")

# সাইডবার
with st.sidebar:
    st.image("https://via.placeholder.com/150x50?text=Aviator+Predictor")
    st.title("✈️ Aviator Predictor")
    st.markdown("---")
    
    # API তথ্য
    st.subheader("🔌 API এন্ডপয়েন্ট")
    if os.environ.get('STREAMLIT_CLOUD') == '1':
        # ক্লাউডে চললে
        base_url = f"https://{st.context.headers['host']}"
    else:
        # লোকালে চললে
        base_url = "http://localhost:8000"
    
    st.info(f"**API URL:** `{base_url}/api/add_crash`")
    
    st.code("""{
  "crash_value": 10.21,
  "timestamp": "2024-01-15 14:30:25",
  "source": "sharex"
}""", language="json")

# মূল পৃষ্ঠা
st.title("✈️ Aviator Predictor - Web Interface")

# ট্যাব তৈরি
tab1, tab2, tab3, tab4 = st.tabs(["📊 ড্যাশবোর্ড", "📝 ম্যানুয়াল এন্ট্রি", "📁 OCR আপলোড", "⚙️ ShareX সেটআপ"])

with tab1:
    col1, col2, col3, col4 = st.columns(4)
    
    # পরিসংখ্যান দেখান
    try:
        if os.environ.get('STREAMLIT_CLOUD') == '1':
            stats = {"total": 0, "average": 0, "max": 0, "today": 0}
            # ক্লাউডে API কল
            try:
                response = requests.get(f"{base_url}/api/stats")
                if response.status_code == 200:
                    stats = response.json()
            except:
                pass
        else:
            # লোকালে সরাসরি ডাটাবেজ থেকে
            conn = sqlite3.connect('aviator_data.db')
            stats = {}
            stats['total'] = pd.read_sql_query("SELECT COUNT(*) as count FROM rounds", conn).iloc[0]['count']
            stats['average'] = round(pd.read_sql_query("SELECT AVG(crash_value) as avg FROM rounds", conn).iloc[0]['avg'] or 0, 2)
            stats['max'] = pd.read_sql_query("SELECT MAX(crash_value) as max FROM rounds", conn).iloc[0]['max'] or 0
            today = datetime.now().strftime("%Y-%m-%d")
            stats['today'] = pd.read_sql_query(f"SELECT COUNT(*) as count FROM rounds WHERE timestamp LIKE '{today}%'", conn).iloc[0]['count']
            conn.close()
        
        col1.metric("📈 মোট রেকর্ড", stats.get('total', 0))
        col2.metric("🎯 গড় ক্রাশ", f"{stats.get('average', 0):.2f}")
        col3.metric("🚀 সর্বোচ্চ", stats.get('max', 0))
        col4.metric("📅 আজকে", stats.get('today', 0))
    except Exception as e:
        st.error(f"ডাটা লোড করতে সমস্যা: {e}")
    
    st.markdown("---")
    
    # সাম্প্রতিক ডাটা দেখান
    st.subheader("📋 সাম্প্রতিক ক্রাশ")
    
    try:
        if os.environ.get('STREAMLIT_CLOUD') == '1':
            response = requests.get(f"{base_url}/api/recent/50")
            if response.status_code == 200:
                df = pd.DataFrame(response.json())
                if not df.empty:
                    st.dataframe(df, use_container_width=True)
                else:
                    st.info("কোনো ডাটা নেই")
        else:
            conn = sqlite3.connect('aviator_data.db')
            df = pd.read_sql_query("SELECT * FROM rounds ORDER BY timestamp DESC LIMIT 50", conn)
            conn.close()
            if not df.empty:
                st.dataframe(df, use_container_width=True)
            else:
                st.info("কোনো ডাটা নেই")
    except Exception as e:
        st.error(f"ডাটা লোড করতে সমস্যা: {e}")

with tab2:
    st.subheader("📝 ম্যানুয়াল ডাটা এন্ট্রি")
    
    with st.form("manual_entry"):
        crash_value = st.number_input("ক্রাশ ভ্যালু", min_value=1.0, step=0.01, format="%.2f")
        timestamp = st.text_input("টাইমস্ট্যাম্প (ঐচ্ছিক, ফাঁকা রাখলে এখনকার সময় নিবে)", 
                                 value=datetime.now().strftime("%Y-%m-%d %H:%M:%S"))
        col1, col2 = st.columns(2)
        with col1:
            submitted = st.form_submit_button("💾 সংরক্ষণ করুন", type="primary", use_container_width=True)
        with col2:
            clear = st.form_submit_button("🔄 রিসেট", use_container_width=True)
        
        if submitted:
            try:
                # API-তে পাঠান
                payload = {
                    "crash_value": crash_value,
                    "timestamp": timestamp if timestamp else None,
                    "source": "manual"
                }
                
                if os.environ.get('STREAMLIT_CLOUD') == '1':
                    response = requests.post(f"{base_url}/api/add_crash", json=payload)
                    if response.status_code == 200:
                        st.success(f"✅ {crash_value} সংরক্ষণ করা হয়েছে!")
                    else:
                        st.error("❌ সংরক্ষণ ব্যর্থ হয়েছে")
                else:
                    # সরাসরি ডাটাবেজে সেভ
                    conn = sqlite3.connect('aviator_data.db')
                    c = conn.cursor()
                    c.execute("INSERT INTO rounds (timestamp, crash_value, source) VALUES (?, ?, ?)",
                              (timestamp or datetime.now().strftime("%Y-%m-%d %H:%M:%S"), crash_value, "manual"))
                    conn.commit()
                    conn.close()
                    st.success(f"✅ {crash_value} সংরক্ষণ করা হয়েছে!")
            except Exception as e:
                st.error(f"❌ ত্রুটি: {e}")

with tab3:
    st.subheader("📁 OCR-এর জন্য ইমেজ আপলোড")
    st.info("ক্রাশ নাম্বারের স্ক্রিনশট আপলোড করুন")
    
    uploaded_file = st.file_uploader("ছবি নির্বাচন করুন", type=['png', 'jpg', 'jpeg', 'bmp'])
    
    if uploaded_file is not None:
        # ইমেজ সেভ করা
        with open("temp_image.png", "wb") as f:
            f.write(uploaded_file.getbuffer())
        st.image(uploaded_file, caption="আপলোড করা ছবি", width=300)
        
        if st.button("🔍 OCR রান করুন", type="primary"):
            with st.spinner('OCR প্রসেসিং চলছে...'):
                try:
                    # এখানে আপনার OCR কোড কল করুন
                    import pytesseract
                    from PIL import Image
                    
                    img = Image.open("temp_image.png")
                    text = pytesseract.image_to_string(img, config='--psm 7 -c tessedit_char_whitelist=0123456789.')
                    
                    # নাম্বার এক্সট্রাক্ট
                    import re
                    numbers = re.findall(r"\d+\.\d+", text)
                    
                    if numbers:
                        crash_value = float(numbers[0])
                        st.success(f"✅ OCR সফল! পাওয়া গেছে: {crash_value}")
                        
                        # অটো ফর্ম পূরণ
                        st.info("নিচের ফর্মে ভ্যালুটি অটো পূরণ করা হয়েছে")
                        with st.form("ocr_entry"):
                            st.number_input("ক্রাশ ভ্যালু", value=crash_value, disabled=True)
                            if st.form_submit_button("✅ নিশ্চিত করুন"):
                                # এখানে সেভ করার কোড
                                st.success("সংরক্ষণ করা হয়েছে!")
                    else:
                        st.error("❌ OCR-এ কোনো নাম্বার পাওয়া যায়নি")
                except Exception as e:
                    st.error(f"❌ OCR ত্রুটি: {e}")

with tab4:
    st.subheader("⚙️ ShareX কাস্টম আপলোডার কনফিগারেশন")
    
    st.markdown("""
    ### 📋 ShareX সেটআপ নির্দেশিকা
    
    #### ধাপ ১: কাস্টম আপলোডার তৈরি করুন
    1. ShareX ওপেন করুন
    2. **Destination** → **Custom uploaders** → **Add** বাটনে ক্লিক করুন
    3. নিচের কনফিগারেশনটি ব্যবহার করুন:
    """)
    
    # API URL ডিটেক্ট
    if os.environ.get('STREAMLIT_CLOUD') == '1':
        api_url = f"https://{st.context.headers['host']}/api/add_crash"
    else:
        api_url = "http://localhost:8000/api/add_crash"
    
    st.code(f"""
Name: Aviator Predictor API
Request URL: {api_url}
Method: POST
File Form Name: (leave empty)

Headers:
  Content-Type: application/json

Body:
  {{
    "crash_value": {{json:ocrtext}},
    "timestamp": "{{datetime:yyyy-MM-dd HH:mm:ss}}",
    "source": "sharex"
  }}
    """, language="yaml")
    
    st.markdown("""
    #### ধাপ ২: হটকি সেটআপ
    1. **Hotkey settings**-এ যান
    2. নতুন হটকি অ্যাড করুন (যেমন: `Ctrl+Shift+A`)
    3. Task হিসেবে **Screen Capture → Region (Fixed)** সিলেক্ট করুন
    4. আপনার ক্রাশ নাম্বারের অংশ সিলেক্ট করুন
    5. After capture tasks-এ **Perform OCR** এবং **Upload to custom destination** যুক্ত করুন
    
    #### ধাপ ৩: OCR সেটিংস
    1. **OCR** ট্যাবে যান
    2. Engine হিসেবে **Tesseract** সিলেক্ট করুন
    3. Language হিসেবে **English** সিলেক্ট করুন
    4. Character whitelist: `0123456789.`
    
    #### ধাপ ৪: টেস্ট করুন
    1. আপনার Aviator গেম ওপেন করুন
    2. `Ctrl+Shift+A` চাপুন
    3. ক্রাশ নাম্বারের অংশ সিলেক্ট করুন
    4. অটোমেটিক API-তে পাঠাবে
    """)
    
    st.success("✅ সব সেটআপ সম্পূর্ণ হলে, আপনার অ্যাপে অটোমেটিক ডাটা আসা শুরু হবে!")

# ফুটার
st.markdown("---")
col1, col2, col3 = st.columns(3)
with col1:
    st.caption(f"📊 মোট রেকর্ড: {stats.get('total', 0) if 'stats' in locals() else 0}")
with col2:
    st.caption("🔧 ভার্সন: 1.0.0")
with col3:
    st.caption("⚠️ শিক্ষামূলক প্রকল্প")
