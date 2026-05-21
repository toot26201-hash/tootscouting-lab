import streamlit as st
import pandas as pd

# إعداد الصفحة لتكون بعرض الشاشة بالكامل
st.set_page_config(page_title="TootScouting - Video Analysis Platform", layout="wide")

st.markdown("<style>.block-container { padding-top: 2rem; }</style>", unsafe_allow_html=True)
st.title("⚽ منصة TootScouting للتحليل الرقمي والفيديو")
st.markdown("---")

# القائمة الجانبية
st.sidebar.header("📁 مركز التحكم بالبيانات")
st.sidebar.markdown("---")

# استقبال ملف الأحداث ورابط الفيديو
uploaded_file = st.sidebar.file_uploader("ارفع ملف أحداث المباراة (CSV)", type=["csv"])
video_url_input = st.sidebar.text_input(
    "رابط فيديو المباراة (YouTube / Direct Link)", 
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
)

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    st.sidebar.success("✅ تم تحميل بيانات المباراة بنجاح!")
    
    st.markdown("### 🔍 فلاتر تصفية اللقطات")
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        event_col = 'event_type' if 'event_type' in df.columns else (df.columns[1] if len(df.columns) > 1 else None)
        selected_event = st.selectbox("اختر نوع الحدث التكتيكي:", ["الكل"] + list(df[event_col].dropna().unique()) if event_col else ["الكل"])
        
    with col_f2:
        player_col = 'player' if 'player' in df.columns else (df.columns[2] if len(df.columns) > 2 else None)
        selected_player = st.selectbox("اختر اللاعب المستهدف:", ["الكل"] + list(df[player_col].dropna().unique()) if player_col else ["الكل"])
            
    filtered_df = df.copy()
    if selected_event != "الكل" and event_col:
        filtered_df = filtered_df[filtered_df[event_col] == selected_event]
    if selected_player != "الكل" and player_col:
        filtered_df = filtered_df[filtered_df[player_col] == selected_player]

    st.markdown("---")
    col_video, col_events = st.columns([1.3, 1])

    with col_video:
        st.markdown("#### 🎥 مشغل الفيديو التفاعلي")
        start_time = st.session_state.get("current_clip_time", 0)
        final_video_url = f"{video_url_input}?t={start_time}"
        st.video(final_video_url, start_time=start_time)
        if start_time > 0:
            st.success(f"▶️ يعرض الآن اللقطة عند التوقيت: {start_time} ثانية")

    with col_events:
        st.markdown(f"#### 📊 اللقطات المستخرجة ({len(filtered_df)} لقطة)")
        if filtered_df.empty:
            st.info("لا توجد لقطات تطابق فلاتر البحث.")
        else:
            for index, row in filtered_df.iterrows():
                time_str = row.get('timestamp', '00:00')
                event_name = row.get('event_type', 'حدث غير مصنف')
                player_name = row.get('player', 'غير محدد')
                seconds_val = row.get('seconds', 0)
                team_name = row.get('team', '')

                st.markdown(f"""
                <div style="background-color: #1e293b; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-right: 4px solid #10b981; color: white;">
                    <span style="color: #10b981; font-weight: bold;">⏱️ {time_str}</span> | 
                    <strong>{event_name}</strong> {f'- {team_name}' if team_name else ''} <br>
                    <span style="color: #94a3b8; font-size: 13px;">اللاعب: {player_name}</span>
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("شاهد اللقطة 📹", key=f"btn_clip_{index}"):
                    st.session_state["current_clip_time"] = int(seconds_val)
                    st.rerun()
else:
    st.info("👋 مرحباً بك يا كابتن! يرجى رفع ملف أحداث المباراة (CSV) من القائمة الجانبية لبدء التحليل.")
    st.markdown("""
    ### 💡 كيف تجهز ملف الـ CSV؟
    تأكد أن ملف الإكسيل يحتوي على الأعمدة التالية بنفس الأسماء قبل حفظه بصيغة CSV:
    * `timestamp` (توقيت اللقطة مثل 14:20)
    * `event_type` (نوع الحدث مثل High Press)
    * `player` (اسم اللاعب)
    * `seconds` (التوقيت بالثواني من بداية الفيديو، مثلاً الدقيقة 2 تُكتب 120)
    """)