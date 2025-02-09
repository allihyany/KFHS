import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# إعداد تصميم الواجهة بأسلوب حديث
st.set_page_config(page_title="نظام تسجيل التطعيمات", page_icon="💉", layout="wide")

# تطبيق تنسيقات مخصصة لجعل الواجهة أكثر حداثة وجاذبية
st.markdown("""
    <style>
        body {
            direction: rtl;
            text-align: right;
            font-family: 'Cairo', sans-serif;
            background-color: #f5f5f5;
        }
        .main-header {
            background-color: #3a7bd5;
            color: white;
            padding: 15px;
            text-align: center;
            font-size: 28px;
            border-radius: 8px;
            font-weight: bold;
        }
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
            df = pd.read_excel(DATA_FILE)
        except Exception:
            st.warning("⚠️ الملف تالف أو غير صالح، سيتم إعادة إنشائه.")
            os.remove(DATA_FILE)
            df = pd.DataFrame()
    else:
        df = pd.DataFrame()
    
    # التحقق من وجود الأعمدة المطلوبة
    required_columns = ["Name", "ID Number", "Class", "Section", "Gender", "Date of Birth", "Phone Number", "Vaccination Status"]
    for col in required_columns:
        if col not in df.columns:
            df[col] = "غير محدد"
    
    df["Vaccination Status"] = df["Vaccination Status"].fillna("لم يتم التطعيم")
    df.to_excel(DATA_FILE, index=False)
    return df

if st.session_state["df"] is None:
    st.session_state["df"] = load_data()

df = st.session_state["df"]

# وظيفة لإنشاء ملف PDF باستخدام reportlab
def create_pdf(dataframe, filename):
    c = canvas.Canvas(filename, pagesize=letter)
    c.setFont("Helvetica", 12)

    c.drawString(100, 750, "تقرير الطلاب")

    x, y = 50, 700
    headers = ["الاسم", "رقم الهوية", "الصف", "الفصل", "حالة التطعيم"]
    for header in headers:
        c.drawString(x, y, header)
        x += 100

    y -= 20
    x = 50

    for index, row in dataframe.iterrows():
        c.drawString(50, y, str(row["Name"]))
        c.drawString(150, y, str(row["ID Number"]))
        c.drawString(250, y, str(row["Class"]))
        c.drawString(350, y, str(row["Section"]))
        c.drawString(450, y, str(row["Vaccination Status"]))
        y -= 20
        if y < 50:
            c.showPage()
            y = 700

    c.save()

# واجهة تسجيل الدخول
if not st.session_state["authenticated"]:
    st.markdown("<div class='main-header'>🔐 تسجيل الدخول</div>", unsafe_allow_html=True)
    username_input = st.text_input("📌 اسم المستخدم:")
    password_input = st.text_input("🔑 كلمة المرور:", type="password")
    
    if st.button("🚀 تسجيل الدخول", use_container_width=True):
        if username_input in USERS and USERS[username_input] == password_input:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username_input
            st.success("✅ تسجيل الدخول ناجح! قم بالانتقال إلى التبويبات.")
            st.rerun()
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")
else:
    # عرض صفحة التقارير
    st.markdown("<div class='main-header'>📄 التقارير</div>", unsafe_allow_html=True)
    if not df.empty:
        st.write("📌 **إنشاء التقارير حسب الفئات المختلفة**")

        # تقرير بالفصل
        class_selected = st.selectbox("🏫 اختر الصف:", ["كل الصفوف"] + sorted(df["Class"].dropna().unique().tolist()))
        section_selected = st.selectbox("📚 اختر الفصل:", ["كل الفصول"] + sorted(df[df["Class"] == class_selected]["Section"].dropna().unique().tolist()) if class_selected != "كل الصفوف" else [])

        filtered_df = df.copy()
        if class_selected != "كل الصفوف":
            filtered_df = filtered_df[filtered_df["Class"] == class_selected]
        if section_selected:
            filtered_df = filtered_df[filtered_df["Section"] == section_selected]

        if not filtered_df.empty:
            st.write("📌 **تقرير الفصل المحدد**")
            st.dataframe(filtered_df)
            report_file = f"report_class_{class_selected}_{section_selected}.xlsx"
            filtered_df.to_excel(report_file, index=False)
            with open(report_file, "rb") as f:
                st.download_button("📥 تحميل تقرير الفصل (Excel)", f, file_name=report_file, mime="application/vnd.ms-excel")

            pdf_file = f"report_class_{class_selected}_{section_selected}.pdf"
            create_pdf(filtered_df, pdf_file)
            with open(pdf_file, "rb") as f:
                st.download_button("📥 تحميل تقرير الفصل (PDF)", f, file_name=pdf_file, mime="application/pdf")

        # تقرير بغير المتطعمين
        not_vaccinated_df = df[df["Vaccination Status"] == "لم يتم التطعيم"]
        if not not_vaccinated_df.empty:
            st.write("📌 **تقرير غير المتطعمين**")
            st.dataframe(not_vaccinated_df)
            report_file = "report_not_vaccinated.xlsx"
            not_vaccinated_df.to_excel(report_file, index=False)
            with open(report_file, "rb") as f:
                st.download_button("📥 تحميل تقرير غير المتطعمين (Excel)", f, file_name=report_file, mime="application/vnd.ms-excel")

            pdf_file = "report_not_vaccinated.pdf"
            create_pdf(not_vaccinated_df, pdf_file)
            with open(pdf_file, "rb") as f:
                st.download_button("📥 تحميل تقرير غير المتطعمين (PDF)", f, file_name=pdf_file, mime="application/pdf")

        # تقرير بالمتطعمين
        vaccinated_df = df[df["Vaccination Status"] == "تم التطعيم"]
        if not vaccinated_df.empty:
            st.write("📌 **تقرير المتطعمين**")
            st.dataframe(vaccinated_df)
            report_file = "report_vaccinated.xlsx"
            vaccinated_df.to_excel(report_file, index=False)
            with open(report_file, "rb") as f:
                st.download_button("📥 تحميل تقرير المتطعمين (Excel)", f, file_name=report_file, mime="application/vnd.ms-excel")

            pdf_file = "report_vaccinated.pdf"
            create_pdf(vaccinated_df, pdf_file)
            with open(pdf_file, "rb") as f:
                st.download_button("📥 تحميل تقرير المتطعمين (PDF)", f, file_name=pdf_file, mime="application/pdf")

        # تقرير للكل
        st.write("📌 **تقرير كامل لجميع الطلاب**")
        st.dataframe(df)
        report_file = "report_all_students.xlsx"
        df.to_excel(report_file, index=False)
        with open(report_file, "rb") as f:
            st.download_button("📥 تحميل التقرير الكامل (Excel)", f, file_name=report_file, mime="application/vnd.ms-excel")

        pdf_file = "report_all_students.pdf"
        create_pdf(df, pdf_file)
        with open(pdf_file, "rb") as f:
            st.download_button("📥 تحميل التقرير الكامل (PDF)", f, file_name=pdf_file, mime="application/pdf")
    else:
        st.warning("⚠️ لا توجد بيانات متاحة لإنشاء التقارير.")
