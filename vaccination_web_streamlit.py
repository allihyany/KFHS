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
USERS = {"1": "1"}

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
    password_input = st.text_input("🔑 كلمة المرور:", type="password", key="password")
    
    if st.button("🚀 تسجيل الدخول", use_container_width=True):
        if username_input in USERS and USERS[username_input] == password_input:
            st.session_state["authenticated"] = True
            if username_input in USERS and USERS[username_input] == password_input:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username_input
            st.success("✅ تسجيل الدخول ناجح! قم بالانتقال إلى التبويبات.")
            st.rerun()
            st.success("✅ تسجيل الدخول ناجح! قم بالانتقال إلى التبويبات.")
            st.rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")
else:
    # إنشاء أزرار التنقل
    st.sidebar.title("📌 القائمة الرئيسية")
    page = st.sidebar.radio("اختر الصفحة", ["📂 إدارة البيانات", "📊 الإحصائيات", "🔍 البحث والتحديث", "👤 إدارة المستخدمين"],
                            index=0, format_func=lambda x: f"🟦 {x}")
    
    if page == "📂 إدارة البيانات":
        st.title("📂 تحميل وإدارة ملف بيانات الطلاب")
        uploaded_file = st.file_uploader("📂 الرجاء تحميل ملف بيانات الطلاب", type=["xlsx"], key="upload")
        
        if uploaded_file is not None:
            st.session_state["df"] = pd.read_excel(uploaded_file)
            st.session_state["df"]["Vaccination Status"] = "لم يتم التطعيم"  # تعيين الحالة الافتراضية عند التحميل
            st.session_state["df"].to_excel(DATA_FILE, index=False)
            st.success("✅ تم حفظ بيانات الطلاب بنجاح! وتم تعيين حالة التطعيم إلى 'لم يتم التطعيم'.")
            st.rerun()
        
        if os.path.exists(DATA_FILE):
            if st.button("🗑️ حذف البيانات", use_container_width=True):
                os.remove(DATA_FILE)
                st.session_state["df"] = None
                st.warning("❌ تم حذف البيانات! يرجى تحميل ملف جديد.")
                st.rerun()
    
    elif page == "📊 الإحصائيات":
        st.title("📊 الإحصائيات المفصلة")
        if not df.empty:
            total_students = len(df)
            vaccinated_count = len(df[df["Vaccination Status"] == "تم التطعيم"])
            not_vaccinated_count = len(df[df["Vaccination Status"] == "لم يتم التطعيم"])
            
            col1, col2, col3 = st.columns(3)
            col1.metric(label="👨‍🎓 إجمالي عدد الطلاب", value=total_students)
            col2.metric(label="💉 تم التطعيم", value=vaccinated_count)
            col3.metric(label="⚠️ لم يتم التطعيم", value=not_vaccinated_count)
            
            fig, ax = plt.subplots()
            ax.pie([vaccinated_count, not_vaccinated_count], labels=["تم التطعيم", "لم يتم التطعيم"], autopct="%1.1f%%", colors=["#1e88e5", "#bbdefb"])
            st.pyplot(fig)
        else:
            st.warning("⚠️ لا توجد بيانات متاحة.")
