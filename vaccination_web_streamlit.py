import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import streamlit.components.v1 as components

# إعداد تصميم الواجهة باستخدام Streamlit
st.set_page_config(page_title="نظام تسجيل التطعيمات", page_icon="💉", layout="wide")

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
    st.markdown("""
        <style>
            .main {text-align: center; padding-top: 50px;}
        </style>
    """, unsafe_allow_html=True)
    
    st.title("🔐 تسجيل الدخول")
    username_input = st.text_input("📌 اسم المستخدم:", key="username")
    password_input = st.text_input("🔑 كلمة المرور:", type="password", key="password")
    
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
    page = st.sidebar.radio("اختر الصفحة", ["📂 إدارة البيانات", "📊 الإحصائيات", "🔍 البحث والتحديث", "👤 إدارة المستخدمين"])
    
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
        st.title("📊 الإحصائيات")
        if not df.empty:
            total_students = len(df)
            vaccinated_count = len(df[df["Vaccination Status"] == "تم التطعيم"])
            not_vaccinated_count = len(df[df["Vaccination Status"] == "لم يتم التطعيم"])
            
            st.metric(label="👨‍🎓 إجمالي عدد الطلاب", value=total_students)
            st.metric(label="💉 عدد الطلاب الذين تم تطعيمهم", value=vaccinated_count)
            st.metric(label="⚠️ عدد الطلاب غير المطعمين", value=not_vaccinated_count)
            
            fig, ax = plt.subplots()
            ax.pie([vaccinated_count, not_vaccinated_count], labels=["تم التطعيم", "لم يتم التطعيم"], autopct="%1.1f%%", colors=["green", "red"])
            st.pyplot(fig)
        else:
            st.warning("⚠️ لا توجد بيانات متاحة.")
    
    elif page == "🔍 البحث والتحديث":
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
