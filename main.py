import random
from faker import Faker

fake = Faker()

# Predefined word banks for realism
ministry_prefixes = ["Ministry of", "Office of", "Department of", "Agency of"]
ministry_domains = ["Education", "Health", "Finance", "Technology", "Agriculture", "Defense", "Energy", "Environment", "Justice", "Transport", "Tourism", "Labor", "Foreign Affairs", "Science", "Culture"]

department_keywords = ["Division", "Bureau", "Unit", "Office", "Branch", "Section"]

def generate_google_map_script(entity_type, id):
    return f"<iframe src='https://maps.google.com/maps?q={entity_type}{id}&output=embed'></iframe>"

# Generate ministries with random names
def generate_ministries_query(num_ministries=100):
    ministries = []
    used_names = set()
    for i in range(1, num_ministries + 1):
        while True:
            prefix = random.choice(ministry_prefixes)
            domain = random.choice(ministry_domains)
            name = f"{prefix} {domain}"
            if name not in used_names:
                used_names.add(name)
                break
        script = generate_google_map_script("Ministry", i)
        ministries.append(f"({i}, '{name}', '{script}')")
    return "INSERT INTO ministries (id, name, google_map_script) VALUES\n" + ",\n".join(ministries) + ";\n"

# Generate departments with random names
def generate_departments_query(num_ministries=100, departments_per_ministry=10):
    departments = []
    dept_id = 1
    used_names = set()
    for ministry_id in range(1, num_ministries + 1):
        for _ in range(departments_per_ministry):
            while True:
                dept_type = random.choice(department_keywords)
                topic = fake.word().capitalize()
                name = f"{dept_type} of {topic}"
                if name not in used_names:
                    used_names.add(name)
                    break
            script = generate_google_map_script("Department", dept_id)
            departments.append(f"({dept_id}, '{name}', '{script}', {ministry_id})")
            dept_id += 1
    return "INSERT INTO departments (id, name, google_map_script, ministry_id) VALUES\n" + ",\n".join(departments) + ";\n"

def generate_full_sql():
    return generate_ministries_query() + "\n" + generate_departments_query()

# Save to file
with open("seed_data.sql", "w", encoding="utf-8") as f:
    f.write(generate_full_sql())

print("✅ SQL insert statements with random names saved to 'seed_data.sql'")
