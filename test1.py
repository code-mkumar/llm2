import streamlit as st
import sqlite3
import pyotp
import qrcode
from io import BytesIO
import google.generativeai as genai
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
    cursor.execute("UPDATE user_detail SET secret_code = ? WHERE id = ?", (secret, user_id))
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
def update_multifactor_status(user_id, status):
    conn = create_connection()
    cursor = conn.cursor()
    cursor.execute("UPDATE user_detail SET multifactor = ? WHERE id = ?", (status, user_id))
    conn.commit()
    conn.close()

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

# Pages
def guest_page():
    # Initialize session state
    if 'qa_list' not in st.session_state:
        st.session_state.qa_list = []
    if st.button("Go to Login"):
        st.session_state.page = "login"
    st.title("Welcome, Guest!")
    st.write("You can explore the site as a guest, but you'll need to log in for full role based access.")
    question = st.text_input('Input your question:', key='input')
    submit = st.button('Ask the question')
    default,default_sql = read_default_files()
    if submit:
        txt=model.generate_content(f"{question} give 1 if the question need sql query or 0")
        #st.write(txt.text)
        data = ''
        if not txt.text == '0':
            response=model.generate_content(f"{default_sql}\n\n{question}")
            raw_query = response.text
            formatted_query = raw_query.replace("sql", "").strip("'''").strip()
            print("formatted :",formatted_query)
            single_line_query = " ".join(formatted_query.split()).replace("```", "")
            # print(single_line_query)
            # Query the database
            data = read_sql_query(single_line_query)
            st.write(data)
        answer = model.generate_content(f"{default} Answer this question: {question} with results {str(data)}")
        result_text = answer.candidates[0].content.parts[0].text

            # Store the question and answer in session state
        st.session_state.qa_list.append({'question': question, 'answer': result_text})

        if st.session_state.qa_list:
            for qa in reversed(st.session_state.qa_list):
        # Display previous questions and answers
                st.write(f"**Question:** {qa['question']}")
                st.write(f"**Answer:** {qa['answer']}")
                st.write("---")


#login page
def login_page():
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
            st.session_state.multifactor = user[7]  # Multifactor column
            st.session_state.secret = user[9]  # Secret code column
            st.success("Login successful!")
            if st.session_state.multifactor == 1:
                st.session_state.page = "otp_verification"  # Direct to OTP verification if MFA is enabled
            else:
                if st.session_state.secret == "None":
                    st.session_state.page = "qr_setup"  # If MFA is not enabled, show QR setup
                else:
                    st.session_state.page = "otp_verification"  # Otherwise show OTP verification
        else:
            st.error("Invalid credentials.")
    if st.button("Visit as Guest"):
        st.session_state.page = "guest"

#qr scanning page
def qr_setup_page():
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
    st.image(qr_code_stream, caption="Scan this QR code with your authenticator app.", use_column_width=False)
    st.write(f"Secret Code: `{secret}` (store this securely!)")

    # Immediate OTP verification
    otp = st.text_input("Enter OTP from Authenticator App", type="password")
    if st.button("Verify OTP"):
        if not verify_otp(secret, otp):
            update_multifactor_status(user_id, 1)  # Update MFA status in the database
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
            st.success("Multifactor authentication is now enabled.")
            st.session_state.page = "welcome"
        else:
            st.error("Invalid OTP. Try again.")

#otp verification page
def otp_verification_page():
    st.title("Verify OTP")
    user_id = st.session_state.user_id
    secret = st.session_state.secret

    otp = st.text_input("Enter OTP", type="password")
    if st.button("Verify"):
        if not verify_otp(secret, otp):
            st.success("OTP Verified! Welcome.")
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
            st.session_state.page = "welcome"
        else:
            st.error("Invalid OTP. Try again.")

#just for combining
def create_combined_prompt(question, sql_prompt):
    return f"{sql_prompt}\n\n{question}\n\n "

# Function to interact with the Google Gemini model
def get_gemini_response(combined_prompt):
    response = model.generate_content(combined_prompt)
    print(response)
    try:
        final = model.generate_content(f"{response.text} if any user_id word found in this statement replace with {st.session_state.id}")
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
        #print(sql)
        conn = create_connection()
        cur = conn.cursor()
        cur.execute(sql)
        rows = cur.fetchall()
        conn.commit()
        conn.close()
        st.write(rows)
        return rows
    except Exception as e:
        #print(sql)
        print(e)
        return f"SQLite error: {e}"

def welcome_page():
    if st.button("Logout"):
        st.session_state.authenticated = False
        st.session_state.page = "login"
    st.title("Welcome to the ANJAC AI")
    st.write(f"Hello, {st.session_state.name}!")
    if st.session_state.role:
        # Initialize session state
        if 'qa_list' not in st.session_state:
            st.session_state.qa_list = []
        # st.header(f"{st.session_state.role} Role Content:")
        # st.text(st.session_state.role_content)
        # st.header(f"{st.session_state.role} SQL Content:")
        # st.text(st.session_state.sql_content)
        role = st.session_state.role
        role_prompt=st.session_state.role_content
        sql_content = st.session_state.sql_content
        question = st.text_input('Input your question:', key='input')
        submit = st.button('Ask the question')

        if submit:
            combined_prompt = create_combined_prompt(question, sql_content)
            response = get_gemini_response(combined_prompt)

            # Display the SQL query
            st.write("Generated SQL Query:", response)
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
            answer = model.generate_content(f"student name :{st.session_state.name} role:{role} prompt:{role_prompt} Answer this question: {question} with results {str(data)}")
            result_text = answer.candidates[0].content.parts[0].text

            # Store the question and answer in session state
            st.session_state.qa_list.append({'question': question, 'answer': result_text})

            if st.session_state.qa_list:
                for qa in reversed(st.session_state.qa_list):
        # Display previous questions and answers
                    st.write(f"**Question:** {qa['question']}")
                    st.write(f"**Answer:** {qa['answer']}")
                    st.write("---")

    

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

# Run the app
if __name__ == "__main__":
    app()
