import csv
from collections import Counter
from datetime import datetime
from pathlib import Path

csv_path = Path(__file__).resolve().parent / "data" / "SFinDSet.csv"

row_count = 0
unique_accounts = set()
mode_counts = Counter()
type_counts = Counter()
min_date = None
max_date = None

with csv_path.open("r", encoding="utf-8-sig", newline="") as file:
    for row in csv.DictReader(file):
        row_count += 1
        unique_accounts.add(row["Account_Number"])
        mode_counts[row["Transaction_Mode"]] += 1
        type_counts[row["Transaction_Type"]] += 1

        date = datetime.strptime(row["Transaction_Date"], "%m/%d/%Y %H:%M")
        if min_date is None or date < min_date:
            min_date = date
        if max_date is None or date > max_date:
            max_date = date

import json

profile = {
    "row_count": row_count,
    "unique_accounts": len(unique_accounts),
    "date_start": min_date.isoformat(sep=" ", timespec="minutes"),
    "date_end": max_date.isoformat(sep=" ", timespec="minutes"),
    "transaction_modes": dict(mode_counts),
    "transaction_types": dict(type_counts),
}

output_path = csv_path.parent / "transaction_profile.json"
output_path.write_text(json.dumps(profile, indent=2), encoding="utf-8")

print(f"Saved transaction profile to: {output_path}")
print(f"Rows: {row_count:,}")
print(f"Unique accounts: {len(unique_accounts):,}")
print(f"Date range: {profile['date_start']} to {profile['date_end']}")