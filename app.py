import streamlit as st
import sqlite3
import bcrypt

# Initialize database connection
def create_connection(db_file):
    conn = None
    try:
        conn = sqlite3.connect(db_file)
    except sqlite3.Error as e:
        st.error(f"Error connecting to database: {e}")
    return conn

def create_tables(conn):
    with conn:
        conn.execute('''CREATE TABLE IF NOT EXISTS users (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            username TEXT NOT NULL,
                            email TEXT NOT NULL,
                            password TEXT NOT NULL);''')
        conn.execute('''CREATE TABLE IF NOT EXISTS diagnoses (
                            id INTEGER PRIMARY KEY AUTOINCREMENT,
                            user_id INTEGER,
                            symptom_ids TEXT,
                            result TEXT,
                            created_at TIMESTAMP DEFAULT CURRENT_TIMESTAMP,
                            FOREIGN KEY (user_id) REFERENCES users (id));''')

conn = create_connection("webuas.db")
create_tables(conn)

def hash_password(password):
    return bcrypt.hashpw(password.encode('utf-8'), bcrypt.gensalt())

def check_password(hashed_password, user_password):
    return bcrypt.checkpw(user_password.encode('utf-8'), hashed_password)

# Registration function
def register_user(username, email, password):
    hashed_password = hash_password(password)
    with conn:
        conn.execute("INSERT INTO users (username, email, password) VALUES (?, ?, ?)", (username, email, hashed_password))
    st.success("Registration successful. Please log in.")
    st.session_state.page = "login"

# Login function
def login_user(username, password):
    cur = conn.cursor()
    cur.execute("SELECT id, password FROM users WHERE username = ?", (username,))
    user = cur.fetchone()
    if user and check_password(user[1], password):
        return user[0]
    return None

# Diagnosis function
def save_diagnosis(user_id, symptoms, result):
    with conn:
        conn.execute("INSERT INTO diagnoses (user_id, symptom_ids, result) VALUES (?, ?, ?)", (user_id, symptoms, result))

# Main application
def main():
    st.title("Mental Health Diagnosis")

    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "page" not in st.session_state:
        st.session_state.page = "home"

    if st.session_state.user_id:
        st.session_state.page = "diagnose"

    if st.session_state.page == "home":
        st.subheader("Welcome to the Mental Health Diagnosis App ByUmbusurya")
        if st.button("Login"):
            st.session_state.page = "login"
        if st.button("Sign Up"):
            st.session_state.page = "signup"

    elif st.session_state.page == "signup":
        st.subheader("Create a New Account")
        username = st.text_input("Username")
        email = st.text_input("Email")
        password = st.text_input("Password", type="password")
        confirm_password = st.text_input("Confirm Password", type="password")

        if st.button("Register"):
            if password == confirm_password:
                register_user(username, email, password)
            else:
                st.error("Passwords do not match.")
    
    elif st.session_state.page == "login":
        st.subheader("Login to Your Account")
        username = st.text_input("Username")
        password = st.text_input("Password", type="password")

        if st.button("Login"):
            user_id = login_user(username, password)
            if user_id:
                st.session_state.user_id = user_id
                st.success("Logged in successfully")
                st.session_state.page = "diagnose"
            else:
                st.error("Invalid username or password")

    elif st.session_state.page == "diagnose":
        st.subheader("Diagnosis Form")
        questions = [
            "Apakah Anda sering merasa sedih?",
            "Apakah Anda sering merasa lelah tanpa alasan?",
            "Apakah Anda kesulitan tidur atau tidur terlalu banyak?",
            "Apakah Anda kehilangan minat pada kegiatan yang biasanya Anda nikmati?",
            "Apakah Anda sering merasa gelisah atau cemas?",
            "Apakah Anda mengalami perubahan berat badan secara signifikan?",
            "Apakah Anda merasa tidak berharga atau bersalah tanpa alasan yang jelas?",
            "Apakah Anda kesulitan berkonsentrasi atau membuat keputusan?"
        ]
        answers = []
        for i, q in enumerate(questions):
            answer = st.radio(q, ("Ya", "Tidak"), key=i)
            answers.append('a' if answer == "Ya" else 'b')

        if st.button("Diagnose"):
            score = answers.count('a')
            if score >= 6:
                result = "Depresi berat"
            elif score >= 4:
                result = "Depresi sedang"
            elif score >= 2:
                result = "Depresi ringan"
            else:
                result = "Tidak ada depresi"

            symptoms = ", ".join([f"{i+1}: {a}" for i, a in enumerate(answers)])
            save_diagnosis(st.session_state.user_id, symptoms, result)
            st.success(f"Diagnosis Result: {result}")

if __name__ == '__main__':
    main()
