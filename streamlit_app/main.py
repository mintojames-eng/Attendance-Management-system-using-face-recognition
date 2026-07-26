import streamlit as st
import os
from dotenv import load_dotenv
from utils.auth import login_user, signup_user
from utils.ui import apply_custom_css

st.set_page_config(page_title="Attendance System", page_icon="🎓", layout="wide")
apply_custom_css()

load_dotenv()

st.title("🎓 Smart Face Recognition Attendance")

if "user" not in st.session_state:
    st.session_state.user = None

if st.session_state.user:
    role = st.session_state.user["role"]
    st.success(f"Welcome back, {st.session_state.user['name']} ({role.title()})!")
    st.write("You are already logged in.")
    
    c1, c2 = st.columns(2)
    with c1:
        if st.button("Go to Dashboard", type="primary"):
            if role == "admin": st.switch_page("pages/1_Admin_Dashboard.py")
            elif role == "teacher": st.switch_page("pages/2_Teacher_Dashboard.py")
            elif role == "student": st.switch_page("pages/3_Student_Dashboard.py")
    with c2:
        if st.button("Logout"):
            st.session_state.user = None
            st.rerun()
else:
    st.subheader("Login to your account")
    tab1, tab2 = st.tabs(["Login", "Signup"])
    
    with tab1:
        with st.form("login_form"):
            email = st.text_input("Email")
            password = st.text_input("Password", type="password")
            submitted = st.form_submit_button("Login")
            
            if submitted:
                if not email or not password:
                    st.error("Please fill all fields")
                else:
                    result = login_user(email, password)
                    if "error" in result:
                        st.error(result["error"])
                    else:
                        st.session_state.user = result
                        role = result["role"]
                        if role == "admin": st.switch_page("pages/1_Admin_Dashboard.py")
                        elif role == "teacher": st.switch_page("pages/2_Teacher_Dashboard.py")
                        elif role == "student": st.switch_page("pages/3_Student_Dashboard.py")
                        
    with tab2:
        with st.form("signup_form"):
            st.write("Register a new account")
            s_name = st.text_input("Full Name")
            s_email = st.text_input("Email Address")
            s_password = st.text_input("Password", type="password")
            
            s_type = st.selectbox("Role", ["student", "teacher", "admin"])
            
            # Additional fields depending on role
            st.write("---")
            st.write("*Additional Information (If applicable)*")
            employee_id = st.text_input("Employee ID (Teachers Only)")
            admin_code = st.text_input("Admin Code (Admins Only)", type="password", help="Enter '123' for this demo")
            
            s_submitted = st.form_submit_button("Sign Up")
            
            if s_submitted:
                if not s_name or not s_email or not s_password:
                    st.error("Please fill all required fields (Name, Email, Password).")
                else:
                    extra = {}
                    if s_type == "teacher":
                        if not employee_id:
                            st.error("Employee ID is required for teachers!")
                            st.stop()
                        extra["employeeId"] = employee_id
                    elif s_type == "admin":
                        if not admin_code:
                            st.error("Admin code required to create Super Admin!")
                            st.stop()
                        extra["adminCode"] = admin_code
                        
                    res = signup_user(s_email, s_password, s_name, s_type, extra)
                    if "error" in res:
                        st.error(res["error"])
                    else:
                        st.success(res["success"])
                        st.balloons()
