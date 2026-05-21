import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# 1. Page Configuration
st.set_page_config(page_title="TootScouting - Central Database", layout="wide")

st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    body { background-color: #0f172a; color: #f8fafc; }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ TootScouting - Central Match Database")
st.markdown("<p style='color: #64748b; font-size: 16px;'>Historical data tracking and multi-match analysis hub.</p>", unsafe_allow_html=True)
st.markdown("---")

# 📊 ربط جوجل شيتس (حط الـ ID بتاع ملفك هنا)
# أنا حاطط رابط افتراضي، غير الـ ID ده بالـ ID بتاع ملفك الحقيقي
SPREADSHEET_ID = "1NzVsnv2g3_FvXZ_N_XmZEm4_5gNpx78f5_example" 
SHEET_NAME = "Sheet1"
GOOGLE_SHEET_URL = f"https://docs.google.com/spreadsheets/d/{SPREADSHEET_ID}/gviz/tq?tqx=out:csv&sheet={SHEET_NAME}"

@st.cache_data(ttl=600) # بيحفظ الداتا في الذاكرة لمدة 10 دقائق عشان الموقع يبقى طيارة
def load_historical_data():
    try:
        data = pd.read_csv(GOOGLE_SHEET_URL)
        return data.dropna(subset=['Event Type'])
    except Exception as e:
        st.error("Connection to Database failed. Please check your Spreadsheet ID.")
        return pd.DataFrame()

df = load_historical_data()

if not df.empty:
    # توحيد الأعمدة
    df['event_type'] = df['Event Type'].str.strip()
    df['player'] = df['Players'].fillna('Unknown Player')
    df['timestamp'] = df['Start (mm:ss)']
    # إضافة عمود للمباراة لو مش موجود بشكل افتراضي للتجربة
    if 'Match' not in df.columns:
        df['Match'] = 'Match 1' # لو عندك عمود للماتشات سمّيه Match في الشيت
    
    if 'Start (ms)' in df.columns:
        df['seconds'] = (df['Start (ms)'] / 1000).astype(int)

    # 2. الفلاتر الاستراتيجية (Multi-Match Filters)
    st.markdown("### 🔍 Multi-Match Analytics Filters")
    col_f1, col_f2, col_f3 = st.columns(3)
    
    with col_f1:
        # هنا يقدر يختار ماتش معين أو يشوف الـ 7 ماتشات مع بعض!
        available_matches = ["All Matches"] + list(df['Match'].unique())
        selected_match = st.selectbox("Select Match/Timeline:", available_matches)
        
    with col_f2:
        available_events = ["All Events"] + list(df['event_type'].unique())
        selected_event = st.selectbox("Select Event Type:", available_events)
        
    with col_f3:
        available_players = ["All Players"] + list(df['player'].unique())
        selected_player = st.selectbox("Select Target Player (e.g. Goalkeeper):", available_players)

    # تطبيق الفلاتر التراكمية
    filtered_df = df.copy()
    if selected_match != "All Matches":
        filtered_df = filtered_df[filtered_df['Match'] == selected_match]
    if selected_event != "All Events":
        filtered_df = filtered_df[filtered_df['event_type'] == selected_event]
    if selected_player != "All Players":
        filtered_df = filtered_df[filtered_df['player'] == selected_player]

    st.markdown("---")

    # 3. العرض: الفيديو والـ Playlist والملعب
    col_video, col_playlist = st.columns([1.4, 1])
    
    with col_video:
        st.markdown("#### 🎥 Video Analysis Player")
        # تنبيه للمدرب لو اختار كل الماتشات إن الفيديو هيشتغل لآخر ماتش تم اختياره
        start_time = st.session_state.get("current_clip_time", 0)
        video_url_input = st.sidebar.text_input("Active Match Video URL", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")
        st.video(f"{video_url_input}?t={start_time}", start_time=start_time)

    with col_playlist:
        st.markdown(f"#### 📊 Cumulative Playlist ({len(filtered_df)} Actions)")
        if filtered_df.empty:
            st.warning("No data found for this combination.")
        else:
            # عرض أول 6 أحداث
            for index, row in filtered_df.head(6).iterrows():
                col_card, col_btn = st.columns([3.5, 1])
                with col_card:
                    st.markdown(f"""
                    <div style="background-color: #1e293b; padding: 8px; border-radius: 6px; border-left: 4px solid #10b981; margin-bottom: 4px;">
                        <span style="color: #10b981; font-weight: bold; font-size: 11px;">{row['Match']} | ⏱️ {row['timestamp']}</span><br>
                        <strong style="color: #f1f5f9; font-size: 13px;">{row['event_type']} - {row['player']}</strong>
                    </div>
                    """, unsafe_allow_html=True)
                with col_btn:
                    st.markdown("<div style='padding-top: 6px;'></div>", unsafe_allow_html=True)
                    if st.button("👁️ Watch", key=f"btn_p_{index}"):
                        st.session_state["current_clip_time"] = int(row['seconds'])
                        st.rerun()

    st.markdown("---")
    
    # 4. خريطة الملعب التراكمية (هنا السحر لـ 7 مباريات)
    st.markdown(f"#### 🏟️ Cumulative Pitch Map | Showing {len(filtered_df)} actions across selection")
    
    pitch = Pitch(pitch_type='opta', pitch_color='#0f172a', line_color='#334155', linewidth=2)
    fig, ax = pitch.draw(figsize=(10, 6))
    fig.patch.set_facecolor('#0f172a')
    
    plot_df = filtered_df.dropna(subset=['X Start', 'Y Start'])
    
    if not plot_df.empty:
        # رسم التمريرات بأسهم
        passes_df = plot_df[plot_df['event_type'].str.lower() == 'pass']
        if not passes_df.empty:
            pitch.arrows(
                passes_df['X Start']*100, passes_df['Y Start']*100,
                passes_df['X End']*100, passes_df['Y End']*100, 
                color='#3b82f6', width=2, headwidth=4, headlength=4, ax=ax
            )
            
        # رسم باقي الأحداث كنقاط
        other_df = plot_df[plot_df['event_type'].str.lower() != 'pass']
        if not other_df.empty:
            pitch.scatter(
                other_df['X Start']*100, other_df['Y Start']*100,
                color='#10b981', edgecolors='#ffffff', s=100, marker='o', ax=ax
            )
            
    st.pyplot(fig)
