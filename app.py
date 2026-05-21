import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# 1. إعدادات الصفحة
st.set_page_config(page_title="TootScouting Hub", layout="wide")

st.title("⚽ TootScouting - Match Analysis Dashboard")
st.markdown("---")

# 📂 قراءة ملف الـ CSV المحلي المرفوع على جيت هاب بأمان
@st.cache_data(ttl=1)
def load_data():
    try:
        # الكود هيقرا الملف المحلي المرفوع
        data = pd.read_csv("match_data.csv")
        return data
    except:
        return pd.DataFrame()

raw_df = load_data()

# خط دفاع ديناميكي لتفادي الـ KeyError نهائياً وتحويل الأعمدة داخلياً
if not raw_df.empty:
    df = raw_df.copy()
    # تنظيف العناوين وتحويلها لحروف صغيرة لتسهيل المقارنة
    df.columns = df.columns.astype(str).str.strip().str.lower()
    
    # البحث عن الأعمدة بمسميات مرنة
    ev_col = next((c for c in df.columns if 'event' in c), df.columns[0])
    pl_col = next((c for c in df.columns if 'name' in c or 'player' in c), df.columns[1] if len(df.columns) > 1 else df.columns[0])
    tm_col = next((c for c in df.columns if 'mm:ss' in c or 'time' in c), df.columns[3] if len(df.columns) > 3 else df.columns[0])
    ms_col = next((c for c in df.columns if 'ms' in c), None)
    
    # تثبيت المسميات للكود الأصلي
    df['Event Type'] = df[ev_col]
    df['Name'] = df[pl_col]
    df['Start (mm:ss)'] = df[tm_col]
    df['Start (ms)'] = df[ms_col] if ms_col else 0
else:
    # داتا احتياطية لو الملف مش مقروء
    df = pd.DataFrame([{'Event Type': 'Pass', 'Name': 'Connecting...', 'Start (mm:ss)': '00:00', 'Start (ms)': 0, 'x start': 0.5, 'y start': 0.5}])

# 2. الفلاتر الأساسية
col1, col2 = st.columns(2)
with col1:
    event_types = ["All"] + list(df['Event Type'].dropna().unique())
    selected_event = st.selectbox("Select Event Type", event_types)
with col2:
    players = ["All"] + list(df['Name'].dropna().unique())
    selected_player = st.selectbox("Select Player", players)

# تصفية البيانات
filtered_df = df.copy()
if selected_event != "All":
    filtered_df = filtered_df[filtered_df['Event Type'] == selected_event]
if selected_player != "All":
    filtered_df = filtered_df[filtered_df['Name'] == selected_player]

st.markdown("---")

# 3. تقسيم الشاشة: الفيديو والقائمة
col_video, col_playlist = st.columns([1.5, 1])

with col_video:
    st.markdown("### 🎥 Match Video")
    current_time = st.session_state.get("video_time", 0)
    
    # 🔗 رابط التشغيل المباشر من جوجل درايف الخاص بك
    VIDEO_URL = "https://docs.google.com/uc?export=download&id=16dhBkjeXxmitljigQgFmz1MX-Jsu2An_"
    st.video(VIDEO_URL, start_time=current_time)

with col_playlist:
    st.markdown(f"### 📊 Event Playlist ({len(filtered_df)} Clips)")
    for index, row in filtered_df.head(15).iterrows():
        ms_val = row.get('Start (ms)', 0)
        seconds = int(pd.to_numeric(ms_val, errors='coerce') / 1000) if not pd.isna(ms_val) else 0
        
        col_text, col_btn = st.columns([3, 1])
        with col_text:
            st.markdown(f"⏱️ **{row['Start (mm:ss)']}** | {row['Event Type']} - {row['Name']}")
        with col_btn:
            if st.button("Watch", key=f"play_{index}"):
                st.session_state["video_time"] = seconds
                st.rerun()

st.markdown("---")

# 4. الملعب التكتيكي
st.markdown("### 🏟️ Tactical Pitch Map")
pitch = Pitch(pitch_type='opta', pitch_color='#0f172a', line_color='#334155')
fig, ax = pitch.draw(figsize=(10, 7))
fig.patch.set_facecolor('#0f172a')

# تحديد أعمدة الإحداثيات آلياً بحروف صغيرة
x1 = next((c for c in filtered_df.columns if 'x start' in c or 'x_start' in c), None)
y1 = next((c for c in filtered_df.columns if 'y start' in c or 'y_start' in c), None)
x2 = next((c for c in filtered_df.columns if 'x end' in c or 'x_end' in c), None)
y2 = next((c for c in filtered_df.columns if 'y end' in c or 'y_end' in c), None)

if x1 and y1:
    for index, row in filtered_df.iterrows():
        if pd.isna(row[x1]) or pd.isna(row[y1]):
            continue
            
        x_start = float(pd.to_numeric(row[x1], errors='coerce')) * 100
        y_start = float(pd.to_numeric(row[y1], errors='coerce')) * 100
        
        if str(row['Event Type']).strip().lower() == 'pass' and x2 and not pd.isna(row[x2]):
            x_end = float(pd.to_numeric(row[x2], errors='coerce')) * 100
            y_end = float(pd.to_numeric(row[y2], errors='coerce')) * 100
            pitch.arrows(x_start, y_start, x_end, y_end, color='#3b82f6', width=2, headwidth=4, ax=ax)
        else:
            pitch.scatter(x_start, y_start, color='#10b981', s=100, edgecolors='#ffffff', ax=ax)

st.pyplot(fig)
