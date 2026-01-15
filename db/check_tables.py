from sqlalchemy import create_engine, text

engine = create_engine(
    "mysql+mysqlconnector://delivery_user:delivery_pass@127.0.0.1:3306/delivery_db"
)

with engine.connect() as conn:
    result = conn.execute(text("SHOW TABLES"))
    print("📋 Tables:")
    for row in result:
        print("-", row[0])

    result = conn.execute(text("SELECT COUNT(*) FROM sales_customers"))
    print("📊 Rows in sales_customers:", result.fetchone()[0])
