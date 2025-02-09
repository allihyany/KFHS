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
    df = pd.DataFrame(columns=["Name", "ID Number", "Class", "Section", "Vaccination Status"])
    df["Vaccination Status"] = "لم يتم التطعيم"  # تعيين الحالة الافتراضية
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
    
    with tab3:
        st.subheader("🔍 البحث وتحديث بيانات الطلاب")
        if os.path.exists(DATA_FILE):
            df = pd.read_excel(DATA_FILE)  # إعادة تحميل البيانات عند البحث
            
            # اختيار الصف والقسم كفلاتر للبحث
            class_filter = st.selectbox("🏫 اختر الصف:", ["كل الصفوف"] + sorted(df["Class"].dropna().unique().tolist()))
            section_filter = st.selectbox("📚 اختر الفصل:", ["كل الفصول"] + sorted(df["Section"].dropna().unique().tolist()))
            
            # تصفية البيانات بناءً على الصف والفصل المحددين
            filtered_df = df.copy()
            if class_filter != "كل الصفوف":
                filtered_df = filtered_df[filtered_df["Class"] == class_filter]
            if section_filter != "كل الفصول":
                filtered_df = filtered_df[filtered_df["Section"] == section_filter]
            
            # اختيار الطالب من القائمة المنسدلة
            selected_student = st.selectbox("🔹 اختر الطالب:", filtered_df.index, 
                                            format_func=lambda x: f"{filtered_df.loc[x, 'Name']} - {filtered_df.loc[x, 'ID Number']}")
            student = filtered_df.loc[selected_student]
            
            # عرض بيانات الطالب
            st.text(f"👤 الاسم: {student['Name']}")
            st.text(f"🆔 رقم الهوية: {student['ID Number']}")
            st.text(f"🏫 الصف: {student['Class']}")
            st.text(f"📚 الفصل: {student['Section']}")
            
            # اختيار حالة التطعيم
            vaccination_status = st.selectbox("💉 حالة التطعيم:", ["", "تم التطعيم", "لم يتم التطعيم"], 
                                              index=["", "تم التطعيم", "لم يتم التطعيم"].index(student.get("Vaccination Status", "")) if pd.notna(student.get("Vaccination Status")) else 0)
            
            if st.button("💾 تحديث البيانات"):
                df.at[selected_student, "Vaccination Status"] = vaccination_status
                df.to_excel(DATA_FILE, index=False)
                st.success("✅ تم تحديث البيانات بنجاح!")
                st.rerun()
        else:
            st.warning("⚠️ لا توجد بيانات متاحة. يرجى تحميل ملف الطلاب أولاً.")
