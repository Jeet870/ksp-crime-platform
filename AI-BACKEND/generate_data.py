import csv
import random
import os
from datetime import datetime, timedelta
from faker import Faker

fake = Faker('en_IN')
random.seed(42)

DISTRICTS = [
    "Bengaluru East",
    "Bengaluru Central", 
    "Bengaluru West",
    "Bengaluru South",
    "Bengaluru North",
]

POLICE_STATIONS = {
    "Bengaluru East":    ["Whitefield PS", "Marathahalli PS", "Indiranagar PS"],
    "Bengaluru Central": ["MG Road PS", "Cubbon Park PS", "Shivajinagar PS"],
    "Bengaluru West":    ["Rajajinagar PS", "Vijayanagar PS", "Magadi Road PS"],
    "Bengaluru South":   ["BTM Layout PS", "Koramangala PS", "JP Nagar PS"],
    "Bengaluru North":   ["Yelahanka PS", "Hebbal PS", "Devanahalli PS"],
}

CRIME_TYPES = ["chain_snatching","burglary","cyber_fraud","vehicle_theft","assault","robbery"]

DISTRICT_COORDS = {
    "Bengaluru East":    (12.9784, 77.6408),
    "Bengaluru Central": (12.9716, 77.5946),
    "Bengaluru West":    (12.9698, 77.5500),
    "Bengaluru South":   (12.9141, 77.5800),
    "Bengaluru North":   (13.0358, 77.5970),
}

VEHICLE_MAKES  = ["Honda Activa","Bajaj Pulsar","Maruti Swift","TVS Jupiter","Hero Splendor"]
VEHICLE_COLORS = ["black","white","red","silver","blue","grey"]
VEHICLE_TYPES  = ["motorcycle","car","auto-rickshaw","truck"]

TEMPLATES = {
    "burglary": [
        "At approximately {time} hours unknown persons cut the electrical supply line at the rear of the premises and gained entry through the rear window by breaking the iron grille. Gold ornaments weighing {weight} grams and cash of Rs {amount} were stolen.",
        "Unknown miscreants gained entry into the premises by forcing the front door lock with a crowbar. Cash of Rs {amount} and electronic items were removed while the family was away.",
    ],
    "chain_snatching": [
        "The victim was walking near {location} when two persons on a motorcycle approached from behind. The pillion rider snatched the gold chain weighing {weight} grams from the victim neck. The accused fled towards {direction}.",
        "At approximately {time} hours two accused on a two-wheeler stopped beside the complainant and grabbed the gold necklace before speeding away.",
    ],
    "cyber_fraud": [
        "The complainant received a call from an unknown number claiming to be a bank official and was convinced to share their OTP. Rs {amount} was subsequently transferred without consent.",
        "The victim responded to a WhatsApp message offering a part-time job and was asked to pay Rs {amount} as a deposit which was never returned.",
    ],
    "vehicle_theft": [
        "The complainant parked their {vehicle} bearing registration {reg_num} near {location} and upon returning after {hours} hours found the vehicle missing.",
        "The accused broke the steering lock of the complainant vehicle {vehicle} with registration {reg_num} parked outside the residence and drove it away.",
    ],
    "assault": [
        "The complainant was physically attacked by {num} unknown persons near {location} at approximately {time} hours. The victim sustained {injury} injuries.",
        "A group of {num} persons attacked the complainant outside {location}. The victim was taken to the government hospital for {injury} injuries.",
    ],
    "robbery": [
        "Armed persons numbering {num} threatened the complainant at {location} and forcibly took cash of Rs {amount} and a mobile phone.",
        "The complainant was intercepted by {num} persons who forcibly snatched their bag containing cash Rs {amount} and jewellery.",
    ],
}

def rand_time():
    return f"{random.randint(0,23):02d}:{random.choice([0,15,30,45]):02d}"

def fill_template(crime_type):
    t = random.choice(TEMPLATES.get(crime_type, ["Incident reported near {location}."]))
    return t.format(
        time=rand_time(),
        weight=random.randint(8,50),
        amount=random.randint(5000,250000),
        location=fake.street_name() + " junction",
        direction=random.choice(["Outer Ring Road","Hosur Road","Bellary Road"]),
        vehicle=random.choice(VEHICLE_MAKES),
        reg_num=f"KA-{random.randint(1,99):02d}-AB-{random.randint(1000,9999)}",
        hours=random.randint(1,8),
        num=random.randint(2,5),
        injury=random.choice(["minor","grievous","moderate"]),
    )

