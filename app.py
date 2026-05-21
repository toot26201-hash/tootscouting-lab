import streamlit as st
import pandas as pd

# 1. إعداد الصفحة لتكون بعرض الشاشة بالكامل (Wide Mode)
st.set_page_config(
    page_title="TootScouting - Professional Video Analysis", 
    layout="wide"
)

# تصميم بسيط وتناسق الألوان
st.markdown("""
    <style>
    .block-container { padding-top: 2rem; }
    body { background-color: #0e1117; color: #ffffff; }
    </style>
""", unsafe_allow_html=True)

st.title("⚽ منصة TootScouting للتحليل الرقمي والفيديو")
st.markdown("---")

# 2. القائمة الجانبية (Sidebar) لرفع الملفات والروابط
st.sidebar.header("📁 مركز التحكم بالبيانات")
st.sidebar.markdown("---")

uploaded_file = st.sidebar.file_uploader("ارفع ملف أحداث المباراة (CSV)", type=["csv"])

# رابط الفيديو الافتراضي
video_url_input = st.sidebar.text_input(
    "رابط فيديو المباراة (YouTube / Direct Link)", 
    "https://www.youtube.com/watch?v=dQw4w9WgXcQ"
)

# 3. التحقق: هل المستخدم رفع ملف الـ CSV؟
if uploaded_file is not None:
    df = pd.read_csv(uploaded_file)
    
    # تنظيف الصفوف الفاضية في الأعمدة الأساسية
    if 'Event Type' in df.columns:
        df = df.dropna(subset=['Event Type'])
    
    st.sidebar.success("✅ تم تحميل ملفك الاحترافي بنجاح!")
    
    # 4. توحيد أسماء الأعمدة ديناميكياً لتتوافق مع ملف العميل
    # تحويل صيغة ملفك ليفهمها مشغل الفيديو
    if 'Event Type' in df.columns:
        df['event_type'] = df['Event Type']
    if 'Players' in df.columns:
        df['player'] = df['Players'].fillna('غير محدد')
    if 'Start (mm:ss)' in df.columns:
        df['timestamp'] = df['Start (mm:ss)']
    if 'Start (ms)' in df.columns:
        # تحويل الملي ثانية إلى ثواني كاملة للفيديو
        df['seconds'] = (df['Start (ms)'] / 1000).astype(int)

    # 5. فلاتر تكتيكية ذكية بناءً على داتا ملفك
    st.markdown("### 🔍 فلاتر تصفية اللقطات")
    col_f1, col_f2 = st.columns(2)
    
    with col_f1:
        if 'event_type' in df.columns:
            available_events = ["الكل"] + list(df['event_type'].dropna().unique())
            selected_event = st.selectbox("اختر نوع الحدث التكتيكي:", available_events)
        else:
            selected_event = "الكل"
        
    with col_f2:
        if 'player' in df.columns:
            available_players = ["الكل"] + list(df['player'].dropna().unique())
            selected_player = st.selectbox("اختر اللاعب المستهدف:", available_players)
        else:
            selected_player = "الكل"
            
    # تطبيق الفلاتر على الجدول
    filtered_df = df.copy()
    if selected_event != "الكل":
        filtered_df = filtered_df[filtered_df['event_type'] == selected_event]
    if selected_player != "الكل":
        filtered_df = filtered_df[filtered_df['player'] == selected_player]

    st.markdown("---")

    # 6. تقسيم مساحة العرض (فيديو يمين، وكروت الأحداث يسار)
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
        st.caption("اضغط على زر الفيديو لتحريك المشغل تلقائياً إلى وقت الحدث")
        
        if filtered_df.empty:
            st.info("لا توجد لقطات تطابق فلاتر البحث الحالية.")
        else:
            # عرض اللقطات في كروت أنيقة
            for index, row in filtered_df.iterrows():
                time_str = row.get('timestamp', '00:00')
                event_name = row.get('event_type', 'حدث غير مصنف')
                player_name = row.get('player', 'غير محدد')
                seconds_val = row.get('seconds', 0)
                tag_info = row.get('Tags', '')

                st.markdown(f"""
                <div style="background-color: #1e293b; padding: 12px; border-radius: 8px; margin-bottom: 8px; border-right: 4px solid #10b981; color: white;">
                    <span style="color: #10b981; font-weight: bold;">⏱️ {time_str}</span> | 
                    <strong>{event_name}</strong> <br>
                    <span style="color: #94a3b8; font-size: 13px;">اللاعب: {player_name}</span>
                    {f'<br><span style="color: #3b82f6; font-size: 12px;">تفاصيل: {tag_info}</span>' if pd.notna(tag_info) else ''}
                </div>
                """, unsafe_allow_html=True)
                
                if st.button("شاهد اللقطة 📹", key=f"btn_clip_{index}"):
                    st.session_state["current_clip_time"] = int(seconds_val)
                    st.rerun()

else:
    st.info("👋 مرحباً بك يا كابتن! يرجى رفع ملفك الحالي (Untitled-spreadsheet.csv) من القائمة الجانبية لبدء التحليل التفاعلي.")
