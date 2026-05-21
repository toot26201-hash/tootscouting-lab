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

# تأمين وجود البيانات وتجهيز الأعمدة لملفك الحقيقي
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

# إدارة وقت الفيديو في الـ session_state لمنع إعادة التشغيل من الأول
if "video_seconds" not in st.session_state:
    st.session_state["video_seconds"] = 0

with col_video:
    st.markdown("### 🎥 Match Video Player")
    
    current_seconds = st.session_state["video_seconds"]
    embed_url = f"https://drive.google.com/file/d/{VIDEO_ID}/preview?t={current_seconds}s"
    
    # عرض مشغل الفيديو في نفس الصفحة وتحديثه ديناميكياً
    st.components.v1.html(
        f'<iframe src="{embed_url}" width="100%" height="400" allow="autoplay; encrypted-media" allowfullscreen></iframe>',
        height=410
    )
    st.caption(f"⏱️ التوقيت الحالي: {int(current_seconds // 60)}:{int(current_seconds % 60):02d}")

with col_playlist:
    st.markdown(f"### 📊 Event Playlist ({len(filtered_df)} Clips)")
    
    # عرض اللقطات المطابقة للفلاتر
    for index, row in filtered_df.head(20).iterrows():
        ms = row.get('Start (ms)', 0)
        seconds = int(float(ms) / 1000) if not pd.isna(ms) else 0
        
        col_text, col_btn = st.columns([3, 1])
        with col_text:
            st.markdown(f"⏱️ **{row['Start (mm:ss)']}** | {row['Event Type']} - {row['Players']}")
        with col_btn:
            if st.button("Watch", key=f"play_{index}"):
                st.session_state["video_seconds"] = seconds
                st.rerun()

st.markdown("---")

# 4. الملعب التكتيكي (أسطر مضغوطة وقصيرة ومحمية من القطع)
st.markdown("### 🏟️ Tactical Pitch Map")
pitch = Pitch(pitch_type='opta', pitch_color='#0f172a', line_color='#334155')
fig, ax = pitch.draw(figsize=(10, 7))
fig.patch.set_facecolor('#0f172a')

for index, row in filtered_df.iterrows():
    if pd.isna(row['X Start']) or pd.isna(row['Y Start']): continue
    
    xs = float(row['X Start']) * 100
    ys = float(row['Y Start']) * 100
    is_pass = str(row['Event Type']).strip().lower() == 'pass'
    
    if is_pass and not pd.isna(row['X End']):
        xe = float(row['X End']) * 100
        ye = float(row['Y End']) * 100
        pitch.arrows(xs, ys, xe, ye, color='#3b82f6', width=2, headwidth=4, ax=ax)
    else:
        # سطر مضغوط تماماً بدون نزول لسطر جديد لمنع الـ SyntaxError
        pitch.scatter(xs, ys, color='#10b981', s=100, edgecolors='#ffffff', ax=ax)

st.pyplot(fig)
