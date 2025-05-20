import random

# Helper function to generate dummy Google Maps embed script
def generate_google_map_script(entity_type, id):
    return f"<iframe src='https://maps.google.com/maps?q={entity_type}{id}&output=embed'></iframe>"

# Generate INSERT queries for Ministries
def generate_ministries_query(num_ministries=100):
    ministries = []
    for i in range(1, num_ministries + 1):
        name = f"Ministry {i}"
        script = generate_google_map_script("Ministry", i)
        ministries.append(f"({i}, '{name}', '{script}')")
    query = "INSERT INTO ministries (id, name, google_map_script) VALUES\n" + ",\n".join(ministries) + ";\n"
    return query

# Generate INSERT queries for Departments
def generate_departments_query(num_ministries=100, departments_per_ministry=10):
    departments = []
    dept_id = 1
    for ministry_id in range(1, num_ministries + 1):
        for j in range(1, departments_per_ministry + 1):
            name = f"Department {dept_id}"
            script = generate_google_map_script("Department", dept_id)
            departments.append(f"({dept_id}, '{name}', '{script}', {ministry_id})")
            dept_id += 1
    query = "INSERT INTO departments (id, name, google_map_script, ministry_id) VALUES\n" + ",\n".join(departments) + ";\n"
    return query

# Output the full SQL
def generate_full_sql():
    ministry_sql = generate_ministries_query()
    department_sql = generate_departments_query()
    full_sql = ministry_sql + "\n" + department_sql
    return full_sql

# Save to file
with open("seed_data.sql", "w", encoding="utf-8") as f:
    f.write(generate_full_sql())

print("✅ SQL insert statements saved to 'seed_data.sql'")
