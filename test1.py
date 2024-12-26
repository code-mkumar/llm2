import streamlit as st
import sqlite3
import pyotp
import qrcode
from io import BytesIO
import json
import google.generativeai as genai
import os
from sklearn.feature_extraction.text import TfidfVectorizer
from sklearn.metrics.pairwise import cosine_similarity
# Configure Google Gemini API key
genai.configure(api_key='AIzaSyD3WqHberJDYyzXkmY1zKaoqd5uCJZDetI')
model = genai.GenerativeModel('gemini-pro')




# SQLite connection
def create_connection():
    return sqlite3.connect("university.db")

# Generate a new TOTP secret for a user
def generate_secret_code(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    secret = pyotp.random_base32()  # Generate a TOTP secret
    
    # st.write(g)
    conn.commit()
    conn.close()
    return secret

# Retrieve the secret code and role for a user
def get_user_details(user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("SELECT secret_code, role, name FROM user_detail WHERE id = ?", (user_id,))
    result = cursor.fetchone()
    conn.close()
    return result if result else (None, None, None)

# Generate a QR code for the TOTP secret
def generate_qr_code(user_id, secret):
    totp = pyotp.TOTP(secret)
    uri = totp.provisioning_uri(name=user_id, issuer_name="University Authenticator")
    qr = qrcode.QRCode()
    qr.add_data(uri)
    qr.make(fit=True)
    img = qr.make_image(fill="black", back_color="white")
    buf = BytesIO()
    img.save(buf, format="PNG")
    buf.seek(0)
    return buf

# Verify the OTP against the secret
def verify_otp(secret, otp):
    totp = pyotp.TOTP(secret)
    return totp.verify(otp)

# Update the multifactor status in the database
def update_multifactor_status(user_id, status, secret):
    conn = create_connection()
    cursor = conn.cursor()

    # Update the multifactor status
    cursor.execute("UPDATE user_detail SET multifactor = ? WHERE id = ?", (status, user_id))
    multifactor_updated = cursor.rowcount  # Rows affected by the first query

    # Update the secret code
    cursor.execute("UPDATE user_detail SET secret_code = ? WHERE id = ?", (secret, user_id))
    secret_updated = cursor.rowcount  # Rows affected by the second query

    # Commit the changes
    conn.commit()
    conn.close()

    # Verify updates
    if multifactor_updated > 0 and secret_updated > 0:
        return 1
    elif multifactor_updated > 0:
        return 0
    elif secret_updated > 0:
        return 0
    else:
        return -1


# Read file content and save to session
def read_student_files():
    with open("student_role.txt", "r") as role_file:
        role_content = role_file.read()
    with open("student_sql.txt", "r") as sql_file:
        sql_content = sql_file.read()
    return role_content, sql_content

def read_default_files():
    with open("default.txt", "r") as role_file:
        role_content = role_file.read()
    with open("default_sql.txt", "r") as sql_file:
        sql_content = sql_file.read()
    return role_content, sql_content

def read_staff_files():
    with open("staff_role.txt", "r") as role_file:
        role_content = role_file.read()
    with open("staff_sql.txt", "r") as sql_file:
        sql_content = sql_file.read()
    return role_content, sql_content

def read_admin_files():
    with open("admin_role.txt", "r") as role_file:
        role_content = role_file.read()
    with open("admin_sql.txt", "r") as sql_file:
        sql_content = sql_file.read()
    return role_content, sql_content
# # Function to chunk text
# def chunk_text(text, chunk_size=500, overlap=100):
#     words = text.split()
#     chunks = []
#     for i in range(0, len(words), chunk_size - overlap):
#         chunks.append(" ".join(words[i:i + chunk_size]))
#     return chunks

# # Function to get relevant chunks using TF-IDF and cosine similarity
# def get_relevant_chunks(query, chunks, top_n=3):
#     vectorizer = TfidfVectorizer()
#     vectors = vectorizer.fit_transform(chunks + [query])
#     cosine_sim = cosine_similarity(vectors[-1:], vectors[:-1])
#     relevant_indices = cosine_sim[0].argsort()[-top_n:][::-1]
#     return [chunks[i] for i in relevant_indices]
# # Pages
# def guest_page():
#     # Initialize session state
#     if 'qa_list' not in st.session_state:
#         st.session_state.qa_list = []
#     # st.write("helo")
#     with st.sidebar:
#         if st.button("Go to Login"):
#             st.session_state.page = "login"
#             st.rerun()
#         for qa in reversed(st.session_state.qa_list):
#                 st.write(f"**Question:** {qa['question']}")
#                 st.write(f"**Answer:** {qa['answer']}")
#                 st.write("---")
#     # st.subheader("Manage Existing Files")
#     #     existing_file = st.selectbox(
#     #     "Select a file to view or edit:",
#     #     ["collegehistory.txt", "departmenthistory.txt"]
#     # )

#     collegehistory=""    
#     with open("collegehistory.txt", "r") as f:
#         collegehistory = f.read()
#     # edited_existing_content = st.text_area("Edit Existing File Content", value=existing_content, height=300)
#     departmenthistory=""    
#     with open("departmenthistory.txt", "r") as f:
#         departmenthistory = f.read()
           
#     default,default_sql=read_default_files()
#     st.title("Welcome, Guest!")
#     st.write("You can explore the site as a guest, but you'll need to log in for full role-based access.")
    
#     # Initialize the name input
#     if 'username' not in st.session_state:
#         st.session_state.username = ''
#     name=''
    
#     if not st.session_state.username:
#         # Ask for the user's name
#         name = st.text_input('Enter your name:', placeholder='John', key='name')
#         if name:
#             st.session_state.username = name
#             st.write(model.generate_content(f"Introduce yourself: {default}").text)
#     if  st.session_state.username:
#         # Display a welcome message once the name is entered
#         st.write(f"Hello, {st.session_state.username}!")
#         if "input" not in st.session_state:
#             st.session_state.input = ""
#         if "stored_value" not in st.session_state:
#             st.session_state.stored_value = ""
#         chunks = chunk_text(f"{collegehistory}\n{departmenthistory}")
#         def process_and_clear():
#             st.session_state.stored_value = st.session_state.input
#             st.session_state.input = ""
#         # Allow the user to ask a question
#         question1 = st.text_area('Input your question:', key='input',on_change=process_and_clear)
#         # submit = st.button('Ask the question')
#         question=st.session_state.stored_value
#         if question:
            
#             # all_chunks.extend(chunks)
#             relevant_chunks = get_relevant_chunks(question,chunks)
#             context = "\n\n".join(relevant_chunks)
            
#             # Display relevant chunks
#             st.write("Relevant context:")
#             st.write(context)
            
#             # Query LM Studio
#             with st.spinner("Generating answer..."):
                

#                 txt = model.generate_content(f"{question} give 1 if the question needs an SQL query or 0")
#                 data = ''
#                 if txt.text.strip() != '0':
#                     response = model.generate_content(f"{default_sql}\n\n{question}")
#                     raw_query = response.text
#                     formatted_query = raw_query.replace("sql", "").strip("'''").strip()
#                     single_line_query = " ".join(formatted_query.split()).replace("```", "")
#                     data = read_sql_query(single_line_query)
#                     # st.write(data)
    
#                 if st.session_state.qa_list:
#                     last_entry = st.session_state.qa_list[-1]
#                     last_question = last_entry['question']
#                     last_answer = last_entry['answer']
#                     # st.write(last_answer,last_question)
#                 else:
#                     last_question = "No previous question available."
#                     last_answer = "No previous answer available."
    
#                 # Format data for readability
#                 formatted_data = json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)
#                 # st.warning(formatted_data)
    
#                 # Generate content using the model
#                 answer = model.generate_content(
#                     # f"{name} this is the user name interact with this name"
#                     # f"{default} Answer this question: {question} with results {formatted_data} make sure on the data. "
#                     f"use the data {context} and frame the answer for this question {question}"
#                     # f"Refer to the previous question and answer if needed only: {last_question} {last_answer}"
#                 )
#                 result_text = answer.candidates[0].content.parts[0].text
    
#                 # Store the question and answer in session state
#                 st.session_state.qa_list.append({'question': question, 'answer': result_text})
    
#                 # Display  questions and answers
#                 st.markdown(question)
#                 st.markdown(result_text)
            
def chunk_text(text, chunk_size=500, overlap=100):
    words = text.split()
    chunks = []
    for i in range(0, len(words), chunk_size - overlap):
        chunks.append(" ".join(words[i:i + chunk_size]))
    return chunks

# Function to get relevant chunks using TF-IDF and cosine similarity
def get_relevant_chunks(query, chunks, top_n=3):
    vectorizer = TfidfVectorizer()
    vectors = vectorizer.fit_transform(chunks + [query])
    cosine_sim = cosine_similarity(vectors[-1:], vectors[:-1])
    relevant_indices = cosine_sim[0].argsort()[-top_n:][::-1]
    return [chunks[i] for i in relevant_indices]

# Guest Page Functionality
def guest_page():
    # Initialize session state variables
    if 'qa_list' not in st.session_state:
        st.session_state.qa_list = []
    if 'username' not in st.session_state:
        st.session_state.username = ''
    if 'input' not in st.session_state:
        st.session_state.input = ""
    if 'stored_value' not in st.session_state:
        st.session_state.stored_value = ""

    # Sidebar for navigation and displaying past Q&A
    with st.sidebar:
        if st.button("Go to Login"):
            st.session_state.page = "login"
            st.rerun()

        for qa in reversed(st.session_state.qa_list):
            st.write(f"**Question:** {qa['question']}")
            st.write(f"**Answer:** {qa['answer']}")
            st.write("---")

    # Load text files for college and department history
    with open("collegehistory.txt", "r") as f:
        collegehistory = f.read()
    with open("departmenthistory.txt", "r") as f:
        departmenthistory = f.read()

    # Display guest welcome message
    st.title("Welcome, Guest!")
    st.write("You can explore the site as a guest, but you'll need to log in for full role-based access.")

    # Ask for the user's name
    name = st.text_input('Enter your name:', placeholder='John', key='name')
    if name and not st.session_state.username:
        st.session_state.username = name
        st.write(f"Hello, {name}!")

    # Process questions if the username is set
    if st.session_state.username:
        chunks = chunk_text(f"{collegehistory}\n{departmenthistory}")

        def process_and_clear():
            st.session_state.stored_value = st.session_state.input
            st.session_state.input = ""

        # Input field for the user's question
        st.text_area('Input your question:', key='input', on_change=process_and_clear)
        question = st.session_state.stored_value

        if question:
            # Retrieve relevant chunks
            relevant_chunks = get_relevant_chunks(question, chunks)
            context = "\n\n".join(relevant_chunks)

            # Display relevant context
            st.write("Relevant context:")
            st.write(context)

            # Query LM Studio for the answer
            with st.spinner("Generating answer..."):
                txt = model.generate_content(f"{question} give 1 if the question needs an SQL query or 0")
                data = ''
                if txt.text.strip() != '0':
                    response = model.generate_content(f"{default_sql}\n\n{question}")
                    raw_query = response.text
                    formatted_query = raw_query.replace("sql", "").strip("'''").strip()
                    single_line_query = " ".join(formatted_query.split()).replace("```", "")
                    data = read_sql_query(single_line_query)

                # Format data for readability
                formatted_data = json.dumps(data, indent=2) if isinstance(data, (dict, list)) else str(data)

                # Generate answer using the context and formatted data
                answer = model.generate_content(
                    f"use the data {context} and frame the answer for this question {question} use this template {default}"
                )
                result_text = answer.candidates[0].content.parts[0].text

                # Store the question and answer in session state
                st.session_state.qa_list.append({'question': question, 'answer': result_text})

                # Display the current question and answer
                st.markdown(f"**Question:** {question}")
                st.markdown(f"**Answer:** {result_text}")
#login page
def login_page():
    st.set_page_config(page_title="Login")
    st.title("Login")
    user_id = st.text_input("User ID")
    password = st.text_input("Password", type="password")

    if st.button("Login"):
        conn = create_connection()
        cursor = conn.cursor()
        cursor.execute("SELECT * FROM user_detail WHERE id = ? AND password = ?", (user_id, password))
        user = cursor.fetchone()
        conn.close()

        if user:
            st.session_state.authenticated = True
            st.session_state.user_id = user_id
            st.session_state.multifactor = user[8]  # Multifactor column
            st.session_state.secret = user[9]  # Secret code column
            st.success("Login successful!")
            if st.session_state.multifactor == 1:
                st.session_state.page = "otp_verification"  # Direct to OTP verification if MFA is enabled
                st.rerun()
            else:
                if st.session_state.secret == "None":
                    st.session_state.page = "qr_setup"  # If MFA is not enabled, show QR setup
                    st.rerun()
                else:
                    st.session_state.page = "otp_verification"  # Otherwise show OTP verification
                    st.rerun()
        else:
            st.error("Invalid credentials.")
    if st.button("Visit as Guest"):
        st.session_state.page = "guest"

#qr scanning page
def qr_setup_page():
    st.set_page_config(page_title="QRcode")
    st.title("Setup Multifactor Authentication")
    user_id = st.session_state.user_id
    
    if st.session_state.secret == "None":
        # Generate a new secret
        secret = generate_secret_code(user_id)
        st.session_state.secret = secret
    else:
        secret = st.session_state.secret

    # Display QR Code
    qr_code_stream = generate_qr_code(user_id, secret)
    st.image(qr_code_stream, caption="Scan this QR code with your authenticator app.", use_container_width=False)
    st.write(f"Secret Code: `{secret}` (store this securely!)")

    # Immediate OTP verification
    otp = st.text_input("Enter OTP from Authenticator App", type="password")
    if st.button("Verify OTP"):
        # secret, role, name = get_user_details(st.session_state.user_id)
        if not verify_otp(secret, otp):
            verify = update_multifactor_status(user_id, 1,secret)  # Update MFA status in the database
            if not verify==1:
                st.markdown("""
        <script>
            alert("This is not done correctly!...");
        </script>
    """, unsafe_allow_html=True)
                return
            st.session_state.multifactor = 1
            _, role, name = get_user_details(user_id)
            st.session_state.id=user_id
            st.session_state.role = role
            st.session_state.name = name
            if role == "student":
                role_content, sql_content = read_student_files()
                st.session_state.role_content = role_content
                st.session_state.sql_content = sql_content
            if role == "staff":
                role_content,sql_content = read_staff_files()
                st.session_state.role_content = role_content
                st.session_state.sql_content = sql_content
            if role == "admin":
                role_content,sql_content = read_admin_files()
                st.session_state.role_content = role_content
                st.session_state.sql_content = sql_content
                st.session_state.page = "admin"
                st.rerun()
            st.success("Multifactor authentication is now enabled.")
            st.session_state.page = "welcome"
            st.rerun()
        else:
            st.error("Invalid OTP. Try again.")

#otp verification page
def otp_verification_page():
    st.set_page_config(page_title="verify")
    st.title("Verify OTP")
    user_id = st.session_state.user_id
    secret, role, name = get_user_details(user_id)
    st.session_state.id=user_id
    st.session_state.role = role
    st.session_state.name = name
    

    otp = st.text_input("Enter OTP", type="password")
    if st.button("Verify"):
        if not  verify_otp(secret, otp):
            st.success("OTP Verified! Welcome.")
            
            if role == "student":
                role_content, sql_content = read_student_files()
                st.session_state.role_content = role_content
                st.session_state.sql_content = sql_content
            if role == "staff":
                role_content,sql_content = read_staff_files()
                st.session_state.role_content = role_content
                st.session_state.sql_content = sql_content
            if role == "admin":
                role_content,sql_content = read_admin_files()
                st.session_state.role_content = role_content
                st.session_state.sql_content = sql_content
                st.session_state.page = "admin"
                st.rerun()
            st.session_state.page = "welcome"
            st.rerun()
        else:
            st.error("Invalid OTP. Try again.")

#just for combining
def create_combined_prompt(question, sql_prompt):
    # Define keywords for user-specific queries
    user_specific_keywords = ["my department", "my course", "my details", "give me"]

    # Define keywords for non-user-specific queries
    general_keywords = [
        "department names", "course names", "college history", 
        "programmes of study", "infrastructure", "placement", "facilities"
    ]

    # Check if the question matches user-specific keywords
    if any(keyword in question.lower() for keyword in user_specific_keywords):
        return f"{sql_prompt}\n\nWrite a query to fetch the relevant information using user_id='{st.session_state.id}'.\n\nQuestion: {question}\n\n"

    # Check if the question matches general keywords
    elif any(keyword in question.lower() for keyword in general_keywords):
        return f"{sql_prompt}\n\nWrite a query to fetch the relevant information without using user_id or any specific filters.\n\nQuestion: {question}\n\n"

    # Default behavior
    return f"{sql_prompt}\n\n{question}\n\n"


# Function to interact with the Google Gemini model
def get_gemini_response(combined_prompt):
    response = model.generate_content(combined_prompt)
    # print(response)
    query=response.text
    # Add user_id for personal queries if not already included
    if "my" in combined_prompt.lower() and "user_id" not in query.lower():
        query = query.strip(";") + f" WHERE user_id='{st.session_state.id}';"

    # Remove unnecessary user_id filters for general queries
    general_contexts = ["department names", "course names", "college history", "programmes of study"]
    if any(context in combined_prompt.lower() for context in general_contexts):
        query = re.sub(r"WHERE\s+user_id\s*=\s*['\"]\w+['\"]", "", query, flags=re.IGNORECASE)

    return query
    id = st.session_state.id
    try:
        final = model.generate_content(f"{response.text} if any user_id word found in this statement replace with {id}")
        #final=model.generate_content(response.text)
    except:
        return "please contact to the staff or admin"
    return final.text
    # if not response or 'candidates' not in response:
    #     return "The model could not generate a valid response. Please try again."

    # candidate_content = response.candidates[0].content.parts[0].text
    # return candidate_content if candidate_content else "No valid content returned from the candidate."

# Function to query the SQL database
def read_sql_query(sql):
    try:
        st.write(sql)
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        # st.write(rows)
        return rows
    except Exception as e:
        #print(sql)
        print(e)
        return f"SQLite error: {e}"

#change pass
def change_pass(password,user_id):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_detail SET password = ? WHERE id = ?", (password, user_id))
    conn.commit()
    conn.close()

def welcome_page():
    st.set_page_config(page_title="Anjac_AI", layout="wide")
    secret, role, name = get_user_details(st.session_state.user_id)

    # Sidebar content
    with st.sidebar:
        st.header("Chat History")
        # if st.button("Logout"):
        #     st.session_state.authenticated = False
        #     st.session_state.page = "login"

        # Display questions and answers in reverse order
        for qa in reversed(st.session_state.qa_list):
            st.write(f"**Question:** {qa['question']}")
            st.write(f"**Answer:** {qa['answer']}")
            st.write("---")

    # Inject custom CSS for the expander
    st.markdown("""
    <style>
    .stExpander {
        position: fixed; /* Keep the expander fixed */
        top: 70px; /* Distance from the top */
        right: 10px; /* Distance from the right */
        width: 200px !important; /* Shrink the width */
        z-index: 9999; /* Bring it to the front */
    }
    .stExpander > div > div {
        background-color: #f5f5f5; /* Light grey background */
        border: 1px solid #ccc; /* Border styling */
        border-radius: 10px; /* Rounded corners */
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow */
    }
    .stButton button {
        width: 90%; /* Make buttons fit nicely */
        margin: 5px auto; /* Center-align buttons */
        display: block;
        background-color: #007bff; /* Blue button */
        color: white;
        border-radius: 5px;
        border: none;
        font-size: 14px;
        cursor: pointer;
    }
    .stpopover button {
        width: 90%; /* Make buttons fit nicely */
        margin: 5px auto; /* Center-align buttons */
        display: block;
        background-color: #007bff; /* Blue button */
        color: white;
        border-radius: 5px;
        border: none;
        font-size: 14px;
        cursor: pointer;
    }
    .stButton button:hover {
        background-color: #0056b3; /* Darker blue on hover */
    }
    </style>
""", unsafe_allow_html=True)

# Main page user menu using expander
    with st.expander(f"Welcome, {name}! 🧑‍💻"):
        st.write("Choose an action:")
        with st.popover("profile"):
            st.write(f"name:{name}")
            st.write(f"rollno:{st.session_state.id}")
        with st.popover("settings"):
            st.write("update the password")
            otp = st.text_input("enter the otp" ,type='password')
            if verify_otp(secret,otp):
                password = st.text_input("enter the new password",type="password")
                change_pass(password,st.session_state.id)
                st.success("changed successfully!!!")
            else:
                st.error("enter the correct otp...")
        if st.button("🚪 Logout"):
            st.session_state.authenticated = False
            st.session_state.page = "login"
            st.rerun()

    # Main page content
    st.title("Welcome to the ANJAC AI")
    st.write(f"Hello, {name}!")

    if role:
        # Initialize session state
        if 'qa_list' not in st.session_state:
            st.session_state.qa_list = []
        # st.header(f"{st.session_state.role} Role Content:")
        # st.text(st.session_state.role_content)
        # st.header(f"{st.session_state.role} SQL Content:")
        # st.text(st.session_state.sql_content)
        # role = st.session_state.role
        role_prompt=st.session_state.role_content
        sql_content = st.session_state.sql_content
        if "input" not in st.session_state:
            st.session_state.input = ""
        if "stored_value" not in st.session_state:
            st.session_state.stored_value = ""

        def process_and_clear():
            st.session_state.stored_value = st.session_state.input
            st.session_state.input = ""
        # Allow the user to ask a question
        question1 = st.text_area('Input your question:', key='input',on_change=process_and_clear)
        # submit = st.button('Ask the question')
        question=st.session_state.stored_value
        if question:
            combined_prompt = create_combined_prompt(question, sql_content)
            response = get_gemini_response(combined_prompt)

            # Display the SQL query
            # st.write("Generated SQL Query:", response)
            raw_query = response
            formatted_query = raw_query.replace("sql", "").strip("'''").strip()
            # print("formatted :",formatted_query)
            single_line_query = " ".join(formatted_query.split()).replace("```", "")
            # print(single_line_query)
            # Query the database
            data = read_sql_query(single_line_query)

            if isinstance(data, list):
                #st.write("according to,")
                #st.table(data)
                pass
                
            else:
                #st.write(data)
                # Display any errors
                pass
            # Generate response for the question and answer
            answer = model.generate_content(f"student name :{name} role:{role} prompt:{role_prompt} Answer this question: {question} with results {str(data)}")
            result_text = answer.candidates[0].content.parts[0].text

            # Store the question and answer in session state
            st.session_state.qa_list.append({'question': question, 'answer': result_text})

            if st.session_state.qa_list:
                for qa in reversed(st.session_state.qa_list):
        # Display previous questions and answers
                    st.write(f"**Question:** {qa['question']}")
                    st.write(f"**Answer:** {qa['answer']}")
                    st.write("---")
def admin_page():
    st.set_page_config(page_title="Admin Dashboard", layout="wide")
    secret, role, name = get_user_details(st.session_state.user_id)

    # Sidebar content
    with st.sidebar:
        st.header("Admin Modules")
        module = st.radio(
            "Select Module",
            options=["File Upload and Edit", "Database Setup", "Query Area", "Logout"]
        )
        # st.rerun()

    # Inject custom CSS for styling
    st.markdown("""
    <style>
    .stExpander {
        position: fixed;
        top: 70px;
        right: 10px;
        width: 200px !important;
        z-index: 9999;
    }
    .stExpander > div > div {
        background-color: #f5f5f5;
        border: 1px solid #ccc;
        border-radius: 10px;
        box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
    }
    .stButton button {
        width: 90%;
        margin: 5px auto;
        display: block;
        background-color: #007bff;
        color: white;
        border-radius: 5px;
        border: none;
        font-size: 14px;
        cursor: pointer;
    }
    .stButton button:hover {
        background-color: #0056b3;
    }
    </style>
    """, unsafe_allow_html=True)

    # Main page content
    st.title("Admin Dashboard")
    st.write(f"Welcome, {name}! 👋")

    for file_name in ["collegehistory.txt", "departmenthistory.txt", "syllabus.txt"]:
        if not os.path.exists(file_name):
            with open(file_name, "w") as f:
                f.write("")

# List of text files
                           
    if module=="File Upload and Edit":
        st.subheader("File Upload and Edit Module")
         # Selection of category to save the file
        category = st.selectbox(
        "Select the category to save the uploaded file:",
        ["collegehistory.txt", "departmenthistory.txt", "syllabus.txt"]
    )

    # File uploader
        uploaded_file = st.file_uploader(
        "Upload a PDF, Word, or Text file", type=["pdf", "docx", "txt"]
    )

        if uploaded_file:
        # Read and display the content of the uploaded file
            if uploaded_file.type == "application/pdf":
                import PyPDF2
                pdf_reader = PyPDF2.PdfReader(uploaded_file)
                file_content = "".join([page.extract_text() for page in pdf_reader.pages])
            elif uploaded_file.type in ["application/vnd.openxmlformats-officedocument.wordprocessingml.document"]:
                from docx import Document
                doc = Document(uploaded_file)
                file_content = "\n".join([p.text for p in doc.paragraphs])
            else:
                file_content = uploaded_file.read().decode('utf-8')

            st.text_area("Uploaded File Content", value=file_content, height=300, disabled=True)

        # Section for editing file content
            edited_content = st.text_area("Edit File Content", value=file_content, height=300)

            if st.button("Save File"):
                with open(category, "a") as f:
                    f.write(edited_content)
                st.success(f"File content saved to {category} successfully!")

    # Section for managing existing files
        st.subheader("Manage Existing Files")
        existing_file = st.selectbox(
        "Select a file to view or edit:",
        ["collegehistory.txt", "departmenthistory.txt", "syllabus.txt"]
    )

        if st.button("Open File"):
            with open(existing_file, "r") as f:
                existing_content = f.read()
            edited_existing_content = st.text_area("Edit Existing File Content", value=existing_content, height=300)

            if st.button("Update File"):
                with open(existing_file, "w") as f:
                    f.write(edited_existing_content)
                st.success(f"Content of {existing_file} updated successfully!")

    # Deletion section
        st.subheader("Delete File Content")
        file_to_delete = st.selectbox(
        "Select a file to delete content:",
        ["collegehistory.txt", "departmenthistory.txt", "syllabus.txt"]
    )

        if st.button("Delete Content"):
            with open(file_to_delete, "w") as f:
                f.write("")
            st.success(f"Content of {file_to_delete} deleted successfully!")


   
    


    elif module == "Database Setup":
        st.subheader("Database Setup Module")
        st.write("Set up the database for students and staff.")
        db_name = st.text_input("Enter Database Name")
        admin_username = st.text_input("Enter Admin Username")
        admin_password = st.text_input("Enter Admin Password", type="password")
        if st.button("Setup Database"):
            # Add actual DB setup logic here
            st.success(f"Database '{db_name}' setup completed!")

    elif module == "Query Area":
        st.subheader("Query Area Module")
        query = st.text_area("Enter your SQL query")
        if st.button("Execute Query"):
            # Add query execution logic here
            st.success(f"Executed query: {query}")

    elif module == "Logout":
        st.session_state.authenticated = False
        st.session_state.page = "login"
        st.success("Logged out successfully!")
        st.rerun()

    

# Main app
def app():
    # Initialize session state attributes
    if "authenticated" not in st.session_state:
        st.session_state.authenticated = False
    if "page" not in st.session_state:
        st.session_state.page = "guest"
    if "user_id" not in st.session_state:
        st.session_state.user_id = None
    if "multifactor" not in st.session_state:
        st.session_state.multifactor = None
    if "secret" not in st.session_state:
        st.session_state.secret = None
    if "role" not in st.session_state:
        st.session_state.role = None
    if "name" not in st.session_state:
        st.session_state.name = None
    if "id" not in st.session_state:
        st.session_state.id = None
    

    # Page navigation
    if st.session_state.page == "guest":
        guest_page()
    elif st.session_state.page == "login":
        login_page()
    elif st.session_state.page == "qr_setup":
        qr_setup_page()
    elif st.session_state.page == "otp_verification":
        otp_verification_page()
    elif st.session_state.page == "welcome":
        welcome_page()
    elif st.session_state.page == "admin":
        admin_page()

# Run the app
if __name__ == "__main__":
    app()
