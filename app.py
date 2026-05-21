import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# 1. Page Configuration
st.set_page_config(
    page_title="TootScouting - Match Analysis", 
    layout="wide"
)

# Custom Style for Premium Dark UI
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    body { background-color: #0f172a; color: #f8fafc; }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ TootScouting - Match Performance Analytics")
st.markdown("<p style='color: #64748b; font-size: 16px;'>Single match tracking dashboard & dynamic pitch maps.</p>", unsafe_allow_index=True)
st.markdown("---")

# 🔗 الرابط المباشر والمتنظف بالـ gid الحقيقي لماتش NJS vs EPS
GOOGLE_SHEET_URL = "https://docs.google.com/spreadsheets/d/1tmE0yxj-KiNZiu8OsP1eQnFzl9YyxK4vXkROGgfejVI/export?format=csv&gid=1424911760"

@st.cache_data(ttl=1) 
def load_database():
    try:
        data = pd.read_csv(GOOGLE_SHEET_URL)
        data.columns = data.columns.astype(str).str.strip()
        return data
    except:
        return pd.DataFrame()

df = load_database()

# خط دفاع آمن لو الشيت لسه بيحمل
if df.empty or 'Event Type' not in df.columns:
    df = pd.DataFrame([{
        'Event Type': 'Pass', 'Players': 'Connecting to Live Sheet...', 'Start (mm:ss)': '00:00', 
        'Start (ms)': 0, 'X Start': 0.50, 'Y Start': 0.50, 'X End': 0.70, 'Y End': 0.50
    }])

# توحيد مسميات الأعمدة والمسافات داخلياً
df['event_final'] = df['Event Type'].astype(str).str.strip()
df['player_final'] = df['Players'].fillna('Unknown Player')
df['timestamp'] = df['Start (mm:ss)'].fillna('00:00')
df['seconds'] = (pd.to_numeric(df['Start (ms)'], errors='coerce') / 1000).fillna(0).astype(int)

# 2. Match Filters (Event & Player Only)
st.markdown("### 🔍 Match Analytics Filters")
col_f1, col_f2 = st.columns(2)
    
with col_f1:
    available_events = ["All Events"] + list(df['event_final'].unique())
    selected_event = st.selectbox("Select Event Type:", available_events)
    
with col_f2:
    available_players = ["All Players"] + list(df['player_final'].unique())
    selected_player = st.selectbox("Select Target Player:", available_players)

# تطبيق الفلاتر على الماتش
filtered_df = df.copy()
if selected_event != "All Events":
    filtered_df = filtered_df[filtered_df['event_final'] == selected_event]
if selected_player != "All Players":
    filtered_df = filtered_df[filtered_df['player_final'] == selected_player]

st.markdown("---")

# 3. Layout: Video Player & Event Playlist
col_video, col_playlist = st.columns([1.4, 1])

with col_video:
    st.markdown("#### 🎥 Video Analysis Player")
    start_time = st.session_state.get("current_clip_time", 0)
    # رابط فيديو المباراة على يوتيوب
    st.video(f"https://www.youtube.com/watch?v=dQw4w9WgXcQ&t={start_time}s", start_time=start_time)

with col_playlist:
    st.markdown(f"#### 📊 Match Playlist ({len(filtered_df)} Clips)")
    for index, row in filtered_df.head(15).iterrows():
        col_card, col_btn = st.columns([3.5, 1])
        with col_card:
            st.markdown(f"""
            <div style="background-color: #1e293b; padding: 10px; border-radius: 6px; border-left: 4px solid #3b82f6; margin-bottom: 5px;">
                <span style="color: #3b82f6; font-weight: bold; font-size: 11px;">⏱️ {row['timestamp']}</span><br>
                <strong style="color: #f1f5f9; font-size: 13px;">{row['event_final']} - {row['player_final']}</strong>
            </div>
            """, unsafe_allow_html=True)
        with col_btn:
            st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
            if st.button("👁️ Watch", key=f"btn_p_{index}"):
                st.session_state["current_clip_time"] = int(row['seconds'])
                st.rerun()

st.markdown("---")

# 4. Tactical Pitch Map (Mplsoccer Opta Layout)
st.markdown("#### 🏟️ Match Tactical Pitch Map")

pitch = Pitch(pitch_type='opta', pitch_color='#0f172a', line_color='#334155', linewidth=2)
fig, ax = pitch.draw(figsize=(10, 6))
fig.patch.set_facecolor('#0f172a')

if 'X Start' in filtered_df.columns and 'Y Start' in filtered_df.columns:
    plot_df = filtered_df.dropna(subset=['X Start', 'Y Start']).copy()
    try:
        plot_df['x_plot'] = pd.to_numeric(plot_df['X Start'], errors='coerce') * 100
        plot_df['y_plot'] = pd.to_numeric(plot_df['Y Start'], errors='coerce') * 100
        
        # رسم أسهم التمريرات
        passes_df = plot_df[plot_df['event_final'].str.lower() == 'pass']
        if not passes_df.empty and 'X End' in plot_df.columns and 'Y End' in plot_df.columns:
            passes_df['x_end_plot'] = pd.to_numeric(passes_df['X End'], errors='coerce') * 100
            passes_df['y_end_plot'] = pd.to_numeric(passes_df['Y End'], errors='coerce') * 100
            pitch.arrows(
                passes_df['x_plot'], passes_df['y_plot'],
                passes_df['x_end_plot'], passes_df['y_end_plot'], 
                color='#3b82f6', width=2.5, headwidth=4, headlength=4, ax=ax
            )
            
        # رسم باقي الأحداث كنقاط خضراء
        other_df = plot_df[plot_df['event_final'].str.lower() != 'pass']
        if not other_df.empty:
            pitch.scatter(
                other_df['x_plot'], other_df['y_plot'],
                color='#10b981', edgecolors='#ffffff', s=130, marker='o', ax=ax
            )
    except:
        pass
        
st.pyplot(fig)
