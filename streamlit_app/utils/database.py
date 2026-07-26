import os
import certifi
from pymongo import MongoClient

def get_db():
    uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017/")
    db_name = os.getenv("DATABASE_NAME", "facerecognition")
    if "mongodb+srv" in uri:
        client = MongoClient(uri, tlsCAFile=certifi.where())
    else:
        client = MongoClient(uri)
    return client[db_name]

def get_attendance_db():
    client = MongoClient(os.getenv("MONGODB_URI", "mongodb://localhost:27017/"))
    return client["facerecognition_db"]
