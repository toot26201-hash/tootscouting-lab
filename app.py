import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# 1. Page Configuration
st.set_page_config(
    page_title="TootScouting Hub - Database & Analytics", 
    layout="wide"
)

# Custom Style for Premium Dark UI
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    body { background-color: #0f172a; color: #f8fafc; }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ TootScouting - Professional Scouting Database")
st.markdown("<p style='color: #64748b; font-size: 16px;'>Multi-match tracking system & cumulative tactical pitch maps.</p>", unsafe_allow_html=True)
st.markdown("---")

# 🔗 Connected Google Sheet Database ID
SPREADSHEET_ID = "1tmE0yxj-KiNZiu8OsP1eQnFzl9YyxK4vXkROGgfejVI"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=5) 
def load_database():
    try:
        data = pd.read_csv(GOOGLE_SHEET_URL)
        # تنظيف أسماء الأعمدة من أي مسافات وتحويلها لحروف صغيرة لتفادي الأخطاء
        data.columns = data.columns.astype(str).str.strip().str.lower()
        return data
    except Exception as e:
        return pd.DataFrame()

df = load_database()

# التحقق من وجود الأعمدة الأساسية بأي صيغة (سمول أو كابيتال)
has_required_columns = any(col in df.columns for col in ['event type', 'event_type', 'eventtype']) and any(col in df.columns for col in ['players', 'player'])

if df.empty or not has_required_columns:
    # داتا تجريبية آمنة لو الشيت لسه بيحمل
    df = pd.DataFrame([{
        'event type': 'Pass', 'players': 'Example Player', 'start (mm:ss)': '01:26', 
        'start (ms)': 86970, 'x start': 0.50, 'y start': 0.50, 'x end': 0.69, 'y end': 0.50, 'match': 'NJS vs EPS'
    }])
    df.columns = df.columns.str.strip().str.lower()

# توحيد مسميات الأعمدة داخلياً للكود
df['event_final'] = df['event type'].astype(str).str.strip()
df['player_final'] = df['players'].fillna('Unknown Player')

if 'start (mm:ss)' in df.columns:
    df['timestamp'] = df['start (mm:ss)']
else:
    df['timestamp'] = "00:00"

if 'match' not in df.columns:
    df['match'] = 'NJS vs EPS'
    
if 'start (ms)' in df.columns:
    df['seconds'] = (pd.to_numeric(df['start (ms)'], errors='coerce') / 1000).fillna(0).astype(int)
else:
    df['seconds'] = 0

# 2. Strategic Filters Section
st.markdown("### 🔍 Multi-Match Analytics Filters")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    available_matches = ["All Matches"] + list(df['match'].unique())
    selected_match = st.selectbox("Select Match / Timeline:", available_matches)
    
with col_f2:
    available_events = ["All Events"] + list(df['event_final'].unique())
    selected_event = st.selectbox("Select Event Type:", available_events)
    
with col_f3:
    available_players = ["All Players"] + list(df['player_final'].unique())
    selected_player = st.selectbox("Select Target Player:", available_players)

# تطبيق الفلاتر
filtered_df = df.copy()
if selected_match != "All Matches":
    filtered_df = filtered_df[filtered_df['match'] == selected_match]
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
    st.video(f"https://www.youtube.com/watch?v=dQw4w9WgXcQ&t={start_time}s", start_time=start_time)

with col_playlist:
    st.markdown(f"#### 📊 Cumulative Playlist ({len(filtered_df)} Clips)")
    
    for index, row in filtered_df.head(15).iterrows():
        col_card, col_btn = st.columns([3.5, 1])
        with col_card:
            st.markdown(f"""
            <div style="background-color: #1e293b; padding: 10px; border-radius: 6px; border-left: 4px solid #3b82f6; margin-bottom: 5px;">
                <span style="color: #3b82f6; font-weight: bold; font-size: 11px;">{row['match']} | ⏱️ {row['timestamp']}</span><br>
                <strong style="color: #f1f5f9; font-size: 13px;">{row['event_final']} - {row['player_final']}</strong>
            </div>
            """, unsafe_allow_html=True)
        with col_btn:
            st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
            if st.button("👁️ Watch", key=f"btn_p_{index}"):
                st.session_state["current_clip_time"] = int(row['seconds'])
                st.rerun()

st.markdown("---")

# 4. Cumulative Tactical Pitch Map (Mplsoccer)
st.markdown(f"#### 🏟️ Cumulative Tactical Pitch Map (Opta Blueprint)")

pitch = Pitch(pitch_type='opta', pitch_color='#0f172a', line_color='#334155', linewidth=2)
fig, ax = pitch.draw(figsize=(10, 6))
fig.patch.set_facecolor('#0f172a')

# تنظيف ورسم الإحداثيات الحقيقية (بأي مسمى حروف صغيرة)
x_start_col = 'x start' if 'x start' in filtered_df.columns else 'x_start'
y_start_col = 'y start' if 'y start' in filtered_df.columns else 'y_start'
x_end_col = 'x end' if 'x end' in filtered_df.columns else 'x_end'
y_end_col = 'y end' if 'y end' in filtered_df.columns else 'y_end'

if x_start_col in filtered_df.columns and y_start_col in filtered_df.columns:
    plot_df = filtered_df.dropna(subset=[x_start_col, y_start_col])
    try:
        plot_df[x_start_col] = pd.to_numeric(plot_df[x_start_col], errors='coerce') * 100
        plot_df[y_start_col] = pd.to_numeric(plot_df[y_start_col], errors='coerce') * 100
        
        # رسم أسهم التمريرات
        passes_df = plot_df[plot_df['event_final'].str.lower() == 'pass']
        if not passes_df.empty and x_end_col in passes_df.columns:
            passes_df[x_end_col] = pd.to_numeric(passes_df[x_end_col], errors='coerce') * 100
            passes_df[y_end_col] = pd.to_numeric(passes_df[y_end_col], errors='coerce') * 100
            pitch.arrows(
                passes_df[x_start_col], passes_df[y_start_col],
                passes_df[x_end_col], passes_df[y_end_col], 
                color='#3b82f6', width=2.5, headwidth=4, headlength=4, ax=ax
            )
            
        # رسم باقي الأحداث
        other_df = plot_df[plot_df['event_final'].str.lower() != 'pass']
        if not other_df.empty:
            pitch.scatter(
                other_df[x_start_col], other_df[y_start_col],
                color='#10b981', edgecolors='#ffffff', s=130, marker='o', ax=ax
            )
    except Exception as e:
        pass
        
st.pyplot(fig)
