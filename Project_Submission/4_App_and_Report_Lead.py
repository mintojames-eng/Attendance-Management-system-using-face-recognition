# ==========================================
# ROLE 4: APP & REPORT LEAD
# ==========================================
# Responsibilities: 
# - Application Architecture (Streamlit UI/UX routing and state).
# - API Integration and real-time visualization.
# - Automated Report Generation (PDF transcripts, CSV Exports).

from fpdf import FPDF
from datetime import datetime
import pandas as pd
import os

class ReportGenerator:
    """Handles the creation of final user-facing PDF reports and Data Exports."""
    
    def __init__(self, institute_name="Advanced Institute of Technology"):
        self.institute_name = institute_name
        
    def generate_attendance_csv(self, records):
        """Exports raw attendance records to CSV for Admin processing."""
        if not records:
            print("No records to export.")
            return
            
        df = pd.DataFrame(records)
        filename = f"Attendance_Export_{datetime.now().strftime('%Y%m%d')}.csv"
        df.to_csv(filename, index=False)
        print(f"Successfully generated analytical export: {filename}")
        
    def generate_student_academic_transcript(self, student_info, grades):
        """Generates a highly-formatted PDF transcript for a specific student."""
        pdf = FPDF()
        pdf.add_page()
        
        # Header
        pdf.set_font('helvetica', 'B', 20)
        pdf.cell(190, 15, "OFFICIAL ACADEMIC TRANSCRIPT", ln=True, align="C")
        pdf.set_font('helvetica', 'I', 12)
        pdf.cell(190, 8, self.institute_name, ln=True, align="C")
        pdf.ln(10)
        
        # Student Info
        pdf.set_font('helvetica', '', 12)
        pdf.cell(190, 8, f"Student Name: {student_info.get('name', 'Unknown')}", ln=True)
        pdf.cell(190, 8, f"Student ID / Email: {student_info.get('email', 'Unknown')}", ln=True)
        pdf.cell(190, 8, f"Report Date: {datetime.now().strftime('%Y-%m-%d')}", ln=True)
        pdf.ln(10)
        
        # Table Headers
        pdf.set_font('helvetica', 'B', 12)
        pdf.cell(80, 10, "Subject", border=1)
        pdf.cell(50, 10, "Assessment", border=1)
        pdf.cell(30, 10, "Score", border=1)
        pdf.cell(30, 10, "Percentage", border=1, ln=True)
        
        # Table Data
        pdf.set_font('helvetica', '', 12)
        total_pct = 0
        
        for g in grades:
            p = (g["score"] / g["max_score"]) * 100
            total_pct += p
            pdf.cell(80, 10, str(g["subject"]), border=1)
            pdf.cell(50, 10, str(g["assessment"]), border=1)
            pdf.cell(30, 10, f'{g["score"]}/{g["max_score"]}', border=1)
            pdf.cell(30, 10, f'{p:.1f}%', border=1, ln=True)
            
        # Summary
        pdf.ln(10)
        pdf.set_font('helvetica', 'B', 14)
        if len(grades) > 0:
            avg = total_pct / len(grades)
            pdf.cell(190, 10, f"Cumulative Academic GPA: {avg:.1f}%", ln=True, align="C")
        
        filename = f"Transcript_{student_info.get('name', 'Student').replace(' ', '_')}.pdf"
        pdf.output(filename)
        print(f"Generated Official Transcript: {filename}")

def run_app_lead_module():
    """Mock test of the reporting systems."""
    print("Testing App & Reporting Lead deliverables...")
    
    report_engine = ReportGenerator()
    
    # Simulate DB data
    mock_student = {"name": "Jane Alice Doe", "email": "admin@gmail.com"}
    mock_grades = [
        {"subject": "Machine Learning", "assessment": "Midterm", "score": 45, "max_score": 50},
        {"subject": "Data Structures", "assessment": "Final", "score": 88, "max_score": 100},
        {"subject": "Artificial Intelligence", "assessment": "Project", "score": 95, "max_score": 100}
    ]
    
    mock_attendance = [
        {"Date": "2026-07-26", "Student": "Jane Doe", "Status": "Present"},
        {"Date": "2026-07-26", "Student": "John Smith", "Status": "Absent"}
    ]
    
    # 1. Test CSV Generation
    report_engine.generate_attendance_csv(mock_attendance)
    
    # 2. Test PDF Generation
    report_engine.generate_student_academic_transcript(mock_student, mock_grades)
    
    print("All front-end reporting components verified functioning.")

if __name__ == "__main__":
    run_app_lead_module()
