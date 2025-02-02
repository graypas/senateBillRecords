import os
import xml.etree.ElementTree as ET
import mysql.connector

DB_CONFIG = {
    "host": "localhost",
    "user": "root",  # Change if needed
    "password": "3picNE$$",  # Change if needed
    "database": "voting_records"
}

def create_database():
    conn = mysql.connector.connect(
        host=DB_CONFIG["host"],
        user=DB_CONFIG["user"],
        password=DB_CONFIG["password"]
    )
    cursor = conn.cursor()
    cursor.execute("CREATE DATABASE IF NOT EXISTS voting_records")  
    conn.commit()
    cursor.close()
    conn.close()
    print("Database 'voting_records' checked/created successfully.")

def setup_database():
    create_database()  # Ensure the database exists

    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()
    print("Connected to MySQL successfully.")

    cursor.execute("""
        CREATE TABLE IF NOT EXISTS senators (
            id INT AUTO_INCREMENT PRIMARY KEY,
            name VARCHAR(255) UNIQUE
        )
    """)
    print("Table 'senators' checked/created successfully.")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS bills (
            id INT AUTO_INCREMENT PRIMARY KEY,
            bill_name VARCHAR(255) UNIQUE,
            year INT
        )
    """)
    print("Table 'bills' checked/created successfully.")
    
    cursor.execute("""
        CREATE TABLE IF NOT EXISTS votes (
            id INT AUTO_INCREMENT PRIMARY KEY,
            senator_id INT,
            bill_id INT,
            vote VARCHAR(50),
            FOREIGN KEY (senator_id) REFERENCES senators(id),
            FOREIGN KEY (bill_id) REFERENCES bills(id)
        )
    """)
    print("Table 'votes' checked/created successfully.")
    
    conn.commit()
    conn.close()
    print("Database setup complete.")

# Insert a record and return its ID
def get_or_create(cursor, table, column, value):
    cursor.execute(f"SELECT id FROM {table} WHERE {column} = %s", (value,))
    row = cursor.fetchone()
    if row:
        return row[0]
    
    cursor.execute(f"INSERT INTO {table} ({column}) VALUES (%s)", (value,))
    print(f"Inserted new record in {table}: {value}")
    return cursor.lastrowid

# Main script to parse XML files and insert data
base_dir = "votingrecords"
setup_database()
conn = mysql.connector.connect(**DB_CONFIG)
cursor = conn.cursor()

for year in sorted(os.listdir(base_dir), reverse=True):
    year_path = os.path.join(base_dir, year, "bill")
    
    if not os.path.isdir(year_path):
        continue  
    
    for bill_file in os.listdir(year_path):
        bill_path = os.path.join(year_path, bill_file)
        
        if not bill_file.endswith(".xml"):
            continue  
        
        try:
            tree = ET.parse(bill_path)
            root = tree.getroot()
            
            # Get bill name (use document_name or amendment number)
            bill_name = root.find(".//document_name")
            if bill_name is None:
                bill_name = root.find(".//amendment_number")
            if bill_name is not None:
                bill_name = bill_name.text.strip()
            else:
                bill_name = bill_file.replace(".xml", "")  # Fallback
            
            bill_id = get_or_create(cursor, "bills", "bill_name", bill_name)
            
            for member in root.findall(".//member"):
                senator_name = member.find("member_full").text.strip()
                vote_cast = member.find("vote_cast").text.strip()
                
                senator_id = get_or_create(cursor, "senators", "name", senator_name)
                
                # Insert vote
                cursor.execute("""
                    INSERT INTO votes (senator_id, bill_id, vote)
                    VALUES (%s, %s, %s)
                """, (senator_id, bill_id, vote_cast))
                print(f"Vote recorded: {senator_name} -> {bill_name} ({vote_cast})")
        
        except ET.ParseError:
            print(f"Error parsing XML: {bill_path}")
        except AttributeError:
            print(f"Missing data in: {bill_path}")

conn.commit()
conn.close()
print("Senator voting records saved to MySQL.")

def display_database_contents():
    conn = mysql.connector.connect(**DB_CONFIG)
    cursor = conn.cursor()

    print("\nSenators Table:")
    cursor.execute("SELECT * FROM senators;")
    for row in cursor.fetchall():
        print(row)

    print("\nBills Table:")
    cursor.execute("SELECT * FROM bills;")
    for row in cursor.fetchall():
        print(row)

    print("\nVotes Table:")
    cursor.execute("""
        SELECT senators.name, bills.bill_name, votes.vote
        FROM votes
        JOIN senators ON votes.senator_id = senators.id
        JOIN bills ON votes.bill_id = bills.id;
    """)
    for row in cursor.fetchall():
        print(row)

    conn.close()

# Call the function to display the database


display_database_contents()
