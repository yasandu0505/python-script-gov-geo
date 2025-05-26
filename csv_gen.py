import random
import csv
from faker import Faker

fake = Faker()

# Vocabulary for random names
ministry_prefixes = ["Ministry of"]
ministry_domains = ["Education", "Health", "Finance", "Technology", "Agriculture", "Defense", "Energy", "Environment", "Justice", "Transport", "Tourism", "Labor", "Foreign Affairs", "Science", "Culture"]
department_keywords = ["Department of"]

# Escape single quotes for safe CSV
def escape_quotes(s):   
    return s.replace("'", "''")

# Simple Google Maps placeholder
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
    with open(filename, mode='w', newline='', encoding='utf-8') as f:
        writer = csv.writer(f)
        writer.writerow(headers)
        writer.writerows(data)
    print(f"📄 Data saved to '{filename}'")

# Main execution
def main():
    try:
        num_ministries = int(input("🔢 Enter number of ministries to generate: "))
        departments_per_ministry = int(input("🔢 Enter number of departments per ministry: "))
    except ValueError:
        print("❌ Please enter valid integer values.")
        return

    print("🚀 Generating ministries and departments...")
    ministries = generate_ministries(num_ministries)
    departments = generate_departments(ministries, departments_per_ministry)

    print(f"✅ Generated {len(ministries)} ministries")
    print(f"✅ Generated {len(departments)} departments")

    write_csv("csv_output/ministries.csv", ministries, ["id", "name", "google_map_script"])
    write_csv("csv_output/departments.csv", departments, ["id", "name", "google_map_script", "ministry_id"])

if __name__ == "__main__":
    main()
