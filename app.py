import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# 1. Page Configuration
st.set_page_config(
    page_title="TootScouting Lab - Video & Analytics Hub", 
    layout="wide"
)

# Custom CSS for Premium Dark UI & Layout Cleanups
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    body { background-color: #0f172a; color: #f8fafc; }
    .stSelectbox label, .stFileUploader label, .stTextInput label {
        color: #94a3b8 !important;
        font-weight: 600;
    }
    div.stButton > button:first-child {
        background-color: #10b981;
        color: white;
        border-radius: 6px;
        border: none;
        width: 100%;
        font-weight: bold;
        transition: 0.3s;
    }
    div.stButton > button:first-child:hover {
        background-color: #059669;
        color: white;
    }
    </style>
""", unsafe_allow_html=True)

# Main Dashboard Header
st.title("⚽ TootScouting - Tactical Video & Analytics Hub")
st.markdown("<p style='color: #64748b; font-size: 16px;'>Synchronize match events data with video clips on an elite tactical pitch layout.</p>", unsafe_allow_html=True)
st.markdown("---")

# 2. Sidebar Control Center
st.sidebar.header("📁 Data Control Center")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("Upload Match Events (CSV)", type=["csv"])
video_url_input = st.sidebar.text_input(
    "Match Video URL (YouTube / Direct Link)", 
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
)

# 3. Checking if File is Uploaded
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file).dropna(subset=['Event Type'])
    st.sidebar.success("✅ Match data parsed successfully!")
    
    # Standardizing your professional CSV columns mapping
    df['event_type'] = df['Event Type'].str.strip()
    df['player'] = df['Players'].fillna('Unknown Player')
    df['timestamp'] = df['Start (mm:ss)']
    if 'Start (ms)' in df.columns:
        df['seconds'] = (df['Start (ms)'] / 1000).astype(int)

    # 4. Tactical Filters Section
    st.markdown("### 🔍 Strategic Filters")
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        available_events = ["All Events"] + list(df['event_type'].unique())
        selected_event = st.selectbox("Filter by Event Type:", available_events)
        
    with col_f2:
        available_players = ["All Players"] + list(df['player'].unique())
        selected_player = st.selectbox("Filter by Player:", available_players)
            
    # Apply Filters
    filtered_df = df.copy()
    if selected_event != "All Events":
        filtered_df = filtered_df[filtered_df['event_type'] == selected_event]
    if selected_player != "All Players":
        filtered_df = filtered_df[filtered_df['player'] == selected_player]

    st.markdown("---")

    # 5. Top Section: Video Player & Event Playlist
    col_video, col_playlist = st.columns([1.4, 1])
    
    with col_video:
        st.markdown("#### 🎥 Video Analysis Player")
        start_time = st.session_state.get("current_clip_time", 0)
        st.video(f"{video_url_input}?t={start_time}", start_time=start_time)
        if start_time > 0:
            st.info(f"⏱️ Playing clip at: **{start_time}** seconds")

    with col_playlist:
        st.markdown(f"#### 📊 Event Playlist ({len(filtered_df)} clips)")
        
        # Container with a fixed layout look
        playlist_placeholder = st.container()
        with playlist_placeholder:
            if filtered_df.empty:
                st.warning("No clips match the selected filters.")
            else:
                # Showing top 8 events for layout clean look
                display_df = filtered_df.head(8)
                for index, row in display_df.iterrows():
                    col_card, col_btn = st.columns([3.5, 1])
                    
                    time_str = row.get('timestamp', '00:00')
                    ev_type = row.get('event_type', 'Event')
                    p_name = row.get('player', 'Player')
                    tag_info = row.get('Tags', '')

                    with col_card:
                        # Premium Clean Card UI Design
                        st.markdown(f"""
                        <div style="background-color: #1e293b; padding: 10px; border-radius: 6px; border-left: 4px solid #3b82f6; margin-bottom: 5px;">
                            <span style="color: #3b82f6; font-weight: bold; font-size: 13px;">⏱️ {time_str}</span> | 
                            <strong style="color: #f1f5f9; font-size: 14px;">{ev_type}</strong><br>
                            <span style="color: #94a3b8; font-size: 12px;">{p_name}</span>
                            {f'<br><span style="color: #10b981; font-size: 11px; font-style: italic;">{tag_info}</span>' if pd.notna(tag_info) else ''}
                        </div>
                        """, unsafe_allow_html=True)
                    
                    with col_btn:
                        st.markdown("<div style='padding-top: 10px;'></div>", unsafe_allow_html=True)
                        if st.button("👁️ Watch", key=f"btn_p_{index}"):
                            st.session_state["current_clip_time"] = int(row['seconds'])
                            st.rerun()

    st.markdown("---")
    
    # 6. Bottom Section: Elite Mplsoccer Pitch
    st.markdown("#### 🏟️ Tactical Event Pitch Map (Opta Dimension)")
    
    # Premium Dark Pitch Styling
    pitch = Pitch(pitch_type='opta', pitch_color='#0f172a', line_color='#334155', linewidth=2)
    fig, ax = pitch.draw(figsize=(10, 6))
    fig.patch.set_facecolor('#0f172a') # Matches Streamlit background
    
    plot_df = filtered_df.dropna(subset=['X Start', 'Y Start'])
    
    if not plot_df.empty:
        # Drawing Passes as Arrows
        passes_df = plot_df[plot_df['event_type'].str.lower() == 'pass']
        if not passes_df.empty:
            pitch.arrows(
                passes_df['X Start']*100, passes_df['Y Start']*100,
                passes_df['X End']*100, passes_df['Y End']*100, 
                color='#3b82f6', width=2.5, headwidth=4, headlength=4,
                ax=ax, label='Passes'
            )
            
        # Drawing other tactical moments as bright tracking spots
        other_df = plot_df[plot_df['event_type'].str.lower() != 'pass']
        if not other_df.empty:
            pitch.scatter(
                other_df['X Start']*100, other_events_df_y:=other_df['Y Start']*100,
                color='#10b981', edgecolors='#ffffff', s=130, marker='o',
                ax=ax, label='Events'
            )
            
            # Subtly adding player's last identity tag on the pitch
            for idx, row in other_df.iterrows():
                last_name = row['player'].split()[-1] if ' ' in row['player'] else row['player']
                ax.text(
                    row['X Start']*100, row['Y Start']*100 + 1.8, 
                    last_name, 
                    color='#94a3b8', fontsize=9, ha='center', weight='bold'
                )

    st.pyplot(fig)

else:
    # Clean English Welcome Screen
    st.info("👋 Welcome Chief! Please upload your match events CSV file from the sidebar to launch the tactical visualizer.")
    st.markdown("""
    ### 💡 Quick Guide to Parse your Sheet:
    Your tracking file is perfectly structured. When you upload it, the engine will automatically map:
    * **Event Types** to your specific playbook categories.
    * **Timestamp & Milliseconds** into instantaneous interactive video triggers.
    * **X & Y Coordinates** onto an elite standard data-provider pitch map layout.
    """)
