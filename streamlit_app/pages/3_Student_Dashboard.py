from fpdf import FPDF
from datetime import datetime
import threading
from scipy.spatial.distance import cosine
import requests
import math
import time
import cv2
import pandas as pd

import streamlit as st
from utils.database import get_db, get_attendance_db
from utils.ui import apply_custom_css

st.set_page_config(page_title="Student Dashboard", page_icon="🎓", layout="wide")
apply_custom_css()

if "user" not in st.session_state or not st.session_state.user or st.session_state.user.get("role") != "student":
    st.error("Student Access Required. Please login from the main page.")
    st.stop()

db = get_db()
att_db = get_attendance_db()
email = st.session_state.user['email']
name = st.session_state.user['name']

st.title("🎓 Student Portal")
st.write(f"Welcome, {name}!")

tab1, tab2, tab3, tab4, tab5 = st.tabs(["Apply for Leave", "Past Leave Requests", "Face Registration", "Academic Standing", "Self Attendance"])

with tab1:
    st.subheader("Leave Application")
    with st.form("leave_form"):
        date = st.date_input("Date")
        reason = st.text_area("Reason")
        submitted = st.form_submit_button("Submit Request")
        
        if submitted:
            if reason.strip() == "":
                st.error("Please provide a reason.")
            else:
                db.leave_requests.insert_one({
                    "studentEmail": email,
                    "studentName": name,
                    "date": str(date),
                    "reason": reason,
                    "status": "pending",
                    "createdAt": time.time()
                })
                st.success("Leave request submitted successfully!")

with tab2:
    st.subheader("Your Past Requests")
    leaves = list(db.leave_requests.find({"studentEmail": email}).sort("createdAt", -1))
    if not leaves:
        st.info("No leave requests found.")
    else:
        for l in leaves:
            status_color = "green" if l["status"] == "approved" else "red" if l["status"] == "rejected" else "orange"
            st.markdown(f"""
            **Date:** {l['date']} | **Status:** :{status_color}[{l['status'].upper()}]  
            **Reason:** {l['reason']}
            """)
            st.divider()

