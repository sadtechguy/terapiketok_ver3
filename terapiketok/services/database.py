import psycopg2, os

from dotenv import load_dotenv

# from flask import current_app
# conn_string = current_app.config["SQLALCHEMY_DATABASE_URI"]
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

conn_string = f"dbname={DATABASE_NAME} user={DATABASE_USER} password={DATABASE_PASSWORD}"

def fetch_available_batch():
    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT batch_date, day_name_ina, schedule_id, schedule_name, 
                        start_time, end_time, max_tickets, current_tickets, status 
                            FROM batches 
                            JOIN workingdays USING (day_id)
                            JOIN schedule USING (schedule_id)
                """)
                rows = cur.fetchall()
                return rows
    except (psycopg2.Error, ValueError) as e:
        raise Exception(f"Error fetching the data")
    return []
