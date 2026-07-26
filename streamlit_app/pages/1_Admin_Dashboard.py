import streamlit as st
from utils.database import get_db
from utils.ui import apply_custom_css

st.set_page_config(page_title="Admin Console", page_icon="🛡️", layout="wide")
apply_custom_css()
if "user" not in st.session_state or not st.session_state.user or st.session_state.user.get("role") != "admin":
    st.error("Admin Access Required. Please login from the main page.")
    st.stop()
    
col1, col2 = st.columns([5, 1])
with col1:
    st.title("🛡️ Super Admin Console")
    st.write(f"Logged in as: {st.session_state.user['name']}")
with col2:
    st.write("")
    if st.button("Logout 🚪", type="secondary"):
        st.session_state.user = None
        st.switch_page("main.py")

db = get_db()

st.subheader("Global Security Overrides")
st.write("Control institution-wide security thresholds and emergency mechanisms.")
special_mode = db.global_settings.find_one({"type": "special_event"})
is_special = special_mode.get("active", False) if special_mode else False

if st.checkbox("🚨 Enable Special Event Bypass (Allow Teachers to ignore Geo-Fencing & Timetables)", value=is_special):
    db.global_settings.update_one({"type": "special_event"}, {"$set": {"active": True}}, upsert=True)
else:
    db.global_settings.update_one({"type": "special_event"}, {"$set": {"active": False}}, upsert=True)
    
st.divider()

tab1, tab2 = st.tabs(["🧑‍🏫 Teacher Management", "🎓 Student Management"])

with tab1:
    st.subheader("Teacher Accounts")
    teachers = list(db.auth_teachers.find({}, {"password": 0}))
    if not teachers:
        st.info("No teachers registered yet.")
    else:
        for t in teachers:
            with st.expander(f"🧑‍🏫 {t['username']} - {t['email']}"):
                with st.container():
                    cols = st.columns([2, 2, 2, 2, 1, 1])
                    cols[0].write(f"**{t['username']}**")
                    cols[1].write(t['email'])
                    cols[2].write(f"ID: {t.get('employeeId', 'N/A')}")
                    cols[3].write(t.get('status', 'inactive').capitalize())
                    
                    new_status = "inactive" if t.get('status') == 'active' else "active"
                    button_label = "Deactivate" if t.get('status') == 'active' else "Activate"
                    
                    if cols[4].button(button_label, key=f"status_{t['_id']}"):
                        db.auth_teachers.update_one({"_id": t["_id"]}, {"$set": {"status": new_status}})
                        st.rerun()
                        
                    if cols[5].button("Delete", key=f"del_{t['_id']}", type="primary"):
                        db.auth_teachers.delete_one({"_id": t["_id"]})
                        st.rerun()
                        
                st.write("---")
                st.markdown(f"**Registered Department:** `{t.get('department', 'N/A')}`")
                
                # Fetch dynamically all historical subjects this teacher created sessions for
                taught = list(db.attendance_records.find({"created_by": t['email']}))
                subjs_taught = list(set([rec.get('subject', 'Unknown') for rec in taught]))
                if subjs_taught:
                    st.markdown(f"**Historical Subjects Taught:** `{', '.join(subjs_taught)}`")
                else:
                    st.write("**Historical Subjects Taught:** None logged dynamically yet.")
                st.divider()

with tab2:
    st.subheader("Student Accounts")
    students = list(db.auth_users.find({}, {"password": 0}))
    if not students:
        st.info("No students registered yet.")
    else:
        # We need the biometrics DB to hard-delete facial arrays if a student is purged
        from utils.database import get_attendance_db
        att_db = get_attendance_db()
        
        for s in students:
            with st.expander(f"🎓 {s['username']} - {s['email']}"):
                with st.container():
                    cols = st.columns([2, 3, 2, 2, 1, 1])
                    cols[0].write(f"**{s['username']}**")
                    cols[1].write(s['email'])
                    cols[2].write(f"ID: {s.get('studentId', 'N/A')}")
                    cols[3].write(s.get('status', 'active').capitalize())
                    
                    new_status = "inactive" if s.get('status', 'active') == 'active' else "active"
                    button_label = "Deactivate" if s.get('status', 'active') == 'active' else "Activate"
                    
                    if cols[4].button(button_label, key=f"s_status_{s['_id']}"):
                        db.auth_users.update_one({"_id": s["_id"]}, {"$set": {"status": new_status}})
                        st.rerun()
                        
                    if cols[5].button("Delete", key=f"s_del_{s['_id']}", type="primary"):
                        db.auth_users.delete_one({"_id": s["_id"]})
                        att_db.users.delete_one({"user_id": s["email"]}) # Hard-delete Biometrics
                        st.rerun()
                        
                st.write("---")
                st.markdown("**Enrolled Course:** `MSc AIML (Master Cohort)`")
                
                # Dynamically scan macro network for classes attended
                student_att = list(db.attendance_records.find({"students.name": s['username']}))
                subjs_attended = list(set([rec.get('subject', 'Unknown') for rec in student_att]))
                if subjs_attended:
                    st.markdown(f"**Active Subjects Participating In:** `{', '.join(subjs_attended)}`")
                else:
                    st.write("**Active Subjects:** No structural attendance points recorded yet.")
                st.divider()
