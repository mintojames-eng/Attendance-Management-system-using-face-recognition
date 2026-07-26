import streamlit as st
from utils.database import get_db

st.set_page_config(page_title="Admin Console", page_icon="🛡️")

if "user" not in st.session_state or not st.session_state.user or st.session_state.user.get("role") != "admin":
    st.error("Admin Access Required. Please login from the main page.")
    st.stop()
    
st.title("🛡️ Super Admin Console")
st.write(f"Logged in as: {st.session_state.user['name']}")

db = get_db()
teachers = list(db.auth_teachers.find({}, {"password": 0}))

st.subheader("Teacher Accounts")

if not teachers:
    st.info("No teachers registered yet.")
else:
    for t in teachers:
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
            st.divider()
