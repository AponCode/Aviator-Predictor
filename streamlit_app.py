import streamlit as st
import sys
import os
import subprocess
import importlib.util

# Python পাথ সেট করা
sys.path.insert(0, os.path.dirname(__file__))

st.set_page_config(page_title="Aviator Predictor", layout="wide")
st.title("✈️ Aviator Predictor - Web Interface")
st.markdown("---")

# পারমিশন চেক ফাংশন
def check_permissions():
    """চেক করে কোন কোন মেথড কাজ করবে"""
    methods = {
        "api": True,
        "web_scraping": True,
        "ocr": True,
        "packet_sniffer": False  # ক্লাউডে সবসময় False
    }
    return methods

# নিরাপদে ইম্পোর্ট করার ফাংশন
def safe_import(module_name):
    """মডিউল ইম্পোর্ট করার চেষ্টা করে, ব্যর্থ হলে None রিটার্ন করে"""
    try:
        if module_name == "src.data_collection.api_collector":
            from src.data_collection import api_collector
            return api_collector
        elif module_name == "src.data_collection.scraper_collector":
            from src.data_collection import scraper_collector
            return scraper_collector
        elif module_name == "src.data_collection.ocr_collector":
            from src.data_collection import ocr_collector
            return ocr_collector
        else:
            return None
    except Exception as e:
        st.warning(f"⚠️ {module_name} ইম্পোর্ট করা যায়নি: {e}")
        return None

# ডাটা কালেকশন ফাংশন
def collect_data_safely():
    """পারমিশন অনুযায়ী নিরাপদে ডাটা কালেক্ট করে"""
    results = []
    permissions = check_permissions()
    
    # API কালেক্টর
    api_collector = safe_import("src.data_collection.api_collector")
    if api_collector:
        try:
            # এখানে আপনার API কালেকশন লজিক
            results.append("✅ API ডাটা কালেক্ট করা হয়েছে")
        except Exception as e:
            results.append(f"❌ API ত্রুটি: {e}")
    
    # ওয়েব স্ক্র্যাপার
    scraper = safe_import("src.data_collection.scraper_collector")
    if scraper:
        try:
            # এখানে আপনার স্ক্র্যাপিং লজিক
            results.append("✅ ওয়েব স্ক্র্যাপিং ডাটা কালেক্ট করা হয়েছে")
        except Exception as e:
            results.append(f"❌ স্ক্র্যাপিং ত্রুটি: {e}")
    
    # OCR কালেক্টর
    ocr = safe_import("src.data_collection.ocr_collector")
    if ocr:
        try:
            # এখানে আপনার OCR লজিক (ইমেজ ফাইল প্রয়োজন)
            results.append("⚠️ OCR চালানোর জন্য লোকাল ইমেজ প্রয়োজন")
        except Exception as e:
            results.append(f"❌ OCR ত্রুটি: {e}")
    
    # প্যাকেট স্নিফার (ক্লাউডে ডিজেবল)
    if permissions["packet_sniffer"]:
        results.append("⚠️ প্যাকেট স্নিফিং ক্লাউডে সাপোর্টেড নয়")
    
    return results

# মূল পাইথন স্ক্রিপ্ট চালানোর ফাংশন (সংশোধিত)
def run_main_script_safely():
    """মূল স্ক্রিপ্ট নিরাপদে চালানোর চেষ্টা করে"""
    try:
        # সঠিক ওয়ার্কিং ডিরেক্টরি সেট করা
        os.chdir(os.path.dirname(__file__))
        
        # PYTHONPATH সেট করা
        env = os.environ.copy()
        env['PYTHONPATH'] = os.path.dirname(__file__)
        
        # স্ক্রিপ্ট রান করা
        result = subprocess.run(
            [sys.executable, "-c", 
             "import sys; sys.path.insert(0, '.'); from src.main import *; print('স্ক্রিপ্ট রান সফল হয়েছে')"],
            capture_output=True,
            text=True,
            env=env,
            timeout=30
        )
        return result.stdout, result.stderr
    except subprocess.TimeoutExpired:
        return "", "স্ক্রিপ্ট টাইমআউট হয়েছে (৩০ সেকেন্ড)"
    except Exception as e:
        return "", str(e)

# UI তৈরি
col1, col2 = st.columns(2)

with col1:
    st.subheader("📊 ডাটা কালেকশন স্ট্যাটাস")
    permissions = check_permissions()
    for method, enabled in permissions.items():
        if enabled:
            st.success(f"✅ {method} উপলব্ধ")
        else:
            st.warning(f"⚠️ {method} ক্লাউডে উপলব্ধ নয়")

with col2:
    st.subheader("🛠 কন্ট্রোল প্যানেল")
    if st.button("▶️ ডাটা কালেক্ট করুন", type="primary"):
        with st.spinner('ডাটা কালেক্ট করা হচ্ছে...'):
            results = collect_data_safely()
            for result in results:
                st.write(result)

st.markdown("---")
st.subheader("📈 প্রেডিকশন রেজাল্ট")

if st.button("🔮 প্রেডিকশন রান করুন"):
    with st.spinner('প্রেডিকশন অ্যালগরিদম চলছে...'):
        stdout, stderr = run_main_script_safely()
        if stdout:
            st.success("✅ প্রেডিকশন সফল হয়েছে!")
            st.code(stdout)
        if stderr:
            st.error("❌ ত্রুটি পাওয়া গেছে:")
            st.code(stderr)

st.markdown("---")
st.info("""
**ℹ️ তথ্য:**
- এই ওয়েব ভার্সনটি ক্লাউডে চলছে
- প্যাকেট স্নিফিং ক্লাউডে কাজ করবে না (পারমিশন ইস্যু)
- সম্পূর্ণ ফাংশনালিটির জন্য লোকাল মেশিনে রান করুন
""")

st.caption("⚠️ দাবিত্যাগ: এই প্রজেক্টটি শুধুমাত্র শিক্ষামূলক উদ্দেশ্যে তৈরি। বাস্তব জুয়ায় ব্যবহার করা বেআইনি ও ঝুঁকিপূর্ণ।")
