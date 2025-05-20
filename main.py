import random
import os
import time
import psycopg2
from dotenv import load_dotenv
from faker import Faker
import matplotlib.pyplot as plt

# Load DB credentials
load_dotenv()
DATABASE_URL = os.getenv("DATABASE_URL")

fake = Faker()

# Word lists
ministry_prefixes = ["Ministry of", "Office of", "Department of", "Agency of"]
ministry_domains = ["Education", "Health", "Finance", "Technology", "Agriculture", "Defense", "Energy", "Environment", "Justice", "Transport", "Tourism", "Labor", "Foreign Affairs", "Science", "Culture"]
department_keywords = ["Division", "Bureau", "Unit", "Office", "Branch", "Section"]

def generate_google_map_script(entity_type, id):
    return f"<iframe src='https://maps.google.com/maps?q={entity_type}{id}&output=embed'></iframe>"

def generate_ministries(num_ministries):
    ministries = []
    for i in range(1, num_ministries + 1):
        name = f"{random.choice(ministry_prefixes)} {random.choice(ministry_domains)} #{random.randint(1000, 9999)}"
        script = generate_google_map_script("Ministry", i)
        ministries.append((i, name, script))
    return ministries

def generate_departments(ministries, departments_per_ministry):
    departments = []
    dept_id = 1
    for ministry in ministries:
        for _ in range(departments_per_ministry):
            name = f"{random.choice(department_keywords)} of {fake.word().capitalize()} #{random.randint(1000, 9999)}"
            script = generate_google_map_script("Department", dept_id)
            departments.append((dept_id, name, script, ministry[0]))
            dept_id += 1
    return departments

def upload_to_postgresql(ministries, departments):
    conn = psycopg2.connect(DATABASE_URL)
    cursor = conn.cursor()

    for m in ministries:
        cursor.execute("""
            INSERT INTO ministry (id, name, google_map_script)
            VALUES (%s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, m)

    for d in departments:
        cursor.execute("""
            INSERT INTO department (id, name, google_map_script, ministry_id)
            VALUES (%s, %s, %s, %s)
            ON CONFLICT (id) DO NOTHING;
        """, d)

    conn.commit()
    cursor.close()
    conn.close()

def main():
    results = []

    while True:
        try:
            num_ministries = int(input("\n🔢 Enter number of ministries to generate: "))
            departments_per_ministry = int(input("🔢 Enter number of departments per ministry: "))
        except ValueError:
            print("❌ Please enter valid integer values.")
            continue

        print("🚀 Generating data...")
        ministries = generate_ministries(num_ministries)
        departments = generate_departments(ministries, departments_per_ministry)
        print(f"✅ Generated {len(ministries)} ministries and {len(departments)} departments.")

        print("📤 Uploading to PostgreSQL...")
        start_time = time.time()
        upload_to_postgresql(ministries, departments)
        end_time = time.time()

        elapsed_time = round(end_time - start_time, 2)
        config_label = f"{num_ministries}M x {departments_per_ministry}D"
        results.append((config_label, elapsed_time))

        print(f"✅ Upload completed in {elapsed_time} seconds.")

        cont = input("\n🔁 Do you want to run another test? (y/n): ").strip().lower()
        if cont != 'y':
            break

    # Plot results
    print("\n📊 Plotting performance graph...")
    labels = [r[0] for r in results]
    times = [r[1] for r in results]

    plt.figure(figsize=(10, 6))
    plt.bar(labels, times, color='skyblue')
    plt.xlabel("Records (Ministries x Departments)")
    plt.ylabel("Upload Time (seconds)")
    plt.title("Upload Time vs Number of Records to PostgreSQL (Neon)")
    plt.xticks(rotation=45, ha="right")
    plt.tight_layout()
    plt.grid(True, axis='y', linestyle='--', alpha=0.7)
    plt.show()

if __name__ == "__main__":
    main()
