from fastapi import FastAPI, Request, Form, HTTPException
from fastapi.responses import HTMLResponse, StreamingResponse, JSONResponse
from fastapi.templating import Jinja2Templates
from fastapi.staticfiles import StaticFiles
from datetime import datetime, timezone, timedelta
from collections import OrderedDict
from bson.objectid import ObjectId
from pymongo import MongoClient
import pandas as pd
import io
import os

# MongoDB Setup
client = MongoClient("mongodb+srv://aaditya:eqscm@eqscm.brs6h.mongodb.net/?retryWrites=true&w=majority&appName=eqscm")
db = client.status_db
collection = db.status_collection

# FastAPI App Setup
app = FastAPI()

# Directory for Templates and Static Files
app.mount("/static", StaticFiles(directory="static"), name="static")
templates = Jinja2Templates(directory="templates")

# Helper Function to Get Current Time in GMT+3
def get_current_time_gmt3():
    return (datetime.now(timezone.utc) + timedelta(hours=3)).strftime("%Y-%m-%d %H:%M:%S")

# Route to Render Status Page with Edit Option
@app.get("/status/{id}", response_class=HTMLResponse)
async def get_status_page(id: str, request: Request):


    if id[:3] not in ["EG1", "ASP", "DMO"]:
        return JSONResponse(content={"error": "Incorrect Job ID."}, status_code=400)

    status_object = collection.find_one({"id": id})

    if status_object:
        status_object.pop("_id", None)

    else:
        # Create New Object if Not Found
        status_object = {"id": id, "created": get_current_time_gmt3()}
        collection.insert_one(status_object)

    return templates.TemplateResponse("status_page.html", {"request": request, "status_id": id, "status_data": status_object})

# Route to Handle Status Update
@app.post("/status/{id}")
async def update_status(id: str, request: Request, new_status: str = Form(...)):


    if id[:3] not in ["EG1", "ASP", "DMO"]:
        return JSONResponse(content={"error": "Incorrect Job ID."}, status_code=400)

    collection.update_one(
        {"id": id},
        {"$set": {new_status: get_current_time_gmt3()}}
    )

    updated_status_object = collection.find_one({"id": id})
    updated_status_object.pop("_id", None)

    reversed_status_object = {key: updated_status_object[key] for key in reversed(updated_status_object)}

    return templates.TemplateResponse("status_page.html", {"request": request, "status_id": id, "status_data": reversed_status_object})

# Route to Add or Update Item
@app.post("/add-item")
async def add_or_update_item(request: Request):
    new_item_data = await request.json()

    # Ensure "Job ID" key exists
    if "Job ID" not in new_item_data:
        return JSONResponse(content={"error": "Missing 'Job ID' in the request."}, status_code=400)

    # Rename "Job ID" back to "id" for database storage
    new_item_data["id"] = new_item_data.pop("Job ID")
    if new_item_data["id"][:3] not in ["EG1", "ASP", "DMO"]:
        return JSONResponse(content={"error": "Incorrect Job ID."}, status_code=400)
    new_item_data["updated"] = get_current_time_gmt3()

    existing_item = collection.find_one({"id": new_item_data["id"]})

    if existing_item:
        collection.update_one(
            {"id": new_item_data["id"]},
            {"$set": new_item_data}
        )
        message = "Item updated successfully."
    else:
        new_item_data["created"] = new_item_data["updated"]
        collection.insert_one(new_item_data)
        message = "Item added successfully."

    return JSONResponse(content={"message": message}, status_code=200)

@app.delete("/delete-stage")
async def delete_stage(request: Request, item_name: str, stage_name: str):
    # Find the document where the key 'item_name' exists and contains 'stage_name'
    stage_name = stage_name.replace("_", " ")
    document = collection.find_one({"id": item_name})

    if document:
        # Delete the specific item (key) in the stage_name
        if document.get(stage_name):
            collection.update_one(
                { "_id": document["_id"] }, 
                {
                    "$unset": { stage_name: "" }  # Remove the stage_name field
                }
            )
            # Redirect back to the referring page after deletion
            return {"message": "Stage deleted successfully"}
        else:
            raise HTTPException(status_code=404, detail=f"Stage '{stage_name}' not found in item '{item_name}'")
    else:
        raise HTTPException(status_code=404, detail="Stage not found")


# Route to Export Data as XLSX
@app.get("/export")
async def export_data():
    data = list(collection.find())

    # Remove "_id" from all objects and rename "id" to "Job ID"
    for item in data:
        item.pop("_id", None)
        if "id" in item:
            item["Job ID"] = item.pop("id")

    # Prepare DataFrame
    df = pd.DataFrame(data)

    # Convert DataFrame to XLSX in Memory
    output = io.BytesIO()
    with pd.ExcelWriter(output, engine="xlsxwriter") as writer:
        df.to_excel(writer, index=False, sheet_name="StatusData")

    output.seek(0)
    headers = {
        'Content-Disposition': 'attachment; filename="status_data.xlsx"',
        'Content-Type': 'application/vnd.openxmlformats-officedocument.spreadsheetml.sheet',
    }

    return StreamingResponse(output, headers=headers)
if __name__ == "__main__":
    import uvicorn
    uvicorn.run(app, host="0.0.0.0", port=9000)