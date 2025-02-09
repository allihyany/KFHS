import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.express as px
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# إعداد تصميم الواجهة بأسلوب أوراكل
st.set_page_config(page_title="نظام تسجيل التطعيمات", page_icon="💉", layout="wide")

# تطبيق تنسيقات مخصصة لجعل الواجهة مستوحاة من تصميم أوراكل
st.markdown("""
    <style>
        body {
            direction: rtl;
            text-align: right;
            font-family: 'Cairo', sans-serif;
            background-color: #f4f4f9;
        }
        .main-header {
            background-color: #2a5298;
            color: white;
            padding: 20px;
            text-align: center;
            font-size: 30px;
            border-radius: 10px;
            font-weight: bold;
            margin-bottom: 20px;
        }
        .container {
            background-color: white;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            padding: 20px;
            margin-bottom: 20px;
        }
        .btn {
            background-color: #2a5298;
            color: white;
            border: none;
            padding: 10px 20px;
            font-size: 16px;
            border-radius: 5px;
            cursor: pointer;
            transition: all 0.3s ease;
        }
        .btn:hover {
            background-color: #1d3b73;
        }
    </style>
""", unsafe_allow_html=True)

# بيانات تسجيل الدخول
USERS = {"1058253616": "0502049396"}

# حالة الجلسة لتتبع تسجيل الدخول
if "authenticated" not in st.session_state:
    st.session_state["authenticated"] = False
if "username" not in st.session_state:
    st.session_state["username"] = ""
if "df" not in st.session_state:
    st.session_state["df"] = None
if "active_page" not in st.session_state:
    st.session_state["active_page"] = "login"

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

# قائمة التنقل الجانبية
if st.session_state["authenticated"]:
    st.sidebar.title("📋 التنقل")
    page = st.sidebar.radio("اختر الصفحة:", ["رفع البيانات", "التقارير", "إدارة البيانات", "إعدادات", "تسجيل الخروج"])

    if page == "رفع البيانات":
        st.session_state["active_page"] = "upload_data"
    elif page == "التقارير":
        st.session_state["active_page"] = "reports"
    elif page == "إدارة البيانات":
        st.session_state["active_page"] = "manage_data"
    elif page == "إعدادات":
        st.session_state["active_page"] = "settings"
    elif page == "تسجيل الخروج":
        st.session_state["active_page"] = "login"
        st.session_state["authenticated"] = False

# واجهة تسجيل الدخول
if st.session_state["active_page"] == "login":
    st.markdown("<div class='main-header'>🔐 تسجيل الدخول</div>", unsafe_allow_html=True)
    username_input = st.text_input("📌 اسم المستخدم:")
    password_input = st.text_input("🔑 كلمة المرور:", type="password")
    
    if st.button("🚀 تسجيل الدخول", use_container_width=True):
        if username_input in USERS and USERS[username_input] == password_input:
            st.session_state["authenticated"] = True
            st.session_state["username"] = username_input
            st.session_state["active_page"] = "reports"
            st.success("✅ تسجيل الدخول ناجح! قم بالانتقال إلى التبويبات.")
        else:
            st.error("❌ اسم المستخدم أو كلمة المرور غير صحيحة.")

# صفحة رفع البيانات
if st.session_state["active_page"] == "upload_data":
    st.markdown("<div class='main-header'>📤 رفع البيانات</div>", unsafe_allow_html=True)
    uploaded_file = st.file_uploader("🔼 قم برفع ملف Excel يحتوي على بيانات الطلاب:", type=["xlsx"])

    if uploaded_file is not None:
        try:
            new_data = pd.read_excel(uploaded_file)
            st.session_state["df"] = pd.concat([df, new_data], ignore_index=True).drop_duplicates()
            st.session_state["df"].to_excel(DATA_FILE, index=False)
            st.success("✅ تم رفع البيانات بنجاح!")
        except Exception as e:
            st.error(f"❌ حدث خطأ أثناء رفع الملف: {e}")

    if st.button("🔙 العودة إلى التقارير"):
        st.session_state["active_page"] = "reports"

# صفحة التقارير
if st.session_state["active_page"] == "reports":
    st.markdown("<div class='main-header'>📄 التقارير</div>", unsafe_allow_html=True)
    if not df.empty:
        st.write("📌 **إنشاء التقارير حسب الفئات المختلفة**")

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

    if st.button("🔙 العودة إلى التقارير"):
        st.session_state["active_page"] = "reports"

# صفحة إدارة البيانات
if st.session_state["active_page"] == "manage_data":
    st.markdown("<div class='main-header'>⚙️ إدارة البيانات</div>", unsafe_allow_html=True)
    st.write("🔧 هنا يمكنك تعديل وإدارة بيانات الطلاب.")

    # إدخال البيانات
    with st.form("add_student_form"):
        st.subheader("إضافة بيانات الطالب")
        name = st.text_input("اسم الطالب")
        id_number = st.text_input("رقم الهوية")
        student_class = st.text_input("الصف")
        section = st.text_input("الفصل")
        gender = st.selectbox("الجنس", ["ذكر", "أنثى"])
        dob = st.date_input("تاريخ الميلاد")
        phone = st.text_input("رقم الهاتف")
        vaccination_status = st.selectbox("حالة التطعيم", ["تم التطعيم", "لم يتم التطعيم"])
        submit = st.form_submit_button("إضافة الطالب")

        if submit:
            new_data = {
                "Name": name,
                "ID Number": id_number,
                "Class": student_class,
                "Section": section,
                "Gender": gender,
                "Date of Birth": dob,
                "Phone Number": phone,
                "Vaccination Status": vaccination_status
            }
            df = df.append(new_data, ignore_index=True)
            df.to_excel(DATA_FILE, index=False)
            st.success("✅ تم إضافة الطالب بنجاح!")

    if st.button("🔙 العودة إلى التقارير"):
        st.session_state["active_page"] = "reports"

# صفحة الإعدادات
if st.session_state["active_page"] == "settings":
    st.markdown("<div class='main-header'>⚙️ الإعدادات</div>", unsafe_allow_html=True)
    st.write("🛠️ قم بتخصيص الإعدادات الخاصة بك هنا.")

    if st.button("🔙 العودة إلى التقارير"):
        st.session_state["active_page"] = "reports"
