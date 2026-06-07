import csv
import random
from faker import Faker

fake = Faker('en_IN')

bangalore_locations = [
    "Koramangala", "Indiranagar", "Whitefield", "Jayanagar", "Marathahalli",
    "HSR Layout", "Bannerghatta Road", "Electronic City", "Yelahanka",
    "Rajajinagar", "Malleshwaram", "BTM Layout", "JP Nagar", "Hebbal",
    "Bellandur", "Sarjapur", "Vijayanagar", "Basavanagudi", "Cunningham Road",
    "MG Road", "Brigade Road", "Shivajinagar", "Frazer Town", "Kammanahalli"
]

crime_types = [
    "Theft", "Robbery", "Burglary", "Chain Snatching", "Vehicle Theft",
    "Cybercrime", "Assault", "Fraud", "Kidnapping", "Domestic Violence",
    "Hit and Run", "Drug Possession", "Vandalism", "Stalking", "Cheating"
]

def generate_description(crime, location):
    templates = [
        f"An incident of {crime.lower()} was reported in {location}, Bangalore. "
        f"The victim approached the local police station and filed a complaint. "
        f"Witnesses present at the scene confirmed the occurrence of the incident. "
        f"Police have registered the case and begun their investigation.",

        f"A case of {crime.lower()} occurred near {location} area in Bangalore. "
        f"The complainant stated that the incident took place during the early hours. "
        f"The accused fled the scene before authorities could arrive. "
        f"Officers have collected evidence and are currently pursuing leads.",

        f"Residents of {location} reported a {crime.lower()} incident to the police. "
        f"The victim sustained losses and immediately notified the nearest police station. "
        f"CCTV footage from nearby cameras is being reviewed by the investigating team. "
        f"The police have assured that the matter will be resolved promptly.",

        f"A complaint regarding {crime.lower()} was lodged at the {location} police station. "
        f"The incident reportedly occurred in a busy area during daylight hours. "
        f"Local authorities have taken cognizance of the matter and filed an FIR. "
        f"Further investigation is underway to identify and apprehend the suspect."
    ]
    return random.choice(templates)

firs = []
for i in range(1, 201):
    location = random.choice(bangalore_locations)
    crime = random.choice(crime_types)
    fir = {
        "FIR_Number": f"BLR-2024-{i:04d}",
        "Date": fake.date_between(start_date='-1y', end_date='today'),
        "Location": location,
        "Crime_Type": crime,
        "Complainant_Name": fake.name(),
        "Complainant_Phone": fake.phone_number(),
        "Officer_Name": fake.name(),
        "Description": generate_description(crime, location)
    }
    firs.append(fir)

with open("bangalore_firs.csv", "w", newline="", encoding="utf-8") as f:
    fieldnames = ["FIR_Number", "Date", "Location", "Crime_Type",
                  "Complainant_Name", "Complainant_Phone", "Officer_Name", "Description"]
    writer = csv.DictWriter(f, fieldnames=fieldnames)
    writer.writeheader()
    writer.writerows(firs)

print("✅ Done! 200 FIRs saved to bangalore_firs.csv")