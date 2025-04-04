import streamlit as st
import matplotlib.pyplot as plt
import pandas as pd
from db import (
    add_topic, get_today_revisions, get_revisions_by_date, get_all_topics,
    delete_topic, get_topics_by_category, mark_topic_completed, get_completed_topics_count,
    add_syllabus_topic, get_syllabus_topics, mark_syllabus_completed , delete_syllabus_topic
)

CATEGORY = ["DSA", "Python", "Web Dev", "Aptitude", "English", "SQL", "Django", "Flask" "Other"]


# ✅ Sample user credentials (Make sure this is properly defined)
SAMPLE_USER = {"username": "sachin_freedom", "password": "sachi108"}

st.set_page_config(page_title="Spaced Repetition", layout="wide")

# ✅ Initialize session state for authentication
if "authenticated" not in st.session_state:
    st.session_state.authenticated = False

# ✅ Logout Function
def logout():
    st.session_state.authenticated = False
    st.rerun()

# ✅ Login Page
if not st.session_state.authenticated:
    st.title("🔐 Login to Spaced Repetition App")

    with st.form("login_form"):
        username = st.text_input("👤 Username:")
        password = st.text_input("🔑 Password:", type="password")
        submit = st.form_submit_button("Login")

    if submit:
        # ✅ Using .get() to prevent KeyError
        if username == SAMPLE_USER.get("username") and password == SAMPLE_USER.get("password"):
            st.session_state.authenticated = True
            st.success("✅ Login successful! Redirecting...")
            st.rerun()
        else:
            st.error("❌ Invalid username or password!")

    st.stop()  # Stop execution if user is not authenticated

# ✅ Sidebar Navigation (After Login)
st.sidebar.title("🔗 Navigation")
menu = st.sidebar.radio("", [
    "➕ Add Topic", "📅 Today's Revisions", "📆 Calendar", "📂 All Topics", "📊 Analytics", "📖 Syllabus Tracker"
])

# ✅ 1️⃣ Add Logout Button in Sidebar
if st.sidebar.button("🚪 Logout"):
    logout()

# ✅ 1️⃣ Add Topic Section
if menu == "➕ Add Topic":
    st.header("📝 Add a New Topic for Spaced Repetition")

    topic = st.text_input("Enter Topic Name:")
    category = st.selectbox("Select Category", CATEGORY)

    if st.button("➕ Add Topic"):
        if topic and category:
            dates = add_topic(topic, category)
            st.success(f"✅ Topic '{topic}' added under '{category}' category!")
        else:
            st.warning("⚠ Please enter a topic and select a category!")

# ✅ 2️⃣ Today's Revisions Section
elif menu == "📅 Today's Revisions":
    st.header("📅 Topics for Today's Revision")
    revisions = get_today_revisions()

    if revisions:
        for rev in revisions:
            st.write(f"🔹 **{rev.get('topic', 'Unknown')}**")
    else:
        st.info("✅ No topics to revise today!")

# ✅ 3️⃣ Calendar-Based Revisions Section
elif menu == "📆 Calendar":
    st.header("📆 Revision Calendar")

    selected_date = st.date_input("📌 Select a Date:")
    if selected_date:
        revisions = get_revisions_by_date(selected_date)
        if revisions:
            st.write("### 📋 Topics for Revision:")
            for rev in revisions:
                st.write(f"🔹 **{rev.get('topic', 'Unknown')}**")
        else:
            st.info("📭 No topics scheduled for this date.")

# ✅ 4️⃣ View & Manage All Topics
elif menu == "📂 All Topics":
    st.header("📂 All Added Topics")

    selected_category = st.selectbox("📌 Filter by Category", ["All"] + CATEGORY)
    topics = get_topics_by_category(selected_category) if selected_category != "All" else get_all_topics()

    if topics:
        topics_to_delete = []
        for topic in topics:
            col1, col2, col3 = st.columns([4, 1, 1])
            topic_name = topic.get("topic", "Unknown")
            category = topic.get("category", "Uncategorized")
            revision_dates = topic.get("revision_dates", [])
            topic_id = str(topic.get("_id", ""))

            col1.write(
                f"🔹 **{topic_name}** | 📆 Revision Dates: {', '.join(revision_dates) if revision_dates else 'None'} | 📂 Category: **{category}**"
            )

            if topic_id and col2.button("✅ Complete", key=f"complete_{topic_id}"):
                mark_topic_completed(topic_id)
                st.rerun()

            if topic_id and col3.button("❌ Delete", key=f"delete_{topic_id}"):
                topics_to_delete.append(topic_id)

        if topics_to_delete:
            for topic_id in topics_to_delete:
                delete_topic(topic_id)
            st.rerun()
    else:
        st.info("🚀 No topics added yet!")


