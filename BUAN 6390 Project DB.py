# BUAN 6390 Project DB
# pip install psycopg2-binary (use this to install postgresql driver)
# pip install pandas pyarrow (convert csv to paraquet)
import os
import psycopg2
import pyarrow
import pandas as pd
import numpy as np
from pathlib import Path  

os.chdir(r"E:/School Project Data") #set working directory

df = pd.read_csv(r"E:/School Project Data/Project_Data.csv", encoding="latin1")  # Load file that contains NYC and Austin filtered data
df['zip_code'] = df['zip_code'].astype(str)
df['billing_code'] = df['billing_code'].astype(str)
df['gross_charge'] = df['gross_charge'].replace({',': ''}, regex=True).astype(float)  # Remove commas
df['additional_generic_notes'] = df['additional_generic_notes'].astype(str)
df['hospital'] = df['hospital'].replace('Baylor Scott & White Medical Center â\x80\x93 Round Rock', 'Baylor Scott & White Medical Center Round Rock') #re-encodes messed up hospital name
#df.to_parquet("Project_Data.parquet", engine="pyarrow")

#region Build database schema
hospital_id_map = {
    "New York Presbyterian Queens": 1,
    "New York Presbyterian System": 3,
    "Newark-Wayne Community Hospital": 10,
    "Newark Beth Israel Medical Center": 11,
    "University Hospital": 12,
    "Saint Michaels Medical Center": 14,
    "Jersey City Medical Center": 15,
    "Saint Josephs Medical Center": 31,
    "Wayne Memorial Hospital": 33,
    "Ascension Seton Medical Center Austin": 16,
    "St. Davids North Austin Medical Center": 17,
    "Ascension Seton Northwest Hospital": 20,
    "Ascension Seton Shoal Creek": 26,
    "Dell Childrens Medical Center North Campus": 28,
    "Heart Hospital of Austin": 29,
    "Baylor Scott & White Medical Center Round Rock": 21,
    "St. Davids Round Rock Medical Center": 22,
    "Ascension Seton Williamson Hospital": 23
}
hospitals = df[['hospital', 'metroplex', 'state', 'zip_code']].drop_duplicates().reset_index(drop=True)
hospitals['hospital_PK'] = hospitals['hospital'].map(hospital_id_map)

billing_codes= df[['billing_code']].drop_duplicates().reset_index(drop=True)

procedures= df[['description','billing_code']].drop_duplicates().reset_index(drop=True)
procedures['procedure_id']= procedures.index + 1

payers = df[['payer_name', 'plan_name']].drop_duplicates().reset_index(drop=True)
payers['payer_plan_combo_id'] = payers.index + 1

charges_df= df.merge(hospitals, on=['hospital', 'metroplex', 'state', 'zip_code'], how='left')
charges_df = charges_df[[
    'hospital_PK','description', 'billing_code', 'payer_name', 'plan_name',
    'gross_charge', 'insurer_price', 'max_price', 'discounted_cash',
    'additional_generic_notes'
]]
charges_df= charges_df.merge(procedures[['billing_code', 'description', 'procedure_id']], on=['billing_code', 'description'], how='left')
charges_df = charges_df[[
    'procedure_id','hospital_PK', 'payer_name', 'plan_name',
    'gross_charge', 'insurer_price', 'max_price', 'discounted_cash',
    'additional_generic_notes'
]]
charges_df= charges_df.merge(payers[['payer_plan_combo_id','payer_name', 'plan_name']], on=['payer_name', 'plan_name'], how='left')
charges_df = charges_df[[
    'procedure_id','hospital_PK', 'payer_plan_combo_id',
    'gross_charge', 'insurer_price', 'max_price', 'discounted_cash',
    'additional_generic_notes'
]]
tables=['hospitals','billing_codes','procedures','payers','charges_df']
#endregion

