import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# 1. إعدادات الصفحة
st.set_page_config(page_title="TootScouting Hub", layout="wide")

st.title("⚽ TootScouting - Match Analysis Dashboard")
st.markdown("---")

# 🔗 الرابط المباشر الصحيح بالـ gid الحقيقي لماتش NJS vs EPS
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1tmE0yxj-KiNZiu8OsP1eQnFzl9YyxK4vXkROGgfejVI/export?format=csv&gid=1424911760"

@st.cache_data(ttl=1)
def load_data():
    try:
        data = pd.read_csv(GOOGLE_SHEET_URL)
        return data
    except:
        return pd.DataFrame()

df = load_data()

# 2. الفلاتر الأساسية (Event & Player)
col1, col2 = st.columns(2)
with col1:
    event_types = ["All"] + list(df['Event Type'].dropna().unique())
    selected_event = st.selectbox("Select Event Type", event_types)
with col2:
    players = ["All"] + list(df['Players'].dropna().unique())
    selected_player = st.selectbox("Select Player", players)

# تصفية البيانات بناءً على الفلاتر
filtered_df = df.copy()
if selected_event != "All":
    filtered_df = filtered_df[filtered_df['Event Type'] == selected_event]
if selected_player != "All":
    filtered_df = filtered_df[filtered_df['Players'] == selected_player]

st.markdown("---")

# 3. تقسيم الشاشة: الفيديو والقائمة
col_video, col_playlist = st.columns([1.5, 1])

with col_video:
    st.markdown("### 🎥 Match Video")
    current_time = st.session_state.get("video_time", 0)
    # رابط الفيديو الافتراضي
    st.video(f"https://www.youtube.com/watch?v=dQw4w9WgXcQ&t={current_time}s", start_time=current_time)

with col_playlist:
    st.markdown("### 📊 Event Playlist")
    for index, row in filtered_df.head(15).iterrows():
        # تحويل الوقت لثواني للفيديو
        ms = row['Start (ms)']
        seconds = int(ms / 1000) if not pd.isna(ms) else 0
        
        col_text, col_btn = st.columns([3, 1])
        with col_text:
            st.markdown(f"⏱️ **{row['Start (mm:ss)']}** | {row['Event Type']} - {row['Players']}")
        with col_btn:
            if st.button("Watch", key=f"play_{index}"):
                st.session_state["video_time"] = seconds
                st.rerun()

st.markdown("---")

# 4. الملعب التكتيكي
st.markdown("### 🏟️ Tactical Pitch Map")
pitch = Pitch(pitch_type='opta', pitch_color='#0f172a', line_color='#334155')
fig, ax = pitch.draw(figsize=(10, 7))
fig.patch.set_facecolor('#0f172a')

# رسم التمريرات والأحداث
for index, row in filtered_df.iterrows():
    if pd.isna(row['X Start']) or pd.isna(row['Y Start']):
        continue
        
    x_start = float(row['X Start']) * 100
    y_start = float(row['Y Start']) * 100
    
    if str(row['Event Type']).strip().lower() == 'pass' and not pd.isna(row['X End']):
        x_end = float(row['X End']) * 100
        y_end = float(row['Y End']) * 100
        pitch.arrows(x_start, y_start, x_end, y_end, color='#3b82f6', width=2, headwidth=4, ax=ax)
    else:
        pitch.scatter(x_start, y_start, color='#10b981', s=100, edgecolors='#ffffff', ax=ax)

st.pyplot(fig)
