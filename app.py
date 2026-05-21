import streamlit as st
import pandas as pd
import os

# إعداد الصفحة
st.set_page_config(page_title="TootScouting", layout="wide")
st.title("⚽ TootScouting Match Analysis")

# قراءة البيانات
@st.cache_data(ttl=1)
def load_data():
    files = [f for f in os.listdir('.') if f.endswith('.csv')]
    return pd.read_csv(files[0]) if files else pd.DataFrame()

df = load_data()

if not df.empty:
    df.columns = df.columns.str.strip()
    
    # 1. المشغل (فوق)
    st.subheader("🎥 Match Video")
    VIDEO_ID = "16dhBkjeXxmitljigQgFmz1MX-Jsu2An_"
    embed_url = f"https://drive.google.com/file/d/{VIDEO_ID}/preview"
    st.components.v1.html(
        f'<iframe src="{embed_url}" width="100%" height="400" allow="autoplay" allowfullscreen></iframe>',
        height=410
    )

    # 2. القائمة (تحت أو جنب الفيديو)
    st.subheader("📊 Event Playlist")
    for index, row in df.head(15).iterrows():
        # إنشاء صف جديد لكل لقطة لضمان ظهور الزرار
        col_name, col_btn = st.columns([4, 1])
        col_name.write(f"⏱️ {row['Start (mm:ss)']} | {row['Event Type']} - {row['Players']}")
        
        # الزرار اللي كان مختفي ظهر تاني هنا
        if col_btn.button("Watch", key=f"btn_{index}"):
            st.info(f"تم اختيار: {row['Event Type']} - {row['Players']}")
            # ملاحظة: جوجل درايف لا يدعم التنقل التلقائي داخل الـ iframe، 
            # لكن الزرار الآن يظهر ويعمل لتسجيل اختيارك.
else:
    st.error("⚠️ ملف CSV غير موجود.")
