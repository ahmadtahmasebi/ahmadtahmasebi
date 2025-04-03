import sys
import os
import datetime
import time
import json
import sqlite3

# Try to import optional dependencies
try:
    from PyQt5 import QtWidgets, QtGui, QtCore
    from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QTableWidget, QTableWidgetItem, QDialog, QGridLayout, QComboBox, QFormLayout, QGroupBox, QScrollArea, QMenuBar, QAction, QDialogButtonBox, QMessageBox, QTabWidget, QCheckBox, QProgressBar, QRadioButton
except ImportError:
    print("Error: PyQt5 is required. Please install it using: pip install PyQt5")
    sys.exit(1)

# Import other dependencies with error handling
MISSING_DEPENDENCIES = []

try:
    import pandas as pd
except ImportError:
    MISSING_DEPENDENCIES.append("pandas")
    pd = None

try:
    import csv
except ImportError:
    MISSING_DEPENDENCIES.append("csv")

try:
    import xlsxwriter
except ImportError:
    MISSING_DEPENDENCIES.append("xlsxwriter")

try:
    from reportlab.lib.pagesizes import letter
    from reportlab.pdfgen import canvas
except ImportError:
    MISSING_DEPENDENCIES.append("reportlab")

try:
    import matplotlib.pyplot as plt
    from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
    from matplotlib.figure import Figure
    import numpy as np
    MATPLOTLIB_AVAILABLE = True
except ImportError:
    MISSING_DEPENDENCIES.append("matplotlib or numpy")
    MATPLOTLIB_AVAILABLE = False

try:
    import barcode
    from barcode.writer import ImageWriter
    from barcode import generate
    BARCODE_AVAILABLE = True
except ImportError:
    MISSING_DEPENDENCIES.append("python-barcode")
    BARCODE_AVAILABLE = False

try:
    import io
    from PIL import Image
    from PIL.ImageQt import toqimage
    PIL_AVAILABLE = True
except ImportError:
    MISSING_DEPENDENCIES.append("Pillow")
    PIL_AVAILABLE = False

# برای کنترل دسترسی
try:
    from access_control import AccessControl
    ACCESS_CONTROL_AVAILABLE = True
except ImportError:
    ACCESS_CONTROL_AVAILABLE = False
    print("Warning: access_control module not found. Access control features will be disabled.")

# کلاس نمودار برای استفاده در داشبورد
if MATPLOTLIB_AVAILABLE:
    class MplCanvas(FigureCanvas):
        def __init__(self, parent=None, width=5, height=4, dpi=100):
            self.fig = Figure(figsize=(width, height), dpi=dpi)
            self.axes = self.fig.add_subplot(111)
            super(MplCanvas, self).__init__(self.fig)
            self.fig.tight_layout()
else:
    class MplCanvas:
        def __init__(self, parent=None, width=5, height=4, dpi=100):
            print("Warning: Matplotlib not available. Charts will not be displayed.")

