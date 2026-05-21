import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch
import os

# 1. إعدادات الصفحة
st.set_page_config(page_title="TootScouting Hub", layout="wide")

st.title("⚽ TootScouting - Match Analysis Dashboard")
st.markdown("---")

# 📂 قراءة ملف الـ CSV أوتوماتيكياً
@st.cache_data(ttl=1)
def load_data():
    try:
        files = [f for f in os.listdir('.') if f.endswith('.csv')]
        if files:
            data = pd.read_csv(files[0])
            data.columns = data.columns.astype(str).str.strip()
            return data
        return pd.DataFrame()
    except:
        return pd.DataFrame()

df = load_data()

if not df.empty:
    event_types = ["All"] + list(df['Event Type'].dropna().unique())
    selected_event = st.selectbox("Select Event Type", event_types)
    
    players_list = ["All"] + list(df['Players'].dropna().unique())
    selected_player = st.selectbox("Select Player", players_list)

    filtered_df = df.copy()
    if selected_event != "All": filtered_df = filtered_df[filtered_df['Event Type'] == selected_event]
    if selected_player != "All": filtered_df = filtered_df[filtered_df['Players'] == selected_player]
else:
    st.warning("⚠️ لم يتم العثور على أي ملف CSV في المستودع!")
    st.stop()

st.markdown("---")

# 3. تقسيم الشاشة: الفيديو والقائمة
col_video, col_playlist = st.columns([1.5, 1])

# ID الفيديو الثابت الخاص بك على جوجل درايف
VIDEO_ID = "16dhBkjeXxmitljigQgFmz1MX-Jsu2An_"

# إدارة وقت البداية والنهاية في الـ session_state
if "start_seconds" not in st.session_state: st.session_state["start_seconds"] = 0
if "end_seconds" not in st.session_state: st.session_state["end_seconds"] = 10

with col_video:
    st.markdown("### 🎥 Match Video Player")
    
    start_s = st.session_state["start_seconds"]
    end_s = st.session_state["end_seconds"]
    
    # رابط تحميل مباشر يخلي بايثون يتحكم في الميديا بالملي
    direct_video_url = f"https://docs.google.com/uc?export=download&id={VIDEO_ID}"
    
    # مشغل بايثون الأصلي اللي هيبدأ ويقف إجباري
    st.video(direct_video_url, start_time=start_s)
    
    # تنبيه ذكي للمحلل بمدة اللقطة
    st.warning(f"⏱️ لقطة مستهدفة: الكليب يمتد من الثانية {start_s} إلى الثانية {end_s} (يرجى إيقاف الفيديو يدوياً عند انتهاء اللقطة لو استمر)")

with col_playlist:
    st.markdown(f"### 📊 Event Playlist ({len(filtered_df)} Clips)")
    
    for index, row in filtered_df.head(20).iterrows():
        start_ms = row.get('Start (ms)', 0)
        stop_ms = row.get('Stop (ms)', start_ms + 5000)
        
        sec_start = int(pd.to_numeric(start_ms, errors='coerce') / 1000) if not pd.isna(start_ms) else 0
        sec_stop = int(pd.to_numeric(stop_ms, errors='coerce') / 1000) if not pd.isna(stop_ms) else sec_start + 5
        
        col_text, col_btn = st.columns([3, 1])
        with col_text:
            st.markdown(f"⏱️ **{row['Start (mm:ss)']}** | {row['Event Type']} - {row['Players']}")
        with col_btn:
            if st.button("Watch", key=f"play_{index}"):
                st.session_state["start_seconds"] = sec_start
                st.session_state["end_seconds"] = sec_stop
                st.rerun()

st.markdown("---")

# 4. الملعب التكتيكي
st.markdown("### 🏟️ Tactical Pitch Map")
pitch = Pitch(pitch_type='opta', pitch_color='#0f172a', line_color='#334155')
fig, ax = pitch.draw(figsize=(10, 7))
fig.patch.set_facecolor('#0f172a')

for index, row in filtered_df.iterrows():
    if pd.isna(row['X Start']) or pd.isna(row['Y Start']): continue
    xs, ys = float(row['X Start']) * 100, float(row['Y Start']) * 100
    if str(row['Event Type']).strip().lower() == 'pass' and not pd.isna(row['X End']):
        xe, ye = float(row['X End']) * 100, float(row['Y End']) * 100
        pitch.arrows(xs, ys, xe, ye, color='#3b82f6', width=2, headwidth=4, ax=ax)
    else:
        pitch.scatter(xs, ys, color='#10b981', s=100, edgecolors='#ffffff', ax=ax)
st.pyplot(fig)
