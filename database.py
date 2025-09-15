import sqlite3
import numpy as np
import json
import pandas as pd
from dataclass import *

class DatabaseHandler:
    def __init__(self, db_path: str = "attendance.db"):
        self.db_path = db_path
        self._ensure_tables()

    def _connect(self):
        return sqlite3.connect(self.db_path)
    
    def _ensure_tables(self):
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS staff (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    name TEXT NOT NULL,
                    is_active BOOLEAN DEFAULT TRUE,
                    embedding TEXT -- JSON list of floats
                );
                """
            )
            cur.execute(
                """
                CREATE TABLE IF NOT EXISTS attendance (
                    id INTEGER PRIMARY KEY AUTOINCREMENT,
                    user_id INTEGER NOT NULL,
                    timestamp TEXT NOT NULL,
                    status TEXT DEFAULT 'present',
                    anti_spoof_status BOOLEAN NOT NULL,
                    FOREIGN KEY(user_id) REFERENCES staff(id)
                );
                """
            )
            conn.commit()

    def insert_staff(self, name: str, embedding: np.ndarray) -> int:
        if embedding is None:
            raise ValueError("Embedding is None. No face was detected or embedding could not be extracted.")
        emb_json = json.dumps(embedding.astype(float).tolist())
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO staff(name, is_active, embedding) VALUES (?, ?, ?)", (name, True, emb_json))
            conn.commit()
            return cur.lastrowid
        
    def delete_staff(self, staff_id: int) -> Optional[Tuple[int, str]]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name FROM staff WHERE id = ? AND is_active = TRUE", (staff_id,))
            row = cur.fetchone()
            if not row:
                return None

            staff_id, staff_name = row

            cur.execute("UPDATE staff SET is_active = FALSE WHERE id = ?", (staff_id,))
            conn.commit()

            return staff_id, staff_name
        
    def get_staff_by_name(self, name: str) -> Optional[Staff]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, embedding FROM staff WHERE name = ? AND is_active = TRUE", (name,))
            row = cur.fetchone()
            if not row:
                return None
            emb = np.array(json.loads(row[2]), dtype=np.float32)
            return Staff(id=row[0], name=row[1], embedding=emb)
    
    def get_all_staffs(self) -> List[Staff]:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT id, name, embedding FROM staff WHERE is_active = TRUE")
            rows = cur.fetchall()
        staffs = []
        for r in rows:
            emb = np.array(json.loads(r[2]), dtype=np.float32)
            staffs.append(Staff(id=r[0], name=r[1], embedding=emb))
        return staffs
    
    def insert_attendance(self, user_id: int, timestamp: datetime, anti_spoof_status: str, status: str = "present") -> int:
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("INSERT INTO attendance(user_id, timestamp, status, anti_spoof_status) VALUES (?, ?, ?, ?)", (user_id, timestamp, status, anti_spoof_status))
            conn.commit()
            return cur.lastrowid, user_id, timestamp
        
    def get_all_attendance(self):
        with self._connect() as conn:
            query = """
                SELECT a.id,
                    s.name AS visitor_name,
                    a.timestamp AS Time,
                    a.status,
                    a.anti_spoof_status
                FROM attendance a
                JOIN staff s ON a.user_id = s.id
                WHERE s.is_active = TRUE
                ORDER BY a.timestamp DESC
            """
            return pd.read_sql_query(query, conn)
        
    def get_attendance_by_date(self, date_str: str) -> List[AttendanceLog]:
        """date_str format: YYYY-MM-DD"""
        with self._connect() as conn:
            cur = conn.cursor()
            cur.execute("SELECT user_id, timestamp, status FROM attendance WHERE date(timestamp) = ?", (date_str,))
            rows = cur.fetchall()
            return [AttendanceLog(user_id=r[0], timestamp=datetime.fromisoformat(r[1]), status=r[2]) for r in rows]