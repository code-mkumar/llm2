import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('university.db')
cursor = conn.cursor()

# Retrieve data from a specific table, e.g., 'user_detail'
cursor.execute("SELECT * FROM user_detail where id ='SEE5' and password = 'jack@1234';")
data = cursor.fetchall()

# Display the retrieved data
print("Data from user_detail:")
for row in data:
    print(row)

# Retrieve and display the schema of the table
cursor.execute("PRAGMA table_info('user_detail');")
schema_info = cursor.fetchall()

print("\nSchema of user_detail:")
for column in schema_info:
    print(column)

# Close the connection
conn.close()
# # # # import streamlit as st

# # # # # Example: Profile Dropdown
# # # # with st.sidebar:  # Can also be in the main page
# # # #     st.image("https://via.placeholder.com/50", width=50, caption="User Avatar")
# # # #     user_menu = st.selectbox(
# # # #         "Account Options",
# # # #         ["Profile", "Settings", "Logout"]
# # # #     )

# # # #     if user_menu == "Profile":
# # # #         st.write("Displaying user profile...")
# # # #     elif user_menu == "Settings":
# # # #         st.write("Displaying settings...")
# # # #     elif user_menu == "Logout":
# # # #         st.write("Logging out...")
# # import streamlit as st

# # # Inject custom CSS to position the expander and style it
# # st.markdown("""
# #     <style>
# #     .stExpander {
# #         position: fixed; /* Keep the expander fixed */
# #         top: 70px; /* Distance from the top */
# #         right: 10px; /* Distance from the right */
# #         width: 200px !important; /* Shrink the width */
# #         z-index: 9999; /* Bring it to the front */
# #     }
# #     .stExpander > div > div {
# #         background-color: #f5f5f5; /* Light grey background */
# #         border: 1px solid #ccc; /* Border styling */
# #         border-radius: 10px; /* Rounded corners */
# #         box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1); /* Subtle shadow */
# #     }
# #     .stButton button {
# #         width: 90%; /* Make buttons fit nicely */
# #         margin: 5px auto; /* Center-align buttons */
# #         display: block;
# #         background-color: #007bff; /* Blue button */
# #         color: white;
# #         border-radius: 5px;
# #         border: none;
# #         font-size: 14px;
# #         cursor: pointer;
# #     }
# #     .stButton button:hover {
# #         background-color: #0056b3; /* Darker blue on hover */
# #     }
# #     </style>
# # """, unsafe_allow_html=True)

# # # Main page user menu using expander
# # with st.expander("Welcome, User! 🧑‍💻"):
# #     st.write("Choose an action:")
# #     if st.button("👤 Profile"):
# #         st.write("Viewing your profile details...")
# #     if st.button("⚙️ Settings"):
# #         st.write("Adjust your preferences here...")
# #     if st.button("🚪 Logout"):
# #         st.write("You have successfully logged out.")


# # # import streamlit as st

# # # # Inject custom HTML and CSS to position the menu
# # # st.markdown("""
# # #     <style>
# # #     .user-menu {
# # #         position: fixed;
# # #         top: 70px;
# # #         right: 10px;
# # #         background-color: #f5f5f5;
# # #         border: 1px solid #ccc;
# # #         border-radius: 10px;
# # #         padding: 10px;
# # #         width: 150px;
# # #         box-shadow: 0 4px 8px rgba(0, 0, 0, 0.1);
# # #         font-family: Arial, sans-serif;
# # #         font-size: 14px;
# # #         z-index: 9999;
# # #     }
# # #     .user-menu button {
# # #         display: block;
# # #         margin: 5px 0;
# # #         padding: 5px 10px;
# # #         background-color: #007bff;
# # #         color: white;
# # #         border: none;
# # #         border-radius: 5px;
# # #         cursor: pointer;
# # #         width: 100%;
# # #         font-size: 12px;
# # #     }
# # #     .user-menu button:hover {
# # #         background-color: #0056b3;
# # #     }
# # #     </style>
    
# # #     <div class="user-menu">
# # #         <p><strong>Welcome, User!</strong></p>
# # #         <button onclick="window.alert('Viewing Profile')">👤 Profile</button>
# # #         <button onclick="window.alert('Opening Settings')">⚙️ Settings</button>
# # #         <button onclick="window.alert('Logging Out')">🚪 Logout</button>
# # #     </div>
# # # """, unsafe_allow_html=True)
# import streamlit as st

# # Set page configuration
# st.set_page_config(page_title="Floating Screen Example", layout="wide")

# # Add custom CSS for the floating screen
# st.markdown("""
#     <style>
#     /* Background overlay */
#     .overlay {
#         position: fixed;
#         top: 0;
#         left: 0;
#         width: 100%;
#         height: 100%;
#         background-color: rgba(0, 0, 0, 0.5);
#         z-index: 9998;
#         display: none;
#     }

#     /* Floating screen (modal) */
#     .floating-screen {
#         position: fixed;
#         top: 50%;
#         left: 50%;
#         transform: translate(-50%, -50%);
#         width: 400px;
#         background-color: white;
#         padding: 20px;
#         border-radius: 10px;
#         box-shadow: 0 4px 8px rgba(0, 0, 0, 0.2);
#         z-index: 9999;
#         display: none;
#     }

#     /* Button to trigger the floating screen */
#     .floating-button {
#         position: fixed;
#         bottom: 20px;
#         right: 20px;
#         background-color: #007bff;
#         color: white;
#         padding: 10px 20px;
#         border: none;
#         border-radius: 5px;
#         font-size: 16px;
#         cursor: pointer;
#     }

#     .floating-button:hover {
#         background-color: #0056b3;
#     }

#     /* Show the modal and overlay when active */
#     .overlay.active,
#     .floating-screen.active {
#         display: block;
#     }
#     </style>
# """, unsafe_allow_html=True)

# # Function to show/hide the modal
# if "show_modal" not in st.session_state:
#     st.session_state["show_modal"] = False

# def toggle_modal():
#     st.session_state["show_modal"] = not st.session_state["show_modal"]

# # Sidebar toggle button
# if st.button("Open Floating Screen"):
#     toggle_modal()

# # Add floating screen using conditional rendering
# if st.session_state["show_modal"]:
#     st.markdown("""
#         <div class="overlay active"></div>
#         <div class="floating-screen active">
#             <h3>Floating Screen</h3>
#             <p>This is a floating screen in Streamlit.</p>
#             <form>
#                 <input type="text" placeholder="Enter text here">
#             </form>
#             <button onclick="toggleFloatingScreen()">Close</button>
#         </div>
#         """, unsafe_allow_html=True)

# # Main page content
# st.title("Main Page Content")
# st.write("This is the main page content. Use the floating button to open the floating screen.")
# import streamlit as st

# with st.popover("Open popover"):
#     st.markdown("Hello World 👋")
#     name = st.text_input("What's your name?")
#     st.write("Your name:", name)