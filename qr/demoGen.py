import csv
import random

# Field names from the image
fields = [
    "Job Status", "Unit", "Job ID", "Area", "System No", "Equipment TAG No",
    "Job Description / Notification Description", "PM/Non-PM", "Work Order No",
    "Discipline", "Workshop", "Additional details", "Scheduled Dropped on",
    "Actual dropped on", "Actual received in Laydown area",
    "Actual Send to Workshop", "Actual receive in Workshop",
    "Actual out from workshop", "Actual Received in Laydown area after O/H",
    "Picked up for Installation", "Scheduled for installation",
    "Installed on", "Final Handover to Operation", "Size & Rating",
    "Valve Type", "Make", "Link for Valve reports & Photos",
    "Unit Inspection required", "Finding / Discoveries", "Remarks/Comments"
]

# Generate random demo data
rows = []
for i in range(1, 51):
    row = [
        "Pending",  # Job Status
        "DMO",  # Unit
        f"DMO{i}",  # Unique Job ID
        random.choice(["Glycol", "Oxide", "Hydro"]),  # Random Area
        random.randint(60, 90),  # System No
        f"MXK-DEMO-{random.randint(1000, 9999)}",  # Equipment TAG No
        "DEMO JOB DESCRIPTION",  # Job Description
        "DEMO",  # PM/Non-PM
        random.randint(10000000, 99999999),  # Work Order No
        "DEMO",  # Discipline
        "DEMO Workshop",  # Workshop
        "DEMO Additional Details",  # Additional details
        f"{random.randint(20, 31)}/{random.randint(1,3)}/2025",  # Scheduled Dropped on
        f"",  # Actual dropped on
        f"",  # Actual received in Laydown area
        f"",  # Actual Send to Workshop
        f"",  # Actual receive in Workshop
        f"",  # Actual out from workshop
        f"",  # Actual Received in Laydown area after O/H
        f"",  # Picked up for Installation
        f"{random.randint(20, 31)}/{random.randint(1,3)}/2025",  # Scheduled for installation
        f"",  # Installed on
        f"",  # Final Handover to Operation
        f"{random.randint(1, 10)} X {random.randint(1, 10)} IN",  # Size & Rating
        random.choice(["3 Way", "Globe", "Butterfly", "Angle", "Ball", "Globe", "Rotary Globe"]),  # Valve Type
        "",  # Make
        "",  # Link for Valve reports & Photos
        random.choice(["Yes", ""]),  # Unit Inspection required
        "",  # Finding / Discoveries
        "This is a Demo Item"  # Remarks/Comments
    ]
    rows.append(row)

# Write to a CSV file
output_file = "demo_job_data_extended.csv"
with open(output_file, mode='w', newline='') as file:
    writer = csv.writer(file)
    writer.writerow(fields)
    writer.writerows(rows)

print(f"Demo job data with 50 rows has been written to '{output_file}'.")
