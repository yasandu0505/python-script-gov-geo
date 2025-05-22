import random
import csv
import os
import time
import pandas as pd
from faker import Faker
from sqlalchemy import create_engine, text
from dotenv import load_dotenv
import matplotlib.pyplot as plt

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

# Initialize Faker
fake = Faker()

# Vocabulary
ministry_prefixes = ["Ministry of"]
ministry_domains = ["Education", "Health", "Finance", "Technology", "Agriculture", "Defense", "Energy", "Environment", "Justice", "Transport", "Tourism", "Labor", "Foreign Affairs", "Science", "Culture"]
department_keywords = ["Department of"]

# Track performance
performance_log = []

def escape_quotes(s):
    return s.replace("'", "''")

def generate_google_map_script(entity_type, id):
    return f"<iframe src='https://maps.google.com/maps?q={entity_type}{id}&output=embed'></iframe>"

def generate_ministries(num_ministries):
    return [(i, escape_quotes(f"{random.choice(ministry_prefixes)} {random.choice(ministry_domains)} - {i}"),
             escape_quotes(generate_google_map_script("Ministry", i)))
            for i in range(1, num_ministries + 1)]

def generate_departments(ministries, departments_per_ministry):
    departments = []
    dept_id = 1
    for ministry in ministries:
        for _ in range(departments_per_ministry):
            name = f"{random.choice(department_keywords)} of {fake.word().capitalize()} - {dept_id}"
            script = generate_google_map_script("Department", dept_id)
            departments.append((dept_id, escape_quotes(name), escape_quotes(script), ministry[0]))
            dept_id += 1
    return departments

def write_csv(filename, data, headers):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, 'w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    print(f"📄 Data saved to '{filename}'")

def import_to_neon():
    try:
        print("🚚 Importing data to Neon...")
        engine = create_engine(DATABASE_URL)
        start_time = time.time()

        ministries_df = pd.read_csv("csv_output/ministries.csv")
        departments_df = pd.read_csv("csv_output/departments.csv")

        ministries_df.to_sql("ministry", engine, if_exists="append", index=False)
        departments_df.to_sql("department", engine, if_exists="append", index=False)

        duration = time.time() - start_time
        print(f"✅ Data imported in {round(duration, 2)} seconds.")
        return duration

    except Exception as e:
        print("❌ Import error:", e)
        return None

def clear_neon_tables():
    try:
        engine = create_engine(DATABASE_URL)
        with engine.connect() as conn:
            conn.execute(text("TRUNCATE TABLE department, ministry RESTART IDENTITY CASCADE;"))
            print("🧹 Tables truncated successfully.")
    except Exception as e:
        print("❌ Error while truncating tables:", e)

def plot_performance(log):
    x = [f"{m}M-{d}D" for m, d, _ in log]
    y = [t for _, _, t in log]

    plt.figure(figsize=(10, 5))
    plt.plot(x, y, marker='o', linestyle='-', color='blue')
    plt.title("Neon Import Time vs. Data Size")
    plt.xlabel("Ministries - Departments")
    plt.ylabel("Import Time (seconds)")
    plt.grid(True)
    plt.xticks(rotation=45)
    plt.tight_layout()
    plt.show()

def main():
    while True:
        try:
            num_ministries = int(input("\n🔢 Enter number of ministries to generate: "))
            departments_per_ministry = int(input("🔢 Enter number of departments per ministry: "))
        except ValueError:
            print("❌ Invalid input. Please enter integers.")
            continue

        print("\n🚀 Generating ministries and departments...")
        ministries = generate_ministries(num_ministries)
        departments = generate_departments(ministries, departments_per_ministry)

        write_csv("csv_output/ministries.csv", ministries, ["id", "name", "google_map_script"])
        write_csv("csv_output/departments.csv", departments, ["id", "name", "google_map_script", "ministry_id"])

        duration = import_to_neon()
        if duration:
            performance_log.append((num_ministries, departments_per_ministry, duration))

        clear_neon_tables()

        choice = input("\n🔁 Do you want to run another test? (y/n): ").lower()
        if choice != 'y':
            break

    print("\n📈 Plotting performance chart...")
    plot_performance(performance_log)

if __name__ == "__main__":
    main()
