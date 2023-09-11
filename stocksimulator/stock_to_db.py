import sqlite3
import json

# Step 1: Read the JSON file and extract data
with open("C:/Users/Jy/PycharmProjects/CS50xProjects/finance/US_STOCK_JSON/nyse_full_tickers.json", "r") as json_file:
    data = json.load(json_file)

# Temporary dictionary to store the extracted data
temp_data = []

for entry in data:
    symbol = entry.get("symbol")
    name = entry.get("name")
    
    if symbol and name:
        temp_data.append({"symbol": symbol, "name": name})

# Step 2: Create and connect to the SQLite database
conn = sqlite3.connect("C:/Users/Jy/PycharmProjects/CS50xProjects/finance/finance.db")
cursor = conn.cursor()

# Step 3: Create the stock_names table if it doesn't exist
cursor.execute("""
    CREATE TABLE IF NOT EXISTS stock_names (
        id INTEGER PRIMARY KEY AUTOINCREMENT,
        symbol TEXT NOT NULL,
        name TEXT NOT NULL,
        FOREIGN KEY (symbol) REFERENCES stock_symbols (symbol)
    )
""")
# Step 4: Insert data into the stock_names table
for entry in temp_data:
    symbol = entry["symbol"]
    name = entry["name"]
    cursor.execute("INSERT INTO stock_names (symbol, name) VALUES (?, ?)", (symbol, name))

# Commit the changes and close the connection
conn.commit()
conn.close()