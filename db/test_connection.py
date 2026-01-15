print("🚀 test_connection.py started")

from sqlalchemy import create_engine, text

engine = create_engine(
    "mysql+mysqlconnector://delivery_user:delivery_pass@127.0.0.1:3306/delivery_db",
    connect_args={
        "connection_timeout": 5,
        "use_pure": True
    }
)

try:
    with engine.connect() as conn:
        result = conn.execute(text("SELECT 1"))
        print("✅ Connected to MySQL successfully!")
except Exception as e:
    print("❌ Connection failed:")
    print(e)

print("🏁 test_connection.py finished")
