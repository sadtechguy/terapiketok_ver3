import psycopg2, os, datetime

from dotenv import load_dotenv

# from flask import current_app
# conn_string = current_app.config["SQLALCHEMY_DATABASE_URI"]
DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

conn_string = f"dbname={DATABASE_NAME} user={DATABASE_USER} password={DATABASE_PASSWORD}"

def fetch_available_batch(start_date):
    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    SELECT batch_date, day_name_ina, schedule_id, schedule_name, 
                        start_time, end_time, max_tickets, current_tickets, status 
                            FROM batches 
                            JOIN workingdays USING (day_id)
                            JOIN schedule USING (schedule_id)
                            WHERE batch_date >= %s
                            ORDER BY batch_date, schedule_id
                """,(start_date,))
                rows = cur.fetchall()
                return rows
    except (psycopg2.Error, ValueError) as e:
        raise Exception(f"Error fetching the data")
    return []

def fetct_queue_number(batch_id):
    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("SELECT ROW_NUMBER() OVER (PARTITION BY batch_id ORDER BY created_at ASC) AS queue_number, ticket_uid FROM booking_tickets WHERE batch_id=%s", (batch_id,))

                queue_number = cur.fetchall()
                if queue_number:
                    return queue_number
                else:
                    return []
    
    except (psycopg2.OperationalError, psycopg2.ProgrammingError) as e:
        print(f"Error connecting to database: {e}")  # Print the original error
        raise Exception(f"Error fetching queue number: {e}")
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
                cur.execute("INSERT INTO booking_tickets (ticket_uid, batch_id, appointment_date, customer_name, phone) VALUES (%s,%s,%s,%s,%s)", (ticket_uid, batch_id, appointment_date, username, phone))
                cur.execute("COMMIT")
                
                return True, "Booking created succesfully"

    except psycopg2.OperationalError as e:
        raise Exception(f"Database error: {e}")
    except psycopg2.ProgrammingError as e:
        raise Exception(f"Invalid SQL query: {e}")
    except Exception as e:
        raise Exception(f"Unknown error: {e}")
    return False, "Failed to create booking"

def add_new_admin(username, hashed_password):
    count = 0
    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute("""
                    INSERT INTO adminuser (username, hashed_password)
                    VALUES (%s, %s)
                """, (username, hashed_password))

                conn.commit()
                count = cur.rowcount
                
    
    except psycopg2.OperationalError as e:
        raise Exception(f"Database error: {e}")
    except psycopg2.ProgrammingError as e:
        raise Exception(f"Invalid SQL query: {e}")
    except Exception as e:
        raise Exception(f"Unknown error: {e}")
    
    return count

def add_default_batch(capacity, booking_limit, num_batches, batch_scedules):
    count = 0
    new_values = [capacity, booking_limit, num_batches] + batch_scedules
    column_names = ["capacity", "booking_limit", "number_of_batches"]
    for i, schdules in enumerate( batch_scedules):
        column_names.append(f"batch{i+1}")
    
    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                columns = ', '.join([f"{column}" for column in column_names])
                values_con = ','.join(["%s" for column in column_names])

                sql = f"""
                    INSERT INTO default_batch ({columns})
                    VALUES ({values_con})
                """
                
                cur.execute(sql, new_values)

                conn.commit()
                count = cur.rowcount
                
    
    except psycopg2.OperationalError as e:
        raise Exception(f"Database error: {e}")
    except psycopg2.ProgrammingError as e:
        raise Exception(f"Invalid SQL query: {e}")
    except Exception as e:
        raise Exception(f"Unknown error: {e}")
    
    return count

def update_default_batch(capacity, booking_limit, num_batches, batch_scedules):
    new_values = [capacity, booking_limit, num_batches] + batch_scedules

    sql = f"""
        UPDATE default_batch
        SET capacity = %s, booking_limit = %s, number_of_batches = %s,
            {", ".join(f"batch{i+1} = %s" for i in range(len(batch_scedules)))}
        WHERE default_batch_id = 1
    """
    
    try:
        with psycopg2.connect(conn_string) as conn:
            with conn.cursor() as cur:
                cur.execute(sql, new_values)

                conn.commit()
                return cur.rowcount
                
    
    except (psycopg2.OperationalError, psycopg2.ProgrammingError) as e:
        raise Exception(f"Database error: {e}")
    except Exception as e:
        raise Exception(f"Unknown error: {e}")
    

