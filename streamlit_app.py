import streamlit as st
import subprocess
import sys
import os

st.set_page_config(page_title="Aviator Predictor", layout="wide")
st.title("✈️ Aviator Predictor - Web Interface")
st.markdown("---")

# মূল পাইথন স্ক্রিপ্ট চালানোর ফাংশন
def run_main_script():
    result = subprocess.run([sys.executable, "src/main.py"], capture_output=True, text=True, cwd=os.path.dirname(__file__))
    return result.stdout, result.stderr

if st.button("▶️ রান প্রেডিকশন"):
    with st.spinner('অনুগ্রহপূর্বক অপেক্ষা করুন, ডাটা কালেক্ট ও অ্যানালাইসিস চলছে...'):
        stdout, stderr = run_main_script()
        if stdout:
            st.success("✅ স্ক্রিপ্ট সফলভাবে রান হয়েছে!")
            st.text("আউটপুট:")
            st.code(stdout)
        if stderr:
            st.error("❌ ত্রুটি পাওয়া গেছে:")
            st.code(stderr)

st.markdown("---")
st.caption("⚠️ দাবিত্যাগ: এই প্রজেক্টটি শুধুমাত্র শিক্ষামূলক উদ্দেশ্যে তৈরি। বাস্তব জুয়ায় ব্যবহার করা বেআইনি ও ঝুঁকিপূর্ণ।")
