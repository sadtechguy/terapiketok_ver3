import psycopg2, os
from flask import redirect, url_for

DATABASE_NAME = os.getenv("DATABASE_NAME")
DATABASE_USER = os.getenv("DATABASE_USER")
DATABASE_PASSWORD = os.getenv("DATABASE_PASSWORD")

conn_string = f"dbname={DATABASE_NAME} user={DATABASE_USER} password={DATABASE_PASSWORD}"

class DatabaseProcess:
    def __init__(self):
        self.conn_string = conn_string
    
    def get_connection(self):
        try:
            return psycopg2.connect(self.conn_string)
        except psycopg2.DatabaseError as e:
            print(f"Error establishing a database connection: {e}")
    
    
    def close_connection(self, conn):
        try:
            conn.close()
        except Exception as e:
            print(f"Error closing connection: {e}")
    
    def delete_batch_by_id(self, batch_id):
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                try:
                    cur.execute(f"SELECT COUNT(*) FROM booking_tickets WHERE batch_id = %s", (batch_id,))
                    
                    num_bookings = cur.fetchone()[0]
                    if num_bookings > 0:
                        return num_bookings

                    # No associated bookings, proceed with deletion
                    cur.execute("DELETE FROM batches WHERE batch_id = %s", (batch_id,))
                    conn.commit()
                    return cur.fetchone()[0]

                except (psycopg2.OperationalError, psycopg2.ProgrammingError) as e:
                    raise Exception(f"Database error: {e}")
                except Exception as e:
                    raise Exception(f"Unknown error: {e}")
            return -1
        finally:
            self.close_connection(conn)
    
    def delete_batch_by_id_with_tickets(self, batch_id):
        try:
            conn = self.get_connection()
            with conn.cursor() as cur:
                try:
                    cur.execute("DELETE FROM booking_tickets WHERE batch_id = %s", (batch_id,))
                    cur.execute("DELETE FROM batches WHERE batch_id = %s", (batch_id,))

                    conn.commit()
                    return True

                except (psycopg2.OperationalError, psycopg2.ProgrammingError) as e:
                    raise Exception(f"Database error: {e}")
                except Exception as e:
                    raise Exception(f"Unknown error: {e}")
            return False
        
        finally:
            self.close_connection(conn)
