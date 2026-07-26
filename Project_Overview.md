# Smart Face Recognition Attendance System
**A Comprehensive Project Overview & Tech Stack Breakdown**

---

## 🏗️ Project Architecture & Tech Stack

This project is a modern, AI-driven attendance and academic management application. Here is a breakdown of the core technologies, libraries, and frameworks that power this application:

### 1. **Frontend & Application Framework**
* **Streamlit (`streamlit`)**: Used as the core framework to build the entire responsive web application and dashboards.
* **Streamlit WebRTC (`streamlit-webrtc`)**: Used to stream the live camera feed securely from the user's browser directly to our Python backend, utilizing modern `VideoProcessorBase` configurations.

### 2. **Artificial Intelligence & Computer Vision**
* **DeepFace (`deepface`)**: A state-of-the-art face recognition framework used to extract high-dimensional facial geometry embeddings (specifically using the `Facenet512` model variant).
* **MTCNN (`mtcnn`)**: Used for highly precise face detection and bounding box clipping before sending the face to DeepFace.
* **OpenCV (`opencv-python-headless`)**: Used for drawing visual overlays (green/red bounding boxes, text) on the live camera stream.
* **SciPy (`scipy.spatial.distance.cosine`)**: Used to mathematically calculate the Cosine Distance between saved facial embeddings and the live camera feed to verify a student's identity.

### 3. **Backend & Database Management**
* **MongoDB (`pymongo[srv]`)**: A NoSQL database serving as the core persistent storage for users, face embeddings, attendance records, leaves, and grades.
* **Bcrypt (`bcrypt`)**: Used for secure, military-grade password hashing so that no plain-text passwords are ever stored in the database.

### 4. **Data Handling & Reporting**
* **Pandas (`pandas`)**: Used extensively to wrangle database query results into beautiful DataFrames, render visual Analytics charts, and export attendance logs directly to CSV files.
* **FPDF (`fpdf`)**: Used to dynamically generate downloadable "Official Academic PDF Transcripts" on the fly for students.
* **NumPy (`numpy`)**: Required for fast image multi-dimensional array operations.

### 5. **Deployment & Infrastructure (DevOps)**
* **Docker & Docker Compose**: The entire application and MongoDB server are containerized, ensuring that they can be spun up safely and consistently across any environment.

---

## ✨ Key Features We Built Together

Over the course of developing this project, we implemented several major functional modules:

### 1. **Role-Based Unified Dashboards**
The system routes users flawlessly to their specific environments:
* **Admin Console**: Monitor and manage all teacher accounts across the institution (activate/deactivate teachers).
* **Teacher Dashboard**: A robust control center to configure Smart Attendance sessions, approve leave requests, and publish grades.
* **Student Portal**: A highly personalized dashboard where students register their facial geometry, track their grades, download transcripts, and apply for leaves.

### 2. **AI Face Recognition & Registration Pipeline**
* Students can sit in front of their webcam to "register" their faces. The system detects the clearest frame, extracts the geometric embedding via DeepFace, and commits it heavily encrypted to MongoDB.

### 3. **Secure Self-Attendance with Teacher Authorization**
* Rather than simple automatic unlocking, students' cameras are **locked by default**. 
* Teachers use their dashboard to actively configure **Class Sessions**, enforcing constraints such as checking if the student is within the correct **Weekly Timetable** layout before authorizing the opening of the Student Self-Attendance cameras. 

### 4. **Data Visualization & CSV Exports**
* As attendance is captured, Teachers can view comprehensive analytics, metric graphs, and perform one-click exports of all captured attendance directly into CSV format.

### 5. **Academic Grading & Dynamic PDF Transcripts**
* Teachers can push test scores to individual students. 
* Students can immediately visualize their trajectory using a Pandas-driven Line Chart and download a physically structured PDF transcript summarizing their performance!

---
*(Note: You can open this file in VS Code or export it to PDF using any Markdown-to-PDF online converter or VS Code extension!)*
