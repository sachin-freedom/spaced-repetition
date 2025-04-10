from pymongo import MongoClient
from datetime import datetime, timedelta
from bson import ObjectId
from dotenv import load_dotenv
import os
import streamlit as st

# Load .env file
load_dotenv()

# Get MongoDB URI from environment variable
# MONGO_URI = os.getenv("MONGO_URI")
MONGO_URI = st.secrets["MONGO_URI"]

# MongoDB Connection
client = MongoClient(MONGO_URI)
db = client.get_database()  # Automatically picks the correct DB from the URI
topics_collection = db["topics"]



syllabus_collection = db["syllabus"]  # Add this line

def get_next_available_date(category, proposed_date):
    """Finds the next available date where the category is not already scheduled for revision."""
    while topics_collection.find_one(
            {"category": category, "revision_dates": {"$in": [proposed_date.strftime("%Y-%m-%d")]}}):
        proposed_date += timedelta(days=1)  # Shift to the next available day
    return proposed_date


def generate_revision_dates(start_date, category):
    intervals = [1, 3, 10, 16, 25]
    revision_dates = []

    for interval in intervals:
        # Interval is always calculated from the original start_date
        proposed_date = start_date + timedelta(days=interval)
        final_date = get_next_available_date(category, proposed_date)

        # Make sure this final_date is not already used in previous revision dates (in this session)
        while final_date.strftime("%Y-%m-%d") in revision_dates:
            final_date += timedelta(days=1)
            final_date = get_next_available_date(category, final_date)

        revision_dates.append(final_date.strftime("%Y-%m-%d"))

    return revision_dates

def add_topic(topic, category="Uncategorized"):
    today = datetime.today()
    revision_dates = generate_revision_dates(today, category)

    # Now that we know the category, adjust revision dates properly
    revision_dates = [get_next_available_date(category, datetime.strptime(date, "%Y-%m-%d")).strftime("%Y-%m-%d") for
                      date in revision_dates]

    topic_data = {
        "topic": topic,
        "category": category,  # ✅ Ensuring category is always added
        "added_date": today.strftime("%Y-%m-%d"),
        "revision_dates": revision_dates,
        "status": "pending"
    }
    topics_collection.insert_one(topic_data)
    return revision_dates

def get_topics_by_category(category):
    """Fetch topics based on selected category."""
    if category == "All":
        return list(topics_collection.find({}, {"_id": 0, "topic": 1, "category": 1}))
    return list(topics_collection.find({"category": category}, {"_id": 0, "topic": 1, "category": 1, "revision_dates": 1}))

def get_today_revisions():
    """Fetch topics scheduled for revision today."""
    today = datetime.today().strftime("%Y-%m-%d")
    return list(topics_collection.find({"revision_dates": {"$in": [today]}}, {"_id": 0, "topic": 1}))

def get_revisions_by_date(date):
    """Fetch topics scheduled for revision on a given date."""
    formatted_date = date.strftime("%Y-%m-%d")
    return list(topics_collection.find({"revision_dates": {"$in": [formatted_date]}}, {"_id": 0, "topic": 1}))

def get_all_topics():
    """Fetch all added topics, including categories."""
    return list(topics_collection.find({}, {"_id": 1, "topic": 1, "revision_dates": 1, "category": 1, "completed": 1}))


def delete_topic(topic_id):
    """Delete a topic by its ID, handling string and ObjectId cases."""
    if isinstance(topic_id, str):
        topic_id = ObjectId(topic_id)  # Convert only if it's a string
    topics_collection.delete_one({"_id": topic_id})
    return "Topic deleted successfully!"

def mark_topic_completed(topic_id):
    """Marks a topic as completed in the database"""
    if isinstance(topic_id, str):
        topic_id = ObjectId(topic_id)  # Convert string ID to ObjectId
    topics_collection.update_one({"_id": topic_id}, {"$set": {"completed": True}})


def get_completed_topics_count():
    """Returns the count of completed topics"""
    return topics_collection.count_documents({"completed": True})


def add_syllabus_topic(topic, category):
    """Adds a syllabus topic to the database"""
    syllabus_collection.insert_one({"topic": topic, "category": category, "completed": False})


def get_syllabus_topics(category=None):
    """Fetches syllabus topics, optionally filtered by category"""
    if category:
        return list(syllabus_collection.find({"category": category}))
    return list(syllabus_collection.find())


def mark_syllabus_completed(topic_id):
    """Marks a syllabus topic as completed in the database"""
    if isinstance(topic_id, str):
        topic_id = ObjectId(topic_id)  # Convert string ID to ObjectId

    syllabus_collection.update_one({"_id": topic_id}, {"$set": {"completed": True}})



def delete_syllabus_topic(topic_id):
    """Deletes a syllabus topic by its ID from the database."""
    syllabus_collection.delete_one({"_id": ObjectId(topic_id)})











