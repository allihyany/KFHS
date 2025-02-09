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
        st.session_state["active_page"] = "manage_data"
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

# صفحة إدارة البيانات
if st.session_state["active_page"] == "manage_data":
    st.markdown("<div class='main-header'>⚙️ إدارة البيانات</div>", unsafe_allow_html=True)
    st.write("🔧 هنا يمكنك تعديل وإدارة بيانات الطلاب.")

    # تصفية البيانات حسب الصف والفصل
    class_filter = st.multiselect("اختر الصفوف", options=sorted(df["Class"].unique()), default=sorted(df["Class"].unique()))
    section_filter = st.multiselect("اختر الفصول", options=sorted(df["Section"].unique()), default=sorted(df["Section"].unique()))

    filtered_df = df[df["Class"].isin(class_filter) & df["Section"].isin(section_filter)]

    # اختيار الطالب من قائمة منسدلة
    student_names = filtered_df["Name"].tolist()
    selected_student = st.selectbox("اختر الطالب", options=student_names)

    # عرض بيانات الطالب
    if selected_student:
        student_data = filtered_df[filtered_df["Name"] == selected_student].iloc[0]
        st.write("### بيانات الطالب")
        st.write(f"**الاسم:** {student_data['Name']}")
        st.write(f"**رقم الهوية:** {student_data['ID Number']}")
        st.write(f"**الصف:** {student_data['Class']}")
        st.write(f"**الفصل:** {student_data['Section']}")
        st.write(f"**حالة التطعيم:** {student_data['Vaccination Status']}")

        # تحديث حالة التطعيم
        new_status = st.radio("تحديث حالة التطعيم", ["تم التطعيم", "لم يتم التطعيم"], index=0 if student_data["Vaccination Status"] == "تم التطعيم" else 1)
        if st.button("تحديث الحالة"):
            df.loc[df["ID Number"] == student_data["ID Number"], "Vaccination Status"] = new_status
            df.to_excel(DATA_FILE, index=False)
            st.success("✅ تم تحديث حالة التطعيم بنجاح!")

    if st.button("🔙 العودة إلى التقارير", key="back_to_reports_manage_data"):
        st.session_state["active_page"] = "reports"
