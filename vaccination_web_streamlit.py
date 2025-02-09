
import streamlit as st
import pandas as pd
import os

# تحميل ملف البيانات
uploaded_file = st.file_uploader("📂 تحميل ملف بيانات الطلاب (Excel)", type=["xlsx"])
if uploaded_file is not None:
    df = pd.read_excel(uploaded_file)
    file_path = "uploaded_students_data.xlsx"
    df.to_excel(file_path, index=False)
else:
    file_path = "الملك فهد.xlsx"  # استخدام الملف المرفوع مسبقًا
    df = pd.read_excel(file_path)

# واجهة Streamlit
st.title("🩺 نظام تسجيل التطعيمات للطلاب")
st.write("قم بالبحث عن الطالب وتحديث حالته الصحية.")

# البحث عن الطالب
search_query = st.text_input("🔍 البحث عن الطالب (الاسم أو رقم الهوية):")
if search_query:
    found_students = df[(df["Name"].str.contains(search_query, na=False, case=False)) | 
                        (df["ID Number"].astype(str) == search_query)]
    
    if not found_students.empty:
        student = found_students.iloc[0]
        student_index = df[df["ID Number"] == student["ID Number"]].index[0]
        
        st.write("### 🧑 معلومات الطالب")
        st.text(f"👤 الاسم: {student['Name']}")
        st.text(f"🆔 رقم الهوية: {student['ID Number']}")
        
        # اختيار حالة التطعيم
        vaccination_status = st.selectbox("💉 حالة التطعيم:", ["", "تم التطعيم", "لم يتم التطعيم"], 
                                          index=["", "تم التطعيم", "لم يتم التطعيم"].index(student["Vaccination Status"]) if pd.notna(student["Vaccination Status"]) else 0)
        
        # اختيار سبب عدم التطعيم في حال "لم يتم"
        reason = ""
        if vaccination_status == "لم يتم التطعيم":
            reason = st.selectbox("⚠️ سبب عدم التطعيم:", ["", "رفض الطالب", "رفض ولي الأمر", "الحالة الصحية لا تسمح", "غائب"], 
                                  index=["", "رفض الطالب", "رفض ولي الأمر", "الحالة الصحية لا تسمح", "غائب"].index(student["Reason"]) if pd.notna(student["Reason"]) else 0)
        
        # زر تحديث البيانات
        if st.button("💾 تحديث البيانات"):
            df.at[student_index, "Vaccination Status"] = vaccination_status
            df.at[student_index, "Reason"] = reason if vaccination_status == "لم يتم التطعيم" else ""
            df.to_excel(file_path, index=False)
            st.success("✅ تم تحديث البيانات بنجاح!")
            st.experimental_rerun()
    else:
        st.warning("❌ لم يتم العثور على الطالب. حاول مرة أخرى.")
