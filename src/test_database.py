from database import get_connection


print("Testing reusable database connection...")

try:
    with get_connection() as connection:
        print("✅ Connected to PostgreSQL!")

        with connection.cursor() as cursor:
            cursor.execute("SELECT current_database();")
            database = cursor.fetchone()[0]

            cursor.execute("SELECT COUNT(*) FROM customers;")
            customer_count = cursor.fetchone()[0]

        print("Database:", database)
        print("Customers:", customer_count)

except Exception as error:
    print("❌ Connection failed:")
    print(repr(error))