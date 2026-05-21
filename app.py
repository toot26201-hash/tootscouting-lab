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

# 🔗 Your Connected Google Sheet Database ID (Fixed)
SPREADSHEET_ID = "1tv2bsiF7RLOIadzO_SBmB9RjnXqk0wzK"
SHEET_NAME = "Sheet1"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# Video Registry (Match Name -> Video Link)
VIDEO_REGISTRY = {
    "NJS vs EPS": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
    "Match 2": "https://www.youtube.com/watch?v=another_video",
    "Match 3": "https://www.youtube.com/watch?v=third_video",
}

@st.cache_data(ttl=300) # Updates every 5 minutes when you add new data
def load_database():
    try:
        data = pd.read_csv(GOOGLE_SHEET_URL)
        return data.dropna(subset=['Event Type'])
    except Exception as e:
        st.warning("⚠️ Reading fallback or file format is being initialized. Checking columns...")
        try:
            return pd.read_csv('Untitled-spreadsheet.csv').dropna(subset=['Event Type'])
        except:
            return pd.DataFrame()

df = load_database()

if not df.empty:
    # Standardizing your CSV columns
    df['event_type'] = df['Event Type'].str.strip()
    df['player'] = df['Players'].fillna('Unknown Player')
    df['timestamp'] = df['Start (mm:ss)']
    
    # Auto-add Match column if not present yet
    if 'Match' not in df.columns:
        df['Match'] = 'NJS vs EPS'
        
    if 'Start (ms)' in df.columns:
        df['seconds'] = (df['Start (ms)'] / 1000).astype(int)

    # 2. Strategic Filters Section
    st.markdown("### 🔍 Multi-Match Analytics Filters")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        available_matches = ["All Matches"] + list(df['Match'].unique())
        selected_match = st.selectbox("Select Match / Timeline:", available_matches)
        
    with col_f2:
        available_events = ["All Events"] + list(df['event_type'].unique())
        selected_event = st.selectbox("Select Event Type:", available_events)
        
    with col_f3:
        available_players = ["All Players"] + list(df['player'].unique())
        selected_player = st.selectbox("Select Target Player:", available_players)

    # Apply Cumulative Filters
    filtered_df = df.copy()
    if selected_match != "All Matches":
        filtered_df = filtered_df[filtered_df['Match'] == selected_match]
    if selected_event != "All Events":
        filtered_df = filtered_df[filtered_df['event_type'] == selected_event]
    if selected_player != "All Players":
        filtered_df = filtered_df[filtered_df['player'] == selected_player]

    st.markdown("---")

    # 3. Layout: Video Player & Event Playlist
    col_video, col_playlist = st.columns([1.4, 1])
    
    with col_video:
        st.markdown("#### 🎥 Video Analysis Player")
        start_time = st.session_state.get("current_clip_time", 0)
        
        if selected_match != "All Matches":
            active_video_url = VIDEO_REGISTRY.get(selected_match, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        else:
            first_match_in_filter = filtered_df['Match'].iloc[0] if not filtered_df.empty else "NJS vs EPS"
            active_video_url = VIDEO_REGISTRY.get(first_match_in_filter, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
            
        st.video(f"{active_video_url}&t={start_time}s" if "youtube" in active_video_url else active_video_url, start_time=start_time)

    with col_playlist:
        st.markdown(f"#### 📊 Cumulative Playlist ({len(filtered_df)} Clips)")
        if filtered_df.empty:
            st.warning("No clips found for the selected tracking combination.")
        else:
            for index, row in filtered_df.head(7).iterrows():
                col_card, col_btn = st.columns([3.5, 1])
                with col_card:
                    st.markdown(f"""
                    <div style="background-color: #1e293b; padding: 10px; border-radius: 6px; border-left: 4px solid #3b82f6; margin-bottom: 5px;">
                        <span style="color: #3b82f6; font-weight: bold; font-size: 11px;">{row['Match']} | ⏱️ {row['timestamp']}</span><br>
                        <strong style="color: #f1f5f9; font-size: 13px;">{row['event_type']} - {row['player']}</strong>
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
    
    plot_df = filtered_df.dropna(subset=['X Start', 'Y Start'])
    
    if not plot_df.empty:
        # Drawing Pass Arrows
        passes_df = plot_df[plot_df['event_type'].str.lower() == 'pass']
        if not passes_df.empty:
            pitch.arrows(
                passes_df['X Start']*100, passes_df['Y Start']*100,
                passes_df['X End']*100, passes_df['Y End']*100, 
                color='#3b82f6', width=2.5, headwidth=4, headlength=4, ax=ax
            )
            
        # Drawing Other tracking spots
        other_df = plot_df[plot_df['event_type'].str.lower() != 'pass']
        if not other_df.empty:
            pitch.scatter(
                other_df['X Start']*100, other_df['Y Start']*100,
                color='#10b981', edgecolors='#ffffff', s=130, marker='o', ax=ax
            )
            
    st.pyplot(fig)
else:
    st.info("👋 Database is initializing. Please populate your centralized tracking file.")
