import sqlite3
import json

# Connect to the SQLite database
conn = sqlite3.connect("C:/Users/Jy/PycharmProjects/CS50xProjects/finance/finance.db")
cursor = conn.cursor()

# Execute a query to retrieve data from the table
cursor.execute("SELECT name FROM stock_names")

# Iterate through the rows
for row in cursor.fetchall():
    data = row[0]  # Assuming "mycolumn" is the first (and only) column in the result
    try:
        # Attempt to parse the data as JSON
        data_dict = json.loads(data)
        
        # Check if the parsed data is a list
        if isinstance(data_dict, list):
            # If it's a list, print its values
            for item in data_dict:
                print("Value:", item)
    except json.JSONDecodeError:
        pass
        # Handle JSON parsing errors

# Close the database connection
conn.close()