from utils.database import get_db, get_attendance_db
import time
from datetime import datetime
import pandas as pd
import requests
import math
import threading

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

import streamlit as st
from utils.ui import apply_custom_css
st.set_page_config(page_title="Teacher Dashboard", page_icon="🏫", layout="wide")
apply_custom_css()

if "user" not in st.session_state or not st.session_state.user or st.session_state.user.get("role") != "teacher":
    st.error("Teacher Access Required.")
    st.stop()

col1, col2 = st.columns([5, 1])
with col1:
    st.title("🏫 Teacher Management Portal")
    st.write(f"Logged in as: {st.session_state.user['name']}")
with col2:
    st.write("")
    if st.button("Logout 🚪", type="secondary"):
        st.session_state.user = None
        st.switch_page("main.py")
db = get_db()
att_db = get_attendance_db()

tab1, tab2, tab3, tab4 = st.tabs(["Leave Approvals", "Start Face Recognition Session", "Analytics & Reports", "Academic Grading"])

with tab1:
    st.subheader("Manage Leave Requests")
    leaves = list(db.leave_requests.find().sort("createdAt", -1))
    
    if not leaves:
        st.info("No pending requests.")
    else:
        for l in leaves:
            col1, col2, col3, col4 = st.columns([3, 2, 2, 3])
            col1.write(f"**{l['studentName']}** ({l['date']})")
            col2.write(l['reason'])
            
            status_color = "green" if l['status'] == 'approved' else "red" if l['status'] == 'rejected' else "orange"
            col3.markdown(f":{status_color}[{l['status'].upper()}]")
            
            if l['status'] == 'pending':
                sub1, sub2 = col4.columns(2)
                if sub1.button("✔ Approve", key=f"app_{l['_id']}"):
                    db.leave_requests.update_one({"_id": l["_id"]}, {"$set": {"status": "approved"}})
                    st.rerun()
                if sub2.button("✖ Reject", key=f"rej_{l['_id']}"):
                    db.leave_requests.update_one({"_id": l["_id"]}, {"$set": {"status": "rejected"}})
                    st.rerun()
            st.divider()

