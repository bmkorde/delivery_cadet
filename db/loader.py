import pandas as pd
from sqlalchemy import create_engine
from pathlib import Path

# MySQL connection string
engine = create_engine(
    "mysql+mysqlconnector://delivery_user:delivery_pass@127.0.0.1:3306/delivery_db",
    connect_args={
        "connection_timeout": 5,
        "use_pure": True
    }
)

def load_csv_to_db(csv_path):
    table_name = csv_path.stem  # filename without extension
    df = pd.read_csv(csv_path)
    df.to_sql(table_name, engine, if_exists='replace', index=False)
    print(f"Loaded {table_name} ({len(df)} rows)")

def load_all_csvs(folder="data"):
    folder_path = Path(folder)
    for csv_file in folder_path.glob("*.csv"):
        load_csv_to_db(csv_file)

if __name__ == "__main__":
    load_all_csvs()
