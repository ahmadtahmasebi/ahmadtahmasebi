import sqlite3
import datetime

class DatabaseManager:
    def __init__(self, db_name='products.db'):
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self.initDB_tables()

    def initDB_tables(self):
        # جدول محصولات
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS products
                                (id INTEGER PRIMARY KEY, name TEXT, price REAL, category TEXT, image TEXT)''')
        self.conn.commit()

        # جدول دسته‌بندی‌ها
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories
                                (id INTEGER PRIMARY KEY, name TEXT)''')
        self.conn.commit()

        # جدول کاربران با سطوح دسترسی
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS users
                                (id INTEGER PRIMARY KEY,
                                username TEXT UNIQUE,
                                password TEXT,
                                full_name TEXT,
                                email TEXT,
                                role TEXT DEFAULT 'user',
                                is_active INTEGER DEFAULT 1,
                                last_login TEXT,
                                created_at TEXT)''')
        self.conn.commit()

        # جدول ثبت فعالیت‌های کاربران
        self.cursor.execute('''CREATE TABLE IF NOT EXISTS user_activities
                                (id INTEGER PRIMARY KEY,
                                user_id INTEGER,
                                activity_type TEXT,
                                description TEXT,
                                timestamp TEXT,
                                ip_address TEXT,
                                FOREIGN KEY (user_id) REFERENCES users(id))''')
        self.conn.commit()

        # بررسی وجود ستون‌های جدید در جدول کاربران و افزودن آنها در صورت نیاز
        self.cursor.execute("PRAGMA table_info(users)")
        columns = [col[1] for col in self.cursor.fetchall()]

        if 'role' not in columns:
            self.cursor.execute("ALTER TABLE users ADD COLUMN role TEXT DEFAULT 'user'")
            self.conn.commit()

        if 'full_name' not in columns:
            self.cursor.execute("ALTER TABLE users ADD COLUMN full_name TEXT")
            self.conn.commit()

        if 'email' not in columns:
            self.cursor.execute("ALTER TABLE users ADD COLUMN email TEXT")
            self.conn.commit()

        if 'is_active' not in columns:
            self.cursor.execute("ALTER TABLE users ADD COLUMN is_active INTEGER DEFAULT 1")
            self.conn.commit()

        if 'last_login' not in columns:
            self.cursor.execute("ALTER TABLE users ADD COLUMN last_login TEXT")
            self.conn.commit()

        if 'created_at' not in columns:
            self.cursor.execute("ALTER TABLE users ADD COLUMN created_at TEXT")
            self.conn.commit()

        # بررسی وجود ستون 'category' و افزودن آن در صورت نیاز
        self.cursor.execute("PRAGMA table_info(products)")
        columns = [col[1] for col in self.cursor.fetchall()]
        if 'category' not in columns:
            self.cursor.execute("ALTER TABLE products ADD COLUMN category TEXT")
            self.conn.commit()

        # اطمینان از وجود حداقل یک کاربر مدیر در سیستم
        self.cursor.execute("SELECT COUNT(*) FROM users WHERE role = 'admin'")
        admin_count = self.cursor.fetchone()[0]

        if admin_count == 0:
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                "INSERT INTO users (username, password, full_name, role, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?)",
                ('admin', 'admin123', 'مدیر سیستم', 'admin', 1, current_time)
            )
            self.conn.commit()
            print("Default admin user created: username='admin', password='admin123'")

    def execute_query(self, query, params=()):
        self.cursor.execute(query, params)
        self.conn.commit()

    def fetch_query(self, query, params=()):
        self.cursor.execute(query, params)
        return self.cursor.fetchall()

    def log_activity(self, user_id, activity_type, description, ip_address="127.0.0.1"):
        """ثبت فعالیت کاربر در پایگاه داده"""
        timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.cursor.execute(
            "INSERT INTO user_activities (user_id, activity_type, description, timestamp, ip_address) VALUES (?, ?, ?, ?, ?)",
            (user_id, activity_type, description, timestamp, ip_address)
        )
        self.conn.commit()

    def __del__(self):
        self.conn.close()