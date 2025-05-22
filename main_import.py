import random
import csv
from faker import Faker
import pandas as pd
from sqlalchemy import create_engine
import os
import time
import matplotlib.pyplot as plt
from dotenv import load_dotenv


# Initialize Faker
fake = Faker()

# Load environment variables
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")
if not DATABASE_URL:
    raise ValueError("❌ DATABASE_URL is not set in the .env file")


# Vocabulary for random names
ministry_prefixes = ["Ministry of"]
ministry_domains = ["Education", "Health", "Finance", "Technology", "Agriculture", "Defense", "Energy", "Environment", "Justice", "Transport", "Tourism", "Labor", "Foreign Affairs", "Science", "Culture"]
department_keywords = ["Department of"]

def escape_quotes(s):
    return s.replace("'", "''")

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

def write_csv(filename, data, headers):
    os.makedirs(os.path.dirname(filename), exist_ok=True)
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)

def import_to_neon():
    try:
        engine = create_engine(DATABASE_URL)
        ministries_df = pd.read_csv("csv_output/ministries.csv")
        departments_df = pd.read_csv("csv_output/departments.csv")
        ministries_df.to_sql("ministry", engine, if_exists="append", index=False)
        departments_df.to_sql("department", engine, if_exists="append", index=False)
    except Exception as e:
        print("❌ Error while importing to Neon:", e)

def plot_results(results):
    plt.figure(figsize=(10, 6))
    for dept_count in sorted(set(r[1] for r in results)):
        x = [r[0] for r in results if r[1] == dept_count]
        y = [r[2] for r in results if r[1] == dept_count]
        plt.plot(x, y, marker='o', label=f'{dept_count} departments/ministery')

    plt.title("📊 Neon Import Time vs. Number of Ministries")
    plt.xlabel("Number of Ministries")
    plt.ylabel("Import Time (s)")
    plt.legend(title="Departments/Ministry")
    plt.grid(True)
    plt.tight_layout()
    plt.show()

def main():
    try:
        ministry_input = input("\n🔢 Enter comma-separated ministry counts to test (e.g. 10,20,30): ")
        dept_input = input("🔢 Enter comma-separated department counts to test (e.g. 2,5,10): ")

        ministry_counts = [int(x.strip()) for x in ministry_input.split(',')]
        department_counts = [int(x.strip()) for x in dept_input.split(',')]
    except ValueError:
        print("❌ Invalid input. Please enter comma-separated integers.")
        return

    results = []

    for num_ministries in ministry_counts:
        for departments_per_ministry in department_counts:
            print(f"\n🧪 Testing with {num_ministries} ministries and {departments_per_ministry} departments each...")

            ministries = generate_ministries(num_ministries)
            departments = generate_departments(ministries, departments_per_ministry)

            write_csv("csv_output/ministries.csv", ministries, ["id", "name", "google_map_script"])
            write_csv("csv_output/departments.csv", departments, ["id", "name", "google_map_script", "ministry_id"])

            start_time = time.time()
            import_to_neon()
            end_time = time.time()

            duration = round(end_time - start_time, 2)
            print(f"⏱️ Import time: {duration} seconds")
            results.append((num_ministries, departments_per_ministry, duration))

            # Ask user whether to continue or stop
            decision = input("🛑 Do you want to stop here and see the results? (y/n): ").strip().lower()
            if decision == "y":
                print("\n📊 Generating performance graph...")
                plot_results(results)
                return

    print("\n✅ All tests completed. Generating graph...")
    plot_results(results)

if __name__ == "__main__":
    main()
