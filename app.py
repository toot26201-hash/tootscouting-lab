import streamlit as st
import pandas as pd
import os

st.set_page_config(layout="wide")
st.title("⚽ TootScouting Match Analysis")

# قراءة الملف وتنظيفه
@st.cache_data(ttl=1)
def load_data():
    files = [f for f in os.listdir('.') if f.endswith('.csv')]
    if files:
        df = pd.read_csv(files[0])
        df.columns = df.columns.str.strip() # تنظيف الأعمدة من المسافات
        return df
    return pd.DataFrame()

df = load_data()

if not df.empty:
    # 1. القوائم المنسدلة (الدروب داون)
    col1, col2 = st.columns(2)
    selected_event = col1.selectbox("اختر الحدث (Event)", ["All"] + list(df['Event Type'].dropna().unique()))
    selected_player = col2.selectbox("اختر اللاعب (Player)", ["All"] + list(df['Players'].dropna().unique()))
    
    # فلترة الداتا
    filtered_df = df.copy()
    if selected_event != "All": filtered_df = filtered_df[filtered_df['Event Type'] == selected_event]
    if selected_player != "All": filtered_df = filtered_df[filtered_df['Players'] == selected_player]

    # 2. المشغل
    st.subheader("🎥 Match Video")
    VIDEO_ID = "16dhBkjeXxmitljigQgFmz1MX-Jsu2An_"
    st.components.v1.html(f'<iframe src="https://drive.google.com/file/d/{VIDEO_ID}/preview" width="100%" height="400"></iframe>', height=410)

    # 3. القائمة والأزرار
    st.subheader("📊 Event Playlist")
    for index, row in filtered_df.head(15).iterrows():
        c1, c2 = st.columns([4, 1])
        c1.write(f"⏱️ {row['Start (mm:ss)']} | {row['Event Type']} - {row['Players']}")
        
        # الرابط المباشر بالثانية
        start_sec = int(row['Start (ms)'] / 1000)
        watch_url = f"https://drive.google.com/file/d/{VIDEO_ID}/view?t={start_sec}s"
        c2.link_button("Watch", watch_url)
else:
    st.error("⚠️ الملف مش موجود! اتأكد من اسم الملف في جيت هاب.")
