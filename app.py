import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# 1. إعدادات الصفحة
st.set_page_config(page_title="TootScouting Hub", layout="wide")

st.title("⚽ TootScouting - Match Analysis Dashboard")
st.markdown("---")

# 📂 قراءة ملف الـ CSV المحلي المرفوع في نفس الفولدر
@st.cache_data(ttl=1)
def load_data():
    try:
        # لو مسمي الملف اسم تاني غير 'match_data.csv' غير الاسم هنا بس
        data = pd.read_csv("match_data.csv")
        data.columns = data.columns.astype(str).str.strip()
        return data
    except:
        return pd.DataFrame()

df = load_data()

# تأمين العثور على الأعمدة ديناميكياً لتفادي الـ KeyError
if not df.empty:
    ev_c = next((c for c in df.columns if 'event' in c.lower()), df.columns[0])
    pl_c = next((c for c in df.columns if 'player' in c.lower()), df.columns[1] if len(df.columns)>1 else df.columns[0])
    tm_c = next((c for c in df.columns if 'mm:ss' in c.lower() or 'time' in c.lower()), df.columns[2] if len(df.columns)>2 else df.columns[0])
    ms_c = next((c for c in df.columns if 'ms' in c.lower()), None)
    
    df['Event Type'] = df[ev_c]
    df['Players'] = df[pl_c]
    df['Start (mm:ss)'] = df[tm_c]
    df['Start (ms)'] = df[ms_c] if ms_c else 0
else:
    df = pd.DataFrame([{'Event Type': 'Pass', 'Players': 'Please upload match_data.csv', 'Start (mm:ss)': '00:00', 'Start (ms)': 0, 'X Start': 0.5, 'Y Start': 0.5}])

# 2. الفلاتر الأساسية (Event & Player)
col1, col2 = st.columns(2)
with col1:
    event_types = ["All"] + list(df['Event Type'].dropna().unique())
    selected_event = st.selectbox("Select Event Type", event_types)
with col2:
    players = ["All"] + list(df['Players'].dropna().unique())
    selected_player = st.selectbox("Select Player", players)

filtered_df = df.copy()
if selected_event != "All": filtered_df = filtered_df[filtered_df['Event Type'] == selected_event]
if selected_player != "All": filtered_df = filtered_df[filtered_df['Players'] == selected_player]

st.markdown("---")

# 3. تقسيم الشاشة: الفيديو والقائمة
col_video, col_playlist = st.columns([1.5, 1])
with col_video:
    st.markdown("### 🎥 Match Video")
    current_time = st.session_state.get("video_time", 0)
    st.video(f"https://www.youtube.com/watch?v=dQw4w9WgXcQ&t={current_time}s", start_time=current_time)

with col_playlist:
    st.markdown("### 📊 Event Playlist")
    for index, row in filtered_df.head(15).iterrows():
        ms_val = row.get('Start (ms)', 0)
        seconds = int(pd.to_numeric(ms_val, errors='coerce') / 1000) if not pd.isna(ms_val) else 0
        
        col_text, col_btn = st.columns([3, 1])
        with col_text:
            st.markdown(f"⏱️ **{row.get('Start (mm:ss)', '00:00')}** | {row.get('Event Type', 'Event')} - {row.get('Players', 'Player')}")
        with col_btn:
            if st.button("Watch", key=f"play_{index}"):
                st.session_state["video_time"] = seconds
                st.rerun()

st.markdown("---")
st.markdown("### 🏟️ Tactical Pitch Map")

pitch = Pitch(pitch_type='opta', pitch_color='#0f1
