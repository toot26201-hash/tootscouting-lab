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
        # تنظيف مسافات أسماء الأعمدة تماماً لتفادي الـ KeyError
        data.columns = data.columns.astype(str).str.strip()
        return data
    except:
        return pd.DataFrame()

df = load_data()

# تأمين الكود: لو بايثون لسه مش شايف الأعمدة بسبب الحروف، هيربطها ديناميكياً
if not df.empty:
    event_col = next((c for c in df.columns if c.lower() in ['event type', 'event_type', 'eventtype']), df.columns[0])
    player_col = next((c for c in df.columns if c.lower() in ['players', 'player']), df.columns[1] if len(df.columns) > 1 else df.columns[0])
    time_col = next((c for c in df.columns if c.lower() in ['start (mm:ss)', 'start(mm:ss)', 'timestamp', 'time']), df.columns[2] if len(df.columns) > 2 else df.columns[0])
    ms_col = next((c for c in df.columns if c.lower() in ['start (ms)', 'start(ms)', 'ms']), None)
    
    # إعادة تسمية الأعمدة داخلياً بشكل آمن
    df['Event Type'] = df[event_col]
    df['Players'] = df[player_col]
    df['Start (mm:ss)'] = df[time_col]
    if ms_col:
        df['Start (ms)'] = df[ms_col]
else:
    # داتا احتياطية لو الشيت مهنج
    df = pd.DataFrame([{'Event Type': 'Pass', 'Players': 'Connecting...', 'Start (mm:ss)': '00:00', 'Start (ms)': 0, 'X Start': 0.5, 'Y Start': 0.5}])

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
    st.video(f"https://www.youtube.com/watch?v=dQw4w9WgXcQ&t={current_time}s", start_time=current_time)

with col_playlist:
    st.markdown("### 📊 Event Playlist")
    for index, row in filtered_df.head(15).iterrows():
        # تحويل الوقت لثواني للفيديو بشكل آمن
        seconds = 0
        if 'Start (ms)' in row and not pd.isna(row['Start (ms)']):
            seconds = int(pd.to_numeric(row['Start (ms)'], errors='coerce') / 1000)
        
        col_text, col_btn = st.columns([3, 1])
        with col_text:
            st.markdown(f"⏱️ **{row.get('Start (mm:ss)', '00:00')}** | {row.get('Event Type', 'Event')} - {row.get('Players', 'Player')}")
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

# تحديد أعمدة الإحداثيات المتاحة في الشيت
x_start_col = next((c for c in filtered_df.columns if c.lower() in ['x start', 'x_start']), None)
y_start_col = next((c for c in filtered_df.columns if c.lower() in ['y start', 'y_start']), None)
x_end_col = next((c for c in filtered_df.columns if c.lower() in ['x end', 'x_end']), None)
y_end_col = next((c for c in filtered_df.columns if c.lower() in ['y end', 'y_end']), None)

if x_start_col and y_start_col:
    for index, row in filtered_df.iterrows():
        if pd.isna(row[x_start_col]) or pd.isna(row[y_start_col]):
            continue
            
        x_s = float(pd.to_numeric(row[x_start_col], errors='coerce')) * 100
        y_s = float(pd.to_numeric(row[y_start_col], errors='coerce')) * 100
        
        if str(row.get('Event Type', '')).strip().lower() == 'pass' and x_end_col and not pd.isna(row
