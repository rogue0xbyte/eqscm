from pymongo import MongoClient

# Connect to MongoDB
client = MongoClient("mongodb+srv://aaditya:eqscm@eqscm.brs6h.mongodb.net/?retryWrites=true&w=majority&appName=eqscm")

# Select the database and collection
db = client.status_db
collection = db.status_collection

# Delete documents where "id" starts with "DMO"
collection.delete_many({"id": {"$regex": "^DMO"}})

print("Deleted documents where id starts with 'DMO'.")
