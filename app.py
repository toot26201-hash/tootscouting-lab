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

# 🔗 Connected Google Sheet Database ID (Line 25)
SPREADSHEET_ID = "1tv2bsiF7RLOIadzO_SBmB9RjnXqk0wzK"
SHEET_NAME = "Sheet1"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

# Video Registry (Match Name -> Video Link)
VIDEO_REGISTRY = {
    "NJS vs EPS": "https://www.youtube.com/watch?v=dQw4w9WgXcQ",
}

@st.cache_data(ttl=60) 
def load_database():
    try:
        # محاولة قراءة شيت جوجل مباشرة
        data = pd.read_csv(GOOGLE_SHEET_URL)
        if 'Event Type' in data.columns:
            return data.dropna(subset=['Event Type'])
        return data
    except Exception as e:
        # لو الشيت مش شغال لأي سبب، الكود يعمل شيت تجريبي عشان الموقع يفتح وميجبش خطأ
        return pd.DataFrame(columns=['Event Type', 'Players', 'Start (mm:ss)', 'Start (ms)', 'X Start', 'Y Start', 'X End', 'Y End', 'Match'])

df = load_database()

# لو الداتا لسه فاضية، هنعرض سطر تجريبي لحين تفعيل الشيت صح
if df.empty or 'Event Type' not in df.columns:
    df = pd.DataFrame([{
        'Event Type': 'Pass', 'Players': 'Example Player', 'Start (mm:ss)': '01:26', 
        'Start (ms)': 86970, 'X Start': 0.50, 'Y Start': 0.50, 'X End': 0.69, 'Y End': 0.50, 'Match': 'NJS vs EPS'
    }])

# توحيد المسميات للأعمدة
df['event_type'] = df['Event Type'].astype(str).str.strip()
df['player'] = df['Players'].fillna('Unknown Player')
df['timestamp'] = df['Start (mm:ss)']

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

# تطبيق الفلاتر
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
    active_video_url = VIDEO_REGISTRY.get(selected_match, "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
    st.video(f"{active_video_url}&t={start_time}s" if "youtube" in active_video_url else active_video_url, start_time=start_time)

with col_playlist:
    st.markdown(f"#### 📊 Cumulative Playlist ({len(filtered_df)} Clips)")
    if filtered_df.empty:
        st.warning("No clips found.")
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

# تنظيف الإحداثيات ورسمها لو موجودة
plot_df = filtered_df.dropna(subset=['X Start', 'Y Start'])
try:
    plot_df['X Start'] = pd.to_numeric(plot_df['X Start']) * 100
    plot_df['Y Start'] = pd.to_numeric(plot_df['Y Start']) * 100
    if 'X End' in plot_df.columns:
        plot_df['X End'] = pd.to_numeric(plot_df['X End']) * 100
        plot_df['Y End'] = pd.to_numeric(plot_df['Y End']) * 100
except:
    pass

if not plot_df.empty:
    passes_df = plot_df[plot_df['event_type'].str.lower() == 'pass']
    if not passes_df.empty and 'X End' in passes_df.columns:
        pitch.arrows(
            passes_df['X Start'], passes_df['Y Start'],
            passes_df['X End'], passes_df['Y End'], 
            color='#3b82f6', width=2.5, headwidth=4, headlength=4, ax=ax
        )
        
    other_df = plot_df[plot_df['event_type'].str.lower() != 'pass']
    if not other_df.empty:
        pitch.scatter(
            other_df['X Start'], other_df['Y Start'],
            color='#10b981', edgecolors='#ffffff', s=130, marker='o', ax=ax
        )
        
st.pyplot(fig)
