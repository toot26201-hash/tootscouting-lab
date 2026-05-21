import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import os

st.set_page_config(page_title="TootScouting Hub", layout="wide")
st.title("⚽ TootScouting - Match Analysis Dashboard")

# 1. قراءة البيانات
@st.cache_data(ttl=1)
def load_data():
    files = [f for f in os.listdir('.') if f.endswith('.csv')]
    return pd.read_csv(files[0]) if files else pd.DataFrame()

df = load_data()

# 2. الفلترة
if not df.empty:
    df.columns = df.columns.str.strip()
    col1, col2 = st.columns(2)
    selected_event = col1.selectbox("Event", ["All"] + list(df['Event Type'].dropna().unique()))
    selected_player = col2.selectbox("Player", ["All"] + list(df['Players'].dropna().unique()))
    
    filtered_df = df.copy()
    if selected_event != "All": filtered_df = filtered_df[filtered_df['Event Type'] == selected_event]
    if selected_player != "All": filtered_df = filtered_df[filtered_df['Players'] == selected_player]

# 3. مشغل الفيديو (حط رابط الفيديو المباشر هنا)
VIDEO_URL = "https://docs.google.com/uc?export=download&id=16dhBkjeXxmitljigQgFmz1MX-Jsu2An_"

if "start_time" not in st.session_state: st.session_state.start_time = 0

st.subheader("🎥 Match Video")
st.video(VIDEO_URL, start_time=st.session_state.start_time)

# 4. القائمة
for index, row in filtered_df.head(15).iterrows():
    sec = int(row['Start (ms)'] / 1000)
    if st.button(f"⏱️ {row['Start (mm:ss)']} | {row['Players']}", key=index):
        st.session_state.start_time = sec
        st.rerun()

# 5. الملعب
pitch = Pitch(pitch_type='opta', pitch_color='#0f172a', line_color='#334155')
fig, ax = pitch.draw(figsize=(8, 5))
for _, row in filtered_df.iterrows():
    if not pd.isna(row['X Start']):
        pitch.scatter(float(row['X Start'])*100, float(row['Y Start'])*100, ax=ax, color='#10b981')
st.pyplot(fig)
