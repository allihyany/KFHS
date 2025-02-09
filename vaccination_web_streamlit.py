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
            st.session_state["df"] = pd.read_excel(uploaded_file)
            st.session_state["df"]["Vaccination Status"] = "لم يتم التطعيم"  # تعيين الحالة الافتراضية عند التحميل
            st.session_state["df"].to_excel(DATA_FILE, index=False)
            st.success("✅ تم حفظ بيانات الطلاب بنجاح! وتم تعيين حالة التطعيم إلى 'لم يتم التطعيم'.")
            st.rerun()
        elif os.path.exists(DATA_FILE):
            st.info("📁 تم تحميل ملف البيانات مسبقًا.")
        else:
            st.warning("⚠️ لم يتم تحميل أي بيانات بعد. الرجاء رفع ملف جديد.")
        
        # زر لحذف البيانات
        if os.path.exists(DATA_FILE) and st.button("🗑️ حذف البيانات"):
            os.remove(DATA_FILE)
            st.session_state["df"] = None
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
            
            fig, ax = plt.subplots()
            ax.pie([vaccinated_count, not_vaccinated_count], labels=["تم التطعيم", "لم يتم التطعيم"], autopct="%1.1f%%", colors=["green", "red"])
            st.pyplot(fig)
        else:
            st.warning("⚠️ لا توجد بيانات متاحة.")
    
    with tab3:
        st.subheader("🔍 البحث وتحديث بيانات الطلاب")
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
                st.text(f"🏫 الصف: {student['Class']}")
                st.text(f"📚 الفصل: {student['Section']}")
                vaccination_status = st.selectbox("💉 حالة التطعيم:", ["", "تم التطعيم", "لم يتم التطعيم"], 
                                                  index=["", "تم التطعيم", "لم يتم التطعيم"].index(student.get("Vaccination Status", "")) if pd.notna(student.get("Vaccination Status")) else 0)
                if st.button("💾 تحديث البيانات"):
                    df.at[selected_student, "Vaccination Status"] = vaccination_status
                    df.to_excel(DATA_FILE, index=False)
                    st.success("✅ تم تحديث البيانات بنجاح!")
                    st.rerun()
            else:
                st.warning("⚠️ لا يوجد طلاب مطابقون للمعايير المحددة.")
    
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
