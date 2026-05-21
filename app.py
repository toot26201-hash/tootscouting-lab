import streamlit as st
import pandas as pd
import plotly.graph_objects as go

# 1. إعداد الصفحة
st.set_page_config(page_title="TootScouting Lab - Analytics", layout="wide")

st.markdown("<style>.block-container { padding-top: 2rem; } body { background-color: #0e1117; color: white; }</style>", unsafe_allow_html=True)
st.title("⚽ منصة TootScouting للتحليل الرقمي وخريطة الملعب التفاعلية")
st.markdown("---")

# 2. القائمة الجانبية
st.sidebar.header("📁 مركز التحكم بالبيانات")
uploaded_file = st.sidebar.file_uploader("ارفع ملف أحداث المباراة (CSV)", type=["csv"])
video_url_input = st.sidebar.text_input("رابط فيديو المباراة", "https://www.youtube.com/watch?v=dQw4w9WgXcQ")

if uploaded_file is not None:
    df = pd.read_csv(uploaded_file).dropna(subset=['Event Type'])
    st.sidebar.success("✅ تم تحميل البيانات بنجاح!")
    
    # توحيد البيانات ديناميكياً من ملفك
    df['event_type'] = df['Event Type']
    df['player'] = df['Players'].fillna('غير محدد')
    df['timestamp'] = df['Start (mm:ss)']
    if 'Start (ms)' in df.columns:
        df['seconds'] = (df['Start (ms)'] / 1000).astype(int)

    # 3. الفلاتر
    st.markdown("### 🔍 فلاتر تصفية اللقطات والداتا")
    col_f1, col_f2 = st.columns(2)
    with col_f1:
        selected_event = st.selectbox("اختر الحدث التكتيكي:", ["الكل"] + list(df['event_type'].unique()))
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
        st.markdown("#### 🎥 مشغل الفيديو")
        start_time = st.session_state.get("current_clip_time", 0)
        st.video(f"{video_url_input}?t={start_time}", start_time=start_time)
        if start_time > 0:
            st.success(f"▶️ لقطة التوقيت الحالي: {start_time} ثانية")

    with col_events:
        st.markdown(f"#### 📊 قائمة اللقطات ({len(filtered_df)})")
        # قصر العرض على أول 5 لقطات عشان المساحة وتحتها الخريطة
        display_df = filtered_df.head(10)
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
    
    # 5. النصف السفلي: خريطة الملعب التفاعلية (Plotly Pitch)
    st.markdown("#### 🏟️ خريطة الملعب التفاعلية للأحداث المفلترة")
    st.caption("قف بالماوس على النقطة لرؤية تفاصيل الحدث، أو اضغط عليها (إذا كان نوع الحدث Pass هيرسم لك سهم التمريرة)")

    # بناء شكل الملعب باستخدام Plotly
    fig = go.Figure()

    # رسم خطوط الملعب الأساسية (الحدود الخارجية والمنتصف)
    fig.add_shape(type="rect", x0=0, y0=0, x1=100, y1=100, line=dict(color="white", width=2), fillcolor="#1e242b")
    fig.add_shape(type="line", x0=50, y0=0, x1=50, y1=100, line=dict(color="white", width=2))
    fig.add_shape(type="circle", x0=41, y0=41, x1=59, y1=59, line=dict(color="white", width=2))
    
    # منطقة الجزاء يمين ويسار
    fig.add_shape(type="rect", x0=0, y0=20, x1=16.5, y1=80, line=dict(color="white", width=2))
    fig.add_shape(type="rect", x0=83.5, y0=20, x1=100, y1=80, line=dict(color="white", width=2))

    # فلترة الصفوف اللي فيها إحداثيات واضحة وجاهزة للرسم
    plot_df = filtered_df.dropna(subset=['X Start', 'Y Start'])
    
    if not plot_df.empty:
        # تحويل داتا ملفك (اللي هي من 0 لـ 1) لمقياس الملعب (من 0 لـ 100)
        x_plots = plot_df['X Start'] * 100
        y_plots = plot_df['Y Start'] * 100
        
        # إضافة نقاط الأحداث على الملعب
        fig.add_trace(go.Scatter(
            x=x_plots,
            y=y_plots,
            mode='markers',
            marker=dict(size=12, color='#10b981', symbol='circle', line=dict(color='white', width=1)),
            text=plot_df['player'] + " - " + plot_df['event_type'] + " (" + plot_df['timestamp'] + ")",
            hoverinfo='text',
            customdata=plot_df['seconds'],
            name='الأحداث'
        ))
        
        # لو حدث تمريرة (Pass)، نرسم سهم من البداية للنهاية
        for idx, row in plot_df.iterrows():
            if row['event_type'].strip().lower() == 'pass' and pd.notna(row['X End']):
                fig.add_trace(go.Scatter(
                    x=[row['X Start']*100, row['X End']*100],
                    y=[row['Y Start']*100, row['Y End']*100],
                    mode='lines+markers',
                    line=dict(color='#3b82f6', width=2),
                    marker=dict(size=4, color='#3b82f6'),
                    showlegend=False,
                    hoverinfo='skip'
                ))

    # إعدادات أبعاد الخريطة واختفاء المحاور المزعجة
    fig.update_layout(
        width=800, height=500,
        margin=dict(l=20, r=20, t=20, b=20),
        xaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-2, 102]),
        yaxis=dict(showgrid=False, zeroline=False, showticklabels=False, range=[-2, 102]),
        paper_bgcolor='rgba(0,0,0,0)',
        plot_bgcolor='rgba(0,0,0,0)',
        showlegend=False
    )

    # عرض الخريطة تفاعلياً في ستريملايت
    st.plotly_chart(fig, use_container_width=True)

else:
    st.info("👋 يرجى رفع ملف أحداث المباراة (CSV) لتوليد خريطة الملعب التفاعلية تلقائياً.")
