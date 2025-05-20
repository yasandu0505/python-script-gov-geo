import random
from faker import Faker

fake = Faker()

# Vocabulary for random names
ministry_prefixes = ["Ministry of", "Office of", "Department of", "Agency of"]
ministry_domains = ["Education", "Health", "Finance", "Technology", "Agriculture", "Defense", "Energy", "Environment", "Justice", "Transport", "Tourism", "Labor", "Foreign Affairs", "Science", "Culture"]
department_keywords = ["Division", "Bureau", "Unit", "Office", "Branch", "Section"]

# Escape single quotes for SQL
def escape_quotes(s):
    return s.replace("'", "''")

# Simple Google Maps placeholder
def generate_google_map_script(entity_type, id):
    return f"<iframe src='https://maps.google.com/maps?q={entity_type}{id}&output=embed'></iframe>"

# Generate ministries
def generate_ministries(num_ministries=100):
    ministries = []
    for i in range(1, num_ministries + 1):
        name = f"{random.choice(ministry_prefixes)} {random.choice(ministry_domains)}"
        script = generate_google_map_script("Ministry", i)
        ministries.append((i, escape_quotes(name), escape_quotes(script)))
    return ministries

# Generate departments
def generate_departments(ministries, departments_per_ministry=10):
    departments = []
    dept_id = 1
    for ministry in ministries:
        ministry_id = ministry[0]
        for _ in range(departments_per_ministry):
            name = f"{random.choice(department_keywords)} of {fake.word().capitalize()}"
            script = generate_google_map_script("Department", dept_id)
            departments.append((dept_id, escape_quotes(name), escape_quotes(script), ministry_id))
            dept_id += 1
    return departments

# Build SQL statements
def generate_sql(ministries, departments):
    ministry_sql = "INSERT INTO ministries (id, name, google_map_script) VALUES\n" + ",\n".join(
        [f"({m[0]}, '{m[1]}', '{m[2]}')" for m in ministries]
    ) + ";\n"

    department_sql = "INSERT INTO departments (id, name, google_map_script, ministry_id) VALUES\n" + ",\n".join(
        [f"({d[0]}, '{d[1]}', '{d[2]}', {d[3]})" for d in departments]
    ) + ";\n"

    return ministry_sql + "\n" + department_sql

# Main execution
def main():
    print("🚀 Generating ministries and departments...")
    ministries = generate_ministries()
    print(f"✅ Generated {len(ministries)} ministries")
    departments = generate_departments(ministries)
    print(f"✅ Generated {len(departments)} departments")
    sql_output = generate_sql(ministries, departments)

    with open("seed_data.sql", "w", encoding="utf-8") as f:
        f.write(sql_output)

    print("📄 SQL data saved to 'seed_data.sql'")

if __name__ == "__main__":
    main()
