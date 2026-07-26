import bcrypt
from utils.database import get_db

def login_user(email, plain_password):
    db = get_db()
    
    # Try admin
    admin = db.auth_admins.find_one({"email": email})
    if admin:
        if bcrypt.checkpw(plain_password.encode('utf-8'), admin['password'].encode('utf-8')):
            return {"role": "admin", "name": admin['username'], "email": email}
            
    # Try teacher
    teacher = db.auth_teachers.find_one({"email": email})
    if teacher:
        if bcrypt.checkpw(plain_password.encode('utf-8'), teacher['password'].encode('utf-8')):
            if teacher.get('status') == 'inactive':
                return {"error": "Account deactivated."}
            return {"role": "teacher", "name": teacher['username'], "email": email}
            
    # Try student
    student = db.auth_users.find_one({"email": email})
    if student:
        if bcrypt.checkpw(plain_password.encode('utf-8'), student['password'].encode('utf-8')):
            if student.get('status') == 'inactive':
                return {"error": "Account deactivated."}
            return {"role": "student", "name": student['username'], "email": email}
            
    return {"error": "Invalid email or password"}

import time

def signup_user(email, password, username, user_type, extra_data=None):
    db = get_db()
    
    # Check if email exists in any collection
    for col in [db.auth_users, db.auth_teachers, db.auth_admins]:
        if col.find_one({"email": email}):
            return {"error": "Email already registered."}
            
    hashed_pw = bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt()).decode("utf-8")
    
    user_doc = {
        "username": username,
        "email": email,
        "password": hashed_pw,
        "status": "active",
        "created_at": time.time()
    }
    
    if user_type == "admin":
        if extra_data and extra_data.get("adminCode") != "123": # hardcoded for demo
            return {"error": "Invalid admin authorization code."}
        user_doc["role"] = "admin"
        db.auth_admins.insert_one(user_doc)
        
    elif user_type == "teacher":
        user_doc.update({
            "employeeId": extra_data.get("employeeId", ""),
            "department": extra_data.get("department", ""),
            "role": "teacher"
        })
        db.auth_teachers.insert_one(user_doc)
        
    elif user_type == "student":
        user_doc.update({
            "studentId": extra_data.get("studentId", ""),
            "role": "student"
        })
        db.auth_users.insert_one(user_doc)
        
    return {"success": f"{user_type.title()} account created! You can now log in."}
