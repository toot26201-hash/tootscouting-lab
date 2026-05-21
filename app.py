import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

st.set_page_config(page_title="TootScouting Hub", layout="wide")
st.title("⚽ TootScouting - Professional Scouting Database")
st.markdown("---")

# 🔗 ربط الشيت المباشر
SPREADSHEET_ID = "1tmE0yxj-KiNZiu8OsP1eQnFzl9YyxK4vXkROGgfejVI"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=1)
def load_data():
    try:
        data = pd.read_csv(GOOGLE_SHEET_URL)
        # تنظيف مسافات الأعمدة وتوحيدها
        data.columns = data.columns.astype(str).str.strip()
        return data
    except:
        return pd.DataFrame()

raw_df = load_data()

# البحث عن الأعمدة ديناميكياً لتفادي اختلاف الكابيتال والسمول والمسافات
if not raw_df.empty:
    df = raw_df.copy()
    event_col = next((c for c in df.columns if c.lower() in ['event type', 'event_type', 'eventtype']), df.columns[0])
    player_col = next((c for c in df.columns if c.lower() in ['players', 'player']), df.columns[1] if len(df.columns) > 1 else df.columns[0])
    time_col = next((c for c in df.columns if c.lower() in ['start (mm:ss)', 'start(mm:ss)', 'timestamp', 'time']), df.columns[2] if len(df.columns) > 2 else df.columns[0])
    ms_col = next((c for c in df.columns if c.lower() in ['start (ms)', 'start(ms)', 'ms']), None)
    
    df['event_final'] = df[event_col].astype(str).str.strip()
    df['player_final'] = df[player_col].fillna('Unknown Player')
    df['timestamp'] = df[time_col].fillna('00:00')
    df['match'] = df['Match'] if 'Match' in df.columns else 'NJS vs EPS'
    df['seconds'] = (pd.to_numeric(df[ms_col], errors='coerce') / 1000).fillna(0).astype(int) if ms_col else 0
else:
    # داتا تجريبية في حالة فشل الاتصال تماماً بالشيت
    df = pd.DataFrame([{'event_final': 'Pass', 'player_final': 'Connecting to Sheet...', 'timestamp': '00:00', 'match': 'NJS vs EPS', 'seconds': 0, 'X Start': 0, 'Y Start': 0}])

# الفلاتر
col_f1, col_f2, col_f3 = st.columns(3)
with col_f1: selected_match = st.selectbox("Match:", ["All Matches"] + list(df['match'].unique()))
with col_f2: selected_event = st.selectbox("Event:", ["All Events"] + list(df['event_final'].unique()))
with col_f3: selected_player = st.selectbox("Player:", ["All Players"] + list(df['player_final'].unique()))

filtered_df = df.copy()
if selected_match != "All Matches": filtered_df = filtered_df[filtered_df['match'] == selected_match]
if selected_event != "All Events": filtered_df = filtered_df[filtered_df['event_final'] == selected_event]
if selected_player != "All Players": filtered_df = filtered_df[filtered_df['player_final'] == selected_player]

# الفيديو والـ Playlist
col_video, col_playlist = st.columns([1.4, 1])
with col_video:
    start_time = st.session_state.get("current_clip_time", 0)
    st.video(f"https://www.youtube.com/watch?v=dQw4w9WgXcQ&t={start_time}s", start_time=start_time)

with col_playlist:
    st.markdown(f"#### 📊 Playlist ({len(filtered_df)} Clips)")
    for index, row in filtered_df.head(15).iterrows():
        col_card, col_btn = st.columns([3.5, 1])
        with col_card: st.markdown(f"<div style='background-color: #1e293b; padding: 10px; border-radius: 6px; color: white; margin-bottom: 5px;'>⏱️ {row['timestamp']} | <b>{row['event_final']}</b><br><small>{row['player_final']}</small></div>", unsafe_allow_html=True)
        with col_btn:
            if st.button("👁️ Watch", key=f"btn_{index}"):
                st.session_state["current_clip_time"] = int(row['seconds'])
                st.rerun()

st.markdown("---")
st.markdown("#### 🏟️ Tactical Pitch Map")

pitch = Pitch(pitch_type='opta', pitch_color='#0f172a', line_color='#334155', linewidth=2)
fig, ax = pitch.draw(figsize=(10, 6))
fig.patch.set_facecolor('#0f172a')

x_start = next((c for c in filtered_df.columns if c.lower() in ['x start', 'x_start']), None)
y_start = next((c for c in filtered_df.columns if c.lower() in ['y start', 'y_start']), None)
x_end = next((c for c in filtered_df.columns if c.lower() in ['x end', 'x_end']), None)
y_end = next((c for c in filtered_df.columns if c.lower() in ['y end', 'y_end']), None)

if x_start and y_start:
    plot_df = filtered_df.dropna(subset=[x_start, y_start]).copy()
    try:
        plot_df['x_plot'] = pd.to_numeric(plot_df[x_start], errors='coerce') * 100
        plot_df['y_plot'] = pd.to_numeric(plot_df[y_start], errors='coerce') * 100
        
        passes_df = plot_df[plot_df['event_final'].str.lower() == 'pass']
        if not passes_df.empty and x_end and y_end:
            passes_df['x_end_plot'] = pd.to_numeric(passes_df[x_end], errors='coerce') * 100
            passes_df['y_end_plot'] = pd.to_numeric(passes_df[y_end], errors='coerce') * 100
            pitch.arrows(passes_df['x_plot'], passes_df['y_plot'], passes_df['x_end_plot'], passes_df['y_end_plot'], color='#3b82f6', width=2, ax=ax)
            
        other_df = plot_df[plot_df['event_final'].str.lower() != 'pass']
        if not other_df.empty:
            pitch.scatter(other_df['x_plot'], other_df['y_plot'], color='#10b981', s=100, ax=ax)
    except:
        pass

st.pyplot(fig)