#region Connect into Railway postgreSQL and upload tables
# https://railway.com/invite/YzF_ceHrzja (view-only)
conn = psycopg2.connect("postgresql://postgres:vbtyhCswCLNVvwsfKjRovjdXoiXAvbMz@nozomi.proxy.rlwy.net:51230/railway")
cur = conn.cursor()
tables = {
    "hospitals": {
        "schema": """
            CREATE TABLE IF NOT EXISTS hospitals (
                hospital_PK INTEGER PRIMARY KEY,
                hospital TEXT,
                metroplex TEXT,
                state TEXT,
                zip_code TEXT
            );
        """,
        "columns": ['hospital_PK', 'hospital', 'metroplex', 'state', 'zip_code'],
        "df": hospitals
    },
    "billing_codes": {
        "schema": """
            CREATE TABLE IF NOT EXISTS billing_codes (
                billing_code TEXT PRIMARY KEY
            );
        """,
        "columns": ['billing_code'],
        "df": billing_codes
    },
    "procedures": {
        "schema": """
            CREATE TABLE IF NOT EXISTS procedures (
                description TEXT,
                billing_code TEXT,
                procedure_id INTEGER PRIMARY KEY
            );
        """,
        "columns": ['description', 'billing_code','procedure_id'],
        "df": procedures
    },
        "payers": {
        "schema": """
            CREATE TABLE IF NOT EXISTS payers (
                payer_name TEXT,
                plan_name TEXT,
                payer_plan_combo_id TEXT PRIMARY KEY
            );
        """,
        "columns": ['payer_name', 'plan_name','payer_plan_combo_id'],
        "df": payers
    },
    "charges": {
        "schema": """
            CREATE TABLE IF NOT EXISTS charges (
                procedure_id INTEGER REFERENCES procedures(procedure_id),
                hospital_PK INTEGER REFERENCES hospitals(hospital_PK),
                payer_plan_combo_id TEXT REFERENCES payers(payer_plan_combo_id),
                gross_charge FLOAT,
                insurer_price FLOAT,
                max_price FLOAT,
                discounted_cash FLOAT,
                additional_generic_notes TEXT,
                PRIMARY KEY (procedure_id, hospital_PK, payer_plan_combo_id)
            );
        """,
        "columns": ['procedure_id', 'hospital_PK','payer_plan_combo_id', 'gross_charge', 'insurer_price',
                    'max_price', 'discounted_cash', 'additional_generic_notes'],
        "df": charges_df
    }
}
from psycopg2.extras import execute_values

for table_name, info in tables.items():
    print(f"Processing table: {table_name}")
    # Create table if it doesn't exist
    cur.execute(info["schema"])
    conn.commit()
    # Convert DataFrame to list of tuples
    rows = info["df"][info["columns"]].drop_duplicates().values.tolist()
    # Build insert query
    placeholders = ", ".join(info["columns"])
    insert_query = f"INSERT INTO {table_name} ({placeholders}) VALUES %s ON CONFLICT DO NOTHING"
    # Insert data
    execute_values(cur, insert_query, rows)
    conn.commit()

cur.close()
conn.close()

#endregion

#region download database tables from Railway as CSV
os.chdir(r"E:/School Project Data/database dump") #set desired working directory
conn = psycopg2.connect("postgresql://postgres:vbtyhCswCLNVvwsfKjRovjdXoiXAvbMz@nozomi.proxy.rlwy.net:51230/railway") #DATABASE_PUBLIC_URL on the Railway dashboard
output_dir = os.getcwd()
table_names = ['hospitals', 'billing_codes', 'procedures', 'payers', 'charges']
for table in table_names:
    print(f"Exporting {table}...")
    query = f"SELECT * FROM {table};"
    df = pd.read_sql_query(query, conn)
    output_path = os.path.join(output_dir, f"{table}_table.csv")
    df.to_csv(output_path, chunksize=1000000,index=False)
    print(f"{table} exported to {output_path}")
conn.close()
#endregion

# data analysis queries
check=df[(df['billing_code']=='85347') & (df['metroplex']=='NYC')& (df['insurer_price'].isnull())]
check[['hospital','description','payer_name','insurer_price','additional_generic_notes']].sort_values('insurer_price', ascending=True)

sorted(df['hospital'].unique())
check=df[(df['metroplex']=='Austin') & (df['hospital']=='Heart Hospital of Austin') & (df['billing_code']=='88271') & (df['insurer_price']>1)]
check[['hospital','description','billing_code','payer_name','insurer_price','additional_generic_notes']].sort_values('insurer_price', ascending=True)


