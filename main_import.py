import random
import csv
from faker import Faker
import pandas as pd
from sqlalchemy import create_engine
import os
import time

# Initialize Faker
fake = Faker()

# Database connection URL (Neon)
DATABASE_URL = "postgresql+psycopg2://neondb_owner:npg_hB62qQynzldf@ep-super-bush-a41t7p8m-pooler.us-east-1.aws.neon.tech/neondb?sslmode=require"

# Vocabulary for random names
ministry_prefixes = ["Ministry of"]
ministry_domains = ["Education", "Health", "Finance", "Technology", "Agriculture", "Defense", "Energy", "Environment", "Justice", "Transport", "Tourism", "Labor", "Foreign Affairs", "Science", "Culture"]
department_keywords = ["Department of"]

# Escape single quotes
def escape_quotes(s):
    return s.replace("'", "''")

# Google Maps iframe placeholder
def generate_google_map_script(entity_type, id):
    return f"<iframe src='https://maps.google.com/maps?q={entity_type}{id}&output=embed'></iframe>"

def generate_ministries(num_ministries):
    ministries = []
    for i in range(1, num_ministries + 1):
        name = f"{random.choice(ministry_prefixes)} {random.choice(ministry_domains)} - {i}"
        script = generate_google_map_script("Ministry", i)
        ministries.append((i, escape_quotes(name), escape_quotes(script)))
    return ministries

def generate_departments(ministries, departments_per_ministry):
    departments = []
    dept_id = 1
    for ministry in ministries:
        ministry_id = ministry[0]
        for _ in range(departments_per_ministry):
            name = f"{random.choice(department_keywords)} of {fake.word().capitalize()} - {dept_id}"
            script = generate_google_map_script("Department", dept_id)
            departments.append((dept_id, escape_quotes(name), escape_quotes(script), ministry_id))
            dept_id += 1
    return departments

# Write to CSV
def write_csv(filename, data, headers):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    print(f"📄 Data saved to '{filename}'")

# Import CSV to Neon using pandas and sqlalchemy
def import_to_neon():
    try:
        print("🚚 Importing data to Neon...")
        start_time = time.time()  # Start timing
        engine = create_engine(DATABASE_URL)

        ministries_df = pd.read_csv("csv_output/ministries.csv")
        departments_df = pd.read_csv("csv_output/departments.csv")

        ministries_df.to_sql("ministry", engine, if_exists="append", index=False)
        print("\n✅ Ministries imported into Neon.")

        departments_df.to_sql("department", engine, if_exists="append", index=False)
        print("✅ Departments imported into Neon.")

        end_time = time.time()  # ⏱️ End timing
        duration_ms = int(((end_time - start_time) * 1000) / 1000)

        print(f"\n⏱️ Total import time: {duration_ms} s")
        print("✅ Data imported successfully into Neon.")

    except Exception as e:
        print("❌ Error while importing to Neon:", e)

# Main execution
def main():
    try:
        num_ministries = int(input("\n🔢 Enter number of ministries to generate: "))
        departments_per_ministry = int(input("🔢 Enter number of departments per ministry: "))
    except ValueError:
        print("❌ Please enter valid integer values.")
        return

    print("\n🚀 Generating ministries and departments...")
    ministries = generate_ministries(num_ministries)
    departments = generate_departments(ministries, departments_per_ministry)

    print(f"\n✅ Generated {len(ministries)} ministries")
    print(f"✅ Generated {len(departments)} departments\n")

    write_csv("csv_output/ministries.csv", ministries, ["id", "name", "google_map_script"])
    write_csv("csv_output/departments.csv", departments, ["id", "name", "google_map_script", "ministry_id"])

    import_to_neon()

if __name__ == "__main__":
    main()
