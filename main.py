import random
import os
import time
import psycopg2
from dotenv import load_dotenv
from faker import Faker
import matplotlib.pyplot as plt
import math

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
        base_name = f"{random.choice(ministry_prefixes)} {random.choice(ministry_domains)}"
        unique_name = f"{base_name} #{i}"  # use id to guarantee uniqueness
        script = generate_google_map_script("Ministry", i)
        ministries.append((i, unique_name, script))
    return ministries

def generate_departments(ministries, departments_per_ministry):
    departments = []
    dept_id = 1
    for ministry in ministries:
        for _ in range(departments_per_ministry):
            base_name = f"{random.choice(department_keywords)} of {fake.word().capitalize()}"
            unique_name = f"{base_name} #{dept_id}"  # use id to guarantee uniqueness
            script = generate_google_map_script("Department", dept_id)
            departments.append((dept_id, unique_name, script, ministry[0]))
            dept_id += 1
    return departments

def upload_to_postgresql(ministries, departments, batch_size=50, sleep_time=0.2):
    def chunked_upload(data, insert_query, is_ministry=True):
        total = len(data)
        for i in range(0, total, batch_size):
            batch = data[i:i + batch_size]
            try:
                conn = psycopg2.connect(DATABASE_URL)
                cursor = conn.cursor()
                cursor.executemany(insert_query, batch)
                conn.commit()
                cursor.close()
                conn.close()
                label = "Ministry" if is_ministry else "Department"
                print(f"✅ Uploaded {label} batch {i // batch_size + 1} / {math.ceil(total / batch_size)}")
                time.sleep(sleep_time)
            except psycopg2.OperationalError as e:
                print(f"❌ Failed to upload batch {i // batch_size + 1}: {e}")
                break  # or retry if you want

    print("\n⏫ Uploading Ministries in Batches...")
    chunked_upload(ministries, """
        INSERT INTO ministry (id, name, google_map_script)
        VALUES (%s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, is_ministry=True)

    print("\n⏫ Uploading Departments in Batches...")
    chunked_upload(departments, """
        INSERT INTO department (id, name, google_map_script, ministry_id)
        VALUES (%s, %s, %s, %s)
        ON CONFLICT (id) DO NOTHING;
    """, is_ministry=False)

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
