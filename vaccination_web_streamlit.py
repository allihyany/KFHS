import streamlit as st
import pandas as pd
import os

# تحديد مسار حفظ الملف
DATA_FILE = "student_data.xlsx"

# تحميل البيانات إذا كان الملف موجودًا
if os.path.exists(DATA_FILE):
    df = pd.read_excel(DATA_FILE)
else:
    df = pd.DataFrame(columns=["No.", "Name", "ID Number", "Birth Date", "Class", "Section", "Vaccination Status", "Reason"])
    df.to_excel(DATA_FILE, index=False)

# واجهة Streamlit
st.title("🩺 نظام تسجيل التطعيمات للطلاب")
st.write("قم برفع ملف البيانات لمرة واحدة، ثم يمكنك البحث عن الطلاب وتحديث حالتهم الصحية.")

# السماح للمستخدم برفع ملف Excel لمرة واحدة فقط
if not os.path.exists(DATA_FILE):
    uploaded_file = st.file_uploader("📂 الرجاء تحميل ملف بيانات الطلاب (مرة واحدة فقط)", type=["xlsx"])
    if uploaded_file is not None:
        df = pd.read_excel(uploaded_file)
        df.to_excel(DATA_FILE, index=False)
        st.success("✅ تم حفظ بيانات الطلاب بنجاح!")
        st.rerun()
else:
    st.info("📁 تم تحميل ملف البيانات مسبقًا. يمكنك الآن البحث عن الطلاب وتحديث البيانات.")

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
            reason_options = ["", "رفض الطالب", "رفض ولي الأمر", "الحالة الصحية لا تسمح", "غائب"]
            reason = st.selectbox("⚠️ سبب عدم التطعيم:", reason_options, 
                                  index=reason_options.index(student.get("Reason", "")) if pd.notna(student.get("Reason")) and student.get("Reason", "") in reason_options else 0)
        
        # زر تحديث البيانات
        if st.button("💾 تحديث البيانات"):
            df.at[selected_index, "Vaccination Status"] = vaccination_status
            df.at[selected_index, "Reason"] = reason if vaccination_status == "لم يتم التطعيم" else ""
            df.to_excel(DATA_FILE, index=False)
            st.success("✅ تم تحديث البيانات بنجاح!")
            st.rerun()
    else:
        st.warning("❌ لم يتم العثور على الطالب. حاول مرة أخرى.")

# عرض تقرير عن التطعيمات
st.subheader("📊 تقرير حالة التطعيمات")
total_students = len(df)
vaccinated_count = len(df[df["Vaccination Status"] == "تم التطعيم"])
not_vaccinated_count = len(df[df["Vaccination Status"] == "لم يتم التطعيم"])

st.text(f"👨‍🎓 إجمالي عدد الطلاب: {total_students}")
st.text(f"💉 عدد الطلاب الذين تم تطعيمهم: {vaccinated_count}")
st.text(f"⚠️ عدد الطلاب غير المطعمين: {not_vaccinated_count}")