elif menu == "📊 Analytics":
    st.header("📊 Learning Progress Analytics")

    # ✅ Get topics from DB (ensure "completed" field is included in get_all_topics())
    all_topics = get_all_topics()

    # ✅ Fetch categories dynamically from DB
    categories = list(set(topic['category'] for topic in all_topics))
    selected_category = st.selectbox("📌 Filter by Category", ["All"] + categories)

    # ✅ Filter topics by selected category
    filtered_topics = (
        all_topics if selected_category == "All"
        else [topic for topic in all_topics if topic['category'] == selected_category]
    )

    # ✅ Compute metrics based on filtered topics
    total_filtered = len(filtered_topics)
    completed_filtered = sum(1 for topic in filtered_topics if topic.get('completed', False))
    pending_filtered = total_filtered - completed_filtered

    st.metric("📚 Total Topics", total_filtered)
    st.metric("✅ Completed Topics", completed_filtered)
    st.metric("⏳ Pending Topics", pending_filtered)

    # ✅ Show Progress Bar based on filtered metrics
    if total_filtered > 0:
        progress = completed_filtered / float(total_filtered)
        st.progress(progress)
    else:
        st.info("📭 No topics available for this category.")


    # ---------------------------------------------
    # 📖 Syllabus Completion Analytics (Already Working)
    # ---------------------------------------------
    st.subheader("📖 Syllabus Completion Overview")

    all_syllabus_topics = get_syllabus_topics()
    syllabus_categories = list(set(topic.get('category', 'Uncategorized') for topic in all_syllabus_topics))

    selected_syllabus_category = st.selectbox("📌 Filter Syllabus by Category", ["All"] + syllabus_categories)

    if selected_syllabus_category == "All":
        filtered_syllabus = all_syllabus_topics
    else:
        filtered_syllabus = [topic for topic in all_syllabus_topics if topic.get('category') == selected_syllabus_category]

    total_syllabus = len(filtered_syllabus)
    completed_syllabus = sum(1 for topic in filtered_syllabus if topic.get("completed", False))
    pending_syllabus = total_syllabus - completed_syllabus

    st.metric("📚 Total Syllabus Topics", total_syllabus)
    st.metric("✅ Completed Syllabus Topics", completed_syllabus)
    st.metric("⏳ Pending Syllabus Topics", pending_syllabus)

    if total_syllabus > 0:
        fig_syllabus, ax_syllabus = plt.subplots(figsize=(4, 4))  # Smaller size
        ax_syllabus.pie(
            [completed_syllabus, pending_syllabus],
            labels=["Completed", "Pending"],
            autopct='%1.1f%%',
            colors=['#4CAF50', '#F44336']
        )
        ax_syllabus.set_title(f"Syllabus Completion: {selected_syllabus_category}")
        st.pyplot(fig_syllabus)
    else:
        st.info("📭 No syllabus topics available.")




# ✅ 3️⃣ Syllabus Tracker with Adding Option
elif menu == "📖 Syllabus Tracker":
    st.header("📖 Manage Your Syllabus")

    # 🎯 Add New Syllabus Topic
    syllabus_topic = st.text_input("Enter Syllabus Topic:")
    syllabus_category = st.selectbox("Select Category", CATEGORY)

    if st.button("➕ Add Syllabus Topic"):
        if syllabus_topic and syllabus_category:
            add_syllabus_topic(syllabus_topic, syllabus_category)
            st.success(f"✅ Syllabus topic '{syllabus_topic}' added under '{syllabus_category}'!")
            st.rerun()
        else:
            st.warning("⚠ Please enter a topic and select a category!")

    # 📌 Display Syllabus Topics
    selected_category = st.selectbox("📌 Filter Syllabus by Category", ["All"] + CATEGORY)
    syllabus_topics = get_syllabus_topics(selected_category) if selected_category != "All" else get_syllabus_topics()

    if syllabus_topics:
        topics_to_delete = []
        for topic in syllabus_topics:
            col1, col2, col3 = st.columns([4, 1, 1])  # Adjust column layout
            topic_name = topic.get("topic", "Unknown")
            topic_id = str(topic.get("_id", ""))

            col1.write(f"🔹 **{topic_name}**")

            if topic_id and col2.button("✅ Mark as Completed", key=f"syllabus_{topic_id}"):
                mark_syllabus_completed(topic_id)
                st.rerun()

            if topic_id and col3.button("❌ Delete", key=f"delete_syllabus_{topic_id}"):
                topics_to_delete.append(topic_id)

        # Delete topics outside loop to avoid button conflicts
        if topics_to_delete:
            for topic_id in topics_to_delete:
                delete_syllabus_topic(topic_id)
            st.rerun()
    else:
        st.info("📭 No syllabus topics found.")









