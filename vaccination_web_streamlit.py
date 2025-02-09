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

# تحميل البيانات أو إنشاء ملف جديد إذا لم يكن موجودًا
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
else:
    df = pd.DataFrame(columns=["Name", "ID Number", "Vaccination Status"])
    df.to_excel(DATA_FILE, index=False)

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
            df.to_excel(DATA_FILE, index=False)
            st.success("✅ تم حفظ بيانات الطلاب بنجاح!")
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
        st.subheader("📊 تقرير حالة التطعيمات")
        if os.path.exists(DATA_FILE):
            df = pd.read_excel(DATA_FILE)
            
            # التحقق من وجود الأعمدة المطلوبة وإضافتها إن لم تكن موجودة
            required_columns = ["Vaccination Status"]
            for col in required_columns:
                if col not in df.columns:
                    df[col] = "غير محدد"
                    df.to_excel(DATA_FILE, index=False)
            
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
            
            # عرض جدول للطلاب غير المطعمين
            st.subheader("📋 قائمة الطلاب غير المطعمين")
            df_not_vaccinated = df[df["Vaccination Status"] == "لم يتم التطعيم"]
            st.dataframe(df_not_vaccinated)
        else:
            st.warning("⚠️ لا توجد بيانات متاحة. يرجى تحميل ملف الطلاب أولاً.")
    
    with tab3:
        st.subheader("🔍 البحث وتحديث بيانات الطلاب")
        if os.path.exists(DATA_FILE):
            df = pd.read_excel(DATA_FILE)  # إعادة تحميل البيانات عند البحث
            search_query = st.text_input("🔍 البحث عن الطالب (الاسم أو رقم الهوية):")
            if search_query:
                found_students = df[(df["Name"].str.contains(search_query, na=False, case=False)) | 
                                    (df["ID Number"].astype(str) == search_query)]
                if not found_students.empty:
                    selected_index = st.selectbox("🔹 اختر الطالب الصحيح:", found_students.index, 
                                                  format_func=lambda x: f"{found_students.loc[x, 'Name']} - {found_students.loc[x, 'ID Number']}")
                    student = found_students.loc[selected_index]
                    
                    st.text(f"👤 الاسم: {student['Name']}")
                    st.text(f"🆔 رقم الهوية: {student['ID Number']}")
                    vaccination_status = st.selectbox("💉 حالة التطعيم:", ["", "تم التطعيم", "لم يتم التطعيم"], 
                                                      index=["", "تم التطعيم", "لم يتم التطعيم"].index(student.get("Vaccination Status", "")) if pd.notna(student.get("Vaccination Status")) else 0)
                    
                    if st.button("💾 تحديث البيانات"):
                        df.at[selected_index, "Vaccination Status"] = vaccination_status
                        df.to_excel(DATA_FILE, index=False)
                        st.success("✅ تم تحديث البيانات بنجاح!")
                        st.rerun()
        else:
            st.warning("⚠️ لا توجد بيانات متاحة. يرجى تحميل ملف الطلاب أولاً.")
