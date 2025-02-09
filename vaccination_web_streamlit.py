import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

# إعداد تصميم الواجهة بأسلوب مدرسي بسيط
st.set_page_config(page_title="نظام تسجيل التطعيمات", page_icon="🎒", layout="wide")

# تطبيق تنسيقات مخصصة لجعل الواجهة أكثر وضوحًا وجاذبية للبيئة المدرسية
st.markdown("""
    <style>
        body {direction: rtl; text-align: right; font-family: 'Cairo', sans-serif; background-color: #fdfdfd;}
        .sidebar .sidebar-content {background: linear-gradient(135deg, #2a9df4, #62b6f7); color: white; padding: 20px; border-radius: 8px;}
        .stButton>button {background-color: #2a9df4; color: white; border-radius: 8px; font-size: 18px; padding: 10px; width: 100%;}
        .stMetric {text-align: center; background-color: #dff6ff; padding: 10px; border-radius: 10px;}
        .main-header {background-color: #62b6f7; color: white; padding: 15px; text-align: center; font-size: 28px; border-radius: 8px; font-weight: bold;}
        .card {background: white; padding: 20px; border-radius: 10px; box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1); margin-bottom: 10px;}
    </style>
""", unsafe_allow_html=True)

# بيانات تسجيل الدخول
USERS = {"1058253616": "0502049396"}

# حالة الجلسة لتتبع تسجيل الدخول
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "df" not in st.session_state:
    st.session_state["df"] = None

# تحديد مسار حفظ الملف
DATA_FILE = "student_data.xlsx"

# تحميل البيانات عند تشغيل التطبيق مرة واحدة فقط
def load_data():
    if os.path.exists(DATA_FILE):
        try:
            df = pd.read_excel(DATA_FILE)
        except Exception:
            st.warning("⚠️ الملف تالف أو غير صالح، سيتم إعادة إنشائه.")
            os.remove(DATA_FILE)
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()
    
    # التحقق من وجود الأعمدة المطلوبة
    required_columns = ["Name", "ID Number", "Class", "Section", "Gender", "Date of Birth", "Phone Number", "Vaccination Status"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = "غير محدد"
    
    df["Vaccination Status"] = df["Vaccination Status"].fillna("لم يتم التطعيم")
    df.to_excel(DATA_FILE, index=False)
    return df

if st.session_state["df"] is None:
    st.session_state["df"] = load_data()

df = st.session_state["df"]

# واجهة تسجيل الدخول
if not st.session_state["authenticated"]:
    st.markdown("<div class='main-header'>🔐 تسجيل الدخول</div>", unsafe_allow_html=True)
    username_input = st.text_input("📌 اسم المستخدم:")
    password_input = st.text_input("🔑 كلمة المرور:", type="password")
    
    if st.button("🚀 تسجيل الدخول", use_container_width=True):
        if username_input in USERS and USERS[username_input] == password_input:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username_input
            st.success("✅ تسجيل الدخول ناجح! قم بالانتقال إلى التبويبات.")
            st.rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")
else:
    # إنشاء أزرار التنقل بأسلوب مدرسي واضح وكبير
    st.sidebar.title("📌 القائمة الرئيسية")
    page = st.sidebar.radio("اختر الصفحة", ["📂 إدارة البيانات", "📊 الإحصائيات", "🔍 البحث والتحديث", "👤 إدارة المستخدمين"],
                            index=0, format_func=lambda x: f"🟦 {x}")
    
    if page == "🔍 البحث والتحديث":
        st.markdown("<div class='main-header'>🔍 البحث وتحديث بيانات الطلاب</div>", unsafe_allow_html=True)
        if not df.empty:
            class_filter = st.selectbox("🏫 اختر الصف:", ["كل الصفوف"] + sorted(df["Class"].dropna().unique().tolist()))
            section_filter = st.selectbox("📚 اختر الفصل:", ["كل الفصول"] + sorted(df[df["Class"] == class_filter]["Section"].dropna().unique().tolist()) if class_filter != "كل الصفوف" else [])
            
            filtered_df = df.copy()
            if class_filter != "كل الصفوف":
                filtered_df = filtered_df[filtered_df["Class"] == class_filter]
            if section_filter:
                filtered_df = filtered_df[filtered_df["Section"] == section_filter]
            
            if not filtered_df.empty:
                selected_student = st.selectbox("🔹 اختر الطالب:", filtered_df["Name"].unique())
                student_data = filtered_df[filtered_df["Name"] == selected_student]
                st.write(student_data)
                new_status = st.radio("💉 تحديث حالة التطعيم:", ["تم التطعيم", "لم يتم التطعيم"])
                if st.button("💾 تحديث الحالة", use_container_width=True):
                    df.loc[df["Name"] == selected_student, "Vaccination Status"] = new_status
                    df.to_excel(DATA_FILE, index=False)
                    st.success("✅ تم تحديث البيانات بنجاح!")
                    st.rerun()
