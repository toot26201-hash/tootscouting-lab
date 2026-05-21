import streamlit as st
import pandas as pd
import os

# إعداد الصفحة
st.set_page_config(page_title="TootScouting - Match View", layout="wide")
st.title("⚽ TootScouting Match Analysis")

# قراءة البيانات
@st.cache_data(ttl=1)
def load_data():
    files = [f for f in os.listdir('.') if f.endswith('.csv')]
    return pd.read_csv(files[0]) if files else pd.DataFrame()

df = load_data()

if not df.empty:
    df.columns = df.columns.str.strip()
    
    col1, col2 = st.columns(2)
    selected_event = col1.selectbox("Event Type", ["All"] + list(df['Event Type'].dropna().unique()))
    selected_player = col2.selectbox("Player", ["All"] + list(df['Players'].dropna().unique()))
    
    filtered_df = df.copy()
    if selected_event != "All": filtered_df = filtered_df[filtered_df['Event Type'] == selected_event]
    if selected_player != "All": filtered_df = filtered_df[filtered_df['Players'] == selected_player]

    # عرض المشغل في نفس التبيوب (حل تقني متقدم)
    st.subheader("🎥 Match Video Player")
    
    # تحويل الرابط للـ Preview ليعمل داخل الـ iframe
    VIDEO_ID = "16dhBkjeXxmitljigQgFmz1MX-Jsu2An_"
    embed_url = f"https://drive.google.com/file/d/{VIDEO_ID}/preview"
    
    # عرض الفيديو
    st.components.v1.html(
        f'<iframe src="{embed_url}" width="100%" height="500" allow="autoplay" allowfullscreen></iframe>',
        height=510
    )

    # القائمة
    st.subheader("📊 Event Playlist")
    for index, row in filtered_df.head(10).iterrows():
        st.write(f"⏱️ {row['Start (mm:ss)']} | {row['Event Type']} - {row['Players']}")
else:
    st.error("⚠️ الملف مش موجود! ارفع ملف CSV في المستودع.")
