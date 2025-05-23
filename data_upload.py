import pandas as pd
from sqlalchemy import create_engine

# Your Neon PostgreSQL connection URL
DATABASE_URL = "postgresql://neondb_owner:npg_BFLav10SQDoy@ep-billowing-pond-a50tgmix-pooler.us-east-2.aws.neon.tech/neondb?sslmode=require"

# Load the CSV files
ministries_df = pd.read_csv("./csv_output/ministries.csv")
departments_df = pd.read_csv("./csv_output/departments.csv")

# Create SQLAlchemy engine
engine = create_engine(DATABASE_URL)

# Insert data into the ministries table
ministries_df.to_sql("ministries", engine, if_exists="append", index=False)

# Insert data into the departments table
departments_df.to_sql("departments", engine, if_exists="append", index=False)

print("Data imported successfully.")
