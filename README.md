# 🎓 Advanced AI Attendance & University Management System

Welcome to the **Fully Containerized SaaS AI Portal**. This project entirely modernizes the concept of Academic Information Systems by integrating native Deep Learning facial geometry extraction directly into a Dockerized web browser.

### 🌟 Core Technologies
* **Frontend/Backend Routing**: Streamlit & Python 3.10
* **Computer Vision**: DeepFace (Facenet512) & MTCNN 
* **Database Pipeline**: MongoDB (NoSQL)
* **Realtime Streaming**: WebRTC via `streamlit-webrtc`
* **Infrastructure**: Full Docker Compose Orchestration

---

## 🔥 Enterprise Features Built-In

* **Real-time WebRTC AI Validation:** No hardware required. Natively streams webcam feeds to compute MTCNN bounds and Facenet512 geometric tensors at ~30FPS.
* **Role-Based Access Control:** Highly secured Admin, Teacher, and Student dashboard hierarchies.
* **Academic Information System (SIS):** A comprehensive internal grades hub capable of generating interactive student GPA line-charts and officially downloading **PDF Report Cards** via FPDF. 
* **Geographical Defenses:** Implements strict IP Geocoding checks against Haversine Mathematics. Physically locks WebRTC sessions from being started by teachers outside a 5km radius of the University Campus.
* **Smart Timetables:** Mathematically refuses to authenticate AI checks if the Teacher attempts to start a session outside the officially designated classroom schedule.
* **One-Click CSV Export:** Natively transforms complex nested NoSQL Array data into readable, flattened Pandas Dataframes for administrative export.

---

## 🚀 How to Run (Zero Configurations Required)

Because this platform has been entirely **Dockerized**, there is zero reliance on Windows background services.

1. Clone the repository.
2. Ensure Docker Desktop is running on your machine.
3. Open a terminal in this root directory and type:
   ```bash
   docker-compose up --build
   ```
4. Access the fully functional web application instantly at: `http://localhost:8501`