def generate():
    os.makedirs("data", exist_ok=True)
    start = datetime(2023, 1, 1)

    # 1. accused
    accused_list = []
    for i in range(1, 31):
        district = random.choice(DISTRICTS)
        accused_list.append({
            "accused_id":        i,
            "name":              fake.name(),
            "alias":             random.choice([fake.first_name(), "", ""]),
            "age":               random.randint(18, 55),
            "gender":            random.choice(["Male","Male","Male","Female"]),
            "address":           fake.address().replace("\n", ", "),
            "phone_number":      fake.phone_number()[:15],
            "aadhaar_last4":     str(random.randint(1000, 9999)),
            "prior_cases_count": 0,
            "district":          district,
        })

    # 2. firs
    firs = []
    for i in range(1, 201):
        district   = random.choice(DISTRICTS)
        ps         = random.choice(POLICE_STATIONS[district])
        crime_type = random.choice(CRIME_TYPES)
        blat, blon = DISTRICT_COORDS[district]
        fir_date   = start + timedelta(days=random.randint(0, 730))
        firs.append({
            "fir_id":               i,
            "fir_number":           f"FIR-{fir_date.year}-{ps[:3].upper()}-{i:03d}",
            "date_filed":           fir_date.strftime("%Y-%m-%d"),
            "time_filed":           rand_time(),
            "police_station":       ps,
            "district":             district,
            "crime_type":           crime_type,
            "ipc_sections":         random.choice(["379","392","394","420","302"]),
            "location_description": fake.street_name() + ", " + ps.replace(" PS",""),
            "latitude":             round(blat + random.uniform(-0.05, 0.05), 6),
            "longitude":            round(blon + random.uniform(-0.05, 0.05), 6),
            "description_text":     fill_template(crime_type),
            "status":               random.choice(["open","open","under_investigation","chargesheeted","closed"]),
        })

    # 3. fir_accused
    fir_accused = []
    for fir in firs:
        district_accused = [a for a in accused_list if a["district"] == fir["district"]]
        pool   = district_accused if district_accused else accused_list
        n      = random.randint(1, min(3, len(pool)))
        chosen = random.sample(pool, n)
        for j, acc in enumerate(chosen):
            fir_accused.append({
                "fir_id":        fir["fir_id"],
                "accused_id":    acc["accused_id"],
                "role_in_case":  "main accused" if j == 0 else "accomplice",
                "arrest_status": random.choice(["arrested","not_arrested","absconding"]),
            })
            acc["prior_cases_count"] += 1

    # 4. victims
    victims = []
    vid = 1
    for fir in firs:
        for _ in range(random.randint(1, 2)):
            victims.append({
                "victim_id":     vid,
                "fir_id":        fir["fir_id"],
                "name":          fake.name(),
                "age":           random.randint(18, 75),
                "gender":        random.choice(["Male","Female"]),
                "address":       fake.address().replace("\n", ", "),
                "phone_number":  fake.phone_number()[:15],
                "injury_details":random.choice([
                    "", "", "",
                    "Minor abrasion on left arm",
                    "Laceration on forehead",
                    "Bruising on neck",
                    "Fracture of right wrist",
                ]),
            })
            vid += 1

    # 5. vehicles
    vehicles = []
    vehicle_id = 1
    used = set()
    for fa in fir_accused:
        fir = next(f for f in firs if f["fir_id"] == fa["fir_id"])
        if fir["crime_type"] in ["vehicle_theft","chain_snatching","robbery"]:
            if fa["accused_id"] not in used and random.random() < 0.6:
                vehicles.append({
                    "vehicle_id":          vehicle_id,
                    "registration_number": f"KA-{random.randint(1,99):02d}-AB-{random.randint(1000,9999)}",
                    "vehicle_type":        random.choice(VEHICLE_TYPES),
                    "make_model":          random.choice(VEHICLE_MAKES),
                    "color":               random.choice(VEHICLE_COLORS),
                    "owner_accused_id":    fa["accused_id"],
                    "fir_id":              fir["fir_id"],
                })
                vehicle_id += 1
                used.add(fa["accused_id"])

    # 6. bank_transactions
    bank_transactions = []
    txn_id = 1
    accounts = {a["accused_id"]: f"SBIN{random.randint(10000000,99999999)}" for a in accused_list}
    for acc in accused_list:
        for _ in range(random.randint(2, 5)):
            amount  = random.randint(500, 150000)
            flagged = amount > 50000 and random.random() < 0.4
            other   = random.choice([a for a in accused_list if a["accused_id"] != acc["accused_id"]])
            bank_transactions.append({
                "transaction_id":       txn_id,
                "account_number":       accounts[acc["accused_id"]],
                "accused_id":           acc["accused_id"],
                "amount":               amount,
                "transaction_date":     (start + timedelta(days=random.randint(0,730))).strftime("%Y-%m-%d"),
                "transaction_type":     random.choice(["credit","debit"]),
                "counterparty_account": accounts[other["accused_id"]],
                "flagged":              flagged,
                "flag_reason":          "Large transaction above threshold" if flagged else "",
            })
            txn_id += 1

    def write_csv(filename, rows):
        if not rows:
            print(f"  WARNING: {filename} has 0 rows")
            return
        with open(f"data/{filename}", "w", newline="", encoding="utf-8") as f:
            w = csv.DictWriter(f, fieldnames=rows[0].keys())
            w.writeheader()
            w.writerows(rows)
        print(f"  Written: data/{filename} ({len(rows)} rows)")

    print("Generating CSV files...")
    write_csv("accused.csv",           accused_list)
    write_csv("firs.csv",              firs)
    write_csv("fir_accused.csv",       fir_accused)
    write_csv("victims.csv",           victims)
    write_csv("vehicles.csv",          vehicles)
    write_csv("bank_transactions.csv", bank_transactions)
    print("Done.")

if __name__ == "__main__":
    generate()