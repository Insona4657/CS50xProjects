import pandas as pd
import sqlite3
# Read the Excel file into a DataFrame
df = pd.read_excel("C:/Users/Jy/PycharmProjects/CS50xProjects/finance/output_modified.xlsx")

conn = sqlite3.connect("C:/Users/Jy/PycharmProjects/CS50xProjects/finance/finance.db")
cursor = conn.cursor()

# Create an empty dictionary to store the key-value pairs
company_dict = []

# Iterate through the DataFrame rows and populate the dictionary
for index, row in df.iterrows():
    key = row['Company Name']  # Assuming 'Company Name' is the column name for company names
    value = row['Stock_Code']  # Assuming 'Stock_Code' is the column name for stock codes
    company_dict.append({"symbol": value, "name": key})



for key in company_dict:
    symbol = key["symbol"]
    name = key["name"]
    print(symbol)
    print(name)
    #cursor.execute("INSERT INTO stock_names (symbol, name) VALUES (?, ?)", (symbol, name))


# Commit the changes and close the connection
#conn.commit()
#conn.close()
