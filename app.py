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

# 🔗 Connected Google Sheet Database ID (Your Live ID)
SPREADSHEET_ID = "1tmE0yxj-KiNZiu8OsP1eQnFzl9YyxK4vXkROGgfejVI"
# الكود هيقرأ أول شيت تلقائياً عن طريق الـ gid=0 من غير ما نسأل عن اسمه
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/export?format=csv&gid=0"

@st.cache_data(ttl=10) 
def load_database():
    try:
        # قراءة الشيت مباشرة بالسلسلة الذكية
        data = pd.read_csv(GOOGLE_SHEET_URL)
        return data
    except Exception as e:
        return pd.DataFrame()

df = load_database()

# لو الداتا لسه مش مقروءة، هنا خط الدفاع التجريبي
if df.empty or 'Event Type' not in df.columns:
    df = pd.DataFrame([{
        'Event Type': 'Pass', 'Players': 'Example Player', 'Start (mm:ss)': '01:26', 
        'Start (ms)': 86970, 'X Start': 0.50, 'Y Start': 0.50, 'X End': 0.69, 'Y End': 0.50, 'Match': 'NJS vs EPS'
    }])

# توحيد المسميات للأعمدة والمسافات
df.columns = df.columns.str.strip()
df['event_type'] = df['Event Type'].astype(str).str.strip()
df['player'] = df['Players'].fillna('Unknown Player')
df['timestamp'] = df['Start (mm:ss)']

if 'Match' not in df.columns:
    df['Match'] = 'NJS vs EPS'
    
if 'Start (ms)' in df.columns:
    df['seconds'] = (pd.to_numeric(df['Start (ms)'], errors='coerce') / 1000).fillna(0).astype(int)

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
    st.video(f"https://www.youtube.com/watch?v=dQw4w9WgXcQ&t={start_time}s", start_time=start_time)

with col_playlist:
    st.markdown(f"#### 📊 Cumulative Playlist ({len(filtered_df)} Clips)")
    if filtered_df.empty or filtered_df.iloc[0]['player'] == 'Example Player':
        st.warning("Connecting to Live Sheet... If this takes too long, please double check sheet headers match 'Event Type' and 'Players'.")
    
    for index, row in filtered_df.head(15).iterrows():
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

# تنظيف ورسم الإحداثيات الحقيقية
if 'X Start' in filtered_df.columns and 'Y Start' in filtered_df.columns:
    plot_df = filtered_df.dropna(subset=['X Start', 'Y Start'])
    try:
        plot_df['X Start'] = pd.to_numeric(plot_df['X Start'], errors='coerce') * 100
        plot_df['Y Start'] = pd.to_numeric(plot_df['Y Start'], errors='coerce') * 100
        if 'X End' in plot_df.columns:
            plot_df['X End'] = pd.to_numeric(plot_df['X End'], errors='coerce') * 100
            plot_df['Y End'] = pd.to_numeric(plot_df['Y End'], errors='coerce') * 100
        
        # رسم أسهم التمريرات
        passes_df = plot_df[plot_df['event_type'].str.lower() == 'pass']
        if not passes_df.empty and 'X End' in passes_df.columns:
            pitch.arrows(
                passes_df['X Start'], passes_df['Y Start'],
                passes_df['X End'], passes_df['Y End'], 
                color='#3b82f6', width=2.5, headwidth=4, headlength=4, ax=ax
            )
            
        # رسم باقي الأحداث
        other_df = plot_df[plot_df['event_type'].str.lower() != 'pass']
        if not other_df.empty:
            pitch.scatter(
                other_df['X Start'], other_df['Y Start'],
                color='#10b981', edgecolors='#ffffff', s=130, marker='o', ax=ax
            )
    except:
        pass
        
st.pyplot(fig)
