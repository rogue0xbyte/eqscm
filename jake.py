from pymongo import MongoClient
from pymongo.operations import UpdateOne

# Connect to MongoDB
client = MongoClient("mongodb+srv://aaditya:eqscm@eqscm.brs6h.mongodb.net/?retryWrites=true&w=majority&appName=eqscm")

# Select the database and collection
db = client.status_db
collection = db.status_collection

# Delete documents where "id" starts with "DMO"
collection.delete_many({"id": {"$regex": "^DMO"}})

print("Deleted documents where id starts with 'DMO'.")

update_operations = []

for doc in collection.find():
    update_fields = {}
    unset_fields = {}

    # Check if both "created" and "updated" fields exist
    if "created" in doc and "updated" in doc:
        # Rename both to "Not Started", using the "created" field's value
        update_fields["Not Started"] = doc["created"]
        # Mark both "created" and "updated" fields for removal
        unset_fields["created"] = ""
        unset_fields["updated"] = ""
    
    # If only "created" exists, rename it to "Not Started"
    elif "created" in doc:
        update_fields["Not Started"] = doc["created"]
        unset_fields["created"] = ""  # To delete the "created" field
    
    # If only "updated" exists, rename it to "Not Started"
    elif "updated" in doc:
        update_fields["Not Started"] = doc["updated"]
        unset_fields["updated"] = ""  # To delete the "updated" field
    
    # Apply changes only if there's an update to be made
    if update_fields or unset_fields:
        # Combine $set (to rename) and $unset (to remove the old field)
        update_operations.append(
            UpdateOne({"_id": doc["_id"]}, {"$set": update_fields, "$unset": unset_fields})
        )

# Perform the bulk update
if update_operations:
    collection.bulk_write(update_operations)
    print("Renamed 'created' and/or 'updated' to 'Not Started' as keys and deleted the old keys.")