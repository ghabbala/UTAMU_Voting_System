# database.py
import sqlite3
import os
from datetime import datetime


DB_NAME = "voting_system.db"


class DatabaseManager:
    def __init__(self):
        self.conn = sqlite3.connect(DB_NAME)
        self.create_tables()

    def create_tables(self):
        cur = self.conn.cursor()

        # Students table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS students (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                username TEXT UNIQUE,
                regno TEXT UNIQUE,
                password TEXT,
                has_voted INTEGER DEFAULT 0
            )
        ''')

        # Admin table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS admins (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                username TEXT UNIQUE,
                password TEXT
            )
        ''')

        # Candidates table (with photo)
        cur.execute('''
            CREATE TABLE IF NOT EXISTS candidates (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT,
                position TEXT,
                photo TEXT,
                logo_path TEXT,
                votes INTEGER DEFAULT 0
            )
        ''')

        # Duration settings table
        cur.execute('''
            CREATE TABLE IF NOT EXISTS voting_settings (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                start_time TEXT,
                end_time TEXT
            )
        ''')

                # Create default admin if none exists
        cur.execute("SELECT * FROM admins")
        if not cur.fetchone():
            cur.execute("INSERT INTO admins (username, password) VALUES (?, ?)", ("admin", "admin123"))
            self.conn.commit()




          # ---------- STUDENT OPERATIONS ----------
    def register_student(self, name, username, regno, password):
        conn = sqlite3.connect(DB_NAME)
        cur = conn.cursor()
        cur.execute("""
            INSERT INTO students (name, username, regno, password)
            VALUES (?, ?, ?, ?)
        """, (name, username, regno, password))
        conn.commit()
        conn.close()

    def verify_student(self, username, password):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM students WHERE username=? AND password=?",
                    (username, password))
        return cur.fetchone()

    def mark_student_voted(self, regno):
        cur = self.conn.cursor()
        cur.execute("UPDATE students SET has_voted=1 WHERE regno=?", (regno,))
        self.conn.commit()

    def student_has_voted(self, regno):
        cur = self.conn.cursor()
        cur.execute("SELECT has_voted FROM students WHERE regno=?", (regno,))
        row = cur.fetchone()
        return row and row[0] == 1

    # ---------- CANDIDATE OPERATIONS ----------
    def add_candidate(self, name, position, photo_path=None, logo_path=None):
        # Convert to absolute paths if provided
        if photo_path:
            photo_path = os.path.abspath(photo_path)
        if logo_path:
            logo_path = os.path.abspath(logo_path)

        cur = self.conn.cursor()
        cur.execute(
            "INSERT INTO candidates (name, position, photo, logo_path) VALUES (?, ?, ?, ?)",
            (name, position, photo_path, logo_path),
        )
        self.conn.commit()


    def update_candidate(self, candidate_id, name, position, photo_path, logo_path):
        """Update all registration details of a candidate."""
        # Convert to absolute paths if provided
        if photo_path:
            photo_path = os.path.abspath(photo_path)
        if logo_path:
            logo_path = os.path.abspath(logo_path)

        cur = self.conn.cursor()
        cur.execute(
            """
            UPDATE candidates
            SET name = ?, position = ?, photo = ?, logo_path = ?
            WHERE id = ?
            """,
            (name, position, photo_path, logo_path, candidate_id),
        )
        self.conn.commit()

    def get_candidates(self, position=None):
        cur = self.conn.cursor()
        if position:
            cur.execute("SELECT id, name, position, votes, photo, logo_path FROM candidates WHERE position=?", (position,))
        else:
            cur.execute("SELECT id, name, position, votes, photo, logo_path FROM candidates")
        return cur.fetchall()
    

    def get_candidate_by_id(self, candidate_id: int):
        """Return one candidate row by id."""
        cur = self.conn.cursor()
        cur.execute(
            "SELECT id, name, position, votes, photo, logo_path FROM candidates WHERE id = ?",
            (candidate_id,),
        )
        return cur.fetchone()

    
  

    def delete_candidate(self, candidate_id):
        """Delete a candidate completely."""
        cur = self.conn.cursor()
        cur.execute("DELETE FROM candidates WHERE id = ?", (candidate_id,))
        self.conn.commit()


    def get_all_positions(self):
        cur = self.conn.cursor()
        cur.execute("SELECT DISTINCT position FROM candidates")
        return [r[0] for r in cur.fetchall()]

    def cast_vote(self, candidate_id):
        cur = self.conn.cursor()
        cur.execute("UPDATE candidates SET votes = votes + 1 WHERE id=?", (candidate_id,))
        self.conn.commit()

    def record_vote(self, regno, candidate_id):
        cur = self.conn.cursor()
        cur.execute("UPDATE candidates SET votes = votes + 1 WHERE id=?", (candidate_id,))
        cur.execute("UPDATE students SET has_voted=1 WHERE regno=?", (regno,))
        self.conn.commit()


    # ---------- VOTING TIME OPERATIONS ----------
    def set_voting_duration(self, start_time, end_time):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM voting_settings")  # keep one record only
        cur.execute("INSERT INTO voting_settings (start_time, end_time) VALUES (?, ?)",
                    (start_time, end_time))
        self.conn.commit()

    def get_voting_duration(self):
        cur = self.conn.cursor()
        cur.execute("SELECT start_time, end_time FROM voting_settings ORDER BY id DESC LIMIT 1")
        return cur.fetchone()

    def is_voting_open(self):
        data = self.get_voting_duration()
        if not data:
            return False, "Voting period not set."

        start_str, end_str = data
        now = datetime.now()

        try:
            start = datetime.fromisoformat(start_str)
            end = datetime.fromisoformat(end_str)
        except ValueError:
            return False, "Invalid voting period format."

        if now < start:
            return False, "Voting has not started yet."
        elif now > end:
            return False, "Voting period is over."
        else:
            return True, "Voting is open."

        
    # ---------------- Position Management ----------------
    def create_positions_table(self):
        cur = self.conn.cursor()
        cur.execute("""
            CREATE TABLE IF NOT EXISTS positions (
                id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT UNIQUE NOT NULL
            )
        """)
        self.conn.commit()

    def add_position(self, position_name):
        self.create_positions_table()
        try:
            cur = self.conn.cursor()
            cur.execute("INSERT INTO positions (name) VALUES (?)", (position_name.strip(),))
            self.conn.commit()
        except Exception as e:
            print("Error adding position:", e)

    def delete_position(self, position_name):
        cur = self.conn.cursor()
        cur.execute("DELETE FROM positions WHERE name = ?", (position_name,))
        self.conn.commit()

    def get_all_positions(self):
        self.create_positions_table()
        cur = self.conn.cursor()
        cur.execute("SELECT name FROM positions ORDER BY name ASC")
        return [row[0] for row in cur.fetchall()]

        
        
        # ---------- POLL STATUS ----------
    def get_poll_status(self):
            cur = self.conn.cursor()
            cur.execute("SELECT position, name, votes FROM candidates ORDER BY position, votes DESC")
            return cur.fetchall()
        

    # ---------- ADMIN OPERATIONS ----------
    def register_admin(self, username, password):
        """Register a new admin (only if not exists)."""
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM admins WHERE username=?", (username,))
        if cur.fetchone():
            return False  # already exists
        cur.execute("INSERT INTO admins (username, password) VALUES (?, ?)", (username, password))
        self.conn.commit()
        return True

    def verify_admin(self, username, password):
        cur = self.conn.cursor()
        cur.execute("SELECT * FROM admins WHERE username=? AND password=?", (username, password))
        admin = cur.fetchone()
        return admin  # This returns the admin record, not just True/False
    
    def update_admin_password(self, username, new_password):
        """Change the admin's password."""
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE admins SET password = ? WHERE username = ?",
            (new_password, username),
        )
        self.conn.commit()

    

        # ---------- ADMIN OPERATIONS ----------
    def reset_votes(self):
        """Reset all candidate votes and student voting status."""
        cur = self.conn.cursor()
        # Reset candidate votes
        cur.execute("UPDATE candidates SET votes = 0")
        # Reset student voted status
        cur.execute("UPDATE students SET has_voted = 0")
        self.conn.commit()

    def verify_admin_login(self, username, password):
        query = "SELECT * FROM admins WHERE username=? AND password=?"
        self.cursor.execute(query, (username, password))
        return self.cursor.fetchone()

    def verify_student_login(self, username, password):
        query = "SELECT * FROM students WHERE username=? AND password=?"
        self.cursor.execute(query, (username, password))
        return self.cursor.fetchone()
    
    def reset_student_password(self, username, regno, new_password):
        """Reset a student's password using username + regno."""
        cur = self.conn.cursor()
        cur.execute(
            "UPDATE students SET password = ? WHERE username = ? AND regno = ?",
            (new_password, username, regno),
        )
        self.conn.commit()
        return cur.rowcount > 0  # True if a row was updated




    def close(self):
        self.conn.close()