with tab3:
    st.subheader("Face Registration")
    st.write("Register your facial geometry so the system can recognize you during attendance sessions.")
    
    existing = att_db.users.find_one({"user_id": email})
    if existing:
        st.success("✅ Your face is already registered in the system database.")
        if st.button("Re-Register Face"):
            att_db.users.delete_one({"user_id": email})
            st.rerun()
    else:
        st.warning("Please look directly at the camera. Registration will trigger automatically when a clear face is detected.")
        try:
            from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
            from mtcnn import MTCNN
            from deepface import DeepFace
            import av
            
            RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
            
            def get_register_factory(user_email, user_name):
                class FaceRegister(VideoProcessorBase):
                    def __init__(self):
                        self.detector = MTCNN()
                        self.registered = False
                        self.frame_count = 0
                        self.overlay = None
                        self.user_email = user_email
                        self.user_name = user_name
                        
                    def recv(self, frame):
                        img = frame.to_ndarray(format="bgr24")
                        if self.registered:
                            cv2.putText(img, "Registration Complete! You can stop the camera.", (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, (0, 255, 0), 2)
                            return av.VideoFrame.from_ndarray(img, format="bgr24")
                            
                        self.frame_count += 1
                        
                        if self.frame_count % 15 == 0:
                            rgb_image = cv2.cvtColor(img, cv2.COLOR_BGR2RGB)
                            self.overlay = None
                            try:
                                faces = self.detector.detect_faces(rgb_image)
                                if len(faces) == 1:
                                    x, y, w, h = faces[0]['box']
                                    x, y = max(0, x), max(0, y)
                                    face_img = rgb_image[y:y+h, x:x+w]
                                    
                                    self.overlay = {'box': (x,y,w,h), 'text': "Extracting Geometric Vector..."}
                                    
                                    # DeepFace represent
                                    try:
                                        embedding_res = DeepFace.represent(face_img, model_name='Facenet512', detector_backend='skip', enforce_detection=False)
                                        if embedding_res:
                                            embedding = embedding_res[0]['embedding']
                                            
                                            # Save permanently to MongoDB users collection
                                            att_db.users.update_one(
                                                {'user_id': self.user_email},
                                                {'$set': {'name': self.user_name, 'embedding': embedding}},
                                                upsert=True
                                            )
                                            self.registered = True
                                            self.overlay = None
                                    except Exception:
                                        pass
                                elif len(faces) > 1:
                                    self.overlay = {'msg': "Too many faces! Please be alone in frame.", 'color': (0,0,255)}
                                else:
                                    self.overlay = {'msg': "Looking for a clear face...", 'color': (0,0,255)}
                            except Exception:
                                pass

                        # Draw cached overlay to keep video stream running at 30 FPS
                        if self.overlay:
                            if 'box' in self.overlay:
                                x,y,w,h = self.overlay['box']
                                cv2.rectangle(img, (x, y), (x+w, y+h), (255, 165, 0), 2)
                                cv2.putText(img, self.overlay['text'], (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.6, (255, 165, 0), 2)
                            elif 'msg' in self.overlay:
                                cv2.putText(img, self.overlay['msg'], (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.7, self.overlay['color'], 2)

                        return av.VideoFrame.from_ndarray(img, format="bgr24")
                return FaceRegister
            
            webrtc_streamer(key="face_registration", video_processor_factory=get_register_factory(email, name), rtc_configuration=RTC_CONFIG)
        except ImportError:
            st.error("Waiting for WebRTC dependencies to load...")

with tab4:
    st.subheader("Academic Standing & Transcripts")
    grades = list(db.academic_grades.find({"student_id": email}))
    
    if not grades:
        st.info("No academic assessment data published yet.")
    else:
        st.write("### Your Academic Trajectory")
        # Structure data
        g_data = []
        for g in grades:
            pct = (g["score"] / g["max_score"]) * 100
            g_data.append({"Assessment": f'{g["subject"]} ({g["assessment"]})', "Score (%)": pct})
            
        df = pd.DataFrame(g_data).set_index("Assessment")
        st.line_chart(df)
        
        st.write("### Absolute Records")
        st.dataframe(df, use_container_width=True)
        
        # Transcript Generation
        def generate_pdf():
            pdf = FPDF()
            pdf.add_page()
            
            pdf.set_font('helvetica', 'B', 20)
            pdf.cell(190, 15, "OFFICIAL ACADEMIC TRANSCRIPT", ln=True, align="C")
            pdf.ln(5)
            
            pdf.set_font('helvetica', '', 12)
            pdf.cell(190, 8, f"Student Name: {name}", ln=True)
            pdf.cell(190, 8, f"Student ID: {email}", ln=True)
            pdf.cell(190, 8, f"Report Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
            pdf.ln(10)
            
            # Grades table
            pdf.set_font('helvetica', 'B', 12)
            pdf.cell(80, 10, "Subject", border=1)
            pdf.cell(50, 10, "Assessment", border=1)
            pdf.cell(30, 10, "Score", border=1)
            pdf.cell(30, 10, "Percentage", border=1, ln=True)
            
            pdf.set_font('helvetica', '', 12)
            total_pct = 0
            for g in grades:
                p = (g["score"] / g["max_score"]) * 100
                total_pct += p
                pdf.cell(80, 10, g["subject"], border=1)
                pdf.cell(50, 10, g["assessment"], border=1)
                pdf.cell(30, 10, f'{g["score"]}/{g["max_score"]}', border=1)
                pdf.cell(30, 10, f'{p:.1f}%', border=1, ln=True)
                
            pdf.ln(10)
            pdf.set_font('helvetica', 'B', 14)
            pdf.cell(190, 10, f"Cumulative Academic GPA: {(total_pct/len(grades)):.1f}%", ln=True, align="C")
            
            # Export to bytes
            return pdf.output(dest='S')
            
        pdf_bytes = generate_pdf()
        st.download_button(
            label="🎓 Download Official PDF Transcript",
            data=pdf_bytes,
            file_name=f"{name.replace(' ', '_')}_Transcript.pdf",
            mime="application/pdf",
            type="primary"
        )

with tab5:
    st.subheader("Automated Class Attendance")
    st.markdown("Mark yourself present using AI. The system checks if your teacher has authorized a self-attendance session.")
    
    MSC_TIMETABLE = {
        "Monday": [{"start": "07:30", "end": "09:00", "subject": "ML(NV)"}, {"start": "09:45", "end": "10:45", "subject": "HED"}, {"start": "10:45", "end": "11:45", "subject": "ADT(BD)"}, {"start": "11:45", "end": "12:45", "subject": "AI(FR)"}],
        "Tuesday": [{"start": "07:30", "end": "09:00", "subject": "ADT(BD)"}, {"start": "09:45", "end": "11:45", "subject": "ML LAB"}, {"start": "11:45", "end": "12:45", "subject": "PP(GR)"}],
        "Wednesday": [{"start": "07:30", "end": "09:00", "subject": "AI(FR)"}, {"start": "09:45", "end": "10:45", "subject": "SM"}, {"start": "10:45", "end": "11:45", "subject": "Library"}, {"start": "11:45", "end": "13:45", "subject": "ADT LAB"}],
        "Thursday": [{"start": "07:30", "end": "09:00", "subject": "CM"}, {"start": "09:45", "end": "11:45", "subject": "PP"}, {"start": "11:45", "end": "13:45", "subject": "ML LAB"}],
        "Friday": [{"start": "07:30", "end": "09:00", "subject": "SM"}, {"start": "09:45", "end": "10:45", "subject": "ML (NV)"}, {"start": "10:45", "end": "12:45", "subject": "CLST"}],
        "Saturday": [{"start": "08:00", "end": "10:00", "subject": "CM"}, {"start": "10:00", "end": "12:00", "subject": "ADT LAB"}],
        "Sunday": [] # Custom logic easily added to test it on weekends!
    }
    
    df_timetable = []
    for day, blocks in MSC_TIMETABLE.items():
        for block in blocks:
            df_timetable.append({"Day": day, "Time": f"{block['start']} - {block['end']}", "Subject": block["subject"]})
            
    if df_timetable:
        with st.expander("📅 View Weekly Class Schedule"):
            st.dataframe(pd.DataFrame(df_timetable), use_container_width=True)
            
    active_session = db.active_sessions.find_one({"active": True, "allow_self": True})
    active_subject = None
    
    if active_session:
        active_subject = active_session.get("department", "Authorized Session") + " (" + active_session.get("year", "") + ")"
        st.success(f"🔓 Self-Attendance Unlocked: {active_subject}")
    else:
        st.error("🔒 Camera Locked: A teacher must explicitly open self-attendance from their dashboard first.")
            
    if active_subject:
        # Load user data natively
        me = att_db.users.find_one({"user_id": email})
        my_embedding = me.get("embedding") if me else None
        
        if not my_embedding:
            st.error("You must register your face in the 'Face Registration' tab first!")
        else:
            try:
                from streamlit_webrtc import webrtc_streamer, VideoProcessorBase, RTCConfiguration
                from mtcnn import MTCNN
                from deepface import DeepFace
                import av
                
                RTC_CONFIG = RTCConfiguration({"iceServers": [{"urls": ["stun:stun.l.google.com:19302"]}]})
                
                def get_attendance_factory(user_email, user_name, embed, subj):
                    class SelfAttendance(VideoProcessorBase):
                        def __init__(self):
                            self.detector = MTCNN()
                            self.my_embedding = embed
                            self.lock = threading.Lock()
                            self.is_processing = False
                            self.overlay = None
                            self.user_email = user_email
                            self.user_name = user_name
                            self.subj = subj
                            
                        def process_frame(self, rgb_image):
                            try:
                                faces = self.detector.detect_faces(rgb_image)
                                if len(faces) == 0:
                                    with self.lock: self.overlay = {'msg': "Waiting...", 'color': (0,0,255)}
                                    self.is_processing = False
                                    return
                                    
                                x, y, w, h = faces[0]['box']
                                face_img = rgb_image[max(0,y):y+h, max(0,x):x+w]
                                
                                res = DeepFace.represent(face_img, model_name='Facenet512', detector_backend='skip', enforce_detection=False)
                                if res:
                                    live_embed = res[0]['embedding']
                                    dist = cosine(live_embed, self.my_embedding)
                                    
                                    if dist < 0.7:
                                        with self.lock: self.overlay = {'box': (x,y,w,h), 'text': "VERIFIED!", 'color': (0,255,0)}
                                        # Log attendance instantly
                                        date_key = datetime.now().strftime("%Y-%m-%d")
                                        db.attendance_records.update_one(
                                            {"session_id": f"Self_{date_key}_{self.subj}"},
                                            {"$set": {"department": "MSc AIML", "subject": self.subj},
                                             "$addToSet": {"students": {"student_id": self.user_email, "name": self.user_name, "present": True, "timestamp": time.time()}}},
                                            upsert=True
                                        )
                                    else:
                                        with self.lock: self.overlay = {'box': (x,y,w,h), 'text': "FACE MISMATCH!", 'color': (0,0,255)}
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
                                if self.overlay:
                                    if 'box' in self.overlay:
                                        x,y,w,h = self.overlay['box']
                                        cv2.rectangle(img, (x, y), (x+w, y+h), self.overlay['color'], 2)
                                        cv2.putText(img, self.overlay['text'], (x, y-10), cv2.FONT_HERSHEY_SIMPLEX, 0.9, self.overlay['color'], 2)
                                    elif 'msg' in self.overlay:
                                        cv2.putText(img, self.overlay['msg'], (20, 50), cv2.FONT_HERSHEY_SIMPLEX, 0.9, self.overlay['color'], 2)
                                        
                            return av.VideoFrame.from_ndarray(img, format="bgr24")
                    return SelfAttendance
                        
                webrtc_streamer(key="self_attendance", video_processor_factory=get_attendance_factory(email, name, my_embedding, active_subject), rtc_configuration=RTC_CONFIG)
            except ImportError:
                st.error("Loading AI dependencies...")
