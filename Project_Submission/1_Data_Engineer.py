# ==========================================
# ROLE 1: DATA ENGINEER
# ==========================================
# Responsibilities: 
# - Data extraction, transformation, and loading (ETL).
# - Managing database connections (MongoDB).
# - Formatting the raw student details and preparing collections.

import pandas as pd
from pymongo import MongoClient
import os
import json
from dotenv import load_dotenv

# Load environment variables
load_dotenv()

def get_database_connections():
    """Establish connection to MongoDB where all core app data lives."""
    MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    client = MongoClient(MONGO_URI)
    return client['facerecognition'], client['facerecognition_db']

def setup_collections(frontend_db, att_db):
    """Ensure required collections exist and have proper indexes."""
    for col in ['auth_users', 'auth_teachers', 'auth_admins', 'leave_requests', 'academic_grades']:
        if col not in frontend_db.list_collection_names():
            frontend_db.create_collection(col)
            print(f"Created collection: {col} in frontend db")
            
    for col in ['users', 'attendance_records']:
        if col not in att_db.list_collection_names():
            att_db.create_collection(col)
            print(f"Created collection: {col} in attendance db")
    # Create indexes for faster queries
    frontend_db.auth_users.create_index("email", unique=True)
    att_db.attendance_records.create_index("session_id")
    print("Database indexing completed.")

def load_student_data(csv_path="StudentDetails/studentdetails.csv"):
    """Load existing student records from CSV, clean, and prepare for DB."""
    try:
        df = pd.read_csv(csv_path)
        print("Raw Data Sample:\\n", df.head())
        
        # Data Cleaning: Handle NaN values and formatting
        df.fillna("Unknown", inplace=True)
        
        # Transform data to the schema expected by the application
        records = []
        for _, row in df.iterrows():
            records.append({
                "name": str(row.get("Name", "Unknown")).strip(),
                "email": str(row.get("Email", "Unknown")).strip(),
                "role": "student",
                "department": str(row.get("Department", "General")),
                "registered_on": pd.Timestamp.now()
            })
        return records
    except Exception as e:
        print(f"Error loading CSV data: {e}")
        return []

def run_etl_pipeline():
    """Main ETL workflow."""
    print("Starting Data Engineer Pipeline...")
    frontend_db, att_db = get_database_connections()
    setup_collections(frontend_db, att_db)
    
    student_records = load_student_data()
    import bcrypt
    if student_records:
        # Load data into MongoDB natively
        for record in student_records:
            if record['email'] != 'Unknown':
                # Generate a default password for them to login
                pw = bcrypt.hashpw("student123".encode('utf-8'), bcrypt.gensalt()).decode("utf-8")
                
                # Update Frontend DB (for login)
                user_doc = {
                    "username": record["name"],
                    "email": record["email"],
                    "password": pw,
                    "status": "active",
                    "role": "student"
                }
                frontend_db.auth_users.update_one(
                    {"email": record["email"]}, 
                    {"$set": user_doc}, 
                    upsert=True
                )
                
                # Also ensure they exist in attendance db
                att_db.users.update_one(
                    {"user_id": record["email"]},
                    {"$set": {"name": record["name"]}},
                    upsert=True
                )
        print(f"Successfully processed and loaded {len(student_records)} student records into Database.")
    else:
        print("No student data found to process.")

if __name__ == "__main__":
    run_etl_pipeline()
