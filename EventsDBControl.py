import sqlite3

class EventDatabase:
    def __init__(self, db_path='db/my_database.db'):
        self.connection = sqlite3.connect(db_path)
        self.cursor = self.connection.cursor()

    def get_event_by_id(self, event_id):
        try:
            self.cursor.execute("SELECT * FROM event WHERE event_id = ?", (event_id,))
            return self.cursor.fetchone()
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    def get_event_id_by_name(self, event_name):
        try:
            self.cursor.execute("SELECT event_id FROM event WHERE event_name = ?", (event_name,))
            result = self.cursor.fetchone()
            return result[0] if result else None  # Return None if not found
        except sqlite3.Error as e:
            print(f"Database error: {e}")
            return None
    def add_event(self, event_name, event_date, event_time, event_budget, event_is_active):
        try:
            self.cursor.execute("""
                INSERT INTO event (event_name, event_date, event_time, event_budget, event_is_active)
                VALUES (?, ?, ?, ?, ?)
            """, (event_name, event_date, event_time, event_budget, event_is_active))
            self.connection.commit()
            return True
        except sqlite3.Error as e:
            print(f"Database error in add_event: {e}")
            return False

    def delete_event(self, event_id):
        try:
            self.cursor.execute("DELETE FROM event WHERE event_id = ?", (event_id,)) # Исправлено: event вместо events
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Database error in delete_event: {e}")
            return False # Добавлено возвращение False для обработки ошибки

    def count_events_by_date(self, event_date):
        try:
            self.cursor.execute("SELECT COUNT(*) FROM event WHERE event_date = ?", (event_date,))
            result = self.cursor.fetchone()
            return result[0]
        except sqlite3.Error as e:
            print(f"Database error in count_events_by_date: {e}")
            return 0

    def update_event(self, event_id, event_name, event_date, event_time, event_budget, event_is_active):
        try:
            self.cursor.execute("""
                   UPDATE event
                   SET event_name = ?, event_date = ?, event_time = ?, event_budget = ?, event_is_active = ?
                   WHERE event_id = ?
               """, (event_name, event_date, event_time, event_budget, event_is_active, event_id))
            self.connection.commit()
        except sqlite3.Error as e:
            print(f"Database error in update_event: {e}")

    def get_events_by_status(self, is_active):
        try:
            self.cursor.execute("SELECT * FROM event WHERE event_is_active = ?", (is_active,))
            return self.cursor.fetchall()
        except sqlite3.Error as e:
            print(f"Database error in get_events_by_status: {e}")
            return []

    def close(self):
        self.cursor.close() #Close the cursor first
        self.connection.close() #Then close the connection