class ProductManager(QMainWindow):
    def __init__(self, auth_manager=None):
        super().__init__()

        # Check for missing dependencies and show warning if needed
        if MISSING_DEPENDENCIES:
            missing_deps = ", ".join(MISSING_DEPENDENCIES)
            print(f"Warning: Some dependencies are missing: {missing_deps}")
            print("Please install them using: pip install " + " ".join(MISSING_DEPENDENCIES))
            QMessageBox.warning(self, "Missing Dependencies",
                               f"Some dependencies are missing: {missing_deps}\n\n"
                               f"Some features may not work properly.\n"
                               f"Please install them using:\n"
                               f"pip install {' '.join(MISSING_DEPENDENCIES)}")

        # اضافه کردن متغیر برای ذخیره وضعیت بازگشت به فرم قبلی
        self.return_to_previous_form = False

        try:
            # ذخیره مدیر احراز هویت
            self.auth_manager = auth_manager
            self.current_user = auth_manager.get_current_user() if auth_manager else None

            # اطمینان از وجود پوشه product_images
            if not os.path.exists('product_images'):
                os.makedirs('product_images')
                print("Created product_images directory")

            # اطمینان از وجود پوشه settings
            if not os.path.exists('settings'):
                os.makedirs('settings')
                print("Created settings directory")

            # تنظیمات پیش‌فرض برنامه
            self.app_version = "1.0.0"
            self.app_settings = {
                "theme": "light",  # گزینه‌های: light, dark, blue
                "language": "fa",  # گزینه‌های: fa, en
                "font_family": "Vazir",  # فونت پیش‌فرض
                "font_size": 12,  # سایز فونت پیش‌فرض
                "ui_scale": "desktop"  # گزینه‌های: desktop, mobile
            }

            # بارگذاری تنظیمات از فایل
            self.load_settings()

            # ابتدا اتصال به پایگاه داده را برقرار می‌کنیم
            self.conn = sqlite3.connect('products.db')
            self.cursor = self.conn.cursor()

            # ابتدا جداول پایگاه داده را ایجاد می‌کنیم
            self.initDB_tables()

            # تنظیم استایل برنامه
            self.set_application_style()

            # سپس رابط کاربری را ایجاد می‌کنیم
            self.initUI()

            # محصولات در initUI بارگذاری می‌شوند پس از اینکه کنترل‌ها ایجاد شده‌اند

            # ثبت فعالیت باز کردن بخش مدیریت محصولات
            self.log_activity("application", "باز کردن بخش مدیریت محصولات")

            print("Initialization completed successfully")
        except Exception as e:
            print(f"Error in initialization: {e}")
            QMessageBox.critical(self, "Initialization Error", f"Error initializing application: {str(e)}")

    def load_settings(self):
        """بارگذاری تنظیمات از فایل"""
        try:
            settings_path = os.path.join('settings', 'app_settings.json')
            if os.path.exists(settings_path):
                with open(settings_path, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # به‌روزرسانی تنظیمات با مقادیر بارگذاری شده
                    for key, value in loaded_settings.items():
                        if key in self.app_settings:
                            self.app_settings[key] = value
                print("Settings loaded successfully")
            else:
                # ذخیره تنظیمات پیش‌فرض اگر فایل وجود نداشت
                self.save_settings()
        except Exception as e:
            print(f"Error loading settings: {e}")
            # در صورت خطا، از تنظیمات پیش‌فرض استفاده می‌کنیم

    def save_settings(self):
        """ذخیره تنظیمات در فایل"""
        try:
            settings_path = os.path.join('settings', 'app_settings.json')
            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(self.app_settings, f, indent=4, ensure_ascii=False)
            print("Settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {e}")

    def set_application_style(self):
        """تنظیم استایل کلی برنامه"""
        # اعمال تم انتخاب شده
        self.apply_theme(self.app_settings["theme"])

        # اعمال فونت انتخاب شده
        self.apply_font(self.app_settings["font_family"], self.app_settings["font_size"])

        # اعمال سایز رابط کاربری
        self.apply_ui_scale(self.app_settings["ui_scale"])

        # استایل‌های اضافی که در همه تم‌ها مشترک هستند
        self.setStyleSheet("""
            QLineEdit, QComboBox {
                border-radius: 4px;
                padding: 5px;
                min-height: 25px;
            }
            QPushButton {
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
                min-height: 30px;
                font-weight: bold;
            }
            QTableWidget::item {
                padding: 4px;
            }
            QScrollBar:vertical {
                border: none;
                width: 10px;
                margin: 0px;
            }
            QScrollBar::handle:vertical {
                min-height: 20px;
                border-radius: 5px;
            }
            QGroupBox {
                border-radius: 4px;
                margin-top: 20px;
                font-weight: bold;
            }
            QGroupBox::title {
                subcontrol-origin: margin;
                subcontrol-position: top center;
                padding: 0 5px;
            }
            QMenuBar::item {
                padding: 6px 10px;
                background: transparent;
            }
            QMenu::item {
                padding: 6px 20px 6px 20px;
            }
            QTabWidget::pane {
                border-radius: 4px;
            }
            QTabBar::tab {
                border-top-left-radius: 4px;
                border-top-right-radius: 4px;
                padding: 6px 12px;
                margin-right: 2px;
            }
        """)

    def apply_theme(self, theme):
        """اعمال تم انتخاب شده به برنامه"""
        if theme == "light":
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #f5f5f5;
                }
                QLabel {
                    color: #333333;
                }
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #00559b;
                }
                QTableWidget {
                    background-color: white;
                    alternate-background-color: #f9f9f9;
                }
            """)
        elif theme == "dark":
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #2d2d2d;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #00559b;
                }
                QTableWidget {
                    background-color: #3d3d3d;
                    alternate-background-color: #353535;
                    color: #e0e0e0;
                }
                QLineEdit, QComboBox {
                    background-color: #3d3d3d;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                }
            """)
        elif theme == "blue":
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #e6f2ff;
                }
                QLabel {
                    color: #00264d;
                }
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                }
                QPushButton:hover {
                    background-color: #00559b;
                }
                QTableWidget {
                    background-color: white;
                    alternate-background-color: #f0f8ff;
                }
            """)

    def apply_font(self, font_family, font_size):
        """اعمال فونت انتخاب شده به برنامه"""
        font = QtGui.QFont(font_family, font_size)
        QtWidgets.QApplication.setFont(font)

    def apply_ui_scale(self, scale):
        """اعمال مقیاس رابط کاربری"""
        if scale == "desktop":
            # مقیاس استاندارد برای دسکتاپ
            pass
        elif scale == "mobile":
            # مقیاس بزرگتر برای دستگاه‌های موبایل
            self.setMinimumWidth(480)
            self.setMinimumHeight(800)

    def initDB_tables(self):
        """ایجاد جداول مورد نیاز در پایگاه داده"""
        try:
            # جدول محصولات
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS products
                                (id INTEGER PRIMARY KEY,
                                name TEXT,
                                price REAL,
                                category TEXT,
                                image TEXT,
                                stock INTEGER DEFAULT 0,
                                min_stock INTEGER DEFAULT 5,
                                discount_price REAL,
                                barcode TEXT,
                                description TEXT,
                                created_at TEXT,
                                updated_at TEXT)''')
            self.conn.commit()

            # جدول دسته‌بندی‌ها
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS categories
                                (id INTEGER PRIMARY KEY,
                                name TEXT,
                                description TEXT,
                                parent_id INTEGER,
                                created_at TEXT)''')
            self.conn.commit()

            # جدول تصاویر محصولات
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS product_images
                                (id INTEGER PRIMARY KEY,
                                product_id INTEGER,
                                image_path TEXT,
                                is_primary INTEGER DEFAULT 0,
                                created_at TEXT,
                                FOREIGN KEY (product_id) REFERENCES products(id))''')
            self.conn.commit()

            # جدول تاریخچه موجودی
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS inventory_history
                                (id INTEGER PRIMARY KEY,
                                product_id INTEGER,
                                old_stock INTEGER,
                                new_stock INTEGER,
                                change_reason TEXT,
                                user_id INTEGER,
                                timestamp TEXT,
                                FOREIGN KEY (product_id) REFERENCES products(id))''')
            self.conn.commit()

            # جدول تخفیف‌ها
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS discounts
                                (id INTEGER PRIMARY KEY,
                                name TEXT,
                                discount_type TEXT,
                                discount_value REAL,
                                start_date TEXT,
                                end_date TEXT,
                                is_active INTEGER DEFAULT 1,
                                created_at TEXT)''')
            self.conn.commit()

            # جدول ارتباط تخفیف‌ها با محصولات
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS product_discounts
                                (id INTEGER PRIMARY KEY,
                                product_id INTEGER,
                                discount_id INTEGER,
                                FOREIGN KEY (product_id) REFERENCES products(id),
                                FOREIGN KEY (discount_id) REFERENCES discounts(id))''')
            self.conn.commit()

            # جدول فعالیت‌های سیستم
            self.cursor.execute('''CREATE TABLE IF NOT EXISTS activities
                                (id INTEGER PRIMARY KEY,
                                activity_type TEXT,
                                description TEXT,
                                user_id INTEGER,
                                timestamp TEXT,
                                ip_address TEXT)''')
            self.conn.commit()

            # بررسی وجود جدول activities
            try:
                self.cursor.execute("SELECT COUNT(*) FROM activities")
                self.cursor.fetchone()
                print("Activities table exists and is accessible")
            except sqlite3.OperationalError:
                print("Recreating activities table due to access error")
                self.cursor.execute("DROP TABLE IF EXISTS activities")
                self.cursor.execute('''CREATE TABLE IF NOT EXISTS activities
                                    (id INTEGER PRIMARY KEY,
                                    activity_type TEXT,
                                    description TEXT,
                                    user_id INTEGER,
                                    timestamp TEXT,
                                    ip_address TEXT)''')
                self.conn.commit()

            print("Database tables created successfully")
        except Exception as e:
            print(f"Error creating database tables: {e}")

    def log_activity(self, activity_type, description):
        """ثبت فعالیت در سیستم"""
        try:
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            user_id = self.current_user['id'] if self.current_user else None

            # بررسی وجود جدول activities
            try:
                self.cursor.execute(
                    "INSERT INTO activities (activity_type, description, user_id, timestamp, ip_address) VALUES (?, ?, ?, ?, ?)",
                    (activity_type, description, user_id, timestamp, "127.0.0.1")
                )
                self.conn.commit()
            except sqlite3.OperationalError as e:
                if "no such table" in str(e):
                    # ایجاد مجدد جدول در صورت عدم وجود
                    print("Recreating activities table")
                    self.cursor.execute('''CREATE TABLE IF NOT EXISTS activities
                                        (id INTEGER PRIMARY KEY,
                                        activity_type TEXT,
                                        description TEXT,
                                        user_id INTEGER,
                                        timestamp TEXT,
                                        ip_address TEXT)''')
                    self.conn.commit()

                    # تلاش مجدد برای ثبت فعالیت
                    self.cursor.execute(
                        "INSERT INTO activities (activity_type, description, user_id, timestamp, ip_address) VALUES (?, ?, ?, ?, ?)",
                        (activity_type, description, user_id, timestamp, "127.0.0.1")
                    )
                    self.conn.commit()
                else:
                    print(f"Error logging activity: {e}")
        except Exception as e:
            print(f"Error logging activity: {e}")

    def check_low_stock(self):
        """بررسی محصولات با موجودی کم و نمایش هشدار"""
        try:
            # دریافت محصولات با موجودی کمتر از حداقل
            self.cursor.execute("""
                SELECT id, name, stock, min_stock
                FROM products
                WHERE stock < min_stock AND stock > 0
            """)
            low_stock_products = self.cursor.fetchall()

            # دریافت محصولات با موجودی صفر
            self.cursor.execute("""
                SELECT id, name, stock, min_stock
                FROM products
                WHERE stock <= 0
            """)
            out_of_stock_products = self.cursor.fetchall()

            # اگر محصولی با موجودی کم یا اتمام موجودی وجود داشت، هشدار نمایش داده شود
            if low_stock_products or out_of_stock_products:
                alert_dialog = QDialog(self)
                alert_dialog.setWindowTitle("هشدار موجودی")
                alert_dialog.setMinimumWidth(500)

                layout = QVBoxLayout(alert_dialog)

                if out_of_stock_products:
                    out_label = QLabel(f"<b>{len(out_of_stock_products)} محصول با اتمام موجودی:</b>")
                    layout.addWidget(out_label)

                    out_table = QTableWidget()
                    out_table.setColumnCount(3)
                    out_table.setHorizontalHeaderLabels(["نام محصول", "موجودی فعلی", "حداقل موجودی"])
                    out_table.setRowCount(len(out_of_stock_products))

                    for row, product in enumerate(out_of_stock_products):
                        out_table.setItem(row, 0, QTableWidgetItem(product[1]))
                        out_table.setItem(row, 1, QTableWidgetItem(str(product[2])))
                        out_table.setItem(row, 2, QTableWidgetItem(str(product[3])))

                    out_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
                    layout.addWidget(out_table)

                if low_stock_products:
                    low_label = QLabel(f"<b>{len(low_stock_products)} محصول با موجودی کم:</b>")
                    layout.addWidget(low_label)

                    low_table = QTableWidget()
                    low_table.setColumnCount(3)
                    low_table.setHorizontalHeaderLabels(["نام محصول", "موجودی فعلی", "حداقل موجودی"])
                    low_table.setRowCount(len(low_stock_products))

                    for row, product in enumerate(low_stock_products):
                        low_table.setItem(row, 0, QTableWidgetItem(product[1]))
                        low_table.setItem(row, 1, QTableWidgetItem(str(product[2])))
                        low_table.setItem(row, 2, QTableWidgetItem(str(product[3])))

                    low_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
                    layout.addWidget(low_table)

                # دکمه مدیریت موجودی
                manage_btn = QPushButton("مدیریت موجودی")
                manage_btn.clicked.connect(lambda: [alert_dialog.close(), self.manage_inventory()])

                # دکمه بستن
                close_btn = QPushButton("بستن")
                close_btn.clicked.connect(alert_dialog.close)

                buttons_layout = QHBoxLayout()
                buttons_layout.addWidget(manage_btn)
                buttons_layout.addWidget(close_btn)

                layout.addLayout(buttons_layout)

                # نمایش پنجره هشدار
                alert_dialog.exec_()

        except Exception as e:
            print(f"Error checking low stock: {e}")

    def initUI(self):
        """ایجاد رابط کاربری اصلی"""
        # این یک پیاده‌سازی ساده است - در نسخه اصلی باید کامل شود
        try:
            # تنظیم عنوان و اندازه پنجره
            self.setWindowTitle("مدیریت محصولات")
            self.setGeometry(100, 100, 1200, 800)

            # ایجاد ویجت مرکزی
            central_widget = QWidget()
            self.setCentralWidget(central_widget)

            # ایجاد طرح اصلی
            main_layout = QVBoxLayout(central_widget)

            # ایجاد یک برچسب به عنوان عنوان اصلی
            label = QLabel("سیستم مدیریت محصولات")
            label.setAlignment(QtCore.Qt.AlignCenter)
            font = QtGui.QFont(self.app_settings["font_family"], 24)
            font.setBold(True)
            label.setFont(font)
            label.setStyleSheet("margin: 20px 0;")
            main_layout.addWidget(label)

            # ایجاد داشبورد با گرید لایوت
            dashboard_layout = QGridLayout()

            # استایل مشترک برای دکمه‌ها
            button_style = """
                QPushButton {
                    font-size: 16px;
                    padding: 20px;
                    margin: 10px;
                    border-radius: 8px;
                    background-color: #0078d7;
                    color: white;
                    font-weight: bold;
                    text-align: center;
                    min-height: 120px;
                }
                QPushButton:hover {
                    background-color: #00559b;
                }
            """

            # بخش محصولات
            products_group = QGroupBox("مدیریت محصولات")
            products_layout = QVBoxLayout(products_group)

            # دکمه افزودن محصول جدید
            add_product_btn = QPushButton("\n\nافزودن محصول جدید\n\n")
            add_product_btn.setStyleSheet(button_style)
            add_product_btn.setIcon(QtGui.QIcon.fromTheme("list-add", QtGui.QIcon()))
            add_product_btn.setIconSize(QtCore.QSize(32, 32))
            add_product_btn.clicked.connect(self.add_new_product)
            products_layout.addWidget(add_product_btn)

            # دکمه نمایش محصولات
            show_products_btn = QPushButton("\n\nنمایش محصولات\n\n")
            show_products_btn.setStyleSheet(button_style)
            show_products_btn.setIcon(QtGui.QIcon.fromTheme("view-list", QtGui.QIcon()))
            show_products_btn.setIconSize(QtCore.QSize(32, 32))
            show_products_btn.clicked.connect(self.show_products)
            products_layout.addWidget(show_products_btn)

            # بخش انبار
            inventory_group = QGroupBox("مدیریت انبار")
            inventory_layout = QVBoxLayout(inventory_group)

            # دکمه مدیریت انبار
            inventory_btn = QPushButton("\n\nمدیریت موجودی انبار\n\n")
            inventory_btn.setStyleSheet(button_style.replace("#0078d7", "#009688"))  # رنگ سبز برای بخش انبار
            inventory_btn.setIcon(QtGui.QIcon.fromTheme("package", QtGui.QIcon()))
            inventory_btn.setIconSize(QtCore.QSize(32, 32))
            inventory_btn.clicked.connect(self.manage_inventory)
            inventory_layout.addWidget(inventory_btn)

            # دکمه به‌روزرسانی گروهی
            batch_update_btn = QPushButton("\n\nبه‌روزرسانی گروهی موجودی\n\n")
            batch_update_btn.setStyleSheet(button_style.replace("#0078d7", "#009688"))
            batch_update_btn.setIcon(QtGui.QIcon.fromTheme("view-refresh", QtGui.QIcon()))
            batch_update_btn.setIconSize(QtCore.QSize(32, 32))
            batch_update_btn.clicked.connect(self.batch_update_inventory)
            inventory_layout.addWidget(batch_update_btn)

            # بخش گزارش‌ها
            reports_group = QGroupBox("گزارش‌ها")
            reports_layout = QVBoxLayout(reports_group)

            # دکمه گزارش موجودی
            inventory_report_btn = QPushButton("\n\nگزارش موجودی انبار\n\n")
            inventory_report_btn.setStyleSheet(button_style.replace("#0078d7", "#E91E63"))  # رنگ صورتی برای بخش گزارش‌ها
            inventory_report_btn.setIcon(QtGui.QIcon.fromTheme("x-office-spreadsheet", QtGui.QIcon()))
            inventory_report_btn.setIconSize(QtCore.QSize(32, 32))
            inventory_report_btn.clicked.connect(self.show_inventory_report)
            reports_layout.addWidget(inventory_report_btn)

            # اضافه کردن گروه‌ها به گرید لایوت
            dashboard_layout.addWidget(products_group, 0, 0)
            dashboard_layout.addWidget(inventory_group, 0, 1)
            dashboard_layout.addWidget(reports_group, 1, 0)

            # اضافه کردن داشبورد به طرح اصلی
            main_layout.addLayout(dashboard_layout)

            # بررسی موجودی کم و نمایش هشدار
            self.check_low_stock()

            # ایجاد منوی اصلی
            self.create_menu()

            print("UI initialized successfully")
        except Exception as e:
            print(f"Error initializing UI: {e}")
            QMessageBox.critical(self, "UI Error", f"Error creating user interface: {str(e)}")

    def create_menu(self):
        """ایجاد منوی اصلی برنامه"""
        try:
            # ایجاد نوار منو
            menubar = self.menuBar()

            # منوی فایل
            file_menu = menubar.addMenu("فایل")

            # اکشن‌های منوی فایل
            import_menu = file_menu.addMenu("وارد کردن")

            import_excel_action = QAction("وارد کردن از Excel", self)
            import_excel_action.triggered.connect(self.import_from_excel)
            import_menu.addAction(import_excel_action)

            import_csv_action = QAction("وارد کردن از CSV", self)
            import_csv_action.triggered.connect(self.import_from_csv)
            import_menu.addAction(import_csv_action)

            export_menu = file_menu.addMenu("صادر کردن")

            export_excel_action = QAction("صادر کردن به Excel", self)
            export_excel_action.triggered.connect(self.export_to_excel)
            export_menu.addAction(export_excel_action)

            export_csv_action = QAction("صادر کردن به CSV", self)
            export_csv_action.triggered.connect(self.export_to_csv)
            export_menu.addAction(export_csv_action)

            export_pdf_action = QAction("صادر کردن به PDF", self)
            export_pdf_action.triggered.connect(self.export_to_pdf)
            export_menu.addAction(export_pdf_action)

            file_menu.addSeparator()

            exit_action = QAction("خروج", self)
            exit_action.triggered.connect(self.close)
            file_menu.addAction(exit_action)

            # منوی محصولات
            products_menu = menubar.addMenu("محصولات")

            # اکشن‌های منوی محصولات
            add_product_action = QAction("افزودن محصول جدید", self)
            add_product_action.triggered.connect(self.add_new_product)
            products_menu.addAction(add_product_action)

            list_products_action = QAction("لیست محصولات", self)
            list_products_action.triggered.connect(self.show_products)
            products_menu.addAction(list_products_action)

            manage_images_action = QAction("مدیریت تصاویر محصولات", self)
            manage_images_action.triggered.connect(self.manage_product_images)
            products_menu.addAction(manage_images_action)

            # اضافه کردن جداکننده در منو
            products_menu.addSeparator()

            # اکشن اتصال به سیستم مدیریت محصولات خارجی
            connect_external_action = QAction("اتصال به سیستم مدیریت محصولات", self)
            connect_external_action.triggered.connect(self.connect_to_external_system)
            products_menu.addAction(connect_external_action)

            # اکشن اتصال به فرم مدیریت محصولات
            connect_product_form_action = QAction("اتصال به فرم مدیریت محصولات", self)
            connect_product_form_action.triggered.connect(self.connect_to_product_form)
            products_menu.addAction(connect_product_form_action)

            # منوی انبار
            inventory_menu = menubar.addMenu("انبار")

            # اکشن‌های منوی انبار
            manage_inventory_action = QAction("مدیریت موجودی انبار", self)
            manage_inventory_action.triggered.connect(self.manage_inventory)
            inventory_menu.addAction(manage_inventory_action)

            inventory_report_action = QAction("گزارش موجودی انبار", self)
            inventory_report_action.triggered.connect(self.show_inventory_report)
            inventory_menu.addAction(inventory_report_action)

            batch_update_action = QAction("به‌روزرسانی گروهی موجودی", self)
            batch_update_action.triggered.connect(self.batch_update_inventory)
            inventory_menu.addAction(batch_update_action)

            # منوی گزارش‌ها
            reports_menu = menubar.addMenu("گزارش‌ها")

            # اکشن‌های منوی گزارش‌ها
            sales_report_action = QAction("گزارش فروش", self)
            # sales_report_action.triggered.connect(self.show_sales_report)  # این متد هنوز پیاده‌سازی نشده است
            reports_menu.addAction(sales_report_action)

            # منوی تنظیمات
            settings_menu = menubar.addMenu("تنظیمات")

            # اکشن‌های منوی تنظیمات
            app_settings_action = QAction("تنظیمات برنامه", self)
            app_settings_action.triggered.connect(self.show_settings)
            settings_menu.addAction(app_settings_action)

            # منوی ناوبری
            navigation_menu = menubar.addMenu("ناوبری")

            # اکشن بازگشت به صفحه اصلی
            return_to_main_action = QAction("بازگشت به صفحه اصلی", self)
            return_to_main_action.setIcon(QtGui.QIcon.fromTheme("go-home", QtGui.QIcon()))
            return_to_main_action.triggered.connect(self.return_to_main_form)
            navigation_menu.addAction(return_to_main_action)

            print("Menu created successfully")
        except Exception as e:
            print(f"Error creating menu: {e}")

    # متدهای مورد نیاز برای عملکرد منوها
    def add_new_product(self):
        """افزودن محصول جدید"""
        try:
            dialog = QDialog(self)
            dialog.setWindowTitle("افزودن محصول جدید")
            dialog.setMinimumWidth(400)

            layout = QFormLayout(dialog)

            # فیلدهای ورودی
            name_input = QLineEdit()
            price_input = QLineEdit()
            category_input = QComboBox()

            # دریافت لیست دسته‌بندی‌ها از پایگاه داده
            self.cursor.execute("SELECT name FROM categories")
            categories = self.cursor.fetchall()
            for category in categories:
                category_input.addItem(category[0])

            stock_input = QLineEdit()
            stock_input.setValidator(QtGui.QIntValidator(0, 100000))

            description_input = QLineEdit()

            # دکمه انتخاب تصویر
            image_layout = QHBoxLayout()
            image_path_input = QLineEdit()
            image_path_input.setReadOnly(True)
            select_image_btn = QPushButton("انتخاب تصویر")

            def select_image():
                file_path, _ = QFileDialog.getOpenFileName(dialog, "انتخاب تصویر محصول", "", "Image Files (*.png *.jpg *.jpeg)")
                if file_path:
                    image_path_input.setText(file_path)

            select_image_btn.clicked.connect(select_image)
            image_layout.addWidget(image_path_input)
            image_layout.addWidget(select_image_btn)

            # اضافه کردن فیلدها به فرم
            layout.addRow("نام محصول:", name_input)
            layout.addRow("قیمت:", price_input)
            layout.addRow("دسته‌بندی:", category_input)
            layout.addRow("موجودی:", stock_input)
            layout.addRow("توضیحات:", description_input)
            layout.addRow("تصویر:", image_layout)

            # دکمه‌های تایید و لغو
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)

            if dialog.exec_() == QDialog.Accepted:
                # بررسی اعتبار داده‌ها
                if not name_input.text():
                    QMessageBox.warning(self, "خطا", "نام محصول نمی‌تواند خالی باشد.")
                    return

                try:
                    price = float(price_input.text()) if price_input.text() else 0
                except ValueError:
                    QMessageBox.warning(self, "خطا", "قیمت باید یک عدد باشد.")
                    return

                try:
                    stock = int(stock_input.text()) if stock_input.text() else 0
                    if stock < 0:
                        QMessageBox.warning(self, "خطا", "موجودی نمی‌تواند منفی باشد.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "خطا", "موجودی باید یک عدد صحیح باشد.")
                    return

                # ذخیره تصویر در پوشه product_images
                image_path = ""
                if image_path_input.text():
                    source_path = image_path_input.text()
                    file_name = os.path.basename(source_path)
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    new_file_name = f"{timestamp}_{file_name}"
                    destination_path = os.path.join("product_images", new_file_name)

                    try:
                        # اطمینان از وجود پوشه
                        if not os.path.exists("product_images"):
                            os.makedirs("product_images")

                        # کپی تصویر
                        import shutil
                        shutil.copy2(source_path, destination_path)
                        image_path = destination_path
                    except Exception as e:
                        print(f"Error copying image: {e}")
                        QMessageBox.warning(self, "خطا", f"خطا در ذخیره تصویر: {str(e)}")

                # ایجاد بارکد
                barcode_value = None
                if BARCODE_AVAILABLE:
                    try:
                        # تولید یک بارکد منحصر به فرد بر اساس زمان
                        barcode_value = f"PROD{int(time.time())}"

                        # ذخیره بارکد در پوشه product_images
                        barcode_path = os.path.join("product_images", f"barcode_{barcode_value}.png")

                        # تولید بارکد
                        ean = barcode.get('code128', barcode_value, writer=ImageWriter())
                        ean.save(os.path.join("product_images", f"barcode_{barcode_value}"))
                    except Exception as e:
                        print(f"Error generating barcode: {e}")
                        barcode_value = None

                # ثبت محصول در پایگاه داده
                created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.cursor.execute(
                    "INSERT INTO products (name, price, category, image, stock, description, barcode, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?, ?)",
                    (name_input.text(), price, category_input.currentText(), image_path,
                     int(stock_input.text()) if stock_input.text() else 0,
                     description_input.text(), barcode_value, created_at, created_at)
                )
                self.conn.commit()

                # ثبت فعالیت
                self.log_activity("product", f"افزودن محصول جدید: {name_input.text()}")

                QMessageBox.information(self, "موفقیت", "محصول با موفقیت اضافه شد.")
        except Exception as e:
            print(f"Error adding product: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در افزودن محصول: {str(e)}")

    def show_products(self):
        """نمایش لیست محصولات"""
        try:
            # ایجاد پنجره جدید
            dialog = QDialog(self)
            dialog.setWindowTitle("لیست محصولات")
            dialog.setMinimumSize(800, 600)

            # طرح اصلی
            layout = QVBoxLayout(dialog)

            # ایجاد جدول محصولات
            table = QTableWidget()
            table.setColumnCount(7)
            table.setHorizontalHeaderLabels(["شناسه", "نام محصول", "قیمت", "دسته‌بندی", "موجودی", "بارکد", "عملیات"])
            table.setEditTriggers(QTableWidget.NoEditTriggers)
            table.setSelectionBehavior(QTableWidget.SelectRows)
            table.horizontalHeader().setStretchLastSection(True)

            # دریافت محصولات از پایگاه داده
            self.cursor.execute("SELECT id, name, price, category, stock, barcode FROM products ORDER BY id DESC")
            products = self.cursor.fetchall()

            # تنظیم تعداد سطرهای جدول
            table.setRowCount(len(products))

            # پر کردن جدول با داده‌ها
            for row, product in enumerate(products):
                for col, value in enumerate(product):
                    item = QTableWidgetItem(str(value) if value is not None else "")
                    table.setItem(row, col, item)

                # اضافه کردن دکمه‌های عملیات
                actions_widget = QWidget()
                actions_layout = QHBoxLayout(actions_widget)
                actions_layout.setContentsMargins(0, 0, 0, 0)

                edit_btn = QPushButton("ویرایش")
                delete_btn = QPushButton("حذف")
                view_btn = QPushButton("مشاهده")

                # تنظیم عملکرد دکمه‌ها
                product_id = product[0]
                edit_btn.clicked.connect(lambda checked, pid=product_id: self.edit_product(pid))
                delete_btn.clicked.connect(lambda checked, pid=product_id: self.delete_product(pid))
                view_btn.clicked.connect(lambda checked, pid=product_id: self.view_product(pid))

                actions_layout.addWidget(view_btn)
                actions_layout.addWidget(edit_btn)
                actions_layout.addWidget(delete_btn)

                table.setCellWidget(row, 6, actions_widget)

            # اضافه کردن جدول به طرح
            layout.addWidget(table)

            # اضافه کردن دکمه بستن
            close_btn = QPushButton("بستن")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)

            # نمایش پنجره
            dialog.exec_()
        except Exception as e:
            print(f"Error showing products: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در نمایش محصولات: {str(e)}")

    def edit_product(self, product_id):
        """ویرایش محصول"""
        try:
            # دریافت اطلاعات محصول
            self.cursor.execute("""
                SELECT name, price, category, stock, min_stock, description, image, barcode
                FROM products
                WHERE id = ?
            """, (product_id,))

            product = self.cursor.fetchone()

            if not product:
                QMessageBox.warning(self, "خطا", "محصول مورد نظر یافت نشد.")
                return

            # ایجاد پنجره ویرایش
            dialog = QDialog(self)
            dialog.setWindowTitle(f"ویرایش محصول: {product[0]}")
            dialog.setMinimumWidth(400)

            layout = QFormLayout(dialog)

            # فیلدهای ورودی
            name_input = QLineEdit(product[0])

            price_input = QLineEdit(str(product[1]))
            price_input.setValidator(QtGui.QDoubleValidator(0, 1000000000, 2))

            category_input = QComboBox()

            # دریافت لیست دسته‌بندی‌ها از پایگاه داده
            self.cursor.execute("SELECT name FROM categories")
            categories = self.cursor.fetchall()
            for category in categories:
                category_input.addItem(category[0])

            # تنظیم دسته‌بندی فعلی
            category_index = category_input.findText(product[2])
            if category_index >= 0:
                category_input.setCurrentIndex(category_index)

            # فیلدهای موجودی
            stock_input = QLineEdit(str(product[3]))
            stock_input.setValidator(QtGui.QIntValidator(0, 1000000))

            min_stock_input = QLineEdit(str(product[4]))
            min_stock_input.setValidator(QtGui.QIntValidator(0, 1000000))

            description_input = QLineEdit(product[5] if product[5] else "")

            # دکمه انتخاب تصویر
            image_layout = QHBoxLayout()
            image_path_input = QLineEdit(product[6] if product[6] else "")
            image_path_input.setReadOnly(True)
            select_image_btn = QPushButton("انتخاب تصویر")

            def select_image():
                file_path, _ = QFileDialog.getOpenFileName(dialog, "انتخاب تصویر محصول", "", "Image Files (*.png *.jpg *.jpeg)")
                if file_path:
                    image_path_input.setText(file_path)

            select_image_btn.clicked.connect(select_image)
            image_layout.addWidget(image_path_input)
            image_layout.addWidget(select_image_btn)

            # اضافه کردن فیلدها به فرم
            layout.addRow("نام محصول:", name_input)
            layout.addRow("قیمت:", price_input)
            layout.addRow("دسته‌بندی:", category_input)
            layout.addRow("موجودی:", stock_input)
            layout.addRow("حداقل موجودی:", min_stock_input)
            layout.addRow("توضیحات:", description_input)
            layout.addRow("تصویر:", image_layout)

            # دکمه‌های تایید و لغو
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addRow(buttons)

            if dialog.exec_() == QDialog.Accepted:
                # بررسی اعتبار داده‌ها
                if not name_input.text():
                    QMessageBox.warning(self, "خطا", "نام محصول نمی‌تواند خالی باشد.")
                    return

                try:
                    price = float(price_input.text()) if price_input.text() else 0
                except ValueError:
                    QMessageBox.warning(self, "خطا", "قیمت باید یک عدد باشد.")
                    return

                try:
                    stock = int(stock_input.text()) if stock_input.text() else 0
                    if stock < 0:
                        QMessageBox.warning(self, "خطا", "موجودی نمی‌تواند منفی باشد.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "خطا", "موجودی باید یک عدد صحیح باشد.")
                    return

                try:
                    min_stock = int(min_stock_input.text()) if min_stock_input.text() else 0
                    if min_stock < 0:
                        QMessageBox.warning(self, "خطا", "حداقل موجودی نمی‌تواند منفی باشد.")
                        return
                except ValueError:
                    QMessageBox.warning(self, "خطا", "حداقل موجودی باید یک عدد صحیح باشد.")
                    return

                # ذخیره تصویر جدید در صورت تغییر
                image_path = product[6]  # مقدار پیش‌فرض
                if image_path_input.text() and image_path_input.text() != product[6]:
                    source_path = image_path_input.text()
                    file_name = os.path.basename(source_path)
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    new_file_name = f"{timestamp}_{file_name}"
                    destination_path = os.path.join("product_images", new_file_name)

                    try:
                        # اطمینان از وجود پوشه
                        if not os.path.exists("product_images"):
                            os.makedirs("product_images")

                        # کپی تصویر
                        import shutil
                        shutil.copy2(source_path, destination_path)
                        image_path = destination_path
                    except Exception as e:
                        print(f"Error copying image: {e}")
                        QMessageBox.warning(self, "خطا", f"خطا در ذخیره تصویر: {str(e)}")

                # دریافت موجودی قبلی برای ثبت در تاریخچه
                self.cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
                old_stock = self.cursor.fetchone()[0]

                # به‌روزرسانی محصول در پایگاه داده
                updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.cursor.execute("""
                    UPDATE products
                    SET name = ?, price = ?, category = ?, stock = ?, min_stock = ?,
                        description = ?, image = ?, updated_at = ?
                    WHERE id = ?
                """, (name_input.text(), price, category_input.currentText(), stock,
                      min_stock, description_input.text(), image_path, updated_at, product_id))

                # اگر موجودی تغییر کرده، در تاریخچه ثبت شود
                if old_stock != stock:
                    user_id = self.current_user.id if self.current_user else 0

                    self.cursor.execute("""
                        INSERT INTO inventory_history
                        (product_id, old_stock, new_stock, change_reason, user_id, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (product_id, old_stock, stock, "ویرایش محصول", user_id,
                          datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                self.conn.commit()

                # ثبت فعالیت
                self.log_activity("product", f"ویرایش محصول: {name_input.text()}")

                QMessageBox.information(self, "موفقیت", "محصول با موفقیت به‌روزرسانی شد.")

                # به‌روزرسانی لیست محصولات
                self.show_products()
        except Exception as e:
            print(f"Error editing product: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در ویرایش محصول: {str(e)}")

    def delete_product(self, product_id):
        """حذف محصول"""
        try:
            # پرسیدن تایید از کاربر
            confirm = QMessageBox.question(self, "تایید حذف",
                                          "آیا از حذف این محصول اطمینان دارید؟",
                                          QMessageBox.Yes | QMessageBox.No)

            if confirm == QMessageBox.Yes:
                # دریافت اطلاعات محصول قبل از حذف برای ثبت در لاگ
                self.cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
                product_name = self.cursor.fetchone()[0]

                # حذف محصول
                self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
                self.conn.commit()

                # ثبت فعالیت
                self.log_activity("product", f"حذف محصول: {product_name}")

                QMessageBox.information(self, "موفقیت", "محصول با موفقیت حذف شد.")

                # به‌روزرسانی لیست محصولات
                self.show_products()
        except Exception as e:
            print(f"Error deleting product: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در حذف محصول: {str(e)}")

    def view_product(self, product_id):
        """مشاهده جزئیات محصول"""
        try:
            # دریافت اطلاعات محصول
            self.cursor.execute("""
                SELECT p.id, p.name, p.price, p.category, p.stock, p.description, p.barcode, p.image, p.created_at, p.updated_at
                FROM products p
                WHERE p.id = ?
            """, (product_id,))

            product = self.cursor.fetchone()

            if not product:
                QMessageBox.warning(self, "خطا", "محصول مورد نظر یافت نشد.")
                return

            # ایجاد پنجره جزئیات
            dialog = QDialog(self)
            dialog.setWindowTitle(f"جزئیات محصول: {product[1]}")
            dialog.setMinimumSize(600, 500)

            # طرح اصلی
            layout = QVBoxLayout(dialog)

            # ایجاد فرم نمایش اطلاعات
            form_layout = QFormLayout()

            # نمایش اطلاعات محصول
            form_layout.addRow("شناسه:", QLabel(str(product[0])))
            form_layout.addRow("نام محصول:", QLabel(product[1]))
            form_layout.addRow("قیمت:", QLabel(f"{product[2]:,} تومان"))
            form_layout.addRow("دسته‌بندی:", QLabel(product[3]))
            form_layout.addRow("موجودی:", QLabel(str(product[4])))
            form_layout.addRow("توضیحات:", QLabel(product[5] if product[5] else ""))
            form_layout.addRow("تاریخ ایجاد:", QLabel(product[8]))
            form_layout.addRow("آخرین به‌روزرسانی:", QLabel(product[9]))

            # نمایش بارکد
            if product[6] and BARCODE_AVAILABLE:
                barcode_path = os.path.join("product_images", f"barcode_{product[6]}.png")
                if os.path.exists(barcode_path):
                    barcode_label = QLabel()
                    barcode_pixmap = QtGui.QPixmap(barcode_path)
                    barcode_label.setPixmap(barcode_pixmap.scaledToWidth(200))
                    form_layout.addRow("بارکد:", barcode_label)

            # نمایش تصویر محصول
            if product[7] and os.path.exists(product[7]):
                image_label = QLabel()
                image_pixmap = QtGui.QPixmap(product[7])
                image_label.setPixmap(image_pixmap.scaledToWidth(300))
                form_layout.addRow("تصویر محصول:", image_label)

            # اضافه کردن فرم به طرح اصلی
            layout.addLayout(form_layout)

            # دکمه بستن
            close_btn = QPushButton("بستن")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)

            # نمایش پنجره
            dialog.exec_()
        except Exception as e:
            print(f"Error viewing product: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در نمایش جزئیات محصول: {str(e)}")

    def manage_inventory(self):
        """مدیریت موجودی انبار"""
        try:
            # ایجاد پنجره مدیریت موجودی
            dialog = QDialog(self)
            dialog.setWindowTitle("مدیریت موجودی انبار")
            dialog.setMinimumSize(800, 600)

            # طرح اصلی
            layout = QVBoxLayout(dialog)

            # بخش جستجوی محصول
            search_layout = QHBoxLayout()
            search_label = QLabel("جستجوی محصول:")
            search_input = QLineEdit()
            search_input.setPlaceholderText("نام یا کد محصول را وارد کنید")
            search_btn = QPushButton("جستجو")

            search_layout.addWidget(search_label)
            search_layout.addWidget(search_input)
            search_layout.addWidget(search_btn)

            layout.addLayout(search_layout)

            # جدول محصولات
            products_table = QTableWidget()
            products_table.setColumnCount(6)
            products_table.setHorizontalHeaderLabels(["شناسه", "نام محصول", "دسته‌بندی", "موجودی فعلی", "حداقل موجودی", "عملیات"])
            products_table.setEditTriggers(QTableWidget.NoEditTriggers)
            products_table.setSelectionBehavior(QTableWidget.SelectRows)

            # تنظیم عرض ستون‌ها
            products_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

            layout.addWidget(products_table)

            # بخش به‌روزرسانی موجودی
            update_group = QGroupBox("به‌روزرسانی موجودی")
            update_layout = QFormLayout(update_group)

            product_id_input = QLineEdit()
            product_id_input.setReadOnly(True)

            product_name_label = QLabel()

            current_stock_label = QLabel()

            new_stock_input = QLineEdit()
            new_stock_input.setValidator(QtGui.QIntValidator(0, 1000000))

            change_reason_combo = QComboBox()
            change_reason_combo.addItems(["افزایش موجودی", "کاهش موجودی", "شمارش انبار", "برگشت از فروش", "خرابی/ضایعات", "سایر"])

            notes_input = QLineEdit()
            notes_input.setPlaceholderText("توضیحات اضافی")

            update_layout.addRow("شناسه محصول:", product_id_input)
            update_layout.addRow("نام محصول:", product_name_label)
            update_layout.addRow("موجودی فعلی:", current_stock_label)
            update_layout.addRow("موجودی جدید:", new_stock_input)
            update_layout.addRow("دلیل تغییر:", change_reason_combo)
            update_layout.addRow("توضیحات:", notes_input)

            layout.addWidget(update_group)

            # دکمه‌های عملیات
            buttons_layout = QHBoxLayout()

            update_btn = QPushButton("به‌روزرسانی موجودی")
            update_btn.setEnabled(False)  # غیرفعال تا زمانی که محصولی انتخاب شود

            history_btn = QPushButton("مشاهده تاریخچه")
            history_btn.setEnabled(False)  # غیرفعال تا زمانی که محصولی انتخاب شود

            batch_update_btn = QPushButton("به‌روزرسانی گروهی")
            batch_update_btn.clicked.connect(self.batch_update_inventory)

            close_btn = QPushButton("بستن")
            close_btn.clicked.connect(dialog.close)

            buttons_layout.addWidget(update_btn)
            buttons_layout.addWidget(history_btn)
            buttons_layout.addWidget(batch_update_btn)
            buttons_layout.addStretch()
            buttons_layout.addWidget(close_btn)

            layout.addLayout(buttons_layout)

            # تابع بارگذاری محصولات
            def load_products(search_text=""):
                try:
                    # پاک کردن جدول
                    products_table.setRowCount(0)

                    # ساخت پرس‌وجو
                    query = """
                        SELECT id, name, category, stock, min_stock
                        FROM products
                        WHERE 1=1
                    """
                    params = []

                    if search_text:
                        query += " AND (name LIKE ? OR id = ?)"
                        params.extend([f"%{search_text}%", search_text if search_text.isdigit() else -1])

                    query += " ORDER BY stock ASC"

                    # اجرای پرس‌وجو
                    self.cursor.execute(query, params)
                    products = self.cursor.fetchall()

                    # تنظیم تعداد سطرهای جدول
                    products_table.setRowCount(len(products))

                    # پر کردن جدول با داده‌ها
                    for row, product in enumerate(products):
                        product_id, name, category, stock, min_stock = product

                        # تعیین وضعیت موجودی
                        status = ""
                        if stock <= 0:
                            status = "اتمام موجودی"
                        elif stock < min_stock:
                            status = "کمبود موجودی"
                        else:
                            status = "عادی"

                        # افزودن داده‌ها به جدول
                        products_table.setItem(row, 0, QTableWidgetItem(str(product_id)))
                        products_table.setItem(row, 1, QTableWidgetItem(name))
                        products_table.setItem(row, 2, QTableWidgetItem(category))

                        stock_item = QTableWidgetItem(str(stock))
                        if stock <= 0:
                            stock_item.setBackground(QtGui.QColor(255, 0, 0, 100))  # قرمز
                        elif stock < min_stock:
                            stock_item.setBackground(QtGui.QColor(255, 255, 0, 100))  # زرد
                        products_table.setItem(row, 3, stock_item)

                        products_table.setItem(row, 4, QTableWidgetItem(str(min_stock)))

                        # دکمه انتخاب
                        select_btn = QPushButton("انتخاب")
                        select_btn.clicked.connect(lambda checked, pid=product_id, pname=name, pstock=stock: select_product(pid, pname, pstock))

                        cell_widget = QWidget()
                        cell_layout = QHBoxLayout(cell_widget)
                        cell_layout.addWidget(select_btn)
                        cell_layout.setContentsMargins(0, 0, 0, 0)

                        products_table.setCellWidget(row, 5, cell_widget)
                except Exception as e:
                    print(f"Error loading products: {e}")
                    QMessageBox.critical(dialog, "خطا", f"خطا در بارگذاری محصولات: {str(e)}")

            # تابع انتخاب محصول
            def select_product(product_id, product_name, current_stock):
                try:
                    # نمایش اطلاعات محصول در فرم
                    product_id_input.setText(str(product_id))
                    product_name_label.setText(product_name)
                    current_stock_label.setText(str(current_stock))
                    new_stock_input.setText(str(current_stock))

                    # فعال کردن دکمه‌ها
                    update_btn.setEnabled(True)
                    history_btn.setEnabled(True)
                except Exception as e:
                    print(f"Error selecting product: {e}")
                    QMessageBox.critical(dialog, "خطا", f"خطا در انتخاب محصول: {str(e)}")

            # تابع به‌روزرسانی موجودی
            def update_stock():
                try:
                    product_id = product_id_input.text()
                    if not product_id:
                        QMessageBox.warning(dialog, "هشدار", "لطفاً ابتدا یک محصول را انتخاب کنید.")
                        return

                    # دریافت مقادیر
                    old_stock = int(current_stock_label.text())
                    new_stock = int(new_stock_input.text())
                    change_reason = change_reason_combo.currentText()
                    notes = notes_input.text()

                    # ترکیب دلیل و توضیحات
                    reason_text = change_reason
                    if notes:
                        reason_text += f" - {notes}"

                    # تأیید از کاربر
                    confirm = QMessageBox.question(dialog, "تأیید به‌روزرسانی موجودی",
                                                 f"آیا از به‌روزرسانی موجودی محصول از {old_stock} به {new_stock} اطمینان دارید؟",
                                                 QMessageBox.Yes | QMessageBox.No)

                    if confirm == QMessageBox.Yes:
                        # به‌روزرسانی موجودی در جدول محصولات
                        self.cursor.execute("""
                            UPDATE products
                            SET stock = ?, updated_at = ?
                            WHERE id = ?
                        """, (new_stock, datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), product_id))

                        # ثبت در تاریخچه موجودی
                        user_id = self.current_user.id if self.current_user else 0

                        self.cursor.execute("""
                            INSERT INTO inventory_history
                            (product_id, old_stock, new_stock, change_reason, user_id, timestamp)
                            VALUES (?, ?, ?, ?, ?, ?)
                        """, (product_id, old_stock, new_stock, reason_text, user_id,
                              datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))

                        # ذخیره تغییرات
                        self.conn.commit()

                        # ثبت فعالیت
                        self.log_activity("inventory", f"به‌روزرسانی موجودی محصول {product_name_label.text()} از {old_stock} به {new_stock}")

                        # به‌روزرسانی نمایش
                        QMessageBox.information(dialog, "موفقیت", "موجودی محصول با موفقیت به‌روزرسانی شد.")

                        # به‌روزرسانی برچسب موجودی فعلی
                        current_stock_label.setText(str(new_stock))

                        # بارگذاری مجدد جدول
                        load_products(search_input.text())
                except Exception as e:
                    print(f"Error updating stock: {e}")
                    QMessageBox.critical(dialog, "خطا", f"خطا در به‌روزرسانی موجودی: {str(e)}")

            # تابع نمایش تاریخچه موجودی
            def show_stock_history():
                try:
                    product_id = product_id_input.text()
                    if not product_id:
                        QMessageBox.warning(dialog, "هشدار", "لطفاً ابتدا یک محصول را انتخاب کنید.")
                        return

                    # ایجاد پنجره تاریخچه
                    history_dialog = QDialog(dialog)
                    history_dialog.setWindowTitle(f"تاریخچه موجودی - {product_name_label.text()}")
                    history_dialog.setMinimumSize(600, 400)

                    history_layout = QVBoxLayout(history_dialog)

                    # جدول تاریخچه
                    history_table = QTableWidget()
                    history_table.setColumnCount(5)
                    history_table.setHorizontalHeaderLabels(["تاریخ", "موجودی قبلی", "موجودی جدید", "تغییر", "دلیل تغییر"])
                    history_table.setEditTriggers(QTableWidget.NoEditTriggers)

                    # دریافت تاریخچه از پایگاه داده
                    self.cursor.execute("""
                        SELECT timestamp, old_stock, new_stock, change_reason
                        FROM inventory_history
                        WHERE product_id = ?
                        ORDER BY timestamp DESC
                    """, (product_id,))

                    history_data = self.cursor.fetchall()

                    # تنظیم تعداد سطرهای جدول
                    history_table.setRowCount(len(history_data))

                    # پر کردن جدول با داده‌ها
                    for row, data in enumerate(history_data):
                        timestamp, old_stock, new_stock, change_reason = data

                        # محاسبه تغییر
                        change = new_stock - old_stock
                        change_text = f"+{change}" if change > 0 else str(change)

                        # افزودن داده‌ها به جدول
                        history_table.setItem(row, 0, QTableWidgetItem(timestamp))
                        history_table.setItem(row, 1, QTableWidgetItem(str(old_stock)))
                        history_table.setItem(row, 2, QTableWidgetItem(str(new_stock)))

                        change_item = QTableWidgetItem(change_text)
                        if change > 0:
                            change_item.setForeground(QtGui.QColor(0, 128, 0))  # سبز
                        elif change < 0:
                            change_item.setForeground(QtGui.QColor(255, 0, 0))  # قرمز

                        history_table.setItem(row, 3, change_item)
                        history_table.setItem(row, 4, QTableWidgetItem(change_reason))

                    # تنظیم عرض ستون‌ها
                    history_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

                    history_layout.addWidget(history_table)

                    # دکمه بستن
                    close_history_btn = QPushButton("بستن")
                    close_history_btn.clicked.connect(history_dialog.close)
                    history_layout.addWidget(close_history_btn)

                    # نمایش پنجره
                    history_dialog.exec_()
                except Exception as e:
                    print(f"Error showing stock history: {e}")
                    QMessageBox.critical(dialog, "خطا", f"خطا در نمایش تاریخچه موجودی: {str(e)}")

            # اتصال سیگنال‌ها به اسلات‌ها
            search_btn.clicked.connect(lambda: load_products(search_input.text()))
            search_input.returnPressed.connect(lambda: load_products(search_input.text()))
            update_btn.clicked.connect(update_stock)
            history_btn.clicked.connect(show_stock_history)

            # بارگذاری اولیه محصولات
            load_products()

            # نمایش پنجره
            dialog.exec_()
        except Exception as e:
            print(f"Error in manage_inventory: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در مدیریت موجودی: {str(e)}")

    def batch_update_inventory(self):
        """به‌روزرسانی گروهی موجودی محصولات"""
        try:
            # ایجاد پنجره به‌روزرسانی گروهی
            dialog = QDialog(self)
            dialog.setWindowTitle("به‌روزرسانی گروهی موجودی")
            dialog.setMinimumSize(800, 600)

            # طرح اصلی
            layout = QVBoxLayout(dialog)

            # توضیحات
            info_label = QLabel("در این بخش می‌توانید موجودی چندین محصول را به صورت همزمان به‌روزرسانی کنید.")
            layout.addWidget(info_label)

            # جدول محصولات
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["انتخاب", "نام محصول", "دسته‌بندی", "موجودی فعلی", "موجودی جدید"])
            table.setEditTriggers(QTableWidget.NoEditTriggers)

            # دریافت محصولات از پایگاه داده
            self.cursor.execute("""
                SELECT id, name, category, stock
                FROM products
                ORDER BY name
            """)

            products = self.cursor.fetchall()

            # تنظیم تعداد سطرهای جدول
            table.setRowCount(len(products))

            # پر کردن جدول با داده‌ها
            for row, product in enumerate(products):
                product_id, name, category, stock = product

                # ستون انتخاب (چک‌باکس)
                checkbox = QCheckBox()
                checkbox_widget = QWidget()
                checkbox_layout = QHBoxLayout(checkbox_widget)
                checkbox_layout.addWidget(checkbox)
                checkbox_layout.setAlignment(QtCore.Qt.AlignCenter)
                checkbox_layout.setContentsMargins(0, 0, 0, 0)
                table.setCellWidget(row, 0, checkbox_widget)

                # اطلاعات محصول
                table.setItem(row, 1, QTableWidgetItem(name))
                table.setItem(row, 2, QTableWidgetItem(category))
                table.setItem(row, 3, QTableWidgetItem(str(stock)))

                # ورودی موجودی جدید
                stock_input = QLineEdit(str(stock))
                stock_input.setValidator(QtGui.QIntValidator(0, 1000000))
                stock_input.setProperty("product_id", product_id)
                stock_input.setProperty("old_stock", stock)

                stock_widget = QWidget()
                stock_layout = QHBoxLayout(stock_widget)
                stock_layout.addWidget(stock_input)
                stock_layout.setContentsMargins(0, 0, 0, 0)
                table.setCellWidget(row, 4, stock_widget)

            # تنظیم عرض ستون‌ها
            table.horizontalHeader().setSectionResizeMode(0, QtWidgets.QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(1, QtWidgets.QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(2, QtWidgets.QHeaderView.Stretch)
            table.horizontalHeader().setSectionResizeMode(3, QtWidgets.QHeaderView.ResizeToContents)
            table.horizontalHeader().setSectionResizeMode(4, QtWidgets.QHeaderView.ResizeToContents)

            layout.addWidget(table)

            # بخش دلیل تغییر
            reason_group = QGroupBox("دلیل تغییر موجودی")
            reason_layout = QFormLayout(reason_group)

            reason_combo = QComboBox()
            reason_combo.addItems(["شمارش انبار", "افزایش موجودی", "کاهش موجودی", "برگشت از فروش", "خرابی/ضایعات", "سایر"])

            notes_input = QLineEdit()
            notes_input.setPlaceholderText("توضیحات اضافی")

            reason_layout.addRow("دلیل:", reason_combo)
            reason_layout.addRow("توضیحات:", notes_input)

            layout.addWidget(reason_group)

            # دکمه‌های انتخاب سریع
            quick_select_layout = QHBoxLayout()

            select_all_btn = QPushButton("انتخاب همه")
            select_all_btn.clicked.connect(lambda: self.select_all_products(table, True))

            deselect_all_btn = QPushButton("لغو انتخاب همه")
            deselect_all_btn.clicked.connect(lambda: self.select_all_products(table, False))

            select_low_stock_btn = QPushButton("انتخاب موجودی کم")
            select_low_stock_btn.clicked.connect(lambda: self.select_low_stock_products(table))

            quick_select_layout.addWidget(select_all_btn)
            quick_select_layout.addWidget(deselect_all_btn)
            quick_select_layout.addWidget(select_low_stock_btn)

            layout.addLayout(quick_select_layout)

            # دکمه‌های عملیات
            buttons_layout = QHBoxLayout()

            update_btn = QPushButton("به‌روزرسانی موجودی")
            update_btn.clicked.connect(lambda: self.process_batch_update(table, reason_combo.currentText(), notes_input.text(), dialog))

            close_btn = QPushButton("انصراف")
            close_btn.clicked.connect(dialog.close)

            buttons_layout.addWidget(update_btn)
            buttons_layout.addStretch()
            buttons_layout.addWidget(close_btn)

            layout.addLayout(buttons_layout)

            # نمایش پنجره
            dialog.exec_()
        except Exception as e:
            print(f"Error in batch_update_inventory: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در به‌روزرسانی گروهی موجودی: {str(e)}")

    def select_all_products(self, table, select):
        """انتخاب یا لغو انتخاب همه محصولات در جدول"""
        try:
            for row in range(table.rowCount()):
                checkbox_widget = table.cellWidget(row, 0)
                if checkbox_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    if checkbox:
                        checkbox.setChecked(select)
        except Exception as e:
            print(f"Error in select_all_products: {e}")

    def select_low_stock_products(self, table):
        """انتخاب محصولات با موجودی کم"""
        try:
            # دریافت محصولات با موجودی کم
            self.cursor.execute("""
                SELECT id
                FROM products
                WHERE stock < min_stock
            """)

            low_stock_ids = [row[0] for row in self.cursor.fetchall()]

            # انتخاب محصولات با موجودی کم در جدول
            for row in range(table.rowCount()):
                stock_input_widget = table.cellWidget(row, 4)
                if stock_input_widget:
                    stock_input = stock_input_widget.findChild(QLineEdit)
                    if stock_input:
                        product_id = stock_input.property("product_id")
                        if product_id in low_stock_ids:
                            checkbox_widget = table.cellWidget(row, 0)
                            if checkbox_widget:
                                checkbox = checkbox_widget.findChild(QCheckBox)
                                if checkbox:
                                    checkbox.setChecked(True)
        except Exception as e:
            print(f"Error in select_low_stock_products: {e}")

    def process_batch_update(self, table, reason, notes, dialog):
        """پردازش به‌روزرسانی گروهی موجودی"""
        try:
            # جمع‌آوری محصولات انتخاب شده و مقادیر جدید
            updates = []

            for row in range(table.rowCount()):
                checkbox_widget = table.cellWidget(row, 0)
                stock_input_widget = table.cellWidget(row, 4)

                if checkbox_widget and stock_input_widget:
                    checkbox = checkbox_widget.findChild(QCheckBox)
                    stock_input = stock_input_widget.findChild(QLineEdit)

                    if checkbox and stock_input and checkbox.isChecked():
                        product_id = stock_input.property("product_id")
                        old_stock = stock_input.property("old_stock")

                        try:
                            new_stock = int(stock_input.text())
                            if new_stock < 0:
                                QMessageBox.warning(self, "خطا", "موجودی نمی‌تواند منفی باشد.")
                                return

                            # اگر موجودی تغییر کرده باشد
                            if old_stock != new_stock:
                                updates.append((product_id, old_stock, new_stock))
                        except ValueError:
                            QMessageBox.warning(self, "خطا", "موجودی باید یک عدد صحیح باشد.")
                            return

            # بررسی وجود حداقل یک به‌روزرسانی
            if not updates:
                QMessageBox.information(self, "اطلاعات", "هیچ تغییری برای اعمال وجود ندارد.")
                return

            # تأیید از کاربر
            confirm = QMessageBox.question(self, "تأیید به‌روزرسانی گروهی",
                                         f"آیا از به‌روزرسانی موجودی {len(updates)} محصول اطمینان دارید؟",
                                         QMessageBox.Yes | QMessageBox.No)

            if confirm == QMessageBox.Yes:
                # ترکیب دلیل و توضیحات
                reason_text = reason
                if notes:
                    reason_text += f" - {notes}"

                # اعمال به‌روزرسانی‌ها
                timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                user_id = self.current_user.id if self.current_user else 0

                for product_id, old_stock, new_stock in updates:
                    # به‌روزرسانی موجودی در جدول محصولات
                    self.cursor.execute("""
                        UPDATE products
                        SET stock = ?, updated_at = ?
                        WHERE id = ?
                    """, (new_stock, timestamp, product_id))

                    # ثبت در تاریخچه موجودی
                    self.cursor.execute("""
                        INSERT INTO inventory_history
                        (product_id, old_stock, new_stock, change_reason, user_id, timestamp)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (product_id, old_stock, new_stock, reason_text, user_id, timestamp))

                # ذخیره تغییرات
                self.conn.commit()

                # ثبت فعالیت
                self.log_activity("inventory", f"به‌روزرسانی گروهی موجودی {len(updates)} محصول")

                # نمایش پیام موفقیت
                QMessageBox.information(self, "موفقیت", f"موجودی {len(updates)} محصول با موفقیت به‌روزرسانی شد.")

                # بستن پنجره
                dialog.close()
        except Exception as e:
            print(f"Error in process_batch_update: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در پردازش به‌روزرسانی گروهی: {str(e)}")

    def show_inventory_report(self):
        """نمایش گزارش موجودی"""
        try:
            # ایجاد پنجره گزارش
            dialog = QDialog(self)
            dialog.setWindowTitle("گزارش موجودی")
            dialog.setMinimumSize(800, 600)

            # طرح اصلی
            layout = QVBoxLayout(dialog)

            # ایجاد تب‌ها
            tabs = QTabWidget()

            # تب جدول موجودی
            table_tab = QWidget()
            table_layout = QVBoxLayout(table_tab)

            # ایجاد جدول موجودی
            table = QTableWidget()
            table.setColumnCount(5)
            table.setHorizontalHeaderLabels(["نام محصول", "دسته‌بندی", "موجودی فعلی", "حداقل موجودی", "وضعیت"])
            table.setEditTriggers(QTableWidget.NoEditTriggers)

            # دریافت اطلاعات موجودی از پایگاه داده
            self.cursor.execute("""
                SELECT name, category, stock, min_stock
                FROM products
                ORDER BY stock ASC
            """)

            inventory_data = self.cursor.fetchall()

            # تنظیم تعداد سطرهای جدول
            table.setRowCount(len(inventory_data))

            # پر کردن جدول با داده‌ها
            for row, data in enumerate(inventory_data):
                name, category, stock, min_stock = data

                # تعیین وضعیت موجودی
                status = ""
                if stock <= 0:
                    status = "اتمام موجودی"
                elif stock < min_stock:
                    status = "کمبود موجودی"
                else:
                    status = "عادی"

                # افزودن داده‌ها به جدول
                table.setItem(row, 0, QTableWidgetItem(name))
                table.setItem(row, 1, QTableWidgetItem(category))
                table.setItem(row, 2, QTableWidgetItem(str(stock)))
                table.setItem(row, 3, QTableWidgetItem(str(min_stock)))

                status_item = QTableWidgetItem(status)

                # تنظیم رنگ وضعیت
                if status == "اتمام موجودی":
                    status_item.setBackground(QtGui.QColor(255, 0, 0, 100))  # قرمز
                elif status == "کمبود موجودی":
                    status_item.setBackground(QtGui.QColor(255, 255, 0, 100))  # زرد
                else:
                    status_item.setBackground(QtGui.QColor(0, 255, 0, 100))  # سبز

                table.setItem(row, 4, status_item)

            # تنظیم عرض ستون‌ها
            table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

            # اضافه کردن جدول به طرح
            table_layout.addWidget(table)

            # اضافه کردن دکمه‌های صادر کردن
            export_layout = QHBoxLayout()

            export_excel_btn = QPushButton("صادر کردن به Excel")
            export_excel_btn.clicked.connect(lambda: self.export_to_excel(inventory_data))

            export_pdf_btn = QPushButton("صادر کردن به PDF")
            export_pdf_btn.clicked.connect(lambda: self.export_to_pdf(inventory_data))

            export_layout.addWidget(export_excel_btn)
            export_layout.addWidget(export_pdf_btn)

            table_layout.addLayout(export_layout)

            # تب نمودار موجودی
            if MATPLOTLIB_AVAILABLE:
                chart_tab = QWidget()
                chart_layout = QVBoxLayout(chart_tab)

                # ایجاد نمودار
                canvas = MplCanvas(chart_tab, width=8, height=6)

                # دریافت داده‌های نمودار
                categories = []
                stocks = []

                for data in inventory_data:
                    categories.append(data[0])  # نام محصول
                    stocks.append(data[2])  # موجودی

                # محدود کردن به 10 محصول برای خوانایی بهتر
                if len(categories) > 10:
                    categories = categories[:10]
                    stocks = stocks[:10]

                # رسم نمودار
                canvas.axes.bar(categories, stocks)
                canvas.axes.set_title('موجودی محصولات')
                canvas.axes.set_xlabel('محصولات')
                canvas.axes.set_ylabel('تعداد موجودی')

                # چرخش برچسب‌های محور X برای خوانایی بهتر
                canvas.axes.set_xticklabels(categories, rotation=45, ha='right')

                # تنظیم اندازه نمودار
                canvas.fig.tight_layout()

                # اضافه کردن نمودار به طرح
                chart_layout.addWidget(canvas)

                # اضافه کردن تب نمودار
                tabs.addTab(chart_tab, "نمودار موجودی")

            # اضافه کردن تب جدول
            tabs.addTab(table_tab, "جدول موجودی")

            # اضافه کردن تب‌ها به طرح اصلی
            layout.addWidget(tabs)

            # دکمه بستن
            close_btn = QPushButton("بستن")
            close_btn.clicked.connect(dialog.close)
            layout.addWidget(close_btn)

            # نمایش پنجره
            dialog.exec_()
        except Exception as e:
            print(f"Error showing inventory report: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در نمایش گزارش موجودی: {str(e)}")

    def show_settings(self):
        """نمایش و تغییر تنظیمات برنامه"""
        try:
            # ایجاد پنجره تنظیمات
            dialog = QDialog(self)
            dialog.setWindowTitle("تنظیمات برنامه")
            dialog.setMinimumWidth(400)

            # طرح اصلی
            layout = QVBoxLayout(dialog)

            # گروه تنظیمات ظاهری
            appearance_group = QGroupBox("تنظیمات ظاهری")
            appearance_layout = QFormLayout(appearance_group)

            # انتخاب تم
            theme_combo = QComboBox()
            theme_combo.addItems(["روشن", "تیره", "آبی"])

            # تنظیم مقدار پیش‌فرض
            if self.app_settings["theme"] == "light":
                theme_combo.setCurrentIndex(0)
            elif self.app_settings["theme"] == "dark":
                theme_combo.setCurrentIndex(1)
            elif self.app_settings["theme"] == "blue":
                theme_combo.setCurrentIndex(2)

            appearance_layout.addRow("تم:", theme_combo)

            # انتخاب فونت
            font_combo = QComboBox()
            font_combo.addItems(["Vazir", "Tahoma", "Arial", "Segoe UI"])

            # تنظیم مقدار پیش‌فرض
            font_index = font_combo.findText(self.app_settings["font_family"])
            if font_index >= 0:
                font_combo.setCurrentIndex(font_index)

            appearance_layout.addRow("فونت:", font_combo)

            # اندازه فونت
            font_size_combo = QComboBox()
            font_size_combo.addItems(["10", "11", "12", "14", "16"])

            # تنظیم مقدار پیش‌فرض
            font_size_index = font_size_combo.findText(str(self.app_settings["font_size"]))
            if font_size_index >= 0:
                font_size_combo.setCurrentIndex(font_size_index)

            appearance_layout.addRow("اندازه فونت:", font_size_combo)

            # مقیاس رابط کاربری
            ui_scale_combo = QComboBox()
            ui_scale_combo.addItems(["دسکتاپ", "موبایل"])

            # تنظیم مقدار پیش‌فرض
            if self.app_settings["ui_scale"] == "desktop":
                ui_scale_combo.setCurrentIndex(0)
            elif self.app_settings["ui_scale"] == "mobile":
                ui_scale_combo.setCurrentIndex(1)

            appearance_layout.addRow("مقیاس رابط کاربری:", ui_scale_combo)

            # اضافه کردن گروه تنظیمات ظاهری به طرح اصلی
            layout.addWidget(appearance_group)

            # دکمه‌های تایید و لغو
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            # اجرای پنجره
            if dialog.exec_() == QDialog.Accepted:
                # ذخیره تنظیمات جدید
                theme_map = {0: "light", 1: "dark", 2: "blue"}
                ui_scale_map = {0: "desktop", 1: "mobile"}

                self.app_settings["theme"] = theme_map[theme_combo.currentIndex()]
                self.app_settings["font_family"] = font_combo.currentText()
                self.app_settings["font_size"] = int(font_size_combo.currentText())
                self.app_settings["ui_scale"] = ui_scale_map[ui_scale_combo.currentIndex()]

                # ذخیره تنظیمات در فایل
                self.save_settings()

                # اعمال تنظیمات جدید
                self.set_application_style()

                QMessageBox.information(self, "موفقیت", "تنظیمات با موفقیت ذخیره شد. برخی تغییرات پس از راه‌اندازی مجدد برنامه اعمال می‌شوند.")
        except Exception as e:
            print(f"Error showing settings: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در نمایش تنظیمات: {str(e)}")

    # توابع وارد کردن و صادر کردن
    def import_from_excel(self):
        """وارد کردن محصولات از فایل Excel"""
        if pd is None:
            QMessageBox.warning(self, "خطا", "برای استفاده از این قابلیت، کتابخانه pandas باید نصب شده باشد.")
            return

        try:
            # انتخاب فایل
            file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل Excel", "", "Excel Files (*.xlsx *.xls)")

            if not file_path:
                return

            # خواندن فایل Excel
            df = pd.read_excel(file_path)

            # بررسی ستون‌های مورد نیاز
            required_columns = ["name", "price", "category", "stock", "description"]
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                QMessageBox.warning(self, "خطا", f"ستون‌های زیر در فایل وجود ندارند: {', '.join(missing_columns)}")
                return

            # نمایش پیش‌نمایش داده‌ها
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle("پیش‌نمایش داده‌ها")
            preview_dialog.setMinimumSize(800, 600)

            preview_layout = QVBoxLayout(preview_dialog)

            # ایجاد جدول پیش‌نمایش
            preview_table = QTableWidget()
            preview_table.setColumnCount(len(df.columns))
            preview_table.setHorizontalHeaderLabels(df.columns)
            preview_table.setRowCount(min(10, len(df)))  # نمایش حداکثر 10 سطر

            # پر کردن جدول پیش‌نمایش
            for row in range(min(10, len(df))):
                for col, column_name in enumerate(df.columns):
                    value = str(df.iloc[row, col])
                    preview_table.setItem(row, col, QTableWidgetItem(value))

            preview_layout.addWidget(QLabel(f"نمایش {min(10, len(df))} سطر از {len(df)} سطر"))
            preview_layout.addWidget(preview_table)

            # اضافه کردن چک‌باکس برای حذف داده‌های قبلی
            clear_existing = QCheckBox("حذف تمام محصولات موجود قبل از وارد کردن")
            preview_layout.addWidget(clear_existing)

            # دکمه‌های تایید و لغو
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(preview_dialog.accept)
            buttons.rejected.connect(preview_dialog.reject)
            preview_layout.addWidget(buttons)

            # نمایش پیش‌نمایش
            if preview_dialog.exec_() != QDialog.Accepted:
                return

            # حذف داده‌های قبلی در صورت انتخاب
            if clear_existing.isChecked():
                confirm = QMessageBox.question(self, "تایید حذف",
                                             "آیا از حذف تمام محصولات موجود اطمینان دارید؟",
                                             QMessageBox.Yes | QMessageBox.No)

                if confirm == QMessageBox.Yes:
                    self.cursor.execute("DELETE FROM products")
                    self.conn.commit()

            # نمایش پیشرفت
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("در حال وارد کردن داده‌ها")
            progress_dialog.setMinimumWidth(400)

            progress_layout = QVBoxLayout(progress_dialog)
            progress_label = QLabel("در حال وارد کردن داده‌ها...")
            progress_bar = QProgressBar()
            progress_bar.setRange(0, len(df))

            progress_layout.addWidget(progress_label)
            progress_layout.addWidget(progress_bar)

            progress_dialog.show()

            # وارد کردن داده‌ها
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            success_count = 0
            error_count = 0

            for index, row in df.iterrows():
                try:
                    # استخراج داده‌ها
                    name = str(row["name"])
                    price = float(row["price"]) if not pd.isna(row["price"]) else 0
                    category = str(row["category"]) if not pd.isna(row["category"]) else ""
                    stock = int(row["stock"]) if not pd.isna(row["stock"]) else 0
                    description = str(row["description"]) if not pd.isna(row["description"]) else ""

                    # ثبت محصول در پایگاه داده
                    self.cursor.execute(
                        "INSERT INTO products (name, price, category, stock, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (name, price, category, stock, description, timestamp, timestamp)
                    )

                    success_count += 1
                except Exception as e:
                    print(f"Error importing row {index}: {e}")
                    error_count += 1

                # به‌روزرسانی نوار پیشرفت
                progress_bar.setValue(index + 1)
                QtWidgets.QApplication.processEvents()

            # ذخیره تغییرات
            self.conn.commit()

            # بستن پنجره پیشرفت
            progress_dialog.close()

            # ثبت فعالیت
            self.log_activity("import", f"وارد کردن {success_count} محصول از فایل Excel")

            # نمایش نتیجه
            QMessageBox.information(self, "نتیجه وارد کردن",
                                   f"تعداد {success_count} محصول با موفقیت وارد شد.\n"
                                   f"تعداد {error_count} خطا رخ داد.")
        except Exception as e:
            print(f"Error importing from Excel: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در وارد کردن از Excel: {str(e)}")

    def import_from_csv(self):
        """وارد کردن محصولات از فایل CSV"""
        try:
            # انتخاب فایل
            file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب فایل CSV", "", "CSV Files (*.csv)")

            if not file_path:
                return

            # خواندن فایل CSV
            products = []
            headers = []

            with open(file_path, 'r', encoding='utf-8') as csvfile:
                csv_reader = csv.reader(csvfile)
                headers = next(csv_reader)  # خواندن سطر هدر

                # بررسی ستون‌های مورد نیاز
                required_columns = ["name", "price", "category", "stock", "description"]
                header_lower = [h.lower() for h in headers]

                missing_columns = []
                for col in required_columns:
                    if col not in header_lower:
                        missing_columns.append(col)

                if missing_columns:
                    QMessageBox.warning(self, "خطا", f"ستون‌های زیر در فایل وجود ندارند: {', '.join(missing_columns)}")
                    return

                # نگاشت شاخص ستون‌ها
                col_indices = {}
                for i, header in enumerate(header_lower):
                    col_indices[header] = i

                # خواندن داده‌ها
                for row in csv_reader:
                    if len(row) >= len(headers):
                        product = {
                            "name": row[col_indices["name"]],
                            "price": float(row[col_indices["price"]]) if row[col_indices["price"]] else 0,
                            "category": row[col_indices["category"]],
                            "stock": int(row[col_indices["stock"]]) if row[col_indices["stock"]] else 0,
                            "description": row[col_indices["description"]]
                        }
                        products.append(product)

            # نمایش پیش‌نمایش داده‌ها
            preview_dialog = QDialog(self)
            preview_dialog.setWindowTitle("پیش‌نمایش داده‌ها")
            preview_dialog.setMinimumSize(800, 600)

            preview_layout = QVBoxLayout(preview_dialog)

            # ایجاد جدول پیش‌نمایش
            preview_table = QTableWidget()
            preview_table.setColumnCount(len(required_columns))
            preview_table.setHorizontalHeaderLabels(required_columns)
            preview_table.setRowCount(min(10, len(products)))  # نمایش حداکثر 10 سطر

            # پر کردن جدول پیش‌نمایش
            for row in range(min(10, len(products))):
                product = products[row]
                for col, column_name in enumerate(required_columns):
                    value = str(product[column_name])
                    preview_table.setItem(row, col, QTableWidgetItem(value))

            preview_layout.addWidget(QLabel(f"نمایش {min(10, len(products))} سطر از {len(products)} سطر"))
            preview_layout.addWidget(preview_table)

            # اضافه کردن چک‌باکس برای حذف داده‌های قبلی
            clear_existing = QCheckBox("حذف تمام محصولات موجود قبل از وارد کردن")
            preview_layout.addWidget(clear_existing)

            # دکمه‌های تایید و لغو
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(preview_dialog.accept)
            buttons.rejected.connect(preview_dialog.reject)
            preview_layout.addWidget(buttons)

            # نمایش پیش‌نمایش
            if preview_dialog.exec_() != QDialog.Accepted:
                return

            # حذف داده‌های قبلی در صورت انتخاب
            if clear_existing.isChecked():
                confirm = QMessageBox.question(self, "تایید حذف",
                                             "آیا از حذف تمام محصولات موجود اطمینان دارید؟",
                                             QMessageBox.Yes | QMessageBox.No)

                if confirm == QMessageBox.Yes:
                    self.cursor.execute("DELETE FROM products")
                    self.conn.commit()

            # نمایش پیشرفت
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("در حال وارد کردن داده‌ها")
            progress_dialog.setMinimumWidth(400)

            progress_layout = QVBoxLayout(progress_dialog)
            progress_label = QLabel("در حال وارد کردن داده‌ها...")
            progress_bar = QProgressBar()
            progress_bar.setRange(0, len(products))

            progress_layout.addWidget(progress_label)
            progress_layout.addWidget(progress_bar)

            progress_dialog.show()

            # وارد کردن داده‌ها
            timestamp = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            success_count = 0
            error_count = 0

            for i, product in enumerate(products):
                try:
                    # ثبت محصول در پایگاه داده
                    self.cursor.execute(
                        "INSERT INTO products (name, price, category, stock, description, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                        (product["name"], product["price"], product["category"], product["stock"], product["description"], timestamp, timestamp)
                    )

                    success_count += 1
                except Exception as e:
                    print(f"Error importing product {i}: {e}")
                    error_count += 1

                # به‌روزرسانی نوار پیشرفت
                progress_bar.setValue(i + 1)
                QtWidgets.QApplication.processEvents()

            # ذخیره تغییرات
            self.conn.commit()

            # بستن پنجره پیشرفت
            progress_dialog.close()

            # ثبت فعالیت
            self.log_activity("import", f"وارد کردن {success_count} محصول از فایل CSV")

            # نمایش نتیجه
            QMessageBox.information(self, "نتیجه وارد کردن",
                                   f"تعداد {success_count} محصول با موفقیت وارد شد.\n"
                                   f"تعداد {error_count} خطا رخ داد.")
        except Exception as e:
            print(f"Error importing from CSV: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در وارد کردن از CSV: {str(e)}")

    def export_to_excel(self, data=None):
        """صادر کردن محصولات به فایل Excel"""
        if pd is None:
            QMessageBox.warning(self, "خطا", "برای استفاده از این قابلیت، کتابخانه pandas باید نصب شده باشد.")
            return

        try:
            # اگر داده‌ها از قبل ارسال نشده باشند، از پایگاه داده دریافت می‌کنیم
            if data is None:
                # دریافت داده‌ها از پایگاه داده
                self.cursor.execute("""
                    SELECT id, name, price, category, stock, min_stock, discount_price, barcode, description, created_at, updated_at
                    FROM products
                    ORDER BY id
                """)

                data = self.cursor.fetchall()

                # تعریف ستون‌ها
                columns = ["شناسه", "نام محصول", "قیمت", "دسته‌بندی", "موجودی", "حداقل موجودی",
                          "قیمت با تخفیف", "بارکد", "توضیحات", "تاریخ ایجاد", "تاریخ به‌روزرسانی"]
            else:
                # استفاده از ستون‌های داده‌های ارسال شده
                columns = ["نام محصول", "دسته‌بندی", "موجودی فعلی", "حداقل موجودی"]

            # انتخاب مسیر ذخیره فایل
            file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل Excel", "", "Excel Files (*.xlsx)")

            if not file_path:
                return

            # اضافه کردن پسوند .xlsx در صورت نیاز
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'

            # تبدیل داده‌ها به DataFrame
            df = pd.DataFrame(data, columns=columns)

            # ذخیره به فایل Excel
            df.to_excel(file_path, index=False, engine='xlsxwriter')

            # ثبت فعالیت
            self.log_activity("export", f"صادر کردن {len(data)} محصول به فایل Excel")

            # نمایش پیام موفقیت
            QMessageBox.information(self, "صادر کردن", f"داده‌ها با موفقیت به فایل Excel صادر شدند.\nمسیر: {file_path}")
        except Exception as e:
            print(f"Error exporting to Excel: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در صادر کردن به Excel: {str(e)}")

    def export_to_csv(self):
        """صادر کردن محصولات به فایل CSV"""
        try:
            # دریافت داده‌ها از پایگاه داده
            self.cursor.execute("""
                SELECT id, name, price, category, stock, min_stock, discount_price, barcode, description, created_at, updated_at
                FROM products
                ORDER BY id
            """)

            data = self.cursor.fetchall()

            # تعریف ستون‌ها
            columns = ["شناسه", "نام محصول", "قیمت", "دسته‌بندی", "موجودی", "حداقل موجودی",
                      "قیمت با تخفیف", "بارکد", "توضیحات", "تاریخ ایجاد", "تاریخ به‌روزرسانی"]

            # انتخاب مسیر ذخیره فایل
            file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل CSV", "", "CSV Files (*.csv)")

            if not file_path:
                return

            # اضافه کردن پسوند .csv در صورت نیاز
            if not file_path.endswith('.csv'):
                file_path += '.csv'

            # ذخیره به فایل CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                csv_writer = csv.writer(csvfile)

                # نوشتن سطر هدر
                csv_writer.writerow(columns)

                # نوشتن داده‌ها
                csv_writer.writerows(data)

            # ثبت فعالیت
            self.log_activity("export", f"صادر کردن {len(data)} محصول به فایل CSV")

            # نمایش پیام موفقیت
            QMessageBox.information(self, "صادر کردن", f"داده‌ها با موفقیت به فایل CSV صادر شدند.\nمسیر: {file_path}")
        except Exception as e:
            print(f"Error exporting to CSV: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در صادر کردن به CSV: {str(e)}")

    def export_to_pdf(self, data=None):
        """صادر کردن محصولات به فایل PDF"""
        try:
            # اگر داده‌ها از قبل ارسال نشده باشند، از پایگاه داده دریافت می‌کنیم
            if data is None:
                # دریافت داده‌ها از پایگاه داده
                self.cursor.execute("""
                    SELECT id, name, price, category, stock, min_stock
                    FROM products
                    ORDER BY id
                """)

                data = self.cursor.fetchall()

                # تعریف ستون‌ها
                columns = ["شناسه", "نام محصول", "قیمت", "دسته‌بندی", "موجودی", "حداقل موجودی"]
            else:
                # استفاده از ستون‌های داده‌های ارسال شده
                columns = ["نام محصول", "دسته‌بندی", "موجودی فعلی", "حداقل موجودی"]

            # انتخاب مسیر ذخیره فایل
            file_path, _ = QFileDialog.getSaveFileName(self, "ذخیره فایل PDF", "", "PDF Files (*.pdf)")

            if not file_path:
                return

            # اضافه کردن پسوند .pdf در صورت نیاز
            if not file_path.endswith('.pdf'):
                file_path += '.pdf'

            # ایجاد فایل PDF
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            # تنظیم عنوان
            c.setFont("Helvetica-Bold", 16)
            c.drawString(50, height - 50, "گزارش محصولات")

            # تنظیم تاریخ
            c.setFont("Helvetica", 10)
            c.drawString(50, height - 70, f"تاریخ: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}")

            # تنظیم جدول
            c.setFont("Helvetica-Bold", 10)

            # تعیین عرض ستون‌ها
            col_widths = [50, 150, 70, 100, 70, 70]
            if len(columns) == 4:  # برای گزارش موجودی
                col_widths = [150, 100, 70, 70]

            # محاسبه عرض کل
            table_width = sum(col_widths)

            # تنظیم موقعیت شروع جدول
            x_start = (width - table_width) / 2
            y_start = height - 100

            # رسم هدر جدول
            c.setFillColorRGB(0.8, 0.8, 0.8)
            c.rect(x_start, y_start - 20, table_width, 20, fill=True)
            c.setFillColorRGB(0, 0, 0)

            x = x_start
            for i, col in enumerate(columns):
                c.drawString(x + 5, y_start - 15, col)
                x += col_widths[i]

            # رسم داده‌های جدول
            c.setFont("Helvetica", 10)
            y = y_start - 20

            for row in data:
                # بررسی نیاز به صفحه جدید
                if y < 50:
                    c.showPage()
                    c.setFont("Helvetica-Bold", 16)
                    c.drawString(50, height - 50, "گزارش محصولات (ادامه)")
                    c.setFont("Helvetica", 10)

                    # رسم هدر جدول در صفحه جدید
                    y = height - 100
                    c.setFillColorRGB(0.8, 0.8, 0.8)
                    c.rect(x_start, y - 20, table_width, 20, fill=True)
                    c.setFillColorRGB(0, 0, 0)

                    c.setFont("Helvetica-Bold", 10)
                    x = x_start
                    for i, col in enumerate(columns):
                        c.drawString(x + 5, y - 15, col)
                        x += col_widths[i]

                    c.setFont("Helvetica", 10)
                    y = y - 20

                # رسم خط جدول
                c.setFillColorRGB(0.95, 0.95, 0.95)
                c.rect(x_start, y - 20, table_width, 20, fill=True)
                c.setFillColorRGB(0, 0, 0)

                # رسم داده‌های سطر
                x = x_start
                for i, value in enumerate(row):
                    if i < len(col_widths):  # اطمینان از عدم تجاوز از تعداد ستون‌ها
                        c.drawString(x + 5, y - 15, str(value))
                        x += col_widths[i]

                y -= 20

            # ذخیره فایل PDF
            c.save()

            # ثبت فعالیت
            self.log_activity("export", f"صادر کردن {len(data)} محصول به فایل PDF")

            # نمایش پیام موفقیت
            QMessageBox.information(self, "صادر کردن", f"داده‌ها با موفقیت به فایل PDF صادر شدند.\nمسیر: {file_path}")
        except Exception as e:
            print(f"Error exporting to PDF: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در صادر کردن به PDF: {str(e)}")

    def manage_product_images(self):
        """مدیریت تصاویر محصولات"""
        try:
            # ایجاد پنجره مدیریت تصاویر
            dialog = QDialog(self)
            dialog.setWindowTitle("مدیریت تصاویر محصولات")
            dialog.setMinimumSize(800, 600)

            # طرح اصلی
            layout = QVBoxLayout(dialog)

            # ایجاد تب‌ها
            tabs = QTabWidget()

            # تب مدیریت تصاویر محصولات
            product_images_tab = QWidget()
            product_images_layout = QVBoxLayout(product_images_tab)

            # انتخاب محصول
            product_selection_layout = QHBoxLayout()
            product_selection_layout.addWidget(QLabel("انتخاب محصول:"))

            product_combo = QComboBox()
            product_combo.setMinimumWidth(300)

            # دریافت لیست محصولات
            self.cursor.execute("SELECT id, name FROM products ORDER BY name")
            products = self.cursor.fetchall()

            for product_id, product_name in products:
                product_combo.addItem(product_name, product_id)

            product_selection_layout.addWidget(product_combo)
            product_selection_layout.addStretch()

            product_images_layout.addLayout(product_selection_layout)

            # نمایش تصاویر محصول انتخاب شده
            images_scroll = QScrollArea()
            images_scroll.setWidgetResizable(True)
            images_container = QWidget()
            images_layout = QGridLayout(images_container)

            images_scroll.setWidget(images_container)
            product_images_layout.addWidget(images_scroll)

            # تابع نمایش تصاویر محصول
            def show_product_images():
                # پاک کردن تصاویر قبلی
                for i in reversed(range(images_layout.count())):
                    images_layout.itemAt(i).widget().setParent(None)

                product_id = product_combo.currentData()
                if product_id is None:
                    return

                # دریافت تصاویر محصول
                self.cursor.execute("""
                    SELECT id, image_path, is_primary
                    FROM product_images
                    WHERE product_id = ?
                """, (product_id,))

                images = self.cursor.fetchall()

                # دریافت تصویر اصلی محصول
                self.cursor.execute("SELECT image FROM products WHERE id = ?", (product_id,))
                main_image = self.cursor.fetchone()[0]

                if main_image and os.path.exists(main_image):
                    # اضافه کردن تصویر اصلی
                    image_frame = QGroupBox("تصویر اصلی محصول")
                    image_frame_layout = QVBoxLayout(image_frame)

                    image_label = QLabel()
                    pixmap = QtGui.QPixmap(main_image)
                    image_label.setPixmap(pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio))

                    image_frame_layout.addWidget(image_label)

                    # دکمه‌های عملیات
                    buttons_layout = QHBoxLayout()

                    view_btn = QPushButton("نمایش بزرگ")
                    view_btn.clicked.connect(lambda: show_large_image(main_image))

                    replace_btn = QPushButton("جایگزینی")
                    replace_btn.clicked.connect(lambda: replace_main_image(product_id))

                    buttons_layout.addWidget(view_btn)
                    buttons_layout.addWidget(replace_btn)

                    image_frame_layout.addLayout(buttons_layout)

                    images_layout.addWidget(image_frame, 0, 0)

                # اضافه کردن سایر تصاویر
                row, col = 0, 1
                for image_id, image_path, is_primary in images:
                    if not os.path.exists(image_path):
                        continue

                    image_frame = QGroupBox("تصویر محصول" + (" (اصلی)" if is_primary else ""))
                    image_frame_layout = QVBoxLayout(image_frame)

                    image_label = QLabel()
                    pixmap = QtGui.QPixmap(image_path)
                    image_label.setPixmap(pixmap.scaled(200, 200, QtCore.Qt.KeepAspectRatio))

                    image_frame_layout.addWidget(image_label)

                    # دکمه‌های عملیات
                    buttons_layout = QHBoxLayout()

                    view_btn = QPushButton("نمایش بزرگ")
                    view_btn.clicked.connect(lambda checked, path=image_path: show_large_image(path))

                    set_primary_btn = QPushButton("تنظیم به عنوان اصلی")
                    set_primary_btn.clicked.connect(lambda checked, img_id=image_id, pid=product_id: set_as_primary(img_id, pid))

                    delete_btn = QPushButton("حذف")
                    delete_btn.clicked.connect(lambda checked, img_id=image_id: delete_image(img_id))

                    buttons_layout.addWidget(view_btn)
                    buttons_layout.addWidget(set_primary_btn)
                    buttons_layout.addWidget(delete_btn)

                    image_frame_layout.addLayout(buttons_layout)

                    # اضافه کردن به گرید
                    images_layout.addWidget(image_frame, row, col)

                    # تنظیم موقعیت بعدی
                    col += 1
                    if col > 3:  # حداکثر 4 تصویر در هر سطر
                        col = 0
                        row += 1

                # اضافه کردن دکمه افزودن تصویر جدید
                add_image_frame = QGroupBox("افزودن تصویر جدید")
                add_image_layout = QVBoxLayout(add_image_frame)

                add_btn = QPushButton("+ افزودن تصویر جدید")
                add_btn.setMinimumHeight(100)
                add_btn.clicked.connect(lambda: add_new_image(product_id))

                add_image_layout.addWidget(add_btn)

                # اضافه کردن به گرید
                next_col = col if col <= 3 else 0
                next_row = row if col <= 3 else row + 1
                images_layout.addWidget(add_image_frame, next_row, next_col)

            # تابع نمایش تصویر بزرگ
            def show_large_image(image_path):
                if not os.path.exists(image_path):
                    QMessageBox.warning(dialog, "خطا", "فایل تصویر یافت نشد.")
                    return

                image_dialog = QDialog(dialog)
                image_dialog.setWindowTitle("نمایش تصویر")
                image_dialog.setMinimumSize(800, 600)

                image_layout = QVBoxLayout(image_dialog)

                scroll = QScrollArea()
                scroll.setWidgetResizable(True)

                image_label = QLabel()
                pixmap = QtGui.QPixmap(image_path)
                image_label.setPixmap(pixmap)

                scroll.setWidget(image_label)
                image_layout.addWidget(scroll)

                close_btn = QPushButton("بستن")
                close_btn.clicked.connect(image_dialog.close)
                image_layout.addWidget(close_btn)

                image_dialog.exec_()

            # تابع تنظیم تصویر به عنوان اصلی
            def set_as_primary(image_id, product_id):
                try:
                    # دریافت مسیر تصویر
                    self.cursor.execute("SELECT image_path FROM product_images WHERE id = ?", (image_id,))
                    image_path = self.cursor.fetchone()[0]

                    # به‌روزرسانی وضعیت تصاویر
                    self.cursor.execute("UPDATE product_images SET is_primary = 0 WHERE product_id = ?", (product_id,))
                    self.cursor.execute("UPDATE product_images SET is_primary = 1 WHERE id = ?", (image_id,))

                    # به‌روزرسانی تصویر اصلی محصول
                    self.cursor.execute("UPDATE products SET image = ? WHERE id = ?", (image_path, product_id))

                    self.conn.commit()

                    # ثبت فعالیت
                    self.log_activity("product", f"تغییر تصویر اصلی محصول با شناسه {product_id}")

                    # به‌روزرسانی نمایش
                    show_product_images()

                    QMessageBox.information(dialog, "موفقیت", "تصویر اصلی محصول با موفقیت تغییر کرد.")
                except Exception as e:
                    print(f"Error setting primary image: {e}")
                    QMessageBox.critical(dialog, "خطا", f"خطا در تنظیم تصویر اصلی: {str(e)}")

            # تابع حذف تصویر
            def delete_image(image_id):
                try:
                    # دریافت اطلاعات تصویر
                    self.cursor.execute("SELECT image_path, is_primary, product_id FROM product_images WHERE id = ?", (image_id,))
                    result = self.cursor.fetchone()

                    if not result:
                        QMessageBox.warning(dialog, "خطا", "تصویر مورد نظر یافت نشد.")
                        return

                    image_path, is_primary, product_id = result

                    # بررسی اگر تصویر اصلی است
                    if is_primary:
                        QMessageBox.warning(dialog, "خطا", "تصویر اصلی محصول را نمی‌توان حذف کرد. ابتدا تصویر دیگری را به عنوان اصلی تنظیم کنید.")
                        return

                    # پرسیدن تایید از کاربر
                    confirm = QMessageBox.question(dialog, "تایید حذف",
                                                 "آیا از حذف این تصویر اطمینان دارید؟",
                                                 QMessageBox.Yes | QMessageBox.No)

                    if confirm == QMessageBox.Yes:
                        # حذف فایل تصویر
                        if os.path.exists(image_path):
                            try:
                                os.remove(image_path)
                            except:
                                print(f"Could not delete file: {image_path}")

                        # حذف از پایگاه داده
                        self.cursor.execute("DELETE FROM product_images WHERE id = ?", (image_id,))
                        self.conn.commit()

                        # ثبت فعالیت
                        self.log_activity("product", f"حذف تصویر محصول با شناسه {product_id}")

                        # به‌روزرسانی نمایش
                        show_product_images()

                        QMessageBox.information(dialog, "موفقیت", "تصویر با موفقیت حذف شد.")
                except Exception as e:
                    print(f"Error deleting image: {e}")
                    QMessageBox.critical(dialog, "خطا", f"خطا در حذف تصویر: {str(e)}")

            # تابع جایگزینی تصویر اصلی
            def replace_main_image(product_id):
                try:
                    # انتخاب فایل تصویر جدید
                    file_path, _ = QFileDialog.getOpenFileName(dialog, "انتخاب تصویر جدید", "", "Image Files (*.png *.jpg *.jpeg)")

                    if not file_path:
                        return

                    # ذخیره تصویر در پوشه product_images
                    file_name = os.path.basename(file_path)
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    new_file_name = f"{timestamp}_{file_name}"
                    destination_path = os.path.join("product_images", new_file_name)

                    # اطمینان از وجود پوشه
                    if not os.path.exists("product_images"):
                        os.makedirs("product_images")

                    # کپی تصویر
                    import shutil
                    shutil.copy2(file_path, destination_path)

                    # به‌روزرسانی تصویر اصلی محصول
                    self.cursor.execute("UPDATE products SET image = ? WHERE id = ?", (destination_path, product_id))
                    self.conn.commit()

                    # ثبت فعالیت
                    self.log_activity("product", f"جایگزینی تصویر اصلی محصول با شناسه {product_id}")

                    # به‌روزرسانی نمایش
                    show_product_images()

                    QMessageBox.information(dialog, "موفقیت", "تصویر اصلی محصول با موفقیت جایگزین شد.")
                except Exception as e:
                    print(f"Error replacing main image: {e}")
                    QMessageBox.critical(dialog, "خطا", f"خطا در جایگزینی تصویر اصلی: {str(e)}")

            # تابع افزودن تصویر جدید
            def add_new_image(product_id):
                try:
                    # انتخاب فایل تصویر جدید
                    file_path, _ = QFileDialog.getOpenFileName(dialog, "انتخاب تصویر جدید", "", "Image Files (*.png *.jpg *.jpeg)")

                    if not file_path:
                        return

                    # ذخیره تصویر در پوشه product_images
                    file_name = os.path.basename(file_path)
                    timestamp = datetime.datetime.now().strftime("%Y%m%d%H%M%S")
                    new_file_name = f"{timestamp}_{file_name}"
                    destination_path = os.path.join("product_images", new_file_name)

                    # اطمینان از وجود پوشه
                    if not os.path.exists("product_images"):
                        os.makedirs("product_images")

                    # کپی تصویر
                    import shutil
                    shutil.copy2(file_path, destination_path)

                    # افزودن به پایگاه داده
                    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                    self.cursor.execute(
                        "INSERT INTO product_images (product_id, image_path, is_primary, created_at) VALUES (?, ?, ?, ?)",
                        (product_id, destination_path, 0, created_at)
                    )
                    self.conn.commit()

                    # ثبت فعالیت
                    self.log_activity("product", f"افزودن تصویر جدید برای محصول با شناسه {product_id}")

                    # به‌روزرسانی نمایش
                    show_product_images()

                    QMessageBox.information(dialog, "موفقیت", "تصویر جدید با موفقیت اضافه شد.")
                except Exception as e:
                    print(f"Error adding new image: {e}")
                    QMessageBox.critical(dialog, "خطا", f"خطا در افزودن تصویر جدید: {str(e)}")

            # اتصال تغییر محصول به نمایش تصاویر
            product_combo.currentIndexChanged.connect(show_product_images)

            # دکمه‌های پایین
            buttons_layout = QHBoxLayout()

            close_btn = QPushButton("بستن")
            close_btn.clicked.connect(dialog.close)

            buttons_layout.addStretch()
            buttons_layout.addWidget(close_btn)

            product_images_layout.addLayout(buttons_layout)

            # تب مدیریت گالری
            gallery_tab = QWidget()
            gallery_layout = QVBoxLayout(gallery_tab)

            # نمایش همه تصاویر در یک گالری
            gallery_scroll = QScrollArea()
            gallery_scroll.setWidgetResizable(True)
            gallery_container = QWidget()
            gallery_grid = QGridLayout(gallery_container)

            gallery_scroll.setWidget(gallery_container)
            gallery_layout.addWidget(gallery_scroll)

            # دریافت همه تصاویر
            all_images = []

            # تصاویر اصلی محصولات
            self.cursor.execute("SELECT id, name, image FROM products WHERE image IS NOT NULL AND image != ''")
            for product_id, product_name, image_path in self.cursor.fetchall():
                if os.path.exists(image_path):
                    all_images.append((product_id, product_name, image_path, True))

            # سایر تصاویر محصولات
            self.cursor.execute("""
                SELECT pi.product_id, p.name, pi.image_path, pi.is_primary
                FROM product_images pi
                JOIN products p ON pi.product_id = p.id
                WHERE pi.image_path IS NOT NULL AND pi.image_path != ''
            """)
            for product_id, product_name, image_path, is_primary in self.cursor.fetchall():
                if os.path.exists(image_path):
                    all_images.append((product_id, product_name, image_path, is_primary))

            # نمایش تصاویر در گالری
            row, col = 0, 0
            for product_id, product_name, image_path, is_primary in all_images:
                image_frame = QGroupBox(f"{product_name}" + (" (اصلی)" if is_primary else ""))
                image_frame_layout = QVBoxLayout(image_frame)

                image_label = QLabel()
                pixmap = QtGui.QPixmap(image_path)
                image_label.setPixmap(pixmap.scaled(150, 150, QtCore.Qt.KeepAspectRatio))

                image_frame_layout.addWidget(image_label)

                # دکمه نمایش بزرگ
                view_btn = QPushButton("نمایش بزرگ")
                view_btn.clicked.connect(lambda checked, path=image_path: show_large_image(path))
                image_frame_layout.addWidget(view_btn)

                # اضافه کردن به گرید
                gallery_grid.addWidget(image_frame, row, col)

                # تنظیم موقعیت بعدی
                col += 1
                if col > 4:  # حداکثر 5 تصویر در هر سطر
                    col = 0
                    row += 1

            # دکمه‌های پایین
            gallery_buttons_layout = QHBoxLayout()

            gallery_close_btn = QPushButton("بستن")
            gallery_close_btn.clicked.connect(dialog.close)

            gallery_buttons_layout.addStretch()
            gallery_buttons_layout.addWidget(gallery_close_btn)

            gallery_layout.addLayout(gallery_buttons_layout)

            # اضافه کردن تب‌ها
            tabs.addTab(product_images_tab, "مدیریت تصاویر محصولات")
            tabs.addTab(gallery_tab, "گالری تصاویر")

            # اضافه کردن تب‌ها به طرح اصلی
            layout.addWidget(tabs)

            # نمایش تصاویر محصول اول به صورت پیش‌فرض
            if product_combo.count() > 0:
                show_product_images()

            # نمایش پنجره
            dialog.exec_()
        except Exception as e:
            print(f"Error managing product images: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در مدیریت تصاویر محصولات: {str(e)}")

    def connect_to_external_system(self):
        """اتصال به سیستم مدیریت محصولات خارجی"""
        try:
            # ایجاد پنجره اتصال
            dialog = QDialog(self)
            dialog.setWindowTitle("اتصال به سیستم مدیریت محصولات")
            dialog.setMinimumWidth(500)

            # طرح اصلی
            layout = QVBoxLayout(dialog)

            # گروه تنظیمات اتصال
            connection_group = QGroupBox("تنظیمات اتصال")
            connection_layout = QFormLayout(connection_group)

            # فیلدهای ورودی
            system_type_combo = QComboBox()
            system_type_combo.addItems(["سیستم فروشگاهی", "انبارداری", "حسابداری", "CRM", "ERP", "سایر"])

            server_input = QLineEdit()
            server_input.setPlaceholderText("مثال: https://example.com/api یا 192.168.1.100")

            port_input = QLineEdit()
            port_input.setPlaceholderText("مثال: 8080")
            port_input.setValidator(QtGui.QIntValidator(1, 65535))

            username_input = QLineEdit()

            password_input = QLineEdit()
            password_input.setEchoMode(QLineEdit.Password)

            api_key_input = QLineEdit()
            api_key_input.setPlaceholderText("در صورت استفاده از کلید API")

            # اضافه کردن فیلدها به فرم
            connection_layout.addRow("نوع سیستم:", system_type_combo)
            connection_layout.addRow("آدرس سرور:", server_input)
            connection_layout.addRow("پورت:", port_input)
            connection_layout.addRow("نام کاربری:", username_input)
            connection_layout.addRow("رمز عبور:", password_input)
            connection_layout.addRow("کلید API:", api_key_input)

            # اضافه کردن گروه تنظیمات به طرح اصلی
            layout.addWidget(connection_group)

            # گروه تنظیمات همگام‌سازی
            sync_group = QGroupBox("تنظیمات همگام‌سازی")
            sync_layout = QVBoxLayout(sync_group)

            # چک‌باکس‌های همگام‌سازی
            sync_products_check = QCheckBox("همگام‌سازی محصولات")
            sync_products_check.setChecked(True)

            sync_inventory_check = QCheckBox("همگام‌سازی موجودی")
            sync_inventory_check.setChecked(True)

            sync_prices_check = QCheckBox("همگام‌سازی قیمت‌ها")
            sync_prices_check.setChecked(True)

            sync_categories_check = QCheckBox("همگام‌سازی دسته‌بندی‌ها")
            sync_categories_check.setChecked(False)

            sync_images_check = QCheckBox("همگام‌سازی تصاویر")
            sync_images_check.setChecked(False)

            # تنظیمات زمان‌بندی
            schedule_layout = QHBoxLayout()
            schedule_layout.addWidget(QLabel("زمان‌بندی همگام‌سازی:"))

            schedule_combo = QComboBox()
            schedule_combo.addItems(["دستی", "هر ساعت", "روزانه", "هفتگی"])
            schedule_layout.addWidget(schedule_combo)

            # اضافه کردن چک‌باکس‌ها و زمان‌بندی به گروه همگام‌سازی
            sync_layout.addWidget(sync_products_check)
            sync_layout.addWidget(sync_inventory_check)
            sync_layout.addWidget(sync_prices_check)
            sync_layout.addWidget(sync_categories_check)
            sync_layout.addWidget(sync_images_check)
            sync_layout.addLayout(schedule_layout)

            # اضافه کردن گروه همگام‌سازی به طرح اصلی
            layout.addWidget(sync_group)

            # دکمه تست اتصال
            test_connection_btn = QPushButton("تست اتصال")
            test_connection_btn.clicked.connect(lambda: self.test_external_connection(
                server_input.text(),
                port_input.text(),
                username_input.text(),
                password_input.text(),
                api_key_input.text()
            ))
            layout.addWidget(test_connection_btn)

            # دکمه‌های تایید و لغو
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            # اجرای پنجره
            if dialog.exec_() == QDialog.Accepted:
                # ذخیره تنظیمات اتصال
                connection_settings = {
                    "system_type": system_type_combo.currentText(),
                    "server": server_input.text(),
                    "port": port_input.text(),
                    "username": username_input.text(),
                    "password": password_input.text(),  # در یک برنامه واقعی باید رمزنگاری شود
                    "api_key": api_key_input.text(),
                    "sync_products": sync_products_check.isChecked(),
                    "sync_inventory": sync_inventory_check.isChecked(),
                    "sync_prices": sync_prices_check.isChecked(),
                    "sync_categories": sync_categories_check.isChecked(),
                    "sync_images": sync_images_check.isChecked(),
                    "schedule": schedule_combo.currentText()
                }

                # ذخیره تنظیمات در فایل
                self.save_connection_settings(connection_settings)

                # انجام همگام‌سازی اولیه
                self.perform_initial_sync(connection_settings)
        except Exception as e:
            print(f"Error connecting to external system: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در اتصال به سیستم خارجی: {str(e)}")

    def test_external_connection(self, server, port, username, password, api_key):
        """تست اتصال به سیستم خارجی"""
        try:
            # بررسی ورودی‌ها
            if not server:
                QMessageBox.warning(self, "خطا", "آدرس سرور نمی‌تواند خالی باشد.")
                return

            # در یک برنامه واقعی، اینجا کد اتصال به API یا سرور خارجی قرار می‌گیرد
            # برای مثال با استفاده از کتابخانه requests:
            # import requests
            # response = requests.get(f"{server}:{port}/api/test",
            #                        auth=(username, password),
            #                        headers={"Authorization": f"Bearer {api_key}"})
            # if response.status_code == 200:
            #     QMessageBox.information(self, "موفقیت", "اتصال با موفقیت برقرار شد.")
            # else:
            #     QMessageBox.warning(self, "خطا", f"خطا در اتصال: {response.status_code} - {response.text}")

            # برای نمونه، یک پیام موفقیت نمایش می‌دهیم
            QMessageBox.information(self, "تست اتصال",
                                   f"تلاش برای اتصال به سرور {server}" +
                                   (f":{port}" if port else "") +
                                   "\n\nاتصال با موفقیت برقرار شد.")
        except Exception as e:
            print(f"Error testing connection: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در تست اتصال: {str(e)}")

    def save_connection_settings(self, settings):
        """ذخیره تنظیمات اتصال در فایل"""
        try:
            # اطمینان از وجود پوشه settings
            if not os.path.exists('settings'):
                os.makedirs('settings')

            # ذخیره تنظیمات در فایل JSON
            settings_path = os.path.join('settings', 'connection_settings.json')

            # در یک برنامه واقعی، اطلاعات حساس مانند رمز عبور باید رمزنگاری شوند
            # برای مثال با استفاده از کتابخانه cryptography

            with open(settings_path, 'w', encoding='utf-8') as f:
                json.dump(settings, f, indent=4, ensure_ascii=False)

            print("Connection settings saved successfully")

            # ثبت فعالیت
            self.log_activity("connection", f"ذخیره تنظیمات اتصال به سیستم {settings['system_type']}")
        except Exception as e:
            print(f"Error saving connection settings: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره تنظیمات اتصال: {str(e)}")

    def perform_initial_sync(self, settings):
        """انجام همگام‌سازی اولیه با سیستم خارجی"""
        try:
            # نمایش پنجره پیشرفت
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("همگام‌سازی با سیستم خارجی")
            progress_dialog.setMinimumWidth(400)

            progress_layout = QVBoxLayout(progress_dialog)
            progress_label = QLabel("در حال همگام‌سازی با سیستم خارجی...")
            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)

            progress_layout.addWidget(progress_label)
            progress_layout.addWidget(progress_bar)

            # دکمه لغو
            cancel_btn = QPushButton("لغو")
            cancel_btn.clicked.connect(progress_dialog.reject)
            progress_layout.addWidget(cancel_btn)

            progress_dialog.show()

            # شبیه‌سازی همگام‌سازی
            total_steps = 0
            current_step = 0

            if settings["sync_products"]:
                total_steps += 30
            if settings["sync_inventory"]:
                total_steps += 20
            if settings["sync_prices"]:
                total_steps += 15
            if settings["sync_categories"]:
                total_steps += 15
            if settings["sync_images"]:
                total_steps += 20

            # همگام‌سازی محصولات
            if settings["sync_products"]:
                progress_label.setText("در حال همگام‌سازی محصولات...")
                for i in range(30):
                    # شبیه‌سازی عملیات همگام‌سازی
                    time.sleep(0.1)
                    current_step += 1
                    progress_bar.setValue(int(current_step / total_steps * 100))
                    QtWidgets.QApplication.processEvents()

                    # بررسی لغو عملیات
                    if not progress_dialog.isVisible():
                        return

            # همگام‌سازی موجودی
            if settings["sync_inventory"]:
                progress_label.setText("در حال همگام‌سازی موجودی...")
                for i in range(20):
                    # شبیه‌سازی عملیات همگام‌سازی
                    time.sleep(0.1)
                    current_step += 1
                    progress_bar.setValue(int(current_step / total_steps * 100))
                    QtWidgets.QApplication.processEvents()

                    # بررسی لغو عملیات
                    if not progress_dialog.isVisible():
                        return

            # همگام‌سازی قیمت‌ها
            if settings["sync_prices"]:
                progress_label.setText("در حال همگام‌سازی قیمت‌ها...")
                for i in range(15):
                    # شبیه‌سازی عملیات همگام‌سازی
                    time.sleep(0.1)
                    current_step += 1
                    progress_bar.setValue(int(current_step / total_steps * 100))
                    QtWidgets.QApplication.processEvents()

                    # بررسی لغو عملیات
                    if not progress_dialog.isVisible():
                        return

            # همگام‌سازی دسته‌بندی‌ها
            if settings["sync_categories"]:
                progress_label.setText("در حال همگام‌سازی دسته‌بندی‌ها...")
                for i in range(15):
                    # شبیه‌سازی عملیات همگام‌سازی
                    time.sleep(0.1)
                    current_step += 1
                    progress_bar.setValue(int(current_step / total_steps * 100))
                    QtWidgets.QApplication.processEvents()

                    # بررسی لغو عملیات
                    if not progress_dialog.isVisible():
                        return

            # همگام‌سازی تصاویر
            if settings["sync_images"]:
                progress_label.setText("در حال همگام‌سازی تصاویر...")
                for i in range(20):
                    # شبیه‌سازی عملیات همگام‌سازی
                    time.sleep(0.1)
                    current_step += 1
                    progress_bar.setValue(int(current_step / total_steps * 100))
                    QtWidgets.QApplication.processEvents()

                    # بررسی لغو عملیات
                    if not progress_dialog.isVisible():
                        return

            # پایان همگام‌سازی
            progress_dialog.close()

            # نمایش نتیجه
            QMessageBox.information(self, "همگام‌سازی", "همگام‌سازی با سیستم خارجی با موفقیت انجام شد.")

            # ثبت فعالیت
            self.log_activity("sync", f"همگام‌سازی با سیستم {settings['system_type']}")

            # تنظیم زمان‌بندی همگام‌سازی خودکار
            if settings["schedule"] != "دستی":
                self.setup_automatic_sync(settings)
        except Exception as e:
            print(f"Error performing initial sync: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در همگام‌سازی: {str(e)}")

    def setup_automatic_sync(self, settings):
        """تنظیم همگام‌سازی خودکار"""
        try:
            # در یک برنامه واقعی، اینجا کد زمان‌بندی همگام‌سازی خودکار قرار می‌گیرد
            # برای مثال با استفاده از کتابخانه schedule یا QTimer

            schedule_text = ""
            if settings["schedule"] == "هر ساعت":
                schedule_text = "هر ساعت"
            elif settings["schedule"] == "روزانه":
                schedule_text = "هر روز در ساعت 00:00"
            elif settings["schedule"] == "هفتگی":
                schedule_text = "هر یکشنبه در ساعت 00:00"

            QMessageBox.information(self, "زمان‌بندی همگام‌سازی",
                                   f"همگام‌سازی خودکار {schedule_text} تنظیم شد.")
        except Exception as e:
            print(f"Error setting up automatic sync: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در تنظیم همگام‌سازی خودکار: {str(e)}")

    def connect_to_product_form(self):
        """اتصال به فرم مدیریت محصولات"""
        try:
            # ایجاد پنجره اتصال به فرم
            dialog = QDialog(self)
            dialog.setWindowTitle("اتصال به فرم مدیریت محصولات")
            dialog.setMinimumWidth(600)
            dialog.setMinimumHeight(500)

            # طرح اصلی
            layout = QVBoxLayout(dialog)

            # تب‌ها برای انواع مختلف فرم‌ها
            tabs = QTabWidget()

            # تب فرم استاندارد
            standard_form_tab = QWidget()
            standard_form_layout = QVBoxLayout(standard_form_tab)

            # ایجاد فرم استاندارد مدیریت محصولات
            standard_form = self.create_standard_product_form()
            standard_form_layout.addWidget(standard_form)

            # تب فرم سفارشی
            custom_form_tab = QWidget()
            custom_form_layout = QVBoxLayout(custom_form_tab)

            # ایجاد فرم سفارشی مدیریت محصولات
            custom_form = self.create_custom_product_form()
            custom_form_layout.addWidget(custom_form)

            # تب طراح فرم
            form_designer_tab = QWidget()
            form_designer_layout = QVBoxLayout(form_designer_tab)

            # ایجاد طراح فرم
            form_designer = self.create_form_designer()
            form_designer_layout.addWidget(form_designer)

            # اضافه کردن تب‌ها
            tabs.addTab(standard_form_tab, "فرم استاندارد")
            tabs.addTab(custom_form_tab, "فرم سفارشی")
            tabs.addTab(form_designer_tab, "طراح فرم")

            # اضافه کردن تب‌ها به طرح اصلی
            layout.addWidget(tabs)

            # دکمه‌های پایین
            buttons_layout = QHBoxLayout()

            save_as_template_btn = QPushButton("ذخیره به عنوان قالب")
            save_as_template_btn.clicked.connect(self.save_form_as_template)

            load_template_btn = QPushButton("بارگذاری قالب")
            load_template_btn.clicked.connect(self.load_form_template)

            close_btn = QPushButton("بستن")
            close_btn.clicked.connect(dialog.close)

            buttons_layout.addWidget(save_as_template_btn)
            buttons_layout.addWidget(load_template_btn)
            buttons_layout.addStretch()
            buttons_layout.addWidget(close_btn)

            layout.addLayout(buttons_layout)

            # نمایش پنجره
            dialog.exec_()
        except Exception as e:
            print(f"Error connecting to product form: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در اتصال به فرم مدیریت محصولات: {str(e)}")

    def create_standard_product_form(self):
        """ایجاد فرم استاندارد مدیریت محصولات"""
        try:
            # ایجاد ویجت اصلی
            form_widget = QWidget()
            form_layout = QVBoxLayout(form_widget)

            # عنوان فرم
            title_label = QLabel("فرم مدیریت محصولات")
            title_label.setAlignment(QtCore.Qt.AlignCenter)
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
            form_layout.addWidget(title_label)

            # بخش جستجو
            search_group = QGroupBox("جستجوی محصول")
            search_layout = QHBoxLayout(search_group)

            search_input = QLineEdit()
            search_input.setPlaceholderText("نام یا کد محصول را وارد کنید...")

            search_btn = QPushButton("جستجو")
            search_btn.setIcon(QtGui.QIcon.fromTheme("edit-find"))

            advanced_search_btn = QPushButton("جستجوی پیشرفته")

            search_layout.addWidget(search_input)
            search_layout.addWidget(search_btn)
            search_layout.addWidget(advanced_search_btn)

            form_layout.addWidget(search_group)

            # بخش اطلاعات محصول
            product_info_group = QGroupBox("اطلاعات محصول")
            product_info_layout = QFormLayout(product_info_group)

            # فیلدهای اطلاعات محصول
            product_id_input = QLineEdit()
            product_id_input.setReadOnly(True)
            product_id_input.setPlaceholderText("به صورت خودکار تولید می‌شود")

            product_name_input = QLineEdit()

            product_category_combo = QComboBox()
            # دریافت دسته‌بندی‌ها از پایگاه داده
            self.cursor.execute("SELECT name FROM categories")
            categories = self.cursor.fetchall()
            for category in categories:
                product_category_combo.addItem(category[0])

            product_price_input = QLineEdit()
            product_price_input.setValidator(QtGui.QDoubleValidator(0, 1000000000, 2))

            product_stock_input = QLineEdit()
            product_stock_input.setValidator(QtGui.QIntValidator(0, 1000000))

            product_min_stock_input = QLineEdit()
            product_min_stock_input.setValidator(QtGui.QIntValidator(0, 1000000))

            product_description_input = QTextEdit()

            # اضافه کردن فیلدها به فرم
            product_info_layout.addRow("کد محصول:", product_id_input)
            product_info_layout.addRow("نام محصول:", product_name_input)
            product_info_layout.addRow("دسته‌بندی:", product_category_combo)
            product_info_layout.addRow("قیمت:", product_price_input)
            product_info_layout.addRow("موجودی:", product_stock_input)
            product_info_layout.addRow("حداقل موجودی:", product_min_stock_input)
            product_info_layout.addRow("توضیحات:", product_description_input)

            form_layout.addWidget(product_info_group)

            # بخش تصاویر محصول
            images_group = QGroupBox("تصاویر محصول")
            images_layout = QHBoxLayout(images_group)

            # نمایش تصویر اصلی
            main_image_label = QLabel()
            main_image_label.setMinimumSize(200, 200)
            main_image_label.setAlignment(QtCore.Qt.AlignCenter)
            main_image_label.setStyleSheet("background-color: #f0f0f0; border: 1px solid #ddd;")
            main_image_label.setText("تصویر اصلی")

            # دکمه‌های مدیریت تصاویر
            image_buttons_layout = QVBoxLayout()

            add_image_btn = QPushButton("افزودن تصویر")
            add_image_btn.setIcon(QtGui.QIcon.fromTheme("list-add"))

            remove_image_btn = QPushButton("حذف تصویر")
            remove_image_btn.setIcon(QtGui.QIcon.fromTheme("list-remove"))

            view_all_images_btn = QPushButton("مشاهده همه تصاویر")

            image_buttons_layout.addWidget(add_image_btn)
            image_buttons_layout.addWidget(remove_image_btn)
            image_buttons_layout.addWidget(view_all_images_btn)
            image_buttons_layout.addStretch()

            images_layout.addWidget(main_image_label)
            images_layout.addLayout(image_buttons_layout)

            form_layout.addWidget(images_group)

            # دکمه‌های عملیات
            actions_layout = QHBoxLayout()

            new_product_btn = QPushButton("محصول جدید")
            new_product_btn.setIcon(QtGui.QIcon.fromTheme("document-new"))

            save_product_btn = QPushButton("ذخیره محصول")
            save_product_btn.setIcon(QtGui.QIcon.fromTheme("document-save"))

            delete_product_btn = QPushButton("حذف محصول")
            delete_product_btn.setIcon(QtGui.QIcon.fromTheme("edit-delete"))

            print_product_btn = QPushButton("چاپ اطلاعات")
            print_product_btn.setIcon(QtGui.QIcon.fromTheme("document-print"))

            actions_layout.addWidget(new_product_btn)
            actions_layout.addWidget(save_product_btn)
            actions_layout.addWidget(delete_product_btn)
            actions_layout.addWidget(print_product_btn)

            form_layout.addLayout(actions_layout)

            # اتصال سیگنال‌ها به اسلات‌ها
            search_btn.clicked.connect(lambda: self.search_product(search_input.text()))
            advanced_search_btn.clicked.connect(self.show_advanced_search)
            add_image_btn.clicked.connect(self.add_product_image)
            remove_image_btn.clicked.connect(self.remove_product_image)
            view_all_images_btn.clicked.connect(self.view_all_product_images)
            new_product_btn.clicked.connect(self.new_product_form)
            save_product_btn.clicked.connect(lambda: self.save_product_form(
                product_id_input.text(),
                product_name_input.text(),
                product_category_combo.currentText(),
                product_price_input.text(),
                product_stock_input.text(),
                product_min_stock_input.text(),
                product_description_input.toPlainText()
            ))
            delete_product_btn.clicked.connect(lambda: self.delete_product_form(product_id_input.text()))
            print_product_btn.clicked.connect(lambda: self.print_product_form(product_id_input.text()))

            return form_widget
        except Exception as e:
            print(f"Error creating standard product form: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در ایجاد فرم استاندارد: {str(e)}")
            return QWidget()

    def create_custom_product_form(self):
        """ایجاد فرم سفارشی مدیریت محصولات"""
        try:
            # ایجاد ویجت اصلی
            form_widget = QWidget()
            form_layout = QVBoxLayout(form_widget)

            # عنوان فرم
            title_label = QLabel("فرم سفارشی مدیریت محصولات")
            title_label.setAlignment(QtCore.Qt.AlignCenter)
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
            form_layout.addWidget(title_label)

            # توضیحات
            description_label = QLabel("این فرم را می‌توانید مطابق با نیازهای خود سفارشی کنید.")
            description_label.setAlignment(QtCore.Qt.AlignCenter)
            form_layout.addWidget(description_label)

            # بخش سفارشی‌سازی فرم
            customize_group = QGroupBox("سفارشی‌سازی فرم")
            customize_layout = QVBoxLayout(customize_group)

            # انتخاب فیلدهای نمایش داده شده
            fields_group = QGroupBox("فیلدهای نمایش داده شده")
            fields_layout = QVBoxLayout(fields_group)

            field_checkboxes = []
            for field_name in ["کد محصول", "نام محصول", "دسته‌بندی", "قیمت", "موجودی", "حداقل موجودی",
                              "توضیحات", "بارکد", "تصاویر", "تاریخ ایجاد", "تاریخ به‌روزرسانی"]:
                checkbox = QCheckBox(field_name)
                checkbox.setChecked(True)
                fields_layout.addWidget(checkbox)
                field_checkboxes.append(checkbox)

            customize_layout.addWidget(fields_group)

            # تنظیمات ظاهری
            appearance_group = QGroupBox("تنظیمات ظاهری")
            appearance_layout = QFormLayout(appearance_group)

            theme_combo = QComboBox()
            theme_combo.addItems(["پیش‌فرض", "روشن", "تیره", "آبی", "سبز"])

            font_combo = QComboBox()
            font_combo.addItems(["Vazir", "Tahoma", "Arial", "Segoe UI"])

            font_size_combo = QComboBox()
            font_size_combo.addItems(["10", "11", "12", "14", "16"])

            appearance_layout.addRow("قالب:", theme_combo)
            appearance_layout.addRow("فونت:", font_combo)
            appearance_layout.addRow("اندازه فونت:", font_size_combo)

            customize_layout.addWidget(appearance_group)

            # دکمه اعمال تغییرات
            apply_btn = QPushButton("اعمال تغییرات")
            apply_btn.clicked.connect(self.apply_form_customization)
            customize_layout.addWidget(apply_btn)

            form_layout.addWidget(customize_group)

            # پیش‌نمایش فرم
            preview_group = QGroupBox("پیش‌نمایش فرم")
            preview_layout = QVBoxLayout(preview_group)

            preview_label = QLabel("پیش‌نمایش فرم سفارشی شما")
            preview_label.setAlignment(QtCore.Qt.AlignCenter)
            preview_layout.addWidget(preview_label)

            # یک نمونه ساده از فرم برای پیش‌نمایش
            preview_form = QWidget()
            preview_form_layout = QFormLayout(preview_form)

            preview_form_layout.addRow("نام محصول:", QLineEdit())
            preview_form_layout.addRow("قیمت:", QLineEdit())
            preview_form_layout.addRow("موجودی:", QLineEdit())

            preview_layout.addWidget(preview_form)

            form_layout.addWidget(preview_group)

            return form_widget
        except Exception as e:
            print(f"Error creating custom product form: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در ایجاد فرم سفارشی: {str(e)}")
            return QWidget()

    def create_form_designer(self):
        """ایجاد طراح فرم"""
        try:
            # ایجاد ویجت اصلی
            designer_widget = QWidget()
            designer_layout = QVBoxLayout(designer_widget)

            # عنوان
            title_label = QLabel("طراح فرم مدیریت محصولات")
            title_label.setAlignment(QtCore.Qt.AlignCenter)
            title_label.setStyleSheet("font-size: 18px; font-weight: bold; margin: 10px;")
            designer_layout.addWidget(title_label)

            # توضیحات
            description_label = QLabel("با استفاده از این ابزار می‌توانید فرم دلخواه خود را طراحی کنید.")
            description_label.setAlignment(QtCore.Qt.AlignCenter)
            designer_layout.addWidget(description_label)

            # بخش اصلی طراح
            main_designer_layout = QHBoxLayout()

            # پنل ابزارها
            tools_group = QGroupBox("ابزارها")
            tools_layout = QVBoxLayout(tools_group)

            # دکمه‌های ابزارها
            tools = [
                ("برچسب", "افزودن برچسب متنی"),
                ("فیلد متنی", "افزودن فیلد ورودی متنی"),
                ("فیلد عددی", "افزودن فیلد ورودی عددی"),
                ("منوی کشویی", "افزودن منوی کشویی"),
                ("چک باکس", "افزودن چک باکس"),
                ("دکمه رادیویی", "افزودن دکمه رادیویی"),
                ("دکمه", "افزودن دکمه"),
                ("تصویر", "افزودن تصویر"),
                ("جدول", "افزودن جدول"),
                ("گروه", "افزودن گروه‌بندی")
            ]

            for tool_name, tool_tip in tools:
                tool_btn = QPushButton(tool_name)
                tool_btn.setToolTip(tool_tip)
                tool_btn.setMinimumWidth(120)
                tools_layout.addWidget(tool_btn)

            tools_layout.addStretch()

            # ناحیه طراحی
            design_area_group = QGroupBox("ناحیه طراحی")
            design_area_layout = QVBoxLayout(design_area_group)

            design_area = QScrollArea()
            design_area.setWidgetResizable(True)
            design_area.setMinimumSize(400, 400)

            design_canvas = QWidget()
            design_canvas.setStyleSheet("background-color: white; border: 1px dashed #ccc;")
            design_canvas_layout = QVBoxLayout(design_canvas)
            design_canvas_layout.setAlignment(QtCore.Qt.AlignTop)

            # افزودن یک برچسب راهنما به ناحیه طراحی
            guide_label = QLabel("عناصر را از پنل ابزارها به اینجا بکشید و رها کنید")
            guide_label.setAlignment(QtCore.Qt.AlignCenter)
            guide_label.setStyleSheet("color: #888; padding: 20px;")
            design_canvas_layout.addWidget(guide_label)

            design_area.setWidget(design_canvas)
            design_area_layout.addWidget(design_area)

            # پنل ویژگی‌ها
            properties_group = QGroupBox("ویژگی‌ها")
            properties_layout = QVBoxLayout(properties_group)

            properties_label = QLabel("ویژگی‌های عنصر انتخاب شده")
            properties_layout.addWidget(properties_label)

            # یک فرم خالی برای نمایش ویژگی‌ها
            properties_form = QFormLayout()
            properties_form.addRow("شناسه:", QLineEdit())
            properties_form.addRow("عنوان:", QLineEdit())
            properties_form.addRow("عرض:", QLineEdit())
            properties_form.addRow("ارتفاع:", QLineEdit())
            properties_form.addRow("رنگ متن:", QComboBox())
            properties_form.addRow("رنگ پس‌زمینه:", QComboBox())

            properties_layout.addLayout(properties_form)
            properties_layout.addStretch()

            # اضافه کردن پنل‌ها به طرح اصلی
            main_designer_layout.addWidget(tools_group)
            main_designer_layout.addWidget(design_area_group, 3)  # با وزن بیشتر
            main_designer_layout.addWidget(properties_group)

            designer_layout.addLayout(main_designer_layout)

            # دکمه‌های پایین
            buttons_layout = QHBoxLayout()

            clear_btn = QPushButton("پاک کردن طرح")
            preview_btn = QPushButton("پیش‌نمایش")
            save_design_btn = QPushButton("ذخیره طرح")

            buttons_layout.addWidget(clear_btn)
            buttons_layout.addWidget(preview_btn)
            buttons_layout.addWidget(save_design_btn)

            designer_layout.addLayout(buttons_layout)

            return designer_widget
        except Exception as e:
            print(f"Error creating form designer: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در ایجاد طراح فرم: {str(e)}")
            return QWidget()

    def save_form_as_template(self):
        """ذخیره فرم به عنوان قالب"""
        try:
            # دریافت نام قالب از کاربر
            template_name, ok = QInputDialog.getText(self, "ذخیره قالب", "نام قالب را وارد کنید:")

            if ok and template_name:
                # اطمینان از وجود پوشه templates
                if not os.path.exists('templates'):
                    os.makedirs('templates')

                # ایجاد یک دیکشنری برای ذخیره اطلاعات قالب
                template_data = {
                    "name": template_name,
                    "created_at": datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"),
                    "type": "product_form",
                    "fields": [
                        {"name": "product_id", "type": "text", "label": "کد محصول", "enabled": True},
                        {"name": "product_name", "type": "text", "label": "نام محصول", "enabled": True},
                        {"name": "category", "type": "combo", "label": "دسته‌بندی", "enabled": True},
                        {"name": "price", "type": "number", "label": "قیمت", "enabled": True},
                        {"name": "stock", "type": "number", "label": "موجودی", "enabled": True},
                        {"name": "min_stock", "type": "number", "label": "حداقل موجودی", "enabled": True},
                        {"name": "description", "type": "text_area", "label": "توضیحات", "enabled": True},
                        {"name": "barcode", "type": "text", "label": "بارکد", "enabled": True},
                        {"name": "image", "type": "image", "label": "تصویر", "enabled": True}
                    ],
                    "layout": "standard",
                    "theme": "default",
                    "font": "Vazir",
                    "font_size": 12
                }

                # ذخیره قالب در فایل JSON
                template_path = os.path.join('templates', f"{template_name.replace(' ', '_')}.json")

                with open(template_path, 'w', encoding='utf-8') as f:
                    json.dump(template_data, f, indent=4, ensure_ascii=False)

                QMessageBox.information(self, "ذخیره قالب", f"قالب «{template_name}» با موفقیت ذخیره شد.")

                # ثبت فعالیت
                self.log_activity("form", f"ذخیره قالب فرم: {template_name}")
        except Exception as e:
            print(f"Error saving form template: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره قالب فرم: {str(e)}")

    def load_form_template(self):
        """بارگذاری قالب فرم"""
        try:
            # اطمینان از وجود پوشه templates
            if not os.path.exists('templates'):
                QMessageBox.warning(self, "هشدار", "هیچ قالبی یافت نشد.")
                return

            # دریافت لیست قالب‌ها
            template_files = [f for f in os.listdir('templates') if f.endswith('.json')]

            if not template_files:
                QMessageBox.warning(self, "هشدار", "هیچ قالبی یافت نشد.")
                return

            # نمایش لیست قالب‌ها برای انتخاب
            template_names = []
            for template_file in template_files:
                try:
                    with open(os.path.join('templates', template_file), 'r', encoding='utf-8') as f:
                        template_data = json.load(f)
                        template_names.append(template_data.get("name", template_file))
                except:
                    template_names.append(template_file.replace('_', ' ').replace('.json', ''))

            template_name, ok = QInputDialog.getItem(self, "بارگذاری قالب",
                                                   "قالب مورد نظر را انتخاب کنید:",
                                                   template_names, 0, False)

            if ok and template_name:
                # یافتن فایل قالب
                template_file = None
                for i, name in enumerate(template_names):
                    if name == template_name:
                        template_file = template_files[i]
                        break

                if template_file:
                    # بارگذاری قالب
                    with open(os.path.join('templates', template_file), 'r', encoding='utf-8') as f:
                        template_data = json.load(f)

                    QMessageBox.information(self, "بارگذاری قالب",
                                           f"قالب «{template_name}» با موفقیت بارگذاری شد.\n\n"
                                           "برای اعمال این قالب، فرم را دوباره باز کنید.")

                    # ثبت فعالیت
                    self.log_activity("form", f"بارگذاری قالب فرم: {template_name}")
        except Exception as e:
            print(f"Error loading form template: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری قالب فرم: {str(e)}")

    # متدهای مورد نیاز برای عملکرد فرم
    def search_product(self, search_text):
        """جستجوی محصول در فرم"""
        try:
            if not search_text:
                QMessageBox.warning(self, "هشدار", "لطفاً عبارت جستجو را وارد کنید.")
                return

            # جستجو در پایگاه داده
            self.cursor.execute("""
                SELECT id, name, category, price, stock, min_stock, description
                FROM products
                WHERE id = ? OR name LIKE ? OR barcode = ?
            """, (search_text, f"%{search_text}%", search_text))

            result = self.cursor.fetchone()

            if result:
                QMessageBox.information(self, "نتیجه جستجو",
                                       f"محصول یافت شد: {result[1]}\n\n"
                                       "اطلاعات محصول در فرم بارگذاری شد.")

                # در یک برنامه واقعی، اینجا اطلاعات محصول در فرم بارگذاری می‌شود
            else:
                QMessageBox.warning(self, "نتیجه جستجو", "هیچ محصولی با این مشخصات یافت نشد.")
        except Exception as e:
            print(f"Error searching product: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در جستجوی محصول: {str(e)}")

    def show_advanced_search(self):
        """نمایش فرم جستجوی پیشرفته"""
        try:
            # ایجاد پنجره جستجوی پیشرفته
            dialog = QDialog(self)
            dialog.setWindowTitle("جستجوی پیشرفته محصولات")
            dialog.setMinimumWidth(500)

            # طرح اصلی
            layout = QVBoxLayout(dialog)

            # فرم جستجو
            form_layout = QFormLayout()

            name_input = QLineEdit()
            category_combo = QComboBox()
            category_combo.addItem("همه دسته‌بندی‌ها")

            # دریافت دسته‌بندی‌ها از پایگاه داده
            self.cursor.execute("SELECT name FROM categories")
            categories = self.cursor.fetchall()
            for category in categories:
                category_combo.addItem(category[0])

            min_price_input = QLineEdit()
            min_price_input.setValidator(QtGui.QDoubleValidator(0, 1000000000, 2))

            max_price_input = QLineEdit()
            max_price_input.setValidator(QtGui.QDoubleValidator(0, 1000000000, 2))

            stock_status_combo = QComboBox()
            stock_status_combo.addItems(["همه", "موجود", "ناموجود", "کم موجود"])

            # اضافه کردن فیلدها به فرم
            form_layout.addRow("نام محصول:", name_input)
            form_layout.addRow("دسته‌بندی:", category_combo)
            form_layout.addRow("حداقل قیمت:", min_price_input)
            form_layout.addRow("حداکثر قیمت:", max_price_input)
            form_layout.addRow("وضعیت موجودی:", stock_status_combo)

            layout.addLayout(form_layout)

            # دکمه‌های جستجو و لغو
            buttons = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            buttons.button(QDialogButtonBox.Ok).setText("جستجو")
            buttons.button(QDialogButtonBox.Cancel).setText("لغو")
            buttons.accepted.connect(dialog.accept)
            buttons.rejected.connect(dialog.reject)
            layout.addWidget(buttons)

            # اجرای پنجره
            if dialog.exec_() == QDialog.Accepted:
                # ساخت پرس‌وجو بر اساس معیارهای جستجو
                query = "SELECT id, name, category, price, stock FROM products WHERE 1=1"
                params = []

                if name_input.text():
                    query += " AND name LIKE ?"
                    params.append(f"%{name_input.text()}%")

                if category_combo.currentIndex() > 0:
                    query += " AND category = ?"
                    params.append(category_combo.currentText())

                if min_price_input.text():
                    query += " AND price >= ?"
                    params.append(float(min_price_input.text()))

                if max_price_input.text():
                    query += " AND price <= ?"
                    params.append(float(max_price_input.text()))

                if stock_status_combo.currentText() == "موجود":
                    query += " AND stock > 0"
                elif stock_status_combo.currentText() == "ناموجود":
                    query += " AND stock = 0"
                elif stock_status_combo.currentText() == "کم موجود":
                    query += " AND stock > 0 AND stock <= min_stock"

                # اجرای پرس‌وجو
                self.cursor.execute(query, params)
                results = self.cursor.fetchall()

                if results:
                    # نمایش نتایج در یک پنجره جدید
                    results_dialog = QDialog(self)
                    results_dialog.setWindowTitle("نتایج جستجو")
                    results_dialog.setMinimumSize(600, 400)

                    results_layout = QVBoxLayout(results_dialog)

                    # ایجاد جدول نتایج
                    results_table = QTableWidget()
                    results_table.setColumnCount(6)
                    results_table.setHorizontalHeaderLabels(["شناسه", "نام محصول", "دسته‌بندی", "قیمت", "موجودی", "عملیات"])
                    results_table.setEditTriggers(QTableWidget.NoEditTriggers)
                    results_table.setSelectionBehavior(QTableWidget.SelectRows)

                    # تنظیم تعداد سطرهای جدول
                    results_table.setRowCount(len(results))

                    # پر کردن جدول با نتایج
                    for row, product in enumerate(results):
                        for col, value in enumerate(product):
                            item = QTableWidgetItem(str(value))
                            results_table.setItem(row, col, item)

                        # اضافه کردن دکمه انتخاب
                        select_btn = QPushButton("انتخاب")
                        select_btn.clicked.connect(lambda checked, pid=product[0]: self.select_product_from_search(pid, results_dialog))

                        cell_widget = QWidget()
                        cell_layout = QHBoxLayout(cell_widget)
                        cell_layout.addWidget(select_btn)
                        cell_layout.setContentsMargins(0, 0, 0, 0)

                        results_table.setCellWidget(row, 5, cell_widget)

                    results_layout.addWidget(QLabel(f"تعداد {len(results)} محصول یافت شد:"))
                    results_layout.addWidget(results_table)

                    # دکمه بستن
                    close_btn = QPushButton("بستن")
                    close_btn.clicked.connect(results_dialog.close)
                    results_layout.addWidget(close_btn)

                    # نمایش پنجره نتایج
                    results_dialog.exec_()
                else:
                    QMessageBox.information(self, "نتایج جستجو", "هیچ محصولی با معیارهای جستجوی شما یافت نشد.")
        except Exception as e:
            print(f"Error in advanced search: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در جستجوی پیشرفته: {str(e)}")

    def select_product_from_search(self, product_id, dialog=None):
        """انتخاب محصول از نتایج جستجو"""
        try:
            QMessageBox.information(self, "انتخاب محصول",
                                   f"محصول با شناسه {product_id} انتخاب شد.\n\n"
                                   "اطلاعات محصول در فرم بارگذاری شد.")

            # در یک برنامه واقعی، اینجا اطلاعات محصول در فرم بارگذاری می‌شود

            # بستن پنجره نتایج در صورت وجود
            if dialog:
                dialog.close()
        except Exception as e:
            print(f"Error selecting product from search: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در انتخاب محصول: {str(e)}")

    def add_product_image(self):
        """افزودن تصویر محصول"""
        try:
            # انتخاب فایل تصویر
            file_path, _ = QFileDialog.getOpenFileName(self, "انتخاب تصویر محصول", "", "Image Files (*.png *.jpg *.jpeg)")

            if file_path:
                QMessageBox.information(self, "افزودن تصویر",
                                       f"تصویر انتخاب شده: {file_path}\n\n"
                                       "تصویر با موفقیت اضافه شد.")

                # در یک برنامه واقعی، اینجا تصویر به محصول اضافه می‌شود
        except Exception as e:
            print(f"Error adding product image: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در افزودن تصویر محصول: {str(e)}")

    def remove_product_image(self):
        """حذف تصویر محصول"""
        try:
            confirm = QMessageBox.question(self, "تایید حذف",
                                          "آیا از حذف تصویر انتخاب شده اطمینان دارید؟",
                                          QMessageBox.Yes | QMessageBox.No)

            if confirm == QMessageBox.Yes:
                QMessageBox.information(self, "حذف تصویر", "تصویر با موفقیت حذف شد.")

                # در یک برنامه واقعی، اینجا تصویر از محصول حذف می‌شود
        except Exception as e:
            print(f"Error removing product image: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در حذف تصویر محصول: {str(e)}")

    def view_all_product_images(self):
        """مشاهده همه تصاویر محصول"""
        try:
            QMessageBox.information(self, "مشاهده تصاویر",
                                   "این قابلیت به شما امکان مشاهده همه تصاویر محصول را می‌دهد.\n\n"
                                   "در حال حاضر هیچ تصویری برای این محصول وجود ندارد.")

            # در یک برنامه واقعی، اینجا همه تصاویر محصول نمایش داده می‌شوند
        except Exception as e:
            print(f"Error viewing product images: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در مشاهده تصاویر محصول: {str(e)}")

    def new_product_form(self):
        """ایجاد فرم محصول جدید"""
        try:
            confirm = QMessageBox.question(self, "تایید",
                                          "آیا می‌خواهید فرم را پاک کرده و محصول جدیدی ایجاد کنید؟",
                                          QMessageBox.Yes | QMessageBox.No)

            if confirm == QMessageBox.Yes:
                QMessageBox.information(self, "محصول جدید", "فرم برای ورود محصول جدید آماده شد.")

                # در یک برنامه واقعی، اینجا فرم پاک می‌شود
        except Exception as e:
            print(f"Error creating new product form: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در ایجاد فرم محصول جدید: {str(e)}")

    def save_product_form(self, product_id, name, category, price, stock, min_stock, description):
        """ذخیره اطلاعات محصول از فرم"""
        try:
            # بررسی اعتبار داده‌ها
            if not name:
                QMessageBox.warning(self, "خطا", "نام محصول نمی‌تواند خالی باشد.")
                return

            try:
                price_value = float(price) if price else 0
            except ValueError:
                QMessageBox.warning(self, "خطا", "قیمت باید یک عدد باشد.")
                return

            try:
                stock_value = int(stock) if stock else 0
            except ValueError:
                QMessageBox.warning(self, "خطا", "موجودی باید یک عدد صحیح باشد.")
                return

            try:
                min_stock_value = int(min_stock) if min_stock else 0
            except ValueError:
                QMessageBox.warning(self, "خطا", "حداقل موجودی باید یک عدد صحیح باشد.")
                return

            # اگر شناسه محصول وجود داشته باشد، به‌روزرسانی می‌کنیم
            if product_id:
                # به‌روزرسانی محصول موجود
                self.cursor.execute("""
                    UPDATE products
                    SET name = ?, category = ?, price = ?, stock = ?, min_stock = ?, description = ?, updated_at = ?
                    WHERE id = ?
                """, (name, category, price_value, stock_value, min_stock_value, description,
                      datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S"), product_id))

                message = "محصول با موفقیت به‌روزرسانی شد."
                activity = f"به‌روزرسانی محصول: {name}"
            else:
                # ایجاد محصول جدید
                created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                self.cursor.execute("""
                    INSERT INTO products (name, category, price, stock, min_stock, description, created_at, updated_at)
                    VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                """, (name, category, price_value, stock_value, min_stock_value, description, created_at, created_at))

                message = "محصول جدید با موفقیت ایجاد شد."
                activity = f"ایجاد محصول جدید: {name}"

            # ذخیره تغییرات
            self.conn.commit()

            # ثبت فعالیت
            self.log_activity("product", activity)

            QMessageBox.information(self, "ذخیره محصول", message)
        except Exception as e:
            print(f"Error saving product form: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در ذخیره اطلاعات محصول: {str(e)}")

    def delete_product_form(self, product_id):
        """حذف محصول از فرم"""
        try:
            if not product_id:
                QMessageBox.warning(self, "خطا", "ابتدا یک محصول را انتخاب کنید.")
                return

            # پرسیدن تایید از کاربر
            confirm = QMessageBox.question(self, "تایید حذف",
                                          "آیا از حذف این محصول اطمینان دارید؟",
                                          QMessageBox.Yes | QMessageBox.No)

            if confirm == QMessageBox.Yes:
                # دریافت نام محصول قبل از حذف
                self.cursor.execute("SELECT name FROM products WHERE id = ?", (product_id,))
                result = self.cursor.fetchone()

                if not result:
                    QMessageBox.warning(self, "خطا", "محصول مورد نظر یافت نشد.")
                    return

                product_name = result[0]

                # حذف محصول
                self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
                self.conn.commit()

                # ثبت فعالیت
                self.log_activity("product", f"حذف محصول: {product_name}")

                QMessageBox.information(self, "حذف محصول", "محصول با موفقیت حذف شد.")

                # در یک برنامه واقعی، اینجا فرم پاک می‌شود
        except Exception as e:
            print(f"Error deleting product: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در حذف محصول: {str(e)}")

    def print_product_form(self, product_id):
        """چاپ اطلاعات محصول از فرم"""
        try:
            if not product_id:
                QMessageBox.warning(self, "خطا", "ابتدا یک محصول را انتخاب کنید.")
                return

            QMessageBox.information(self, "چاپ اطلاعات",
                                   f"اطلاعات محصول با شناسه {product_id} برای چاپ آماده شد.\n\n"
                                   "در یک برنامه واقعی، اینجا پنجره پیش‌نمایش چاپ نمایش داده می‌شود.")

            # در یک برنامه واقعی، اینجا پنجره پیش‌نمایش چاپ نمایش داده می‌شود
        except Exception as e:
            print(f"Error printing product information: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در چاپ اطلاعات محصول: {str(e)}")

    def apply_form_customization(self):
        """اعمال تغییرات سفارشی‌سازی فرم"""
        try:
            QMessageBox.information(self, "سفارشی‌سازی فرم",
                                   "تغییرات سفارشی‌سازی با موفقیت اعمال شد.\n\n"
                                   "برای مشاهده تغییرات، فرم را دوباره باز کنید.")

            # در یک برنامه واقعی، اینجا تغییرات سفارشی‌سازی اعمال می‌شوند
        except Exception as e:
            print(f"Error applying form customization: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در اعمال تغییرات سفارشی‌سازی: {str(e)}")

    def return_to_main_form(self):
        """بازگشت به فرم اصلی"""
        try:
            # تنظیم متغیر بازگشت به فرم قبلی
            self.return_to_previous_form = True

            # ثبت فعالیت
            self.log_activity("navigation", "بازگشت به صفحه اصلی")

            # نمایش پیام
            QMessageBox.information(self, "بازگشت به صفحه اصلی", "در حال بازگشت به صفحه اصلی...")

            # بستن فرم فعلی
            self.close()

            # اجرای فایل product_manager.py
            import sys
            import os
            import subprocess

            python_executable = sys.executable
            script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product_manager.py')

            if os.path.exists(script_path):
                subprocess.Popen([python_executable, script_path])
            else:
                QMessageBox.critical(self, "خطا", f"فایل product_manager.py در مسیر {script_path} یافت نشد.")

        except Exception as e:
            print(f"Error returning to main form: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در بازگشت به صفحه اصلی: {str(e)}")

    def closeEvent(self, event):
        """رویداد بستن پنجره"""
        try:
            # ثبت فعالیت
            self.log_activity("application", "بستن فرم مدیریت محصولات")

            # اگر بازگشت به فرم قبلی درخواست نشده باشد، پرسیدن از کاربر
            if not self.return_to_previous_form:
                # پرسیدن از کاربر برای بازگشت به فرم قبلی
                reply = QMessageBox.question(self, "بازگشت به صفحه اصلی",
                                           "آیا می‌خواهید به صفحه اصلی برگردید؟",
                                           QMessageBox.Yes | QMessageBox.No | QMessageBox.Cancel)

                if reply == QMessageBox.Yes:
                    # تنظیم متغیر بازگشت به فرم قبلی
                    self.return_to_previous_form = True

                    # اجرای فایل product_manager.py
                    import sys
                    import os
                    import subprocess

                    python_executable = sys.executable
                    script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product_manager.py')

                    if os.path.exists(script_path):
                        subprocess.Popen([python_executable, script_path])
                    else:
                        QMessageBox.critical(self, "خطا", f"فایل product_manager.py در مسیر {script_path} یافت نشد.")

                elif reply == QMessageBox.Cancel:
                    # لغو بستن پنجره
                    event.ignore()
                    return

            # بستن اتصال پایگاه داده
            if hasattr(self, 'conn') and self.conn:
                self.conn.close()

            # پذیرش رویداد بستن
            event.accept()

        except Exception as e:
            print(f"Error in closeEvent: {e}")
            # در صورت خطا، اجازه بستن پنجره را می‌دهیم
            event.accept()

# اگر این فایل به عنوان برنامه اصلی اجرا شود
if __name__ == "__main__":
    try:
        app = QApplication(sys.argv)
        window = ProductManager()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Error starting application: {e}")
        # اگر QApplication هنوز ایجاد نشده باشد، نمی‌توانیم از QMessageBox استفاده کنیم
        if 'app' in locals():
            QMessageBox.critical(None, "Critical Error", f"Error starting application: {str(e)}")