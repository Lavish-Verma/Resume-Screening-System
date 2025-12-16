from pymongo import MongoClient

client = MongoClient("mongodb://localhost:27017/")

# Database
db = client["user_database"]

# Collections
users_collection = db.get_collection("users")
reports_collection = db.get_collection("resume_reports")

