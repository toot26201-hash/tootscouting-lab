import streamlit as st
import pandas as pd
import os

st.set_page_config(page_title="TootScouting", layout="wide")
st.title("⚽ TootScouting Match View")

# قراءة الملف (أوتوماتيك)
@st.cache_data(ttl=1)
def load_data():
    files = [f for f in os.listdir('.') if f.endswith('.csv')]
    return pd.read_csv(files[0]) if files else pd.DataFrame()

df = load_data()
if not df.empty:
    df.columns = df.columns.str.strip()

    # تحديد توقيت الفيديو
    if "clip_url" not in st.session_state:
        st.session_state.clip_url = "https://drive.google.com/file/d/16dhBkjeXxmitljigQgFmz1MX-Jsu2An_/preview"

    # عرض الفيديو
    st.components.v1.html(f'<iframe src="{st.session_state.clip_url}" width="100%" height="450" allow="autoplay" allowfullscreen></iframe>', height=460)

    # القائمة والأزرار
    st.subheader("📊 Event Playlist")
    for index, row in df.head(15).iterrows():
        col1, col2 = st.columns([4, 1])
        col1.write(f"⏱️ {row['Start (mm:ss)']} | {row['Event Type']} - {row['Players']}")
        
        # الزرار اللي بيغير التوقيت
        if col2.button("Watch Clip", key=f"btn_{index}"):
            start_sec = int(row['Start (ms)'] / 1000)
            # تحديث الرابط بالثانية المطلوبة
            st.session_state.clip_url = f"https://drive.google.com/file/d/16dhBkjeXxmitljigQgFmz1MX-Jsu2An_/preview?t={start_sec}s"
            st.rerun()
else:
    st.error("ارفع ملف الـ CSV يا كابتن!")
