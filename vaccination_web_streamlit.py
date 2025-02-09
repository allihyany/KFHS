import streamlit as st
import pandas as pd
import os

# بيانات تسجيل الدخول
USERNAME = "1058253616"
PASSWORD = "0502049396"

# حالة الجلسة لتتبع تسجيل الدخول
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False

# واجهة تسجيل الدخول
if not st.session_state["authenticated"]:
    st.title("🔐 تسجيل الدخول")
    username_input = st.text_input("اسم المستخدم:")
    password_input = st.text_input("كلمة المرور:", type="password")
    
    if st.button("تسجيل الدخول"):
        if username_input == USERNAME and password_input == PASSWORD:
            st.session_state["authenticated"] = True
            st.success("✅ تسجيل الدخول ناجح! قم بالانتقال إلى التبويبات.")
            st.rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")
else:
    # تحديد مسار حفظ الملف
    DATA_FILE = "student_data.xlsx"

    # تحميل البيانات إذا كان الملف موجودًا
    if os.path.exists(DATA_FILE):
        df = pd.read_excel(DATA_FILE)
    else:
        df = pd.DataFrame(columns=["No.", "Name", "ID Number", "Birth Date", "Class", "Section", "Vaccination Status", "Reason"])
        df.to_excel(DATA_FILE, index=False)

    # إنشاء تبويبات
    tab1, tab2 = st.tabs(["📂 رفع البيانات", "📊 الإحصائيات"])
    
    with tab1:
        st.subheader("📂 تحميل ملف بيانات الطلاب")
        if not os.path.exists(DATA_FILE):
            uploaded_file = st.file_uploader("📂 الرجاء تحميل ملف بيانات الطلاب (مرة واحدة فقط)", type=["xlsx"])
            if uploaded_file is not None:
                df = pd.read_excel(uploaded_file)
                df.to_excel(DATA_FILE, index=False)
                st.success("✅ تم حفظ بيانات الطلاب بنجاح!")
                st.experimental_rerun()
        else:
            st.info("📁 تم تحميل ملف البيانات مسبقًا. يمكنك الآن البحث عن الطلاب وتحديث البيانات.")
    
    with tab2:
        st.subheader("📊 تقرير حالة التطعيمات")
        total_students = len(df)
        vaccinated_count = len(df[df["Vaccination Status"] == "تم التطعيم"])
        not_vaccinated_count = len(df[df["Vaccination Status"] == "لم يتم التطعيم"])
        
        st.text(f"👨‍🎓 إجمالي عدد الطلاب: {total_students}")
        st.text(f"💉 عدد الطلاب الذين تم تطعيمهم: {vaccinated_count}")
        st.text(f"⚠️ عدد الطلاب غير المطعمين: {not_vaccinated_count}")
        
        # عرض جدول للطلاب غير المطعمين
        st.subheader("📋 قائمة الطلاب غير المطعمين")
        df_not_vaccinated = df[df["Vaccination Status"] == "لم يتم التطعيم"]
        st.dataframe(df_not_vaccinated)
