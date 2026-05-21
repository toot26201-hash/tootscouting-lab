import streamlit as st
import pandas as pd
import matplotlib.pyplot as plt
from mplsoccer import Pitch

# 1. إعداد الصفحة
st.set_page_config(page_title="TootScouting Lab - Mplsoccer", layout="wide")

st.markdown("<style>.block-container { padding-top: 2rem; } body { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)
st.title("⚽ منصة TootScouting للتحليل التكتيكي المطور")
st.markdown("---")

# 2. القائمة الجانبية
st.sidebar.header("📁 مركز التحكم بالبيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف أحداث المباراة (CSV)", type=["csv"])
video_url_input = st.sidebar.text_input("رابط فيديو المباراة", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file).dropna(subset=['Event Type'])
    st.sidebar.success("✅ تم تحميل البيانات بنجاح!")
    
    # توحيد البيانات ديناميكياً من ملفك
    df['event_type'] = df['Event Type'].str.strip()
    df['player'] = df['Players'].fillna('غير محدد')
    df['timestamp'] = df['Start (mm:ss)']
    if 'Start (ms)' in df.columns:
        df['seconds'] = (df['Start (ms)'] / 1000).astype(int)

    # 3. الفلاتر التكتيكية
    st.markdown("### 🔍 فلاتر تصفية اللقطات والداتا")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_event = st.selectbox("اختر الحدث الفني:", ["الكل"] + list(df['event_type'].unique()))
    with col_f2:
        selected_player = st.selectbox("اختر اللاعب:", ["الكل"] + list(df['player'].unique()))
            
    filtered_df = df.copy()
    if selected_event != "الكل":
        filtered_df = filtered_df[filtered_df['event_type'] == selected_event]
    if selected_player != "الكل":
        filtered_df = filtered_df[filtered_df['player'] == selected_player]

    st.markdown("---")

    # 4. النصف العلوي: الفيديو والكروت
    col_video, col_events = st.columns([1.3, 1])
    
    with col_video:
        st.markdown("#### 🎥 مشغل الفيديو التفاعلي")
        start_time = st.session_state.get("current_clip_time", 0)
        st.video(f"{video_url_input}?t={start_time}", start_time=start_time)
        if start_time > 0:
            st.success(f"▶️ لقطة التوقيت الحالي: {start_time} ثانية")

    with col_events:
        st.markdown(f"#### 📊 قائمة اللقطات المتاحة ({len(filtered_df)})")
        # عرض أول 8 لقطات لتوفير مساحة الرؤية
        display_df = filtered_df.head(8)
        for index, row in display_df.iterrows():
            col_card, col_btn = st.columns([3, 1])
            with col_card:
                st.markdown(f"""
                <div style="background-color: #1e293b; padding: 6px; border-radius: 5px; border-right: 3px solid #10b981; color: white; font-size:13px;">
                    <strong>⏱️ {row['timestamp']}</strong> | {row['event_type']} - {row['player']}
                </div>
                """, unsafe_allow_html=True)
            with col_btn:
                if st.button("شاهد 📹", key=f"btn_{index}"):
                    st.session_state["current_clip_time"] = int(row['seconds'])
                    st.rerun()

    st.markdown("---")
    
    # 5. النصف السفلي: رسم ملعب Opta الاحترافي عبر mplsoccer
    st.markdown("#### 🏟️ خريطة التحليل التكتيكي (Opta Pitch Design)")
    
    # تجهيز الملعب بأبعاد Opta وألوان احترافية (خلفية داكنة متناسقة مع الموقع)
    pitch = Pitch(pitch_type='opta', pitch_color='#1e242b', line_color='#f8fafc', linewidth=2)
    fig, ax = pitch.draw(figsize=(10, 7))
    
    # فلترة الصفوف الجاهزة للرسم وتواجد الإحداثيات فيها
    plot_df = filtered_df.dropna(subset=['X Start', 'Y Start'])
    
    if not plot_df.empty:
        # ضرب الإحداثيات في 100 لأن داتا ملفك من 0 لـ 1 وملعب Opta من 0 لـ 100
        x_start = plot_df['X Start'] * 100
        y_start = plot_df['Y Start'] * 100
        
        # تفكيك الأحداث: تمريرات لوحدها، وباقي الأحداث (مثل التسديدات أو الضغط) لوحدها
        passes_df = plot_df[plot_df['event_type'].str.lower() == 'pass']
        other_events_df = plot_df[plot_df['event_type'].str.lower() != 'pass']
        
        # 1. رسم التمريرات بأسهم (خطوط ممتدة من البداية للنهاية)
        if not passes_df.empty:
            x_end = passes_df['X End'] * 100
            y_end = passes_df['Y End'] * 100
            pitch.arrows(
                passes_df['X Start']*100, passes_df['Y Start']*100,
                x_end, y_end, 
                color='#3b82f6', width=2, headwidth=4, headlength=4,
                ax=ax, label='Passes'
            )
            
        # 2. رسم باقي الأحداث (Shots, Pressing, etc.) كنقاط مضيئة على الملعب
        if not other_events_df.empty:
            pitch.scatter(
                other_events_df['X Start']*100, other_events_df['Y Start']*100,
                color='#10b981', edgecolors='white', s=120, marker='o',
                ax=ax, label='Other Events'
            )
            
            # إضافة أسماء اللاعبين فوق النقطة في الملعب بشكل خفيف
            for idx, row in other_events_df.iterrows():
                ax.text(
                    row['X Start']*100, row['Y Start']*100 + 1.5, 
                    row['player'].split()[-1], # اسم عائلة اللاعب فقط لمنع زحمة الملعب
                    color='#94a3b8', fontsize=9, ha='center'
                )

    # عرض رسمة الـ mplsoccer الاحترافية داخل الـ Streamlit
    st.pyplot(fig)

else:
    st.info("👋 يرجى رفع ملف أحداث المباراة (CSV) لتوليد خريطة الملعب الاحترافية.")
