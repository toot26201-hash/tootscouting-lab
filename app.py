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

# 🔗 Your Real Google Sheet ID (From your spreadsheet tab screenshot)
SPREADSHEET_ID = "1tmE0yxj-KiNZiu8OsP1eQnFzl9YyxK4vXkROGgfejVI"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=1) # Updates immediately
def load_database():
    try:
        data = pd.read_csv(GOOGLE_SHEET_URL)
        # Clean columns to bypass lowercase/uppercase mixing
        data.columns = data.columns.astype(str).str.strip()
        return data
    except Exception as e:
        return pd.DataFrame()

raw_df = load_database()

# Map columns dynamically based on what is available in your file
if not raw_df.empty:
    df = raw_df.copy()
    
    # Dynamic Column Matchers
    event_col = next((c for c in df.columns if c.lower() in ['event type', 'event_type', 'eventtype']), None)
    player_col = next((c for c in df.columns if c.lower() in ['players', 'player']), None)
    time_col = next((c for c in df.columns if c.lower() in ['start (mm:ss)', 'start(mm:ss)', 'timestamp']), None)
    ms_col = next((c for c in df.columns if c.lower() in ['start (ms)', 'start(ms)']), None)
    match_col = next((c for c in df.columns if c.lower() == 'match'), None)

    # Standardizing data fields
    df['event_final'] = df[event_col].astype(str).str.strip() if event_col else "Event"
    df['player_final'] = df[player_col].fillna('Unknown Player') if player_col else "Unknown Player"
    df['timestamp'] = df[time_col] if time_col else "00:00"
    df['match'] = df[match_col] if match_col else "NJS vs EPS"
    
    if ms_col:
        df['seconds'] = (pd.to_numeric(df[ms_col], errors='coerce') / 1000).fillna(0).astype(int)
    else:
        df['seconds'] = 0
else:
    # Safest Fallback if sheet is completely unreachable
    df = pd.DataFrame([{
        'event_final': 'Pass', 'player_final': 'Connecting to Sheet...', 'timestamp': '00:00', 
        'seconds': 0, 'match': 'NJS vs EPS', 'X Start': 0, 'Y Start': 0
    }])

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

# Apply Filters
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
    
    if filtered_df.empty:
        st.warning("No tracking lines match your active filters.")
    else:
        for index, row in filtered_df.head(20).iterrows():
            col_card, col_btn = st.columns([3.5, 1])
            with col_card:
                st.markdown(f"""
                <div style="background-color: #1e293b; padding: 10px; border-radius: 6px; border-left: 4px solid #3b82f6; margin-bottom: 5px;">
                    <span style="color: #3b82f6; font-weight: bold; font-size: 11px;">{row['match']} | ⏱️ {
