import pandas as pd
import requests
from pymongo import MongoClient

# Configuration
file_path = "TA 25 EG1ASP.xlsx"
api_url = "http://localhost:9000/add-item"
qr_code_size = (300, 300)  # Size for individual QR codes

def clean_row(row):
    """Filter out keys with invalid values (NaN, empty, etc.)."""
    return {k: v for k, v in row.items() if pd.notna(v) and v != '' and v != 'NULL' and v != 'NaN'}

def purge_db():
    client = MongoClient("mongodb+srv://aaditya:eqscm@eqscm.brs6h.mongodb.net/?retryWrites=true&w=majority&appName=eqscm")
    db = client.status_db
    collection = db.status_collection

    collection.delete_many({})

# Define function to post data to the API
def main(file_path: str, api_url: str):
    # Load Excel data
    df = pd.read_excel(file_path)

    # Iterate over rows and post data
    for idx, row in df.iterrows():
        cleaned_data = clean_row(row.to_dict())

        try:
            # Make API call to add or update item
            response = requests.post(api_url, json=cleaned_data)
            
            if response.status_code == 200:
                print(f"Row {idx + 1}: {response.json()['message']}")
            else:
                print(f"Row {idx + 1}: Error {response.status_code} - {response.text}")

        except requests.RequestException as e:
            print(f"Row {idx + 1}: Request failed - {e}")

if __name__ == "__main__":
    purge_db()
    main(file_path, api_url)
