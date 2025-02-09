import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt

# بيانات تسجيل الدخول
USERS = {"1058253616": "0502049396"}

# حالة الجلسة لتتبع تسجيل الدخول
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""

# تحديد مسار حفظ الملف
DATA_FILE = "student_data.xlsx"

# التحقق من صحة الملف قبل قراءته
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

# تحميل البيانات
df = load_data()

# واجهة تسجيل الدخول
if not st.session_state["authenticated"]:
    st.title("🔐 تسجيل الدخول")
    username_input = st.text_input("اسم المستخدم:")
    password_input = st.text_input("كلمة المرور:", type="password")
    
    if st.button("تسجيل الدخول"):
        if username_input in USERS and USERS[username_input] == password_input:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username_input
            st.success("✅ تسجيل الدخول ناجح! قم بالانتقال إلى التبويبات.")
            st.rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")
else:
    # إنشاء تبويبات
    tab1, tab2, tab3, tab4 = st.tabs(["📂 إدارة البيانات", "📊 الإحصائيات", "🔍 البحث والتحديث", "👤 إدارة المستخدمين"])
    
    with tab1:
        st.subheader("📂 تحميل وإدارة ملف بيانات الطلاب")
        uploaded_file = st.file_uploader("📂 الرجاء تحميل ملف بيانات الطلاب", type=["xlsx"])
        
        if uploaded_file is not None:
            df = pd.read_excel(uploaded_file)
            df["Vaccination Status"] = "لم يتم التطعيم"  # تعيين الحالة الافتراضية عند التحميل
            df.to_excel(DATA_FILE, index=False)
            st.success("✅ تم حفظ بيانات الطلاب بنجاح! وتم تعيين حالة التطعيم إلى 'لم يتم التطعيم'.")
            st.rerun()
        elif os.path.exists(DATA_FILE):
            st.info("📁 تم تحميل ملف البيانات مسبقًا.")
        else:
            st.warning("⚠️ لم يتم تحميل أي بيانات بعد. الرجاء رفع ملف جديد.")
        
        # زر لحذف البيانات
        if os.path.exists(DATA_FILE) and st.button("🗑️ حذف البيانات"):
            os.remove(DATA_FILE)
            st.warning("❌ تم حذف البيانات! يرجى تحميل ملف جديد.")
            st.rerun()
    
    with tab2:
        st.subheader("📊 الإحصائيات")
        if not df.empty:
            total_students = len(df)
            vaccinated_count = len(df[df["Vaccination Status"] == "تم التطعيم"])
            not_vaccinated_count = len(df[df["Vaccination Status"] == "لم يتم التطعيم"])
            
            st.text(f"👨‍🎓 إجمالي عدد الطلاب: {total_students}")
            st.text(f"💉 عدد الطلاب الذين تم تطعيمهم: {vaccinated_count}")
            st.text(f"⚠️ عدد الطلاب غير المطعمين: {not_vaccinated_count}")
            
            # رسم بياني لحالة التطعيم
            fig, ax = plt.subplots()
            ax.pie([vaccinated_count, not_vaccinated_count], labels=["تم التطعيم", "لم يتم التطعيم"], autopct="%1.1f%%", colors=["green", "red"])
            st.pyplot(fig)
        else:
            st.warning("⚠️ لا توجد بيانات متاحة.")
    
    with tab4:
        st.subheader("👤 إدارة المستخدمين")
        new_username = st.text_input("📌 اسم المستخدم الجديد:")
        new_password = st.text_input("🔑 كلمة المرور الجديدة:", type="password")
        
        if st.button("➕ إضافة مستخدم"):
            if new_username and new_password:
                USERS[new_username] = new_password
                st.success("✅ تم إضافة المستخدم بنجاح!")
            else:
                st.error("⚠️ الرجاء إدخال اسم مستخدم وكلمة مرور صحيحة.")
