import sqlite3

# Connect to SQLite database
conn = sqlite3.connect('university.db')
cursor = conn.cursor()

# Retrieve data from a specific table, e.g., 'user_detail'
cursor.execute("SELECT * FROM user_detail;")
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
