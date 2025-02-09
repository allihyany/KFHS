import streamlit as st
import pandas as pd
import os

# تحميل ملف البيانات
file_path = "الملك_فهد_محدث.xlsx"

# التحقق مما إذا كان ملف Excel موجودًا، وإذا لم يكن موجودًا يتم إنشاء ملف جديد
if not os.path.exists(file_path):
    df = pd.DataFrame(columns=["No.", "Name", "ID Number", "Birth Date", "Class", "Section", "Vaccination Status", "Reason"])
    df.to_excel(file_path, index=False)
else:
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
        if len(found_students) > 1:
            selected_index = st.selectbox("🔹 اختر الطالب الصحيح:", found_students.index, 
                                          format_func=lambda x: f"{found_students.loc[x, 'Name']} - {found_students.loc[x, 'ID Number']}")
            student = found_students.loc[selected_index]
        else:
            student = found_students.iloc[0]
            selected_index = df[df["ID Number"] == student["ID Number"]].index[0]
        
        st.write("### 🧑 معلومات الطالب")
        st.text(f"👤 الاسم: {student['Name']}")
        st.text(f"🆔 رقم الهوية: {student['ID Number']}")
        st.text(f"📅 تاريخ الميلاد: {student['Birth Date']}")
        st.text(f"🏫 الصف: {student['Class']}")
        st.text(f"📚 الفصل: {student['Section']}")
        
        # اختيار حالة التطعيم
        vaccination_status = st.selectbox("💉 حالة التطعيم:", ["", "تم التطعيم", "لم يتم التطعيم"], 
                                          index=["", "تم التطعيم", "لم يتم التطعيم"].index(student.get("Vaccination Status", "")) if pd.notna(student.get("Vaccination Status")) else 0)
        
        # اختيار سبب عدم التطعيم في حال "لم يتم"
        reason = ""
        if vaccination_status == "لم يتم التطعيم":
            reason = st.selectbox("⚠️ سبب عدم التطعيم:", ["", "رفض الطالب", "رفض ولي الأمر", "الحالة الصحية لا تسمح", "غائب"], 
                                  index=["", "رفض الطالب", "رفض ولي الأمر", "الحالة الصحية لا تسمح", "غائب"].index(student.get("Reason", "")) if pd.notna(student.get("Reason")) else 0)
        
        # زر تحديث البيانات
        if st.button("💾 تحديث البيانات"):
            df.at[selected_index, "Vaccination Status"] = vaccination_status
            df.at[selected_index, "Reason"] = reason if vaccination_status == "لم يتم التطعيم" else ""
            df.to_excel(file_path, index=False)
            st.success("✅ تم تحديث البيانات بنجاح!")
            st.experimental_rerun()
    else:
        st.warning("❌ لم يتم العثور على الطالب. حاول مرة أخرى.")
