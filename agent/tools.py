from sqlalchemy import create_engine, inspect
from sqlalchemy import text




engine = create_engine(
    "mysql+mysqlconnector://delivery_user:delivery_pass@127.0.0.1:3306/delivery_db",
    connect_args={
        "connection_timeout": 5,
        "use_pure": True
    }
)

def forbid_non_mysql(sql: str):
    forbidden = ["QUALIFY", "FILTER", "ARRAY_AGG"]
    for word in forbidden:
        if word.lower() in sql.lower():
            return {
                "error": f"Forbidden MySQL syntax detected: {word}",
                "sql": sql
            }
    return None

def get_schema():
    inspector = inspect(engine)
    schema_info = {}
    for table_name in inspector.get_table_names():
        schema_info[table_name] = [col['name'] for col in inspector.get_columns(table_name)]
    return schema_info

def clean_sql(sql: str) -> str:
    
    if not sql:
        return sql

    sql = sql.strip()

    
    if sql.startswith("```"):
        sql = sql.replace("```sql", "")
        sql = sql.replace("```", "")

    return sql.strip()


def run_sql(query: str):
    try:
        forbidden_error = forbid_non_mysql(query)
        if forbidden_error:
             return forbidden_error
        clean_query = clean_sql(query)

        with engine.connect() as conn:
            print("\n================ EXECUTING SQL ================\n")
            print(clean_query)
            print("\n===============================================\n")

            result = conn.execute(text(clean_query))
            columns = result.keys()
            rows = [dict(zip(columns, r)) for r in result.fetchall()]

        # Mask any personal names
        masked = [
            {k: "***" if "name" in k.lower() else v for k, v in row.items()}
            for row in rows
        ]

        return {
            "success": True,
            "data": masked,
            "row_count": len(masked)
        }

    except ValueError as e:
        # SQL dialect violation (QUALIFY etc.)
        return {
            "success": False,
            "type": "SQL_DIALECT_ERROR",
            "error": str(e),
            "sql": query
        }

    except Exception as e:
        # Any DB / execution error
        return {
            "success": False,
            "type": "SQL_EXECUTION_ERROR",
            "error": str(e),
            "sql": query
        }