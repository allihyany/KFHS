import streamlit as st
import pandas as pd
import os
import matplotlib.pyplot as plt
import plotly.express as px

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
        .grid-container {
            display: grid;
            grid-template-columns: repeat(auto-fit, minmax(300px, 1fr));
            gap: 20px;
            padding: 20px;
        }
        .grid-item {
            background: white;
            padding: 20px;
            border-radius: 10px;
            box-shadow: 0px 4px 6px rgba(0, 0, 0, 0.1);
            text-align: center;
            cursor: pointer;
            transition: transform 0.2s;
        }
        .grid-item:hover {
            transform: scale(1.05);
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
    # عرض التبويبات كمربعات
    st.markdown("<div class='main-header'>لوحة التحكم</div>", unsafe_allow_html=True)
    st.markdown("<div class='grid-container'>", unsafe_allow_html=True)

    if st.button("📂 إدارة البيانات", use_container_width=True):
        st.session_state["selected_page"] = "إدارة البيانات"
    if st.button("📊 الإحصائيات", use_container_width=True):
        st.session_state["selected_page"] = "الإحصائيات"
    if st.button("🔍 البحث والتحديث", use_container_width=True):
        st.session_state["selected_page"] = "البحث والتحديث"
    if st.button("👤 إدارة المستخدمين", use_container_width=True):
        st.session_state["selected_page"] = "إدارة المستخدمين"
    if st.button("📄 التقارير", use_container_width=True):
        st.session_state["selected_page"] = "التقارير"

    st.markdown("</div>", unsafe_allow_html=True)

    # عرض الصفحة المحددة بناءً على الاختيار
    if "selected_page" in st.session_state:
        if st.session_state["selected_page"] == "إدارة البيانات":
            st.markdown("<div class='main-header'>📂 إدارة البيانات</div>", unsafe_allow_html=True)
            uploaded_file = st.file_uploader("📂 الرجاء تحميل ملف بيانات الطلاب", type=["xlsx"], key="upload")
            
            if uploaded_file is not None:
                st.session_state["df"] = pd.read_excel(uploaded_file)
                st.session_state["df"]["Vaccination Status"] = "لم يتم التطعيم"
                st.session_state["df"].to_excel(DATA_FILE, index=False)
                st.success("✅ تم حفظ بيانات الطلاب بنجاح! وتم تعيين حالة التطعيم إلى 'لم يتم التطعيم'.")
                st.rerun()
            
            if os.path.exists(DATA_FILE):
                st.write("📁 البيانات الحالية:")
                st.dataframe(st.session_state["df"])
                if st.button("🗑️ حذف البيانات", use_container_width=True):
                    os.remove(DATA_FILE)
                    st.session_state["df"] = None
                    st.warning("❌ تم حذف البيانات! يرجى تحميل ملف جديد.")
                    st.rerun()
        
        elif st.session_state["selected_page"] == "الإحصائيات":
            st.markdown("<div class='main-header'>📊 الإحصائيات التفصيلية</div>", unsafe_allow_html=True)
            if not df.empty:
                total_students = len(df)
                vaccinated_count = len(df[df["Vaccination Status"] == "تم التطعيم"])
                not_vaccinated_count = len(df[df["Vaccination Status"] == "لم يتم التطعيم"])
                
                male_students = len(df[df["Gender"] == "ذكر"])
                female_students = len(df[df["Gender"] == "أنثى"])
                
                col1, col2, col3, col4, col5 = st.columns(5)
                col1.metric(label="👨‍🎓 إجمالي عدد الطلاب", value=total_students)
                col2.metric(label="💉 تم التطعيم", value=vaccinated_count)
                col3.metric(label="⚠️ لم يتم التطعيم", value=not_vaccinated_count)
                col4.metric(label="👦 عدد الذكور", value=male_students)
                col5.metric(label="👧 عدد الإناث", value=female_students)
                
                fig = px.pie(values=[vaccinated_count, not_vaccinated_count],
                             names=["تم التطعيم", "لم يتم التطعيم"],
                             title="حالة التطعيم",
                             color_discrete_sequence=["#3a7bd5", "#a3d5ff"])
                st.plotly_chart(fig)
            else:
                st.warning("⚠️ لا توجد بيانات متاحة.")

        elif st.session_state["selected_page"] == "التقارير":
            st.markdown("<div class='main-header'>📄 التقارير</div>", unsafe_allow_html=True)
            if not df.empty:
                st.write("📌 **توليد تقرير لكل فصل دراسي**")
                class_selected = st.selectbox("🏫 اختر الصف:", ["كل الصفوف"] + sorted(df["Class"].dropna().unique().tolist()))
                section_selected = st.selectbox("📚 اختر الفصل:", ["كل الفصول"] + sorted(df[df["Class"] == class_selected]["Section"].dropna().unique().tolist()) if class_selected != "كل الصفوف" else [])
                
                filtered_df = df.copy()
                if class_selected != "كل الصفوف":
                    filtered_df = filtered_df[filtered_df["Class"] == class_selected]
                if section_selected:
                    filtered_df = filtered_df[filtered_df["Section"] == section_selected]
                
                if not filtered_df.empty:
                    st.write("📌 **ملخص بيانات الفصل المحدد**")
                    st.dataframe(filtered_df)
                    
                    # زر لتنزيل التقرير كملف Excel
                    report_file = f"student_report_{class_selected}_{section_selected}.xlsx"
                    filtered_df.to_excel(report_file, index=False)
                    with open(report_file, "rb") as f:
                        st.download_button("📥 تحميل التقرير كملف Excel", f, file_name=report_file, mime="application/vnd.ms-excel")
                else:
                    st.warning("⚠️ لا توجد بيانات متاحة لهذا الفصل الدراسي.")
