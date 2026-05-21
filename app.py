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

# داتا الـ Example Player الافتراضية ثابتة وجاهزة للعرض الفوري
demo_data = [
    {'Event Type': 'Pass', 'Players': 'Example Player (Goalkeeper)', 'Start (mm:ss)': '01:15', 'Start (ms)': 75000, 'X Start': 0.15, 'Y Start': 0.50, 'X End': 0.45, 'Y End': 0.20, 'Match': 'NJS vs EPS'},
    {'Event Type': 'Pass', 'Players': 'Example Player (Goalkeeper)', 'Start (mm:ss)': '02:40', 'Start (ms)': 160000, 'X Start': 0.10, 'Y Start': 0.45, 'X End': 0.65, 'Y End': 0.80, 'Match': 'NJS vs EPS'},
    {'Event Type': 'Pass', 'Players': 'Example Player (Goalkeeper)', 'Start (mm:ss)': '04:12', 'Start (ms)': 252000, 'X Start': 0.20, 'Y Start': 0.55, 'X End': 0.55, 'Y End': 0.52, 'Match': 'Match 2'},
    {'Event Type': 'Shot', 'Players': 'Example Striker', 'Start (mm:ss)': '05:30', 'Start (ms)': 330000, 'X Start': 0.88, 'Y Start': 0.48, 'X End': 1.00, 'Y End': 0.50, 'Match': 'NJS vs EPS'},
    {'Event Type': 'Interception', 'Players': 'Example Defender', 'Start (mm:ss)': '07:18', 'Start (ms)': 438000, 'X Start': 0.35, 'Y Start': 0.70, 'X End': 0.35, 'Y End': 0.70, 'Match': 'Match 2'}
]

df = pd.DataFrame(demo_data)

# توحيد مسميات الأعمدة داخلياً للكود
df.columns = df.columns.str.strip()
df['event_final'] = df['Event Type'].astype(str).str.strip()
df['player_final'] = df['Players'].fillna('Unknown Player')
df['timestamp'] = df['Start (mm:ss)']
df['seconds'] = (df['Start (ms)'] / 1000).astype(int)

if 'Match' not in df.columns:
    df['Match'] = 'NJS vs EPS'

# 2. Strategic Filters Section
st.markdown("### 🔍 Multi-Match Analytics Filters (Demo Mode)")
col_f1, col_f2, col_f3 = st.columns(3)

with col_f1:
    available_matches = ["All Matches"] + list(df['Match'].unique())
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
    filtered_df = filtered_df[filtered_df['Match'] == selected_match]
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
    # تشغيل فيديو يوتيوب الافتراضي متزامن بالثانية
    st.video(f"https://www.youtube.com/watch?v=dQw4w9WgXcQ&t={start_time}s", start_time=start_time)

with col_playlist:
    st.markdown(f"#### 📊 Cumulative Playlist ({len(filtered_df)} Clips)")
    
    for index, row in filtered_df.iterrows():
        col_card, col_btn = st.columns([3.5, 1])
        with col_card:
            st.markdown(f"""
            <div style="background-color: #1e293b; padding: 10px; border-radius: 6px; border-left: 4px solid #3b82f6; margin-bottom: 5px;">
                <span style="color: #3b82f6; font-weight: bold; font-size: 11px;">{row['Match']} | ⏱️ {row['timestamp']}</span><br>
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

# ضرب الإحداثيات في 100 لتتناسب مع ملعب أوبتا
plot_df = filtered_df.copy()
plot_df['X Start'] = plot_df['X Start'] * 100
plot_df['Y Start'] = plot_df['Y Start'] * 100
plot_df['X End'] = plot_df['X End'] * 100
plot_df['Y End'] = plot_df['Y End'] * 100

if not plot_df.empty:
    # رسم التمريرات بأسهم
    passes_df = plot_df[plot_df['event_final'].str.lower() == 'pass']
    if not passes_df.empty:
        pitch.arrows(
            passes_df['X Start'], passes_df['Y Start'],
            passes_df['X End'], passes_df['Y End'], 
            color='#3b82f6', width=2.5, headwidth=4, headlength=4, ax=ax
        )
        
    # رسم باقي الأحداث كنقاط
    other_df = plot_df[plot_df['event_final'].str.lower() != 'pass']
    if not other_df.empty:
        pitch.scatter(
            other_df['X Start'], other_df['Y Start'],
            color='#10b981', edgecolors='#ffffff', s=130, marker='o', ax=ax
        )
        
st.pyplot(fig)
