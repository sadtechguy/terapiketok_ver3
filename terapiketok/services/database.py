import psycopg2, os, datetime

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
                            ORDER BY batch_date, schedule_id
                """)
                rows = cur.fetchall()
                return rows
    except (psycopg2.Error, ValueError) as e:
        raise Exception(f"Error fetching the data")
    return []

def create_booking(batch_id, username, phone, appointment_date, ticket_uid):
    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("BEGIN TRANSACTION;")
                cur.execute("SELECT * FROM Batches WHERE batch_id = %s FOR UPDATE;", (batch_id,))
                batch = cur.fetchone()

                if batch[7] >= batch[6]:
                    conn.rollback()
                    return False,"Batch is full"
                
                # Check if the phone number has already booked a ticket for the batch's date
                cur.execute("SELECT COUNT(*) FROM booking_tickets WHERE phone=%s AND appointment_date=%s", (phone, appointment_date))
                existing_booking_count = cur.fetchone()[0]

                if existing_booking_count > 10:
                    conn.rollback()
                    return False, "No HP ini sudah tidak bisa booking lagi hari ini"
                
                cur.execute("UPDATE Batches SET current_tickets = current_tickets + 1 WHERE batch_id=%s", (batch_id,))
                
                # Insert booking data into the booking_tickets table
                cur.execute("INSERT INTO booking_tickets (ticket_uid, batch_id, appointment_date, customer_name, phone) VALUES (%s,%s,%s,%s, %s)", (ticket_uid, batch_id, appointment_date, username, phone))
                cur.execute("COMMIT")
                
                return True, "Booking created succesfully"

    except (psycopg2.Error, ValueError) as e:
        raise Exception(f"Error fetching the data")
    return False, "Failed to create booking"