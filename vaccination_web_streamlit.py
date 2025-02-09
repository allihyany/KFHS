import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

# إعداد تصميم الواجهة باستخدام Streamlit
st.set_page_config(page_title="نظام تسجيل التطعيمات", page_icon="💉", layout="wide")

# تطبيق تنسيقات مخصصة لجعل الواجهة RTL وتحسين الألوان
st.markdown("""
    <style>
        body {direction: rtl; text-align: right; font-family: 'Cairo', sans-serif;}
        .sidebar .sidebar-content {background: linear-gradient(135deg, #004e92, #000428); color: white;}
        .stButton>button {background-color: #004e92; color: white; border-radius: 8px;}
        .stMetric {text-align: center; background-color: #e0f2ff; padding: 10px; border-radius: 10px;}
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
            return pd.read_excel(DATA_FILE)
        except Exception:
            st.warning("⚠️ الملف تالف أو غير صالح، سيتم إعادة إنشائه.")
            os.remove(DATA_FILE)
    
    df = pd.DataFrame(columns=["Name", "ID Number", "Class", "Section", "Vaccination Status"])
    df["Vaccination Status"] = "لم يتم التطعيم"  # تعيين الحالة الافتراضية
    df.to_excel(DATA_FILE, index=False)
    return df

if st.session_state["df"] is None:
    st.session_state["df"] = load_data()

df = st.session_state["df"]

# واجهة تسجيل الدخول
if not st.session_state["authenticated"]:
    st.markdown("<h1 style='text-align: center; color: #004e92;'>🔐 تسجيل الدخول</h1>", unsafe_allow_html=True)
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
    # إنشاء أزرار التنقل
    st.sidebar.title("📌 القائمة الرئيسية")
    page = st.sidebar.radio("اختر الصفحة", ["📂 إدارة البيانات", "📊 الإحصائيات", "🔍 البحث والتحديث", "👤 إدارة المستخدمين"],
                            index=0, format_func=lambda x: f"🟦 {x}")
    
    if page == "🔍 البحث والتحديث":
        st.title("🔍 البحث وتحديث بيانات الطلاب")
        if not df.empty:
            class_filter = st.selectbox("🏫 اختر الصف:", ["كل الصفوف"] + sorted(df["Class"].dropna().unique().tolist()))
            section_filter = st.selectbox("📚 اختر الفصل:", ["كل الفصول"] + sorted(df["Section"].dropna().unique().tolist()))
            
            filtered_df = df.copy()
            if class_filter != "كل الصفوف":
                filtered_df = filtered_df[filtered_df["Class"] == class_filter]
            if section_filter != "كل الفصول":
                filtered_df = filtered_df[filtered_df["Section"] == section_filter]
            
            if not filtered_df.empty:
                selected_student = st.selectbox("🔹 اختر الطالب:", filtered_df.index, 
                                                format_func=lambda x: f"{filtered_df.loc[x, 'Name']} - {filtered_df.loc[x, 'ID Number']}")
                student = filtered_df.loc[selected_student]
                st.text(f"👤 الاسم: {student['Name']}")
                st.text(f"🆔 رقم الهوية: {student['ID Number']}")
                vaccination_status = st.radio("💉 حالة التطعيم:", ["تم التطعيم", "لم يتم التطعيم"], key="vaccination")
                if st.button("💾 تحديث البيانات", use_container_width=True):
                    df.at[selected_student, "Vaccination Status"] = vaccination_status
                    df.to_excel(DATA_FILE, index=False)
                    st.success("✅ تم تحديث البيانات بنجاح!")
                    st.rerun()
    
    elif page == "👤 إدارة المستخدمين":
        st.title("👤 إدارة المستخدمين")
        new_username = st.text_input("📌 اسم المستخدم الجديد:")
        new_password = st.text_input("🔑 كلمة المرور الجديدة:", type="password")
        
        if st.button("➕ إضافة مستخدم", use_container_width=True):
            if new_username and new_password:
                USERS[new_username] = new_password
                st.success("✅ تم إضافة المستخدم بنجاح!")