with tab2:
    if "popped_present" in st.session_state:
        st.success("Session Ended and attendance saved securely to MongoDB.")
        with st.expander("✅ See Session Results", expanded=True):
            col1, col2 = st.columns(2)
            with col1:
                st.write("### Present")
                if st.session_state.popped_present:
                    for name in st.session_state.popped_present:
                        st.write(f"- {name}")
                else:
                    st.write("None")
                    
            with col2:
                st.write("### Absent")
                if "popped_absent" in st.session_state and st.session_state.popped_absent:
                    for name in st.session_state.popped_absent:
                        st.write(f"- {name}")
                else:
                    st.write("None")
                    
            # Generate CSV seamlessly here
            csv_str = "Student Name,Attendance Status\\n"
            for n in st.session_state.popped_present: csv_str += f"{n},Present\\n"
            if "popped_absent" in st.session_state:
                for n in st.session_state.popped_absent: csv_str += f"{n},Absent\\n"
                
            st.download_button("📥 Download Final Roster (.csv)", data=csv_str.encode('utf-8'), file_name=f"{st.session_state.get('popped_sess_id', 'Session')}_Report.csv", mime="text/csv", type="primary")
            
            if st.button("Close Window"):
                del st.session_state.popped_present
                if "popped_absent" in st.session_state: del st.session_state.popped_absent
                if "popped_sess_id" in st.session_state: del st.session_state.popped_sess_id
                st.rerun()

    st.subheader("Start Attendance Session")
    st.warning("WebRTC integration for production requires HTTPS and STUN/TURN servers.")
    
    # Institution coordinates (e.g., Campus Center)
    INSTITUTION_LAT = 19.0760 
    INSTITUTION_LON = 72.8777
    
    # Institution Timetable (Department defaults for demonstration)
    TIMETABLE = {
        "IT": {"start": "08:00", "end": "17:00"},
        "CS": {"start": "10:00", "end": "11:00"}
    }
    
    with st.form("session_setup"):
        dept = st.text_input("Department (e.g. IT, CS)")
        year = st.text_input("Year (e.g. TE, BE)")
        subject = st.text_input("Subject (e.g. Data Structures)")
        session_code = st.text_input("Session Code (e.g. DS101)")
        
        st.markdown("### 🔒 Security Gates & Parameters")
        enforce_geo = st.checkbox("Enforce Geo-Fencing (Within Campus)", value=True)
        is_extra = st.checkbox("🌟 Mark as 'Extra Class / Special Session' (Bypasses Timetable Lock)", value=False)
        extra_desc = st.text_input("Extra Class Description (e.g. Midterm Prep, Cultural Event, Extra Lab)") if is_extra else ""
        allow_self = st.checkbox("Grant Students Permission for Self Attendance", value=False)
        
        submit_sess = st.form_submit_button("Create Session", type="primary")
        
        if submit_sess:
            allowed = True
            
            override_doc = db.global_settings.find_one({"type": "special_event"})
            admin_bypass = override_doc.get("active", False) if override_doc else False
            
            # 1. Geo-Fencing Check
            if enforce_geo:
                if admin_bypass:
                    st.warning("🚨 Admin Override Active: Geo-Fence Verification Bypassed for Special Event.")
                else:
                    try:
                        res = requests.get("https://ipinfo.io/json", timeout=5).json()
                        loc = res.get("loc", "0,0").split(",")
                        t_lat, t_lon = float(loc[0]), float(loc[1])
                        dist = haversine(INSTITUTION_LAT, INSTITUTION_LON, t_lat, t_lon)
                        
                        if dist > 5.0:
                            st.error(f"📍 Geo-Fence Blocked: You are {dist:.1f}km away from campus. Contact Admin to activate the Special Event portal.")
                            allowed = False
                        else:
                            st.success(f"📍 Geo-Fence Passed: You are {dist:.1f}km from the campus center.")
                    except Exception as e:
                        st.warning("Could not verify location. Bypassing Geo-Fence securely.")
                    
            # 2. Smart Timetable Check
            if allowed and not is_extra:
                if admin_bypass:
                    st.warning("🚨 Admin Override Active: Timetable Restrictions Bypassed for Special Event.")
                else:
                    sched = TIMETABLE.get(dept.upper())
                    if not sched:
                        st.error(f"⏱️ Timetable Blocked: No schedule found for Department '{dept}'. (Try 'IT' or 'CS')")
                        allowed = False
                    else:
                        curr_time = datetime.now().strftime("%H:%M")
                        if curr_time < sched["start"] or curr_time > sched["end"]:
                            st.error(f"⏱️ Timetable Blocked: The '{dept}' schedule is strictly between {sched['start']} and {sched['end']}. It is currently {curr_time}. Contact Admin to activate the Special Event portal or check 'Extra Class'.")
                            allowed = False
                        else:
                            st.success(f"⏱️ Timetable Passed: Session is operating within the legal {sched['start']} - {sched['end']} timeframe.")
            elif allowed and is_extra:
                if admin_bypass:
                    st.warning("🚨 Admin Override Active: Timetable Restrictions Bypassed for Special Event.")
                else:
                    st.success("🌟 Extra Class Authorized: Standard Timetable bypassed securely.")
                    subject = f"{subject} (Extra Class: {extra_desc})" if extra_desc else f"{subject} (Extra Class)"
            
            # Final Approval
            if allowed:
                now_stamp = datetime.now()
                st.session_state.current_session = {
                    "department": dept, "year": year, "subject": subject, "session_code": session_code, "created_at": now_stamp
                }
                db.active_sessions.update_one(
                    {"teacher_email": st.session_state.user['email']},
                    {"$set": {"department": dept, "year": year, "subject": subject, "session_code": session_code, "created_at": now_stamp, "allow_self": allow_self, "active": True}},
                    upsert=True
                )
                st.success("Session configured and live!")
    
    if "current_session" in st.session_state:
        # 5 Minute Auto-Timeout Check
        elapsed = (datetime.now() - st.session_state.current_session["created_at"]).total_seconds() / 60.0
        if elapsed > 5.0:
            date_key = datetime.now().strftime("%Y-%m-%d")
            sess_id = f"{st.session_state.current_session['session_code']}_{date_key}"
            record = db.attendance_records.find_one({"session_id": sess_id})
            
            # Calculate Present vs Absent for automatic Stop
            present_names = sorted(list(set([s["name"] for s in record.get("students", []) if s.get("present")]))) if record else []
            all_students = [u["name"] for u in list(att_db.users.find())]
            absent_names = sorted([n for n in all_students if n not in present_names])
            
            st.session_state.popped_present = present_names
            st.session_state.popped_absent = absent_names
            st.session_state.popped_sess_id = sess_id
            
            db.active_sessions.delete_one({"teacher_email": st.session_state.user['email']})
            del st.session_state.current_session
            st.rerun()

        st.write("---")
        st.write("### Camera Live Feed")
        st.info(f"⏳ Session Auto-Closes in: {5.0 - elapsed:.1f} minutes.")
        
        # Native Streamlit autorefresh for timeout enforcement
        from streamlit_autorefresh import st_autorefresh
        st_autorefresh(interval=5000, limit=None, key="teacher_autotimer")
        
        try:
            from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
            from mtcnn import MTCNN
            from deepface import DeepFace
            from scipy.spatial.distance import cosine
            import av
            
            RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
            
            # Fetch all user embeddings from DB natively
            users_in_db = list(att_db.users.find())
            
            class FaceCapture(VideoProcessorBase):
                def __init__(self):
                    self.detector = MTCNN()
                    self.users = users_in_db
                    self.lock = threading.Lock()
                    self.last_faces = []
                    self.is_processing = False
                    
                def process_frame(self, rgb_image):
                    try:
                        if "current_session" in st.session_state:
                            session_time = st.session_state.current_session.get("created_at", datetime.now())
                            if (datetime.now() - session_time).total_seconds() / 60.0 > 5.0:
                                with self.lock:
                                    self.last_faces = [{'box': (10, 30, 0, 0), 'text': "SESSION EXPIRED", 'color': (0,0,255)}]
                                self.is_processing = False
                                return
                                
                        faces = self.detector.detect_faces(rgb_image)
                        temp_faces = []
                        for face in faces:
                            x, y, w, h = face['box']
                            face_img = rgb_image[max(0,y):y+h, max(0,x):x+w]
                            
                            res = DeepFace.represent(face_img, model_name='Facenet512', detector_backend='skip', enforce_detection=False)
                            label = "Unknown"
                            color = (0, 0, 255) # Red
                            
                            if res:
                                live_embed = res[0]['embedding']
                                # Find best match
                                best_dist = float('inf')
                                for u in self.users:
                                    if 'embedding' in u:
                                        dist = cosine(live_embed, u['embedding'])
                                        if dist < best_dist and dist < 0.30:
                                            best_dist = dist
                                            label = u['name']
                                            color = (0, 255, 0) # Green
                                            
                                # Auto Log if known!
                                if label != "Unknown":
                                    date_key = datetime.now().strftime("%Y-%m-%d")
                                    db.attendance_records.update_one(
                                        {"session_id": f"{st.session_state.current_session['session_code']}_{date_key}"},
                                        {"$set": {"department": st.session_state.current_session.get("department", "Unknown"), 
                                                  "year": st.session_state.current_session.get("year", "Unknown")},
                                         "$addToSet": {"students": {"name": label, "present": True}}},
                                        upsert=True
                                    )
                                            
                            temp_faces.append({'box': (x,y,w,h), 'text': label, 'color': color})
                            
                        with self.lock:
                            self.last_faces = temp_faces
                    except:
                        pass
                    self.is_processing = False
                    
                def recv(self, frame):
                    img = frame.to_ndarray(format="bgr24")
                    
                    if not self.is_processing:
                        self.is_processing = True
                        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        threading.Thread(target=self.process_frame, args=(rgb_image,)).start()

                    with self.lock:
                        for face in self.last_faces:
                            x, y, w, h = face['box']
                            cv2.rectangle(img, (x, y), (x+w, y+h), face['color'], 2)
                            cv2.putText(img, face['text'], (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, face['color'], 2)

                    return av.VideoFrame.from_ndarray(img, format="bgr24")
            
            webrtc_streamer(key="attendance", video_processor_factory=FaceCapture, rtc_configuration=RTC_CONFIG)
            
            if st.button("🛑 Stop Session & Finalize Attendance", type="primary"):
                date_key = datetime.now().strftime("%Y-%m-%d")
                sess_id = f"{st.session_state.current_session['session_code']}_{date_key}"
                record = db.attendance_records.find_one({"session_id": sess_id})
                
                # Calculate Present vs Absent
                present_names = sorted(list(set([s["name"] for s in record.get("students", []) if s.get("present")]))) if record else []
                all_students = [u["name"] for u in list(att_db.users.find())]
                absent_names = sorted([n for n in all_students if n not in present_names])
                
                st.session_state.popped_present = present_names
                st.session_state.popped_absent = absent_names
                st.session_state.popped_sess_id = sess_id
                
                db.active_sessions.delete_one({"teacher_email": st.session_state.user['email']})
                del st.session_state.current_session
                st.rerun()
                
        except ImportError:
            st.error("Waiting for streamlit-webrtc installation to complete or failed to import.")

with tab3:
    st.subheader("Attendance Analytics & CSV Export")
    records = list(db.attendance_records.find().sort("session_id", -1))
    
    if not records:
        st.info("No attendance records found yet.")
    else:
        flat_data = []
        for r in records:
            sess_date = r.get("session_id", "Unknown Date")
            try:
                # Format for readable charts if possible
                sess_date = sess_date.split(".")[0] 
            except: pass
            
            dept = r.get("department", "N/A")
            yr = r.get("year", "N/A")
            for student in r.get("students", []):
                flat_data.append({
                    "Date & Time": sess_date,
                    "Department": dept,
                    "Subject & Event Details": r.get("subject", "N/A"),
                    "Year": yr,
                    "Student ID": student.get("student_id"),
                    "Student Name": student.get("name"),
                    "Status": "Present" if student.get("present") else "Absent"
                })
        
        if flat_data:
            df = pd.DataFrame(flat_data)
            
            # Retroactively drop duplicate logs from legacy sessions
            df = df.drop_duplicates(subset=["Date & Time", "Student Name", "Status"])
            
            st.write("### 📊 View Attendance Percentages")
            subjects = list(set([r.get("subject", "N/A") for r in records if "subject" in r]))
            selected_subject = st.selectbox("Pick any subject to view percentage:", ["-- Select --"] + subjects)
            
            if selected_subject != "-- Select --":
                subj_records = [r for r in records if r.get("subject") == selected_subject]
                total_classes = len(subj_records)
                
                attendance_counts = {}
                for r in subj_records:
                    present_students = set([s["name"] for s in r.get("students", []) if s.get("present")])
                    for student in present_students:
                        attendance_counts[student] = attendance_counts.get(student, 0) + 1
                
                if attendance_counts:
                    pct_data = []
                    for s, count in attendance_counts.items():
                        pct = (count / total_classes) * 100
                        pct_data.append({"Student": s, "Classes Attended": count, "Total Classes": total_classes, "Attendance %": f"{pct:.1f}%"})
                    pct_df = pd.DataFrame(pct_data).sort_values(by="Attendance %", ascending=False)
                    st.dataframe(pct_df, use_container_width=True)
                else:
                    st.info("No attendance recorded for this subject yet.")
            
            st.write("---")
            
            # High-level Metrics
            total_sessions = len(records)
            total_presences = len(df)
            
            c1, c2, c3 = st.columns(3)
            c1.metric("Total Sessions Conducted", total_sessions)
            c2.metric("Total Presences Logged", total_presences)
            c3.metric("Unique Students Seen", df["Student ID"].nunique())
            
            st.write("### Attendance Volume By Session")
            try:
                # Group by session string and plot
                date_counts = df.groupby("Date & Time").size()
                st.bar_chart(date_counts)
            except Exception:
                st.write("Not enough data to graph.")
            
            st.write("### Raw Database Snapshot")
            st.dataframe(df, use_container_width=True)
            
            # CSV Download logic
            csv = df.to_csv(index=False).encode('utf-8')
            st.download_button(
                label="📥 Download Full Report as CSV",
                data=csv,
                file_name=f'attendance_export_{datetime.now().strftime("%Y%m%d")}.csv',
                mime='text/csv',
                type="primary"
            )

with tab4:
    st.subheader("Academic Grading Hub")
    st.write("Upload assessment scores directly to a student's official transcript.")
    
    # Fetch all students from users db to select
    students = list(db.auth_users.find({"role": "student"}))
    if not students:
        st.warning("No registered students found.")
    else:
        student_opts = {s["email"]: f"{s.get('username', 'Unknown')} ({s['email']})" for s in students}
        
        with st.form("grade_form"):
            target = st.selectbox("Select Student:", options=list(student_opts.keys()), format_func=lambda x: student_opts[x])
            col1, col2 = st.columns(2)
            subj = col1.text_input("Subject (e.g. Data Structures)")
            assess = col2.text_input("Assessment (e.g. Midterm, Final)")
            
            c3, c4 = st.columns(2)
            score = c3.number_input("Score Achieved", min_value=0.0, step=0.5)
            max_score = c4.number_input("Maximum Possible Score", min_value=1.0, value=100.0, step=1.0)
            
            if st.form_submit_button("Publish Grade", type="primary"):
                db.academic_grades.insert_one({
                    "student_id": target,
                    "student_name": student_opts[target].split(" (")[0],
                    "subject": subj,
                    "assessment": assess,
                    "score": score,
                    "max_score": max_score,
                    "timestamp": datetime.now()
                })
                st.success(f"Successfully published {score}/{max_score} in {subj} for {student_opts[target].split(' (')[0]}!")
