from utils.database import get_db, get_attendance_db
import time
from datetime import datetime
import pandas as pd
import requests
import math
import threading
import requests
import math

def haversine(lat1, lon1, lat2, lon2):
    R = 6371.0 # Earth radius in km
    dlat = math.radians(lat2 - lat1)
    dlon = math.radians(lon2 - lon1)
    a = math.sin(dlat / 2)**2 + math.cos(math.radians(lat1)) * math.cos(math.radians(lat2)) * math.sin(dlon / 2)**2
    c = 2 * math.atan2(math.sqrt(a), math.sqrt(1 - a))
    return R * c

st.set_page_config(page_title="Teacher Dashboard", page_icon="🏫", layout="wide")

if "user" not in st.session_state or not st.session_state.user or st.session_state.user.get("role") != "teacher":
    st.error("Teacher Access Required.")
    st.stop()

st.title("🏫 Teacher Management Portal")
st.write(f"Logged in as: {st.session_state.user['name']}")
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
        
        st.markdown("### 🔒 Security Gates")
        enforce_geo = st.checkbox("Enforce Geo-Fencing (Must be within 5km of Campus)", value=True)
        enforce_time = st.checkbox("Enforce Smart Timetable (Must be within scheduled hours)", value=True)
        
        submit_sess = st.form_submit_button("Create Session", type="primary")
        
        if submit_sess:
            allowed = True
            
            # 1. Geo-Fencing Check
            if enforce_geo:
                try:
                    res = requests.get("https://ipinfo.io/json", timeout=5).json()
                    loc = res.get("loc", "0,0").split(",")
                    t_lat, t_lon = float(loc[0]), float(loc[1])
                    dist = haversine(INSTITUTION_LAT, INSTITUTION_LON, t_lat, t_lon)
                    
                    if dist > 5.0:
                        st.error(f"📍 Geo-Fence Blocked: You are {dist:.1f}km away from campus. Sessions must be started on-site.")
                        allowed = False
                    else:
                        st.success(f"📍 Geo-Fence Passed: You are {dist:.1f}km from the campus center.")
                except Exception as e:
                    st.warning("Could not verify location. Bypassing Geo-Fence securely.")
                    
            # 2. Smart Timetable Check
            if allowed and enforce_time:
                sched = TIMETABLE.get(dept.upper())
                if not sched:
                    st.error(f"⏱️ Timetable Blocked: No schedule found for Department '{dept}'. (Try 'IT' or 'CS')")
                    allowed = False
                else:
                    curr_time = datetime.now().strftime("%H:%M")
                    if curr_time < sched["start"] or curr_time > sched["end"]:
                        st.error(f"⏱️ Timetable Blocked: The '{dept}' schedule is strictly between {sched['start']} and {sched['end']}. It is currently {curr_time}.")
                        allowed = False
                    else:
                        st.success(f"⏱️ Timetable Passed: Session is operating within the legal {sched['start']} - {sched['end']} timeframe.")
            
            # Final Approval
            if allowed:
                st.session_state.current_session = {
                    "department": dept, "year": year, "created_at": datetime.now()
                }
                st.success("Session configured and live!")
    
    if "current_session" in st.session_state:
        st.write("---")
        st.write("### Camera Live Feed")
        try:
            from streamlit_webrtc import webrtc_streamer, VideoTransformerBase
            from mtcnn import MTCNN
            from deepface import DeepFace
            from scipy.spatial.distance import cosine
            
            # Fetch all user embeddings from DB natively
            users_in_db = list(att_db.users.find())
            
            class FaceCapture(VideoTransformerBase):
                def __init__(self):
                    self.detector = MTCNN()
                    self.users = users_in_db
                    self.threshold = 0.7
                    self.last_faces = []
                    self.lock = threading.Lock()
                    self.is_processing = False
                    
                def process_frame(self, rgb_image):
                    temp_faces = []
                    try:
                        faces = self.detector.detect_faces(rgb_image)
                        for face in faces:
                            x, y, w, h = face['box']
                            x, y = max(0, x), max(0, y)
                            face_img = rgb_image[y:y+h, x:x+w]
                            
                            try:
                                embedding_res = DeepFace.represent(face_img, model_name='Facenet512', detector_backend='skip', enforce_detection=False)
                                if embedding_res:
                                    embedding = embedding_res[0]['embedding']
                                    best_match = None
                                    min_distance = float('inf')
                                    
                                    for user in self.users:
                                        if 'embedding' in user:
                                            distance = cosine(embedding, user['embedding'])
                                            if distance < min_distance:
                                                min_distance = distance
                                                best_match = user
                                                
                                    if min_distance < self.threshold and best_match:
                                        name_text = f"{best_match['name']}"
                                        color = (0, 255, 0)
                                        # Background save
                                        db.attendance_records.update_one(
                                            {"session_id": str(st.session_state.current_session["created_at"])},
                                            {"$set": {"department": st.session_state.current_session["department"], "year": st.session_state.current_session["year"]},
                                             "$addToSet": {"students": {"student_id": best_match["user_id"], "name": best_match["name"], "present": True, "timestamp": time.time()}}},
                                            upsert=True
                                        )
                                    else:
                                        name_text = "Unknown"
                                        color = (0, 0, 255)
                                        
                                    temp_faces.append({'box': (x,y,w,h), 'text': name_text, 'color': color})
                            except Exception:
                                pass
                    except Exception:
                        pass
                        
                    with self.lock:
                        self.last_faces = temp_faces
                    self.is_processing = False
                    
                def transform(self, frame):
                    img = frame.to_ndarray(format="bgr24")
                    
                    if not self.is_processing:
                        self.is_processing = True
                        rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                        # Offload AI completely to background thread to preserve 30fps camera!
                        threading.Thread(target=self.process_frame, args=(rgb_image,)).start()

                    # Draw the bounding boxes smoothly on the main thread
                    with self.lock:
                        for face in self.last_faces:
                            x, y, w, h = face['box']
                            cv2.rectangle(img, (x, y), (x+w, y+h), face['color'], 2)
                            cv2.putText(img, face['text'], (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, face['color'], 2)

                    return img
            
            webrtc_streamer(key="attendance", video_transformer_factory=FaceCapture)
            
            if st.button("End Session & Finalize Attendance"):
                del st.session_state.current_session
                st.success("Session Ended and attendance saved securely to MongoDB.")
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
                    "Year": yr,
                    "Student ID": student.get("student_id"),
                    "Student Name": student.get("name"),
                    "Status": "Present" if student.get("present") else "Absent"
                })
        
        if flat_data:
            df = pd.DataFrame(flat_data)
            
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
    students = list(db.users.find({"role": "student"}))
    if not students:
        st.warning("No registered students found.")
    else:
        student_opts = {s["email"]: f"{s['name']} ({s['email']})" for s in students}
        
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
