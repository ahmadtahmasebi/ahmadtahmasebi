from PyQt5 import QtWidgets, QtGui, QtCore
from PyQt5.QtWidgets import QMainWindow, QApplication, QLabel, QLineEdit, QPushButton, QVBoxLayout, QHBoxLayout, QWidget, QFileDialog, QTableWidget, QTableWidgetItem, QDialog, QGridLayout, QComboBox, QFormLayout, QGroupBox, QScrollArea, QMenuBar, QAction, QDialogButtonBox, QMessageBox, QTabWidget, QCheckBox, QProgressBar, QRadioButton
import pandas as pd
import csv
import xlsxwriter
import sqlite3
import sys
import os
import datetime
import time
from reportlab.lib.pagesizes import letter
from reportlab.pdfgen import canvas

# برای رسم نمودار
import matplotlib.pyplot as plt
from matplotlib.backends.backend_qt5agg import FigureCanvasQTAgg as FigureCanvas
from matplotlib.figure import Figure
import numpy as np

# برای تولید و مدیریت بارکد
import barcode
from barcode.writer import ImageWriter
from barcode import generate
import io
from PIL import Image
from PIL.ImageQt import toqimage
import json

# برای کنترل دسترسی
from access_control import AccessControl

# کلاس نمودار برای استفاده در داشبورد
class MplCanvas(FigureCanvas):
    def __init__(self, parent=None, width=5, height=4, dpi=100):
        self.fig = Figure(figsize=(width, height), dpi=dpi)
        self.axes = self.fig.add_subplot(111)
        super(MplCanvas, self).__init__(self.fig)
        self.fig.tight_layout()

class ProductManager(QMainWindow):
    def __init__(self, auth_manager=None):
        super().__init__()

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
                    # فقط خطا را چاپ می‌کنیم و ادامه می‌دهیم تا برنامه متوقف نشود
                    print(f"Error in log_activity: {e}")
        except Exception as e:
            # فقط خطا را چاپ می‌کنیم و ادامه می‌دهیم تا برنامه متوقف نشود
            print(f"Error logging activity: {e}")

    # منوی گزارش‌ها
    def generate_report(self):
        """ایجاد گزارش از محصولات"""
        try:
            QMessageBox.information(self, "گزارش", "در حال ایجاد گزارش...")
            self.log_activity("report", "ایجاد گزارش محصولات")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ایجاد گزارش: {str(e)}")

    # منوی دسته‌بندی‌ها
    def manage_categories(self):
        """مدیریت دسته‌بندی‌های محصولات"""
        try:
            QMessageBox.information(self, "دسته‌بندی‌ها", "بخش مدیریت دسته‌بندی‌ها")
            self.log_activity("category", "باز کردن بخش مدیریت دسته‌بندی‌ها")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن بخش دسته‌بندی‌ها: {str(e)}")

    # منوی داشبورد
    def show_dashboard(self):
        """نمایش داشبورد آماری"""
        try:
            QMessageBox.information(self, "داشبورد", "در حال بارگذاری داشبورد...")
            self.log_activity("dashboard", "نمایش داشبورد آماری")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در نمایش داشبورد: {str(e)}")

    # منوی موجودی
    def manage_stock(self):
        """مدیریت موجودی محصولات"""
        try:
            QMessageBox.information(self, "موجودی", "بخش مدیریت موجودی")
            self.log_activity("inventory", "باز کردن بخش مدیریت موجودی")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن بخش موجودی: {str(e)}")

    def view_inventory_history(self):
        """نمایش تاریخچه تغییرات موجودی"""
        try:
            QMessageBox.information(self, "تاریخچه موجودی", "در حال بارگذاری تاریخچه...")
            self.log_activity("inventory", "مشاهده تاریخچه موجودی")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در نمایش تاریخچه موجودی: {str(e)}")

    def show_low_stock_alert(self):
        """نمایش هشدار محصولات با موجودی کم"""
        try:
            QMessageBox.information(self, "هشدار موجودی", "در حال بررسی موجودی محصولات...")
            self.log_activity("inventory", "بررسی هشدار موجودی کم")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بررسی موجودی کم: {str(e)}")

    # منوی بارکد
    def generate_barcode(self):
        """ایجاد بارکد برای محصولات"""
        try:
            QMessageBox.information(self, "بارکد", "در حال ایجاد بارکد...")
            self.log_activity("barcode", "ایجاد بارکد")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در ایجاد بارکد: {str(e)}")

    def scan_barcode(self):
        """اسکن بارکد محصولات"""
        try:
            QMessageBox.information(self, "اسکن بارکد", "لطفاً بارکد را اسکن کنید...")
            self.log_activity("barcode", "اسکن بارکد")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در اسکن بارکد: {str(e)}")

    def print_barcodes(self):
        """چاپ بارکدهای محصولات"""
        try:
            QMessageBox.information(self, "چاپ بارکد", "در حال آماده‌سازی برای چاپ...")
            self.log_activity("barcode", "چاپ بارکدها")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در چاپ بارکدها: {str(e)}")

    # منوی تخفیف‌ها
    def manage_discounts(self):
        """مدیریت تخفیف‌های محصولات"""
        try:
            QMessageBox.information(self, "تخفیف‌ها", "بخش مدیریت تخفیف‌ها")
            self.log_activity("discount", "باز کردن بخش مدیریت تخفیف‌ها")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن بخش تخفیف‌ها: {str(e)}")

    def apply_discount_to_product(self):
        """اعمال تخفیف به یک محصول"""
        try:
            QMessageBox.information(self, "تخفیف محصول", "در حال اعمال تخفیف به محصول...")
            self.log_activity("discount", "اعمال تخفیف به محصول")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در اعمال تخفیف به محصول: {str(e)}")

    def apply_discount_to_category(self):
        """اعمال تخفیف به یک دسته‌بندی"""
        try:
            QMessageBox.information(self, "تخفیف دسته‌بندی", "در حال اعمال تخفیف به دسته‌بندی...")
            self.log_activity("discount", "اعمال تخفیف به دسته‌بندی")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در اعمال تخفیف به دسته‌بندی: {str(e)}")

    def clear_all_discounts(self):
        """حذف همه تخفیف‌های اعمال شده"""
        try:
            QMessageBox.information(self, "حذف تخفیف‌ها", "در حال حذف همه تخفیف‌ها...")
            self.log_activity("discount", "حذف همه تخفیف‌ها")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در حذف تخفیف‌ها: {str(e)}")

    # منوی تنظیمات
    def show_settings(self):
        """نمایش پنجره تنظیمات برنامه"""
        try:
            QMessageBox.information(self, "تنظیمات", "بخش تنظیمات برنامه")
            self.log_activity("settings", "باز کردن بخش تنظیمات برنامه")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن بخش تنظیمات: {str(e)}")

    def show_about(self):
        """نمایش اطلاعات درباره برنامه"""
        try:
            about_text = f"""
            <h2>سیستم مدیریت محصولات</h2>
            <p>نسخه: {self.app_version}</p>
            <p>این برنامه برای مدیریت محصولات، موجودی و فروش طراحی شده است.</p>
            <p>امکانات:</p>
            <ul>
                <li>مدیریت محصولات و دسته‌بندی‌ها</li>
                <li>کنترل موجودی</li>
                <li>مدیریت تخفیف‌ها</li>
                <li>تولید و اسکن بارکد</li>
                <li>گزارش‌گیری</li>
                <li>داشبورد آماری</li>
            </ul>
            """
            QMessageBox.about(self, "درباره برنامه", about_text)
            self.log_activity("about", "مشاهده اطلاعات درباره برنامه")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در نمایش اطلاعات برنامه: {str(e)}")

    # متدهای مدیریت محصولات
    def browse_image(self):
        """انتخاب تصویر برای محصول"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                'انتخاب تصویر',
                '',
                'Image Files (*.png *.jpg *.jpeg *.bmp *.gif)'
            )

            if file_path:
                # کپی تصویر به پوشه product_images
                file_name = os.path.basename(file_path)
                destination = os.path.join('product_images', file_name)

                # اگر فایل قبلاً وجود نداشت، آن را کپی می‌کنیم
                if not os.path.exists(destination):
                    import shutil
                    shutil.copy2(file_path, destination)

                self.image_path.setText(destination)
                self.log_activity("product", f"انتخاب تصویر برای محصول: {file_name}")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در انتخاب تصویر: {str(e)}")

    def manage_product_images(self):
        """مدیریت تصاویر محصول"""
        try:
            # بررسی انتخاب محصول
            selected_items = self.products_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک محصول را انتخاب کنید.")
                return

            # دریافت شناسه و نام محصول انتخاب شده
            row = selected_items[0].row()
            product_id = int(self.products_table.item(row, 0).text())
            product_name = self.products_table.item(row, 1).text()

            # ایجاد دیالوگ مدیریت تصاویر
            dialog = QDialog(self)
            dialog.setWindowTitle(f"مدیریت تصاویر محصول: {product_name}")
            dialog.setMinimumSize(600, 400)

            layout = QVBoxLayout()

            # عنوان
            title_label = QLabel(f"مدیریت تصاویر محصول: {product_name}")
            title_label.setStyleSheet("font-size: 14px; font-weight: bold; margin-bottom: 10px;")
            layout.addWidget(title_label)

            # دکمه افزودن تصویر جدید
            add_image_button = QPushButton("افزودن تصویر جدید")
            add_image_button.clicked.connect(lambda: self.add_product_image(product_id))
            layout.addWidget(add_image_button)

            # جدول تصاویر
            images_table = QTableWidget()
            images_table.setColumnCount(4)
            images_table.setHorizontalHeaderLabels(['شناسه', 'مسیر تصویر', 'تصویر اصلی', 'عملیات'])
            images_table.setSelectionBehavior(QTableWidget.SelectRows)
            images_table.setEditTriggers(QTableWidget.NoEditTriggers)
            layout.addWidget(images_table)

            # دکمه‌های عملیات
            buttons_layout = QHBoxLayout()
            close_button = QPushButton("بستن")
            close_button.clicked.connect(dialog.accept)
            buttons_layout.addWidget(close_button)
            layout.addLayout(buttons_layout)

            dialog.setLayout(layout)

            # نمایش دیالوگ
            self.log_activity("product", f"باز کردن بخش مدیریت تصاویر محصول: {product_name}")
            dialog.exec_()

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در باز کردن بخش مدیریت تصاویر: {str(e)}")

    def add_product_image(self, product_id):
        """افزودن تصویر جدید به محصول"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self,
                'انتخاب تصویر',
                '',
                'Image Files (*.png *.jpg *.jpeg *.bmp *.gif)'
            )

            if file_path:
                # کپی تصویر به پوشه product_images
                file_name = os.path.basename(file_path)
                destination = os.path.join('product_images', file_name)

                # اگر فایل قبلاً وجود نداشت، آن را کپی می‌کنیم
                if not os.path.exists(destination):
                    import shutil
                    shutil.copy2(file_path, destination)

                # ثبت تصویر در پایگاه داده
                created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

                # بررسی اینکه آیا این اولین تصویر محصول است یا خیر
                self.cursor.execute("SELECT COUNT(*) FROM product_images WHERE product_id = ?", (product_id,))
                is_primary = 1 if self.cursor.fetchone()[0] == 0 else 0

                self.cursor.execute(
                    "INSERT INTO product_images (product_id, image_path, is_primary, created_at) VALUES (?, ?, ?, ?)",
                    (product_id, destination, is_primary, created_at)
                )
                self.conn.commit()

                # اگر این تصویر اصلی است، آن را در جدول محصولات نیز به‌روزرسانی می‌کنیم
                if is_primary:
                    self.cursor.execute(
                        "UPDATE products SET image = ? WHERE id = ?",
                        (destination, product_id)
                    )
                    self.conn.commit()

                self.log_activity("product", f"افزودن تصویر جدید به محصول با شناسه {product_id}")
                QMessageBox.information(self, "موفقیت", "تصویر با موفقیت افزوده شد.")

                # به‌روزرسانی فیلد تصویر در فرم اصلی اگر این تصویر اصلی است
                if is_primary:
                    self.image_path.setText(destination)

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در افزودن تصویر: {str(e)}")

    def add_product(self):
        """افزودن محصول جدید"""
        try:
            # دریافت اطلاعات از فیلدها
            name = self.name_input.text().strip()
            price_text = self.price_input.text().strip()
            category = self.category_input.currentText()
            image = self.image_path.text().strip()
            stock_text = self.stock_input.text().strip()
            min_stock_text = self.min_stock_input.text().strip()

            # اعتبارسنجی ورودی‌ها
            if not name:
                QMessageBox.warning(self, "خطا", "لطفاً نام محصول را وارد کنید.")
                return

            if not price_text:
                QMessageBox.warning(self, "خطا", "لطفاً قیمت محصول را وارد کنید.")
                return

            try:
                price = float(price_text)
                if price < 0:
                    QMessageBox.warning(self, "خطا", "قیمت نمی‌تواند منفی باشد.")
                    return
            except ValueError:
                QMessageBox.warning(self, "خطا", "قیمت باید عدد باشد.")
                return

            try:
                stock = int(stock_text) if stock_text else 0
                if stock < 0:
                    QMessageBox.warning(self, "خطا", "موجودی نمی‌تواند منفی باشد.")
                    return
            except ValueError:
                QMessageBox.warning(self, "خطا", "موجودی باید عدد صحیح باشد.")
                return

            try:
                min_stock = int(min_stock_text) if min_stock_text else 5
                if min_stock < 0:
                    QMessageBox.warning(self, "خطا", "حداقل موجودی نمی‌تواند منفی باشد.")
                    return
            except ValueError:
                QMessageBox.warning(self, "خطا", "حداقل موجودی باید عدد صحیح باشد.")
                return

            # ثبت زمان ایجاد
            created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # افزودن محصول به پایگاه داده
            self.cursor.execute(
                "INSERT INTO products (name, price, category, image, stock, min_stock, created_at, updated_at) VALUES (?, ?, ?, ?, ?, ?, ?, ?)",
                (name, price, category, image, stock, min_stock, created_at, created_at)
            )
            self.conn.commit()

            # ثبت فعالیت
            self.log_activity("product", f"افزودن محصول جدید: {name}")

            # پاک کردن فیلدها
            self.clear_product_fields()

            # به‌روزرسانی لیست محصولات
            self.load_products()

            QMessageBox.information(self, "موفقیت", f"محصول '{name}' با موفقیت افزوده شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در افزودن محصول: {str(e)}")

    def update_product(self):
        """به‌روزرسانی محصول انتخاب شده"""
        try:
            # بررسی انتخاب محصول
            selected_items = self.products_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک محصول را انتخاب کنید.")
                return

            # دریافت شناسه محصول انتخاب شده
            product_id = int(self.products_table.item(selected_items[0].row(), 0).text())

            # دریافت اطلاعات از فیلدها
            name = self.name_input.text().strip()
            price_text = self.price_input.text().strip()
            category = self.category_input.currentText()
            image = self.image_path.text().strip()
            stock_text = self.stock_input.text().strip()
            min_stock_text = self.min_stock_input.text().strip()

            # اعتبارسنجی ورودی‌ها
            if not name:
                QMessageBox.warning(self, "خطا", "لطفاً نام محصول را وارد کنید.")
                return

            if not price_text:
                QMessageBox.warning(self, "خطا", "لطفاً قیمت محصول را وارد کنید.")
                return

            try:
                price = float(price_text)
                if price < 0:
                    QMessageBox.warning(self, "خطا", "قیمت نمی‌تواند منفی باشد.")
                    return
            except ValueError:
                QMessageBox.warning(self, "خطا", "قیمت باید عدد باشد.")
                return

            try:
                stock = int(stock_text) if stock_text else 0
                if stock < 0:
                    QMessageBox.warning(self, "خطا", "موجودی نمی‌تواند منفی باشد.")
                    return
            except ValueError:
                QMessageBox.warning(self, "خطا", "موجودی باید عدد صحیح باشد.")
                return

            try:
                min_stock = int(min_stock_text) if min_stock_text else 5
                if min_stock < 0:
                    QMessageBox.warning(self, "خطا", "حداقل موجودی نمی‌تواند منفی باشد.")
                    return
            except ValueError:
                QMessageBox.warning(self, "خطا", "حداقل موجودی باید عدد صحیح باشد.")
                return

            # ثبت زمان به‌روزرسانی
            updated_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")

            # به‌روزرسانی محصول در پایگاه داده
            self.cursor.execute(
                "UPDATE products SET name=?, price=?, category=?, image=?, stock=?, min_stock=?, updated_at=? WHERE id=?",
                (name, price, category, image, stock, min_stock, updated_at, product_id)
            )
            self.conn.commit()

            # ثبت فعالیت
            self.log_activity("product", f"به‌روزرسانی محصول: {name}")

            # به‌روزرسانی لیست محصولات
            self.load_products()

            QMessageBox.information(self, "موفقیت", f"محصول '{name}' با موفقیت به‌روزرسانی شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در به‌روزرسانی محصول: {str(e)}")

    def delete_product(self):
        """حذف محصول انتخاب شده"""
        try:
            # بررسی انتخاب محصول
            selected_items = self.products_table.selectedItems()
            if not selected_items:
                QMessageBox.warning(self, "خطا", "لطفاً ابتدا یک محصول را انتخاب کنید.")
                return

            # دریافت شناسه و نام محصول انتخاب شده
            row = selected_items[0].row()
            product_id = int(self.products_table.item(row, 0).text())
            product_name = self.products_table.item(row, 1).text()

            # تأیید حذف
            reply = QMessageBox.question(
                self,
                'تأیید حذف',
                f"آیا از حذف محصول '{product_name}' اطمینان دارید؟",
                QMessageBox.Yes | QMessageBox.No,
                QMessageBox.No
            )

            if reply == QMessageBox.Yes:
                # حذف محصول از پایگاه داده
                self.cursor.execute("DELETE FROM products WHERE id=?", (product_id,))
                self.conn.commit()

                # ثبت فعالیت
                self.log_activity("product", f"حذف محصول: {product_name}")

                # پاک کردن فیلدها
                self.clear_product_fields()

                # به‌روزرسانی لیست محصولات
                self.load_products()

                QMessageBox.information(self, "موفقیت", f"محصول '{product_name}' با موفقیت حذف شد.")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در حذف محصول: {str(e)}")

    def search_products(self):
        """جستجوی محصولات"""
        try:
            search_text = self.search_input.text().strip()
            if not search_text:
                self.load_products()  # نمایش همه محصولات اگر متن جستجو خالی باشد
                return

            # جستجو در پایگاه داده
            self.cursor.execute(
                "SELECT id, name, price, discount_price, category, stock FROM products WHERE name LIKE ? OR category LIKE ?",
                (f"%{search_text}%", f"%{search_text}%")
            )
            products = self.cursor.fetchall()

            # نمایش نتایج
            self.display_products(products)

            # ثبت فعالیت
            self.log_activity("product", f"جستجوی محصولات: {search_text}")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در جستجوی محصولات: {str(e)}")

    def load_products(self):
        """بارگذاری محصولات از پایگاه داده"""
        try:
            category_filter = self.filter_input.currentText()
            sort_by = self.sort_input.currentText()

            # تعیین فیلد مرتب‌سازی
            sort_field = "name" if sort_by == "نام" else "price"

            # اعمال فیلتر دسته‌بندی
            if category_filter == "همه":
                self.cursor.execute(f"SELECT id, name, price, discount_price, category, stock FROM products ORDER BY {sort_field}")
            else:
                self.cursor.execute(
                    f"SELECT id, name, price, discount_price, category, stock FROM products WHERE category = ? ORDER BY {sort_field}",
                    (category_filter,)
                )

            products = self.cursor.fetchall()

            # نمایش محصولات
            self.display_products(products)

            # بارگذاری دسته‌بندی‌ها برای فیلتر و کمبوباکس
            self.load_categories()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری محصولات: {str(e)}")

    def show_products(self):
        """نمایش همه محصولات"""
        try:
            # پاک کردن فیلتر جستجو
            self.search_input.clear()

            # تنظیم فیلتر دسته‌بندی به "همه"
            index = self.filter_input.findText("همه")
            if index >= 0:
                self.filter_input.setCurrentIndex(index)

            # بارگذاری همه محصولات
            self.load_products()

            # ثبت فعالیت
            self.log_activity("product", "نمایش همه محصولات")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در نمایش محصولات: {str(e)}")

    def load_product(self, row, column):
        """بارگذاری اطلاعات محصول انتخاب شده در فرم"""
        try:
            # دریافت شناسه محصول انتخاب شده
            product_id = int(self.products_table.item(row, 0).text())

            # دریافت اطلاعات محصول از پایگاه داده
            self.cursor.execute(
                "SELECT name, price, category, image, stock, min_stock FROM products WHERE id = ?",
                (product_id,)
            )
            product = self.cursor.fetchone()

            if product:
                # نمایش اطلاعات در فرم
                self.name_input.setText(product[0])
                self.price_input.setText(str(product[1]))

                # تنظیم دسته‌بندی
                category_index = self.category_input.findText(product[2])
                if category_index >= 0:
                    self.category_input.setCurrentIndex(category_index)

                self.image_path.setText(product[3] if product[3] else "")
                self.stock_input.setText(str(product[4]))
                self.min_stock_input.setText(str(product[5]))

                # ثبت فعالیت
                self.log_activity("product", f"بارگذاری اطلاعات محصول: {product[0]}")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری اطلاعات محصول: {str(e)}")

    def display_products(self, products):
        """نمایش محصولات در جدول"""
        try:
            self.products_table.setRowCount(0)

            for row_number, product in enumerate(products):
                self.products_table.insertRow(row_number)

                for column_number, data in enumerate(product):
                    item = QTableWidgetItem(str(data if data is not None else ""))
                    self.products_table.setItem(row_number, column_number, item)

            # تنظیم عرض ستون‌ها
            self.products_table.resizeColumnsToContents()
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در نمایش محصولات در جدول: {str(e)}")

    def load_categories(self):
        """بارگذاری دسته‌بندی‌ها از پایگاه داده"""
        try:
            # ذخیره دسته‌بندی فعلی
            current_category = self.category_input.currentText()
            current_filter = self.filter_input.currentText()

            # دریافت دسته‌بندی‌ها از پایگاه داده
            self.cursor.execute("SELECT DISTINCT name FROM categories ORDER BY name")
            categories = [category[0] for category in self.cursor.fetchall()]

            # اگر دسته‌بندی‌ای در پایگاه داده نبود، یک دسته‌بندی پیش‌فرض اضافه می‌کنیم
            if not categories:
                categories = ["عمومی"]
                self.cursor.execute("INSERT INTO categories (name, created_at) VALUES (?, ?)",
                                   ("عمومی", datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")))
                self.conn.commit()

            # به‌روزرسانی کمبوباکس دسته‌بندی
            self.category_input.clear()
            self.category_input.addItems(categories)

            # تنظیم مجدد دسته‌بندی قبلی
            index = self.category_input.findText(current_category)
            if index >= 0:
                self.category_input.setCurrentIndex(index)

            # به‌روزرسانی کمبوباکس فیلتر
            self.filter_input.clear()
            self.filter_input.addItems(["همه"] + categories)

            # تنظیم مجدد فیلتر قبلی
            index = self.filter_input.findText(current_filter)
            if index >= 0:
                self.filter_input.setCurrentIndex(index)
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در بارگذاری دسته‌بندی‌ها: {str(e)}")

    def clear_product_fields(self):
        """پاک کردن فیلدهای فرم محصول"""
        self.name_input.clear()
        self.price_input.clear()
        self.image_path.clear()
        self.stock_input.clear()
        self.min_stock_input.setText("5")  # مقدار پیش‌فرض

    def import_products_from_excel(self):
        """وارد کردن محصولات از فایل Excel"""
        try:
            # انتخاب فایل Excel
            file_path, _ = QFileDialog.getOpenFileName(
                self, 'انتخاب فایل Excel', '', 'Excel Files (*.xlsx *.xls)'
            )

            if not file_path:
                return

            # ایجاد دیالوگ پیشرفت
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("وارد کردن محصولات")
            progress_dialog.setFixedSize(400, 150)

            layout = QVBoxLayout()

            info_label = QLabel("در حال وارد کردن محصولات از فایل Excel...")
            layout.addWidget(info_label)

            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            layout.addWidget(progress_bar)

            status_label = QLabel("آماده‌سازی...")
            layout.addWidget(status_label)

            progress_dialog.setLayout(layout)
            progress_dialog.show()
            QApplication.processEvents()

            # خواندن فایل Excel
            df = pd.read_excel(file_path)

            # بررسی ستون‌های مورد نیاز
            required_columns = ['name', 'price', 'category', 'stock', 'min_stock']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                QMessageBox.warning(
                    self,
                    "خطا در ساختار فایل",
                    f"ستون‌های زیر در فایل یافت نشد: {', '.join(missing_columns)}\n"
                    "فایل باید شامل ستون‌های name, price, category, stock, min_stock باشد."
                )
                progress_dialog.close()
                return

            # تعداد کل رکوردها
            total_records = len(df)
            successful_imports = 0
            failed_imports = 0

            # شروع تراکنش
            self.conn.execute("BEGIN TRANSACTION")

            try:
                # پردازش هر سطر
                for i, row in enumerate(df.itertuples()):
                    try:
                        # به‌روزرسانی نوار پیشرفت
                        progress = int((i / total_records) * 100)
                        progress_bar.setValue(progress)
                        status_label.setText(f"در حال پردازش رکورد {i+1} از {total_records}...")
                        QApplication.processEvents()

                        # استخراج داده‌ها
                        name = getattr(row, 'name', '')
                        price = float(getattr(row, 'price', 0))
                        category = getattr(row, 'category', '')
                        stock = int(getattr(row, 'stock', 0))
                        min_stock = int(getattr(row, 'min_stock', 5))
                        image = getattr(row, 'image', '') if hasattr(row, 'image') else ''
                        description = getattr(row, 'description', '') if hasattr(row, 'description') else ''

                        # بررسی اعتبار داده‌ها
                        if not name or price < 0 or stock < 0 or min_stock < 0:
                            failed_imports += 1
                            continue

                        # افزودن دسته‌بندی اگر وجود نداشت
                        if category:
                            self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
                            if not self.cursor.fetchone():
                                self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))

                        # افزودن محصول
                        self.cursor.execute(
                            "INSERT INTO products (name, price, category, image, stock, min_stock, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (name, price, category, image, stock, min_stock, description)
                        )

                        successful_imports += 1

                    except Exception as e:
                        print(f"Error importing row {i}: {e}")
                        failed_imports += 1

                # پایان تراکنش
                self.conn.commit()

                # به‌روزرسانی لیست محصولات
                self.load_products()

                # نمایش نتیجه
                QMessageBox.information(
                    self,
                    "وارد کردن محصولات",
                    f"عملیات وارد کردن محصولات با موفقیت انجام شد.\n"
                    f"تعداد کل رکوردها: {total_records}\n"
                    f"وارد شده با موفقیت: {successful_imports}\n"
                    f"ناموفق: {failed_imports}"
                )

                # ثبت فعالیت
                self.log_activity("import", f"وارد کردن {successful_imports} محصول از فایل Excel")

            except Exception as e:
                # برگرداندن تراکنش در صورت خطا
                self.conn.rollback()
                QMessageBox.critical(self, "خطا", f"خطا در وارد کردن محصولات: {str(e)}")

            finally:
                progress_dialog.close()

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در وارد کردن محصولات: {str(e)}")

    def import_products_from_csv(self):
        """وارد کردن محصولات از فایل CSV"""
        try:
            # انتخاب فایل CSV
            file_path, _ = QFileDialog.getOpenFileName(
                self, 'انتخاب فایل CSV', '', 'CSV Files (*.csv)'
            )

            if not file_path:
                return

            # ایجاد دیالوگ پیشرفت
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("وارد کردن محصولات")
            progress_dialog.setFixedSize(400, 150)

            layout = QVBoxLayout()

            info_label = QLabel("در حال وارد کردن محصولات از فایل CSV...")
            layout.addWidget(info_label)

            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            layout.addWidget(progress_bar)

            status_label = QLabel("آماده‌سازی...")
            layout.addWidget(status_label)

            progress_dialog.setLayout(layout)
            progress_dialog.show()
            QApplication.processEvents()

            # خواندن فایل CSV
            df = pd.read_csv(file_path)

            # بررسی ستون‌های مورد نیاز
            required_columns = ['name', 'price', 'category', 'stock', 'min_stock']
            missing_columns = [col for col in required_columns if col not in df.columns]

            if missing_columns:
                QMessageBox.warning(
                    self,
                    "خطا در ساختار فایل",
                    f"ستون‌های زیر در فایل یافت نشد: {', '.join(missing_columns)}\n"
                    "فایل باید شامل ستون‌های name, price, category, stock, min_stock باشد."
                )
                progress_dialog.close()
                return

            # تعداد کل رکوردها
            total_records = len(df)
            successful_imports = 0
            failed_imports = 0

            # شروع تراکنش
            self.conn.execute("BEGIN TRANSACTION")

            try:
                # پردازش هر سطر
                for i, row in enumerate(df.itertuples()):
                    try:
                        # به‌روزرسانی نوار پیشرفت
                        progress = int((i / total_records) * 100)
                        progress_bar.setValue(progress)
                        status_label.setText(f"در حال پردازش رکورد {i+1} از {total_records}...")
                        QApplication.processEvents()

                        # استخراج داده‌ها
                        name = getattr(row, 'name', '')
                        price = float(getattr(row, 'price', 0))
                        category = getattr(row, 'category', '')
                        stock = int(getattr(row, 'stock', 0))
                        min_stock = int(getattr(row, 'min_stock', 5))
                        image = getattr(row, 'image', '') if hasattr(row, 'image') else ''
                        description = getattr(row, 'description', '') if hasattr(row, 'description') else ''

                        # بررسی اعتبار داده‌ها
                        if not name or price < 0 or stock < 0 or min_stock < 0:
                            failed_imports += 1
                            continue

                        # افزودن دسته‌بندی اگر وجود نداشت
                        if category:
                            self.cursor.execute("SELECT id FROM categories WHERE name = ?", (category,))
                            if not self.cursor.fetchone():
                                self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (category,))

                        # افزودن محصول
                        self.cursor.execute(
                            "INSERT INTO products (name, price, category, image, stock, min_stock, description) VALUES (?, ?, ?, ?, ?, ?, ?)",
                            (name, price, category, image, stock, min_stock, description)
                        )

                        successful_imports += 1

                    except Exception as e:
                        print(f"Error importing row {i}: {e}")
                        failed_imports += 1

                # پایان تراکنش
                self.conn.commit()

                # به‌روزرسانی لیست محصولات
                self.load_products()

                # نمایش نتیجه
                QMessageBox.information(
                    self,
                    "وارد کردن محصولات",
                    f"عملیات وارد کردن محصولات با موفقیت انجام شد.\n"
                    f"تعداد کل رکوردها: {total_records}\n"
                    f"وارد شده با موفقیت: {successful_imports}\n"
                    f"ناموفق: {failed_imports}"
                )

                # ثبت فعالیت
                self.log_activity("import", f"وارد کردن {successful_imports} محصول از فایل CSV")

            except Exception as e:
                # برگرداندن تراکنش در صورت خطا
                self.conn.rollback()
                QMessageBox.critical(self, "خطا", f"خطا در وارد کردن محصولات: {str(e)}")

            finally:
                progress_dialog.close()

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در وارد کردن محصولات: {str(e)}")

    def export_products_to_excel(self):
        """صادر کردن محصولات به فایل Excel"""
        try:
            # انتخاب مسیر ذخیره فایل
            file_path, _ = QFileDialog.getSaveFileName(
                self, 'ذخیره فایل Excel', '', 'Excel Files (*.xlsx)'
            )

            if not file_path:
                return

            # اضافه کردن پسوند .xlsx اگر نداشت
            if not file_path.endswith('.xlsx'):
                file_path += '.xlsx'

            # ایجاد دیالوگ پیشرفت
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("صادر کردن محصولات")
            progress_dialog.setFixedSize(400, 150)

            layout = QVBoxLayout()

            info_label = QLabel("در حال صادر کردن محصولات به فایل Excel...")
            layout.addWidget(info_label)

            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            layout.addWidget(progress_bar)

            status_label = QLabel("آماده‌سازی...")
            layout.addWidget(status_label)

            progress_dialog.setLayout(layout)
            progress_dialog.show()
            QApplication.processEvents()

            # دریافت همه محصولات
            self.cursor.execute("""
                SELECT id, name, price, discount_price, category, stock, min_stock, image, description
                FROM products
                ORDER BY name
            """)

            products = self.cursor.fetchall()
            total_products = len(products)

            # ایجاد فایل Excel
            workbook = xlsxwriter.Workbook(file_path)
            worksheet = workbook.add_worksheet('Products')

            # تعریف فرمت‌ها
            header_format = workbook.add_format({
                'bold': True,
                'bg_color': '#0078D7',
                'color': 'white',
                'border': 1
            })

            cell_format = workbook.add_format({
                'border': 1
            })

            # نوشتن سرستون‌ها
            headers = ['شناسه', 'نام محصول', 'قیمت', 'قیمت با تخفیف', 'دسته‌بندی',
                      'موجودی', 'حداقل موجودی', 'مسیر تصویر', 'توضیحات']

            for col, header in enumerate(headers):
                worksheet.write(0, col, header, header_format)
                worksheet.set_column(col, col, 15)  # تنظیم عرض ستون

            # نوشتن داده‌ها
            for row, product in enumerate(products):
                # به‌روزرسانی نوار پیشرفت
                progress = int(((row + 1) / total_products) * 100)
                progress_bar.setValue(progress)
                status_label.setText(f"در حال صادر کردن محصول {row+1} از {total_products}...")
                QApplication.processEvents()

                for col, value in enumerate(product):
                    worksheet.write(row + 1, col, value if value is not None else '', cell_format)

            # بستن فایل Excel
            workbook.close()

            progress_dialog.close()

            # نمایش پیام موفقیت
            QMessageBox.information(
                self,
                "صادر کردن محصولات",
                f"تعداد {total_products} محصول با موفقیت به فایل Excel صادر شد."
            )

            # ثبت فعالیت
            self.log_activity("export", f"صادر کردن {total_products} محصول به فایل Excel")

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در صادر کردن محصولات: {str(e)}")

    def export_products_to_csv(self):
        """صادر کردن محصولات به فایل CSV"""
        try:
            # انتخاب مسیر ذخیره فایل
            file_path, _ = QFileDialog.getSaveFileName(
                self, 'ذخیره فایل CSV', '', 'CSV Files (*.csv)'
            )

            if not file_path:
                return

            # اضافه کردن پسوند .csv اگر نداشت
            if not file_path.endswith('.csv'):
                file_path += '.csv'

            # ایجاد دیالوگ پیشرفت
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("صادر کردن محصولات")
            progress_dialog.setFixedSize(400, 150)

            layout = QVBoxLayout()

            info_label = QLabel("در حال صادر کردن محصولات به فایل CSV...")
            layout.addWidget(info_label)

            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            layout.addWidget(progress_bar)

            status_label = QLabel("آماده‌سازی...")
            layout.addWidget(status_label)

            progress_dialog.setLayout(layout)
            progress_dialog.show()
            QApplication.processEvents()

            # دریافت همه محصولات
            self.cursor.execute("""
                SELECT id, name, price, discount_price, category, stock, min_stock, image, description
                FROM products
                ORDER BY name
            """)

            products = self.cursor.fetchall()
            total_products = len(products)

            # نوشتن به فایل CSV
            with open(file_path, 'w', newline='', encoding='utf-8') as csvfile:
                writer = csv.writer(csvfile)

                # نوشتن سرستون‌ها
                headers = ['id', 'name', 'price', 'discount_price', 'category',
                          'stock', 'min_stock', 'image', 'description']
                writer.writerow(headers)

                # نوشتن داده‌ها
                for row, product in enumerate(products):
                    # به‌روزرسانی نوار پیشرفت
                    progress = int(((row + 1) / total_products) * 100)
                    progress_bar.setValue(progress)
                    status_label.setText(f"در حال صادر کردن محصول {row+1} از {total_products}...")
                    QApplication.processEvents()

                    # تبدیل None به رشته خالی
                    product_data = ['' if value is None else value for value in product]
                    writer.writerow(product_data)

            progress_dialog.close()

            # نمایش پیام موفقیت
            QMessageBox.information(
                self,
                "صادر کردن محصولات",
                f"تعداد {total_products} محصول با موفقیت به فایل CSV صادر شد."
            )

            # ثبت فعالیت
            self.log_activity("export", f"صادر کردن {total_products} محصول به فایل CSV")

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در صادر کردن محصولات: {str(e)}")

    def export_products_to_pdf(self):
        """صادر کردن محصولات به فایل PDF"""
        try:
            # انتخاب مسیر ذخیره فایل
            file_path, _ = QFileDialog.getSaveFileName(
                self, 'ذخیره فایل PDF', '', 'PDF Files (*.pdf)'
            )

            if not file_path:
                return

            # اضافه کردن پسوند .pdf اگر نداشت
            if not file_path.endswith('.pdf'):
                file_path += '.pdf'

            # ایجاد دیالوگ پیشرفت
            progress_dialog = QDialog(self)
            progress_dialog.setWindowTitle("صادر کردن محصولات")
            progress_dialog.setFixedSize(400, 150)

            layout = QVBoxLayout()

            info_label = QLabel("در حال صادر کردن محصولات به فایل PDF...")
            layout.addWidget(info_label)

            progress_bar = QProgressBar()
            progress_bar.setRange(0, 100)
            layout.addWidget(progress_bar)

            status_label = QLabel("آماده‌سازی...")
            layout.addWidget(status_label)

            progress_dialog.setLayout(layout)
            progress_dialog.show()
            QApplication.processEvents()

            # دریافت همه محصولات
            self.cursor.execute("""
                SELECT id, name, price, discount_price, category, stock, min_stock
                FROM products
                ORDER BY name
            """)

            products = self.cursor.fetchall()
            total_products = len(products)

            # ایجاد فایل PDF
            c = canvas.Canvas(file_path, pagesize=letter)
            width, height = letter

            # تنظیم عنوان
            c.setFont("Helvetica-Bold", 18)
            c.drawString(50, height - 50, "لیست محصولات")

            # تنظیم تاریخ
            c.setFont("Helvetica", 10)
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            c.drawString(50, height - 70, f"تاریخ: {current_date}")

            # تنظیم سرستون‌ها
            c.setFont("Helvetica-Bold", 12)
            headers = ['شناسه', 'نام محصول', 'قیمت', 'قیمت با تخفیف', 'دسته‌بندی', 'موجودی', 'حداقل موجودی']
            header_widths = [50, 150, 70, 90, 100, 60, 80]

            x_position = 50
            for i, header in enumerate(headers):
                c.drawString(x_position, height - 100, header)
                x_position += header_widths[i]

            # رسم خط زیر سرستون‌ها
            c.line(50, height - 110, 550, height - 110)

            # تنظیم داده‌ها
            c.setFont("Helvetica", 10)
            y_position = height - 130
            items_per_page = 30
            item_count = 0
            page_num = 1

            for row, product in enumerate(products):
                # به‌روزرسانی نوار پیشرفت
                progress = int(((row + 1) / total_products) * 100)
                progress_bar.setValue(progress)
                status_label.setText(f"در حال صادر کردن محصول {row+1} از {total_products}...")
                QApplication.processEvents()

                # بررسی نیاز به صفحه جدید
                if item_count >= items_per_page:
                    c.drawString(width - 50, 30, f"صفحه {page_num}")
                    c.showPage()
                    page_num += 1

                    # تنظیم عنوان در صفحه جدید
                    c.setFont("Helvetica-Bold", 18)
                    c.drawString(50, height - 50, "لیست محصولات")

                    # تنظیم سرستون‌ها در صفحه جدید
                    c.setFont("Helvetica-Bold", 12)
                    x_position = 50
                    for i, header in enumerate(headers):
                        c.drawString(x_position, height - 100, header)
                        x_position += header_widths[i]

                    # رسم خط زیر سرستون‌ها
                    c.line(50, height - 110, 550, height - 110)

                    # بازنشانی متغیرها
                    c.setFont("Helvetica", 10)
                    y_position = height - 130
                    item_count = 0

                # نوشتن داده‌های محصول
                x_position = 50
                for i, value in enumerate(product):
                    text = str(value) if value is not None else ''
                    c.drawString(x_position, y_position, text)
                    x_position += header_widths[i]

                # رسم خط نازک بین ردیف‌ها
                c.line(50, y_position - 5, 550, y_position - 5)

                y_position -= 20
                item_count += 1

            # شماره صفحه آخر
            c.drawString(width - 50, 30, f"صفحه {page_num}")

            # ذخیره فایل PDF
            c.save()

            progress_dialog.close()

            # نمایش پیام موفقیت
            QMessageBox.information(
                self,
                "صادر کردن محصولات",
                f"تعداد {total_products} محصول با موفقیت به فایل PDF صادر شد."
            )

            # ثبت فعالیت
            self.log_activity("export", f"صادر کردن {total_products} محصول به فایل PDF")

        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در صادر کردن محصولات: {str(e)}")

    def initUI(self):
        self.setWindowTitle('مدیریت محصولات')
        self.setGeometry(100, 100, 1000, 700)  # سایز جمع‌تر
        # تنظیم آیکون برنامه
        try:
            self.setWindowIcon(QtGui.QIcon('product_images/app_icon.png'))
        except:
            pass

        # منوی اصلی
        menu_bar = QMenuBar(self)
        self.setMenuBar(menu_bar)

        # منوی گزارش‌ها
        reports_menu = menu_bar.addMenu('گزارش‌ها')
        generate_report_action = QAction('ایجاد گزارش', self)
        generate_report_action.triggered.connect(self.generate_report)
        reports_menu.addAction(generate_report_action)

        # منوی دسته‌بندی‌ها
        categories_menu = menu_bar.addMenu('دسته‌بندی‌ها')
        manage_categories_action = QAction('مدیریت دسته‌بندی‌ها', self)
        manage_categories_action.triggered.connect(self.manage_categories)
        categories_menu.addAction(manage_categories_action)

        # منوی داشبورد
        dashboard_menu = menu_bar.addMenu('داشبورد')
        show_dashboard_action = QAction('نمایش داشبورد آماری', self)
        show_dashboard_action.triggered.connect(self.show_dashboard)
        dashboard_menu.addAction(show_dashboard_action)

        # منوی موجودی
        inventory_menu = menu_bar.addMenu('موجودی')

        manage_stock_action = QAction('مدیریت موجودی', self)
        manage_stock_action.triggered.connect(self.manage_stock)
        inventory_menu.addAction(manage_stock_action)

        view_history_action = QAction('تاریخچه موجودی', self)
        view_history_action.triggered.connect(self.view_inventory_history)
        inventory_menu.addAction(view_history_action)

        low_stock_action = QAction('هشدار موجودی کم', self)
        low_stock_action.triggered.connect(self.show_low_stock_alert)
        inventory_menu.addAction(low_stock_action)

        # منوی بارکد
        barcode_menu = menu_bar.addMenu('بارکد')

        generate_barcode_action = QAction('ایجاد بارکد', self)
        generate_barcode_action.triggered.connect(self.generate_barcode)
        barcode_menu.addAction(generate_barcode_action)

        scan_barcode_action = QAction('اسکن بارکد', self)
        scan_barcode_action.triggered.connect(self.scan_barcode)
        barcode_menu.addAction(scan_barcode_action)

        print_barcode_action = QAction('چاپ بارکدها', self)
        print_barcode_action.triggered.connect(self.print_barcodes)
        barcode_menu.addAction(print_barcode_action)

        # منوی تخفیف‌ها
        discounts_menu = menu_bar.addMenu('تخفیف‌ها')

        manage_discounts_action = QAction('مدیریت تخفیف‌ها', self)
        manage_discounts_action.triggered.connect(self.manage_discounts)
        discounts_menu.addAction(manage_discounts_action)

        apply_discount_action = QAction('اعمال تخفیف به محصول', self)
        apply_discount_action.triggered.connect(self.apply_discount_to_product)
        discounts_menu.addAction(apply_discount_action)

        category_discount_action = QAction('اعمال تخفیف به دسته‌بندی', self)
        category_discount_action.triggered.connect(self.apply_discount_to_category)
        discounts_menu.addAction(category_discount_action)

        clear_discounts_action = QAction('حذف همه تخفیف‌ها', self)
        clear_discounts_action.triggered.connect(self.clear_all_discounts)
        discounts_menu.addAction(clear_discounts_action)

        # منوی تنظیمات
        settings_menu = menu_bar.addMenu('تنظیمات')

        app_settings_action = QAction('تنظیمات برنامه', self)
        app_settings_action.setIcon(QtGui.QIcon.fromTheme("preferences-system", QtGui.QIcon()))
        app_settings_action.triggered.connect(self.show_settings)
        settings_menu.addAction(app_settings_action)

        about_action = QAction('درباره برنامه', self)
        about_action.setIcon(QtGui.QIcon.fromTheme("help-about", QtGui.QIcon()))
        about_action.triggered.connect(self.show_about)
        settings_menu.addAction(about_action)

        # منوی مدیریت محصولات
        product_manager_menu = menu_bar.addMenu('مدیریت محصولات')

        product_manager_fixed_action = QAction('مدیریت محصولات (نسخه جدید)', self)
        product_manager_fixed_action.setIcon(QtGui.QIcon.fromTheme("document-new", QtGui.QIcon()))
        product_manager_fixed_action.triggered.connect(self.open_product_manager_fixed)
        product_manager_menu.addAction(product_manager_fixed_action)

        self.name_label = QLabel('نام:')
        self.name_input = QLineEdit()

        self.price_label = QLabel('قیمت:')
        self.price_input = QLineEdit()

        self.category_label = QLabel('دسته‌بندی:')
        self.category_input = QComboBox()

        self.image_label = QLabel('تصاویر:')
        self.image_path = QLineEdit()
        self.image_browse = QPushButton('انتخاب')
        self.image_browse.clicked.connect(self.browse_image)
        self.manage_images_button = QPushButton('مدیریت تصاویر')
        self.manage_images_button.clicked.connect(self.manage_product_images)

        # فیلدهای موجودی
        self.stock_label = QLabel('موجودی:')
        self.stock_input = QLineEdit()
        self.stock_input.setValidator(QtGui.QIntValidator(0, 999999))  # فقط اعداد صحیح مثبت

        self.min_stock_label = QLabel('حداقل موجودی:')
        self.min_stock_input = QLineEdit()
        self.min_stock_input.setValidator(QtGui.QIntValidator(0, 999999))  # فقط اعداد صحیح مثبت
        self.min_stock_input.setText("5")  # مقدار پیش‌فرض

        self.add_button = QPushButton('افزودن محصول')
        self.add_button.clicked.connect(self.add_product)

        self.update_button = QPushButton('به‌روزرسانی محصول')
        self.update_button.clicked.connect(self.update_product)

        self.delete_button = QPushButton('حذف محصول')
        self.delete_button.clicked.connect(self.delete_product)

        self.search_label = QLabel('جستجو:')
        self.search_input = QLineEdit()
        self.search_button = QPushButton('جستجو')
        self.search_button.clicked.connect(self.search_products)

        self.filter_label = QLabel('فیلتر بر اساس دسته‌بندی:')
        self.filter_input = QComboBox()
        self.filter_input.addItems(['همه'])
        self.filter_input.currentIndexChanged.connect(self.load_products)

        self.sort_label = QLabel('مرتب‌سازی بر اساس:')
        self.sort_input = QComboBox()
        self.sort_input.addItems(['نام', 'قیمت'])
        self.sort_input.currentIndexChanged.connect(self.load_products)

        self.show_button = QPushButton('نمایش همه محصولات')
        self.show_button.clicked.connect(self.show_products)

        self.products_table = QTableWidget()
        self.products_table.setColumnCount(6)
        self.products_table.setHorizontalHeaderLabels(['شناسه', 'نام', 'قیمت', 'قیمت با تخفیف', 'دسته‌بندی', 'موجودی'])
        self.products_table.cellClicked.connect(self.load_product)

        # ایجاد گروه برای اطلاعات اصلی محصول
        product_info_group = QGroupBox("اطلاعات محصول")
        product_info_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                padding-top: 12px;
            }
        """)

        form_layout = QFormLayout()
        form_layout.setSpacing(8)
        form_layout.setContentsMargins(10, 10, 10, 10)

        # تحسين شكل الحقول
        self.name_label.setStyleSheet("font-weight: bold;")
        self.price_label.setStyleSheet("font-weight: bold;")
        self.category_label.setStyleSheet("font-weight: bold;")
        self.stock_label.setStyleSheet("font-weight: bold;")
        self.min_stock_label.setStyleSheet("font-weight: bold;")
        self.image_label.setStyleSheet("font-weight: bold;")

        form_layout.addRow(self.name_label, self.name_input)
        form_layout.addRow(self.price_label, self.price_input)
        form_layout.addRow(self.category_label, self.category_input)
        form_layout.addRow(self.stock_label, self.stock_input)
        form_layout.addRow(self.min_stock_label, self.min_stock_input)

        # تحسين حقل الصورة
        image_layout = QHBoxLayout()
        image_layout.addWidget(self.image_path)
        image_layout.addWidget(self.image_browse)
        image_layout.addWidget(self.manage_images_button)
        form_layout.addRow(self.image_label, image_layout)

        product_info_group.setLayout(form_layout)

        # ایجاد گروه برای دکمه‌های عملیات
        actions_group = QGroupBox("عملیات")
        actions_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                padding-top: 12px;
            }
        """)

        button_layout = QHBoxLayout()
        button_layout.setSpacing(8)
        button_layout.setContentsMargins(10, 10, 10, 10)

        # بهبود ظاهر دکمه‌ها
        self.add_button.setIcon(QtGui.QIcon.fromTheme("list-add", QtGui.QIcon()))
        self.update_button.setIcon(QtGui.QIcon.fromTheme("document-save", QtGui.QIcon()))
        self.delete_button.setIcon(QtGui.QIcon.fromTheme("edit-delete", QtGui.QIcon()))
        self.show_button.setIcon(QtGui.QIcon.fromTheme("view-list-details", QtGui.QIcon()))

        # تغییر رنگ دکمه حذف
        self.delete_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
            QPushButton:pressed {
                background-color: #ac2925;
            }
        """)

        button_layout.addWidget(self.add_button)
        button_layout.addWidget(self.update_button)
        button_layout.addWidget(self.delete_button)
        button_layout.addWidget(self.show_button)

        actions_group.setLayout(button_layout)

        # ایجاد گروه برای جستجو و فیلتر
        search_filter_group = QGroupBox("جستجو و فیلتر")
        search_filter_group.setStyleSheet("""
            QGroupBox {
                font-size: 13px;
                font-weight: bold;
                padding-top: 12px;
            }
        """)

        search_filter_layout = QVBoxLayout()
        search_filter_layout.setSpacing(8)
        search_filter_layout.setContentsMargins(10, 10, 10, 10)

        # تحسين شكل البحث
        search_layout = QHBoxLayout()
        self.search_label.setStyleSheet("font-weight: bold;")
        self.search_button.setIcon(QtGui.QIcon.fromTheme("system-search", QtGui.QIcon()))

        search_layout.addWidget(self.search_label)
        search_layout.addWidget(self.search_input)
        search_layout.addWidget(self.search_button)

        # تحسين شكل التصفية
        filter_layout = QHBoxLayout()
        self.filter_label.setStyleSheet("font-weight: bold;")
        self.sort_label.setStyleSheet("font-weight: bold;")

        filter_layout.addWidget(self.filter_label)
        filter_layout.addWidget(self.filter_input)
        filter_layout.addWidget(self.sort_label)
        filter_layout.addWidget(self.sort_input)

        search_filter_layout.addLayout(search_layout)
        search_filter_layout.addLayout(filter_layout)

        search_filter_group.setLayout(search_filter_layout)

        # تحسين شكل جدول المنتجات
        self.products_table.setAlternatingRowColors(True)
        self.products_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.products_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
        self.products_table.horizontalHeader().setStretchLastSection(True)
        self.products_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)
        self.products_table.setStyleSheet("""
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 6px;
                padding: 5px;
            }
            QTableWidget::item:alternate {
                background-color: #f9f9f9;
            }
        """)

        # چیدمان جدید و جمع‌تر با استفاده از لایه افقی
        main_layout = QHBoxLayout()
        main_layout.setSpacing(10)
        main_layout.setContentsMargins(10, 10, 10, 10)

        # لایه سمت راست برای فرم‌ها
        right_layout = QVBoxLayout()
        right_layout.setSpacing(8)

        # تنظیم اندازه فیلدها برای چیدمان جمع‌تر
        self.name_input.setFixedHeight(28)
        self.price_input.setFixedHeight(28)
        self.category_input.setFixedHeight(28)
        self.stock_input.setFixedHeight(28)
        self.min_stock_input.setFixedHeight(28)
        self.image_path.setFixedHeight(28)
        self.image_browse.setFixedHeight(28)
        self.image_browse.setFixedWidth(80)

        # تنظیم اندازه دکمه‌ها
        self.add_button.setFixedHeight(32)
        self.update_button.setFixedHeight(32)
        self.delete_button.setFixedHeight(32)
        self.show_button.setFixedHeight(32)

        # تنظیم اندازه فیلدهای جستجو
        self.search_input.setFixedHeight(28)
        self.search_button.setFixedHeight(28)
        self.search_button.setFixedWidth(80)
        self.filter_input.setFixedHeight(28)
        self.sort_input.setFixedHeight(28)

        # اضافه کردن گروه‌ها به لایه سمت راست
        right_layout.addWidget(product_info_group)
        right_layout.addWidget(actions_group)
        right_layout.addWidget(search_filter_group)
        right_layout.addStretch()  # فضای خالی در انتهای لایه سمت راست

        # لایه سمت چپ برای جدول محصولات
        left_layout = QVBoxLayout()

        # اضافه کردن عنوان به بخش جدول
        table_title = QLabel("لیست محصولات")
        table_title.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #0078d7;
            padding: 5px;
        """)
        table_title.setAlignment(QtCore.Qt.AlignCenter)

        left_layout.addWidget(table_title)
        left_layout.addWidget(self.products_table)

        # اضافه کردن لایه‌های سمت راست و چپ به لایه اصلی
        main_layout.addLayout(right_layout, 1)  # با نسبت 1
        main_layout.addLayout(left_layout, 2)   # با نسبت 2 (فضای بیشتر برای جدول)

        container = QWidget()
        container.setLayout(main_layout)
        self.setCentralWidget(container)

        # حالا که همه کنترل‌ها ایجاد شده‌اند، دسته‌بندی‌ها را بارگذاری می‌کنیم
        self.load_categories()

        # و سپس محصولات را بارگذاری می‌کنیم
        self.load_products()

    # این متد برای حفظ سازگاری با کد قبلی است
    def initDB(self):
        self.initDB_tables()
        self.load_categories()
        self.load_products()

    def browse_image(self):
        options = QFileDialog.Options()
        file_name, _ = QFileDialog.getOpenFileName(self, "Select Product Image", "", "Image Files (*.png *.jpg *.bmp)", options=options)
        if file_name:
            self.image_path.setText(file_name)

    def add_product(self):
        try:
            # Get input values
            name = self.name_input.text().strip()
            price_text = self.price_input.text().strip()
            category = self.category_input.currentText()
            image = self.image_path.text().strip()
            stock_text = self.stock_input.text().strip()
            min_stock_text = self.min_stock_input.text().strip()

            # Validate inputs
            if not name:
                QMessageBox.warning(self, "Validation Error", "Product name cannot be empty")
                self.name_input.setFocus()
                return

            # Validate price is a number
            try:
                price = float(price_text) if price_text else 0
                if price < 0:
                    QMessageBox.warning(self, "Validation Error", "Price cannot be negative")
                    self.price_input.setFocus()
                    return
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Price must be a valid number")
                self.price_input.setFocus()
                return

            # Validate stock values
            try:
                stock = int(stock_text) if stock_text else 0
                if stock < 0:
                    QMessageBox.warning(self, "Validation Error", "Stock cannot be negative")
                    self.stock_input.setFocus()
                    return
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Stock must be a valid integer")
                self.stock_input.setFocus()
                return

            try:
                min_stock = int(min_stock_text) if min_stock_text else 5
                if min_stock < 0:
                    QMessageBox.warning(self, "Validation Error", "Minimum stock cannot be negative")
                    self.min_stock_input.setFocus()
                    return
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Minimum stock must be a valid integer")
                self.min_stock_input.setFocus()
                return

            # Validate image path if provided
            if image and not os.path.exists(image):
                response = QMessageBox.question(
                    self, "Image Not Found",
                    f"The image file '{image}' does not exist. Do you want to continue anyway?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if response == QMessageBox.No:
                    self.image_path.setFocus()
                    return

            # Insert the product
            self.cursor.execute(
                "INSERT INTO products (name, price, category, image, stock, min_stock) VALUES (?, ?, ?, ?, ?, ?)",
                (name, price, category, image, stock, min_stock)
            )
            product_id = self.cursor.lastrowid
            self.conn.commit()

            # اگر موجودی اولیه بیشتر از صفر باشد، یک رکورد در تاریخچه موجودی ثبت می‌کنیم
            if stock > 0:
                self.add_inventory_history(product_id, stock, "initial", "Initial stock")

            # Clear inputs after successful addition
            self.name_input.clear()
            self.price_input.clear()
            self.stock_input.clear()
            self.min_stock_input.setText("5")  # مقدار پیش‌فرض
            self.image_path.clear()

            # Reload products to show the new one
            self.load_products()

            QMessageBox.information(self, "Success", f"Product '{name}' added successfully")

        except Exception as e:
            error_msg = f"Error adding product: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Add Error", error_msg)
            # Rollback in case of error
            self.conn.rollback()

    def add_inventory_history(self, product_id, change_amount, change_type, notes=""):
        """ثبت تغییرات موجودی در تاریخچه"""
        try:
            current_date = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            self.cursor.execute(
                "INSERT INTO inventory_history (product_id, change_amount, change_type, change_date, notes) VALUES (?, ?, ?, ?, ?)",
                (product_id, change_amount, change_type, current_date, notes)
            )
            self.conn.commit()
            print(f"Inventory history added for product {product_id}: {change_amount} ({change_type})")
        except Exception as e:
            print(f"Error adding inventory history: {e}")
            self.conn.rollback()

    def update_product(self):
        try:
            selected_row = self.products_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Selection Error", "Please select a product to update")
                return

            product_id = self.products_table.item(selected_row, 0).text()

            # Get input values
            name = self.name_input.text().strip()
            price_text = self.price_input.text().strip()
            category = self.category_input.currentText()
            image = self.image_path.text().strip()
            stock_text = self.stock_input.text().strip()
            min_stock_text = self.min_stock_input.text().strip()

            # Validate inputs
            if not name:
                QMessageBox.warning(self, "Validation Error", "Product name cannot be empty")
                self.name_input.setFocus()
                return

            # Validate price is a number
            try:
                price = float(price_text) if price_text else 0
                if price < 0:
                    QMessageBox.warning(self, "Validation Error", "Price cannot be negative")
                    self.price_input.setFocus()
                    return
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Price must be a valid number")
                self.price_input.setFocus()
                return

            # Validate stock values
            try:
                stock = int(stock_text) if stock_text else 0
                if stock < 0:
                    QMessageBox.warning(self, "Validation Error", "Stock cannot be negative")
                    self.stock_input.setFocus()
                    return
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Stock must be a valid integer")
                self.stock_input.setFocus()
                return

            try:
                min_stock = int(min_stock_text) if min_stock_text else 5
                if min_stock < 0:
                    QMessageBox.warning(self, "Validation Error", "Minimum stock cannot be negative")
                    self.min_stock_input.setFocus()
                    return
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Minimum stock must be a valid integer")
                self.min_stock_input.setFocus()
                return

            # Validate image path if provided
            if image and not os.path.exists(image):
                response = QMessageBox.question(
                    self, "Image Not Found",
                    f"The image file '{image}' does not exist. Do you want to continue anyway?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if response == QMessageBox.No:
                    self.image_path.setFocus()
                    return

            # دریافت موجودی قبلی برای ثبت تغییرات
            self.cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
            old_stock = self.cursor.fetchone()[0] or 0

            # دریافت قیمت تخفیف‌دار فعلی (اگر وجود داشته باشد)
            self.cursor.execute("SELECT discount_price FROM products WHERE id = ?", (product_id,))
            current_discount_price = self.cursor.fetchone()[0]

            # اگر قیمت تخفیف‌دار وجود داشته باشد و قیمت اصلی تغییر کرده باشد، قیمت تخفیف‌دار را به‌روزرسانی می‌کنیم
            if current_discount_price is not None:
                # دریافت قیمت اصلی قبلی
                self.cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
                old_price = self.cursor.fetchone()[0] or 0

                if price != old_price:
                    # محاسبه درصد تخفیف فعلی
                    discount_percent = ((old_price - current_discount_price) / old_price) * 100 if old_price > 0 else 0

                    # محاسبه قیمت تخفیف‌دار جدید با همان درصد تخفیف
                    new_discount_price = price * (1 - discount_percent / 100)

                    # Update the product with new discount price
                    self.cursor.execute(
                        "UPDATE products SET name = ?, price = ?, category = ?, image = ?, stock = ?, min_stock = ?, discount_price = ? WHERE id = ?",
                        (name, price, category, image, stock, min_stock, new_discount_price, product_id)
                    )
                else:
                    # Update the product preserving current discount price
                    self.cursor.execute(
                        "UPDATE products SET name = ?, price = ?, category = ?, image = ?, stock = ?, min_stock = ? WHERE id = ?",
                        (name, price, category, image, stock, min_stock, product_id)
                    )
            else:
                # Update the product without discount price
                self.cursor.execute(
                    "UPDATE products SET name = ?, price = ?, category = ?, image = ?, stock = ?, min_stock = ? WHERE id = ?",
                    (name, price, category, image, stock, min_stock, product_id)
                )
            self.conn.commit()

            # ثبت تغییرات موجودی در تاریخچه اگر تغییر کرده باشد
            if stock != old_stock:
                change_amount = stock - old_stock
                change_type = "increase" if change_amount > 0 else "decrease"
                self.add_inventory_history(
                    product_id,
                    abs(change_amount),
                    change_type,
                    f"Stock updated from {old_stock} to {stock}"
                )

            # Reload products to show the updated one
            self.load_products()

            QMessageBox.information(self, "Success", f"Product '{name}' updated successfully")

        except Exception as e:
            error_msg = f"Error updating product: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Update Error", error_msg)
            # Rollback in case of error
            self.conn.rollback()

    def delete_product(self):
        try:
            selected_row = self.products_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Selection Error", "Please select a product to delete")
                return

            product_id = self.products_table.item(selected_row, 0).text()
            product_name = self.products_table.item(selected_row, 1).text()

            # Ask for confirmation before deleting
            response = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete the product '{product_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )

            if response == QMessageBox.Yes:
                self.cursor.execute("DELETE FROM products WHERE id = ?", (product_id,))
                self.conn.commit()
                self.load_products()

                # Clear the input fields
                self.name_input.clear()
                self.price_input.clear()
                self.image_path.clear()

                QMessageBox.information(self, "Success", f"Product '{product_name}' deleted successfully")

        except Exception as e:
            error_msg = f"Error deleting product: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Delete Error", error_msg)
            # Rollback in case of error
            self.conn.rollback()

    def load_product(self, row, column):
        try:
            product_id = self.products_table.item(row, 0).text()
            self.cursor.execute("SELECT * FROM products WHERE id = ?", (product_id,))
            product = self.cursor.fetchone()

            if not product:
                print(f"No product found with ID {product_id}")
                return

            # Clear previous values first
            self.name_input.clear()
            self.price_input.clear()
            self.stock_input.clear()
            self.min_stock_input.clear()
            self.image_path.clear()

            # Set new values with proper error handling
            self.name_input.setText(product[1] if product[1] else "")
            self.price_input.setText(str(product[2]) if product[2] is not None else "")

            # نمایش اطلاعات قیمت تخفیف‌دار در کنسول
            if product[7] is not None:  # discount_price
                discount_amount = product[2] - product[7]
                discount_percent = (discount_amount / product[2]) * 100 if product[2] > 0 else 0
                print(f"Product has a discount: Original: {product[2]}, Discounted: {product[7]} (Save: {discount_amount:.2f}, {discount_percent:.1f}%)")

            # Set category if it exists
            if product[3] and hasattr(self, 'category_input'):
                index = self.category_input.findText(product[3])
                if index >= 0:
                    self.category_input.setCurrentIndex(index)

            # Set image path
            self.image_path.setText(product[4] if product[4] else "")

            # Set stock values
            # در اینجا فرض می‌کنیم که ستون‌های stock و min_stock به ترتیب در ایندکس‌های 5 و 6 قرار دارند
            if len(product) > 5:
                self.stock_input.setText(str(product[5]) if product[5] is not None else "0")

            if len(product) > 6:
                self.min_stock_input.setText(str(product[6]) if product[6] is not None else "5")

            # نمایش تاریخچه موجودی در کنسول
            self.cursor.execute("""
                SELECT change_amount, change_type, change_date, notes
                FROM inventory_history
                WHERE product_id = ?
                ORDER BY change_date DESC
                LIMIT 5
            """, (product_id,))
            history = self.cursor.fetchall()

            if history:
                print(f"\nRecent inventory history for {product[1]}:")
                for record in history:
                    print(f"  {record[2]}: {record[0]} ({record[1]}) - {record[3]}")

            print(f"Loaded product: {product[1]}")
        except Exception as e:
            error_msg = f"Error loading product details: {e}"
            print(error_msg)
            QMessageBox.warning(self, "Load Error", error_msg)

    def load_products(self):
        try:
            # بررسی وجود فیلترها و مرتب‌سازی
            if hasattr(self, 'filter_input') and hasattr(self, 'sort_input'):
                filter_category = self.filter_input.currentText()
                sort_field = self.sort_input.currentText().lower()
            else:
                # مقادیر پیش‌فرض اگر هنوز کنترل‌ها ایجاد نشده‌اند
                filter_category = 'All'
                sort_field = 'name'

            # ساخت کوئری با پارامترهای امن
            query = "SELECT id, name, price, discount_price, category, stock, min_stock FROM products"
            params = []

            if filter_category != 'All':
                query += " WHERE category = ?"
                params.append(filter_category)

            # استفاده از پارامترهای امن برای مرتب‌سازی
            if sort_field == 'price':
                query += " ORDER BY COALESCE(discount_price, price)"  # اگر قیمت تخفیف‌دار وجود داشت، بر اساس آن مرتب می‌کنیم
            elif sort_field == 'stock':
                query += " ORDER BY stock"
            else:
                query += " ORDER BY name"  # پیش‌فرض مرتب‌سازی بر اساس نام

            # اجرای کوئری
            self.cursor.execute(query, params)
            products = self.cursor.fetchall()

            # نمایش محصولات در جدول
            if hasattr(self, 'products_table'):
                self.products_table.setRowCount(len(products))
                for i, product in enumerate(products):
                    # ستون‌های اصلی
                    self.products_table.setItem(i, 0, QTableWidgetItem(str(product[0])))
                    self.products_table.setItem(i, 1, QTableWidgetItem(product[1] if product[1] else ""))

                    # قیمت اصلی
                    price_item = QTableWidgetItem(str(product[2]) if product[2] is not None else "")
                    self.products_table.setItem(i, 2, price_item)

                    # قیمت با تخفیف
                    if product[3] is not None:
                        discount_price_item = QTableWidgetItem(str(product[3]))
                        discount_price_item.setForeground(QtGui.QBrush(QtGui.QColor(0, 128, 0)))  # رنگ سبز
                        discount_price_item.setBackground(QtGui.QColor(240, 255, 240))  # پس‌زمینه سبز بسیار کمرنگ
                        self.products_table.setItem(i, 3, discount_price_item)

                        # قیمت اصلی را با خط خورده نمایش می‌دهیم
                        font = price_item.font()
                        font.setStrikeOut(True)
                        price_item.setFont(font)
                        price_item.setForeground(QtGui.QBrush(QtGui.QColor(128, 128, 128)))  # رنگ خاکستری
                    else:
                        self.products_table.setItem(i, 3, QTableWidgetItem(""))

                    # دسته‌بندی
                    self.products_table.setItem(i, 4, QTableWidgetItem(product[4] if product[4] else ""))

                    # ستون موجودی با رنگ‌بندی
                    stock_item = QTableWidgetItem(str(product[5]) if product[5] is not None else "0")

                    # اگر موجودی کمتر از حداقل موجودی باشد، با رنگ قرمز نمایش داده می‌شود
                    if product[5] is not None and product[6] is not None and product[5] < product[6]:
                        stock_item.setBackground(QtGui.QColor(255, 200, 200))  # رنگ قرمز کمرنگ

                    self.products_table.setItem(i, 5, stock_item)

                # بررسی محصولات با موجودی کم و نمایش هشدار
                self.check_low_stock()

                print(f"Loaded {len(products)} products in table")
        except Exception as e:
            print(f"Error in load_products: {e}")
            if hasattr(self, 'products_table'):
                QMessageBox.warning(self, "Load Error", f"Error loading products: {str(e)}")

    def check_low_stock(self):
        """بررسی محصولات با موجودی کم و نمایش هشدار"""
        try:
            self.cursor.execute("""
                SELECT name, stock, min_stock
                FROM products
                WHERE stock < min_stock
            """)
            low_stock_products = self.cursor.fetchall()

            if low_stock_products:
                message = "The following products have low stock:\n\n"
                for product in low_stock_products:
                    message += f"• {product[0]}: {product[1]} (Min: {product[2]})\n"

                QMessageBox.warning(self, "Low Stock Warning", message)
        except Exception as e:
            print(f"Error checking low stock: {e}")

    def search_products(self):
        try:
            search_term = self.search_input.text().strip()
            if not search_term:
                # If search term is empty, just reload all products
                self.load_products()
                return

            # Use parameterized query to prevent SQL injection
            self.cursor.execute("SELECT id, name, price, discount_price, category, stock, min_stock FROM products WHERE name LIKE ?", ('%' + search_term + '%',))
            products = self.cursor.fetchall()

            self.products_table.setRowCount(len(products))
            for i, product in enumerate(products):
                # ستون‌های اصلی
                self.products_table.setItem(i, 0, QTableWidgetItem(str(product[0])))
                self.products_table.setItem(i, 1, QTableWidgetItem(product[1] if product[1] else ""))

                # قیمت اصلی
                price_item = QTableWidgetItem(str(product[2]) if product[2] is not None else "")
                self.products_table.setItem(i, 2, price_item)

                # قیمت با تخفیف
                if product[3] is not None:
                    discount_price_item = QTableWidgetItem(str(product[3]))
                    discount_price_item.setForeground(QtGui.QBrush(QtGui.QColor(0, 128, 0)))  # رنگ سبز
                    discount_price_item.setBackground(QtGui.QColor(240, 255, 240))  # پس‌زمینه سبز بسیار کمرنگ
                    self.products_table.setItem(i, 3, discount_price_item)

                    # قیمت اصلی را با خط خورده نمایش می‌دهیم
                    font = price_item.font()
                    font.setStrikeOut(True)
                    price_item.setFont(font)
                    price_item.setForeground(QtGui.QBrush(QtGui.QColor(128, 128, 128)))  # رنگ خاکستری
                else:
                    self.products_table.setItem(i, 3, QTableWidgetItem(""))

                # دسته‌بندی
                self.products_table.setItem(i, 4, QTableWidgetItem(product[4] if product[4] else ""))

                # ستون موجودی با رنگ‌بندی
                stock_item = QTableWidgetItem(str(product[5]) if product[5] is not None else "0")

                # اگر موجودی کمتر از حداقل موجودی باشد، با رنگ قرمز نمایش داده می‌شود
                if product[5] is not None and product[6] is not None and product[5] < product[6]:
                    stock_item.setBackground(QtGui.QColor(255, 200, 200))  # رنگ قرمز کمرنگ

                self.products_table.setItem(i, 5, stock_item)

            print(f"Search found {len(products)} products matching '{search_term}'")

            # Show a message if no products were found
            if len(products) == 0:
                QMessageBox.information(self, "Search Results", f"No products found matching '{search_term}'")

        except Exception as e:
            error_msg = f"Error in search_products: {e}"
            print(error_msg)
            QMessageBox.warning(self, "Search Error", error_msg)

    def show_products(self):
        try:
            # دریافت همه محصولات با قیمت تخفیف‌دار
            self.cursor.execute("SELECT name, price, discount_price, category, image FROM products ORDER BY category")
            products = self.cursor.fetchall()

            self.products_dialog = QDialog(self)
            self.products_dialog.setWindowTitle('نمایش محصولات')
            self.products_dialog.setMinimumWidth(800)
            self.products_dialog.setMinimumHeight(600)

            # تنظیم استایل دیالوگ
            self.products_dialog.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                }
                QLabel {
                    color: #333333;
                }
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    margin-top: 20px;
                    font-weight: bold;
                    background-color: white;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 10px;
                    color: #0078d7;
                    font-size: 14px;
                }
            """)

            # ایجاد تب‌ویجت برای نمایش دسته‌بندی‌ها
            tab_widget = QTabWidget()
            tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    background-color: white;
                }
                QTabBar::tab {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 8px 16px;
                    margin-right: 2px;
                    font-weight: bold;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    border-bottom: 2px solid #0078d7;
                }
            """)

            # گروه‌بندی محصولات بر اساس دسته‌بندی
            categories = {}
            for product in products:
                category = product[3] if product[3] else "بدون دسته‌بندی"
                if category not in categories:
                    categories[category] = []
                categories[category].append(product)

            # ایجاد تب "همه محصولات"
            all_products_tab = QWidget()
            all_products_layout = QVBoxLayout()

            # ایجاد فلوویجت برای نمایش کارت‌های محصول
            all_products_flow = QWidget()
            flow_layout = QGridLayout(all_products_flow)
            flow_layout.setSpacing(15)

            # تعداد ستون‌ها در هر ردیف
            columns = 3

            # ایجاد کارت برای هر محصول
            for i, product in enumerate(products):
                product_card = self.create_product_card(product)
                row = i // columns
                col = i % columns
                flow_layout.addWidget(product_card, row, col)

            # اضافه کردن اسکرول به فلوویجت
            scroll_area = QScrollArea()
            scroll_area.setWidgetResizable(True)
            scroll_area.setWidget(all_products_flow)
            all_products_layout.addWidget(scroll_area)
            all_products_tab.setLayout(all_products_layout)

            # اضافه کردن تب همه محصولات
            tab_widget.addTab(all_products_tab, f"همه محصولات ({len(products)})")

            # ایجاد تب برای هر دسته‌بندی
            for category, category_products in categories.items():
                category_tab = QWidget()
                category_layout = QVBoxLayout()

                # ایجاد فلوویجت برای نمایش کارت‌های محصول در این دسته‌بندی
                category_flow = QWidget()
                cat_flow_layout = QGridLayout(category_flow)
                cat_flow_layout.setSpacing(15)

                # ایجاد کارت برای هر محصول در این دسته‌بندی
                for i, product in enumerate(category_products):
                    product_card = self.create_product_card(product)
                    row = i // columns
                    col = i % columns
                    cat_flow_layout.addWidget(product_card, row, col)

                # اضافه کردن اسکرول به فلوویجت
                cat_scroll_area = QScrollArea()
                cat_scroll_area.setWidgetResizable(True)
                cat_scroll_area.setWidget(category_flow)
                category_layout.addWidget(cat_scroll_area)
                category_tab.setLayout(category_layout)

                # اضافه کردن تب دسته‌بندی
                tab_widget.addTab(category_tab, f"{category} ({len(category_products)})")

            # اضافه کردن تب‌ویجت به دیالوگ
            dialog_layout = QVBoxLayout()
            dialog_layout.addWidget(tab_widget)
            self.products_dialog.setLayout(dialog_layout)

            self.products_dialog.exec_()

            print(f"Displayed {len(products)} products in dialog")
        except Exception as e:
            print(f"Error in show_products: {e}")
            QMessageBox.warning(self, "Display Error", f"Error displaying products: {str(e)}")

    def create_product_card(self, product):
        """ایجاد کارت محصول با طراحی جدید"""
        # استخراج اطلاعات محصول
        name = product[0] if product[0] else "بدون نام"
        price = product[1] if product[1] is not None else 0
        discount_price = product[2]
        image_path = product[4]

        # ایجاد کارت محصول
        card = QGroupBox()
        card.setFixedSize(220, 280)
        card.setStyleSheet("""
            QGroupBox {
                border: 1px solid #dddddd;
                border-radius: 8px;
                background-color: white;
            }
            QGroupBox:hover {
                border: 1px solid #0078d7;
                background-color: #f0f7ff;
            }
        """)

        # لایه عمودی برای چیدمان عناصر کارت
        card_layout = QVBoxLayout()
        card_layout.setAlignment(QtCore.Qt.AlignCenter)
        card_layout.setSpacing(5)
        card_layout.setContentsMargins(10, 10, 10, 10)

        # نام محصول
        name_label = QLabel(name)
        name_label.setStyleSheet("""
            font-size: 14px;
            font-weight: bold;
            color: #333333;
        """)
        name_label.setAlignment(QtCore.Qt.AlignCenter)
        name_label.setWordWrap(True)

        # تصویر محصول
        image_label = QLabel()
        image_label.setFixedSize(150, 150)
        image_label.setAlignment(QtCore.Qt.AlignCenter)
        image_label.setStyleSheet("""
            border: 1px solid #eeeeee;
            border-radius: 4px;
            background-color: #f9f9f9;
        """)

        # بررسی وجود تصویر
        if image_path and os.path.exists(image_path):
            try:
                pixmap = QtGui.QPixmap(image_path)
                if not pixmap.isNull():
                    image_label.setPixmap(pixmap.scaled(150, 150, QtCore.Qt.KeepAspectRatio))
                else:
                    image_label.setText("تصویر نامعتبر")
            except Exception as e:
                print(f"Error loading image for product {name}: {e}")
                image_label.setText("خطای تصویر")
        else:
            image_label.setText("بدون تصویر")

        # قیمت محصول
        price_layout = QVBoxLayout()
        price_layout.setAlignment(QtCore.Qt.AlignCenter)
        price_layout.setSpacing(2)

        if discount_price is not None:
            # قیمت اصلی با خط خورده
            original_price_label = QLabel(f"{price:,} تومان")
            original_price_label.setStyleSheet("""
                font-size: 12px;
                color: #999999;
                text-decoration: line-through;
            """)
            original_price_label.setAlignment(QtCore.Qt.AlignCenter)

            # قیمت با تخفیف
            discount_price_label = QLabel(f"{discount_price:,} تومان")
            discount_price_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #e91e63;
            """)
            discount_price_label.setAlignment(QtCore.Qt.AlignCenter)

            # محاسبه درصد تخفیف
            if price > 0:
                discount_percent = ((price - discount_price) / price) * 100
                discount_badge = QLabel(f"{discount_percent:.0f}% تخفیف")
                discount_badge.setStyleSheet("""
                    background-color: #e91e63;
                    color: white;
                    border-radius: 4px;
                    padding: 2px 6px;
                    font-size: 11px;
                    font-weight: bold;
                """)
                discount_badge.setAlignment(QtCore.Qt.AlignCenter)
                price_layout.addWidget(discount_badge)

            price_layout.addWidget(original_price_label)
            price_layout.addWidget(discount_price_label)
        else:
            # فقط قیمت اصلی
            price_label = QLabel(f"{price:,} تومان")
            price_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #333333;
            """)
            price_label.setAlignment(QtCore.Qt.AlignCenter)
            price_layout.addWidget(price_label)

        # اضافه کردن عناصر به کارت
        card_layout.addWidget(name_label)
        card_layout.addWidget(image_label)
        card_layout.addLayout(price_layout)

        card.setLayout(card_layout)
        return card

    def generate_report(self):
        try:
            self.cursor.execute("SELECT name, price, category FROM products")
            products = self.cursor.fetchall()

            if not products:
                QMessageBox.information(self, "No Data", "There are no products to include in the report.")
                return

            report_file = QFileDialog.getSaveFileName(self, "Save Report", "", "PDF Files (*.pdf)")[0]
            if report_file:
                try:
                    # Make sure the directory exists
                    report_dir = os.path.dirname(report_file)
                    if report_dir and not os.path.exists(report_dir):
                        os.makedirs(report_dir)

                    c = canvas.Canvas(report_file, pagesize=letter)
                    c.setFont("Helvetica-Bold", 16)
                    c.drawString(100, 750, "Product Report")
                    c.setFont("Helvetica", 12)
                    c.drawString(100, 730, "=================")

                    # Add date to the report
                    from datetime import datetime
                    c.drawString(400, 750, datetime.now().strftime("%Y-%m-%d"))

                    c.setFont("Helvetica", 10)
                    y = 700

                    # Add table headers
                    c.drawString(100, y, "Name")
                    c.drawString(250, y, "Price")
                    c.drawString(400, y, "Category")
                    y -= 20

                    # Add a line under headers
                    c.line(100, y+10, 500, y+10)

                    for product in products:
                        # Handle potential None values
                        name = product[0] if product[0] else "N/A"
                        price = str(product[1]) if product[1] is not None else "N/A"
                        category = product[2] if product[2] else "N/A"

                        c.drawString(100, y, f"{name}")
                        c.drawString(250, y, f"{price}")
                        c.drawString(400, y, f"{category}")
                        y -= 20

                        if y < 50:
                            c.showPage()
                            c.setFont("Helvetica", 10)
                            y = 750

                    c.save()
                    print(f"Report generated successfully: {report_file}")
                    QMessageBox.information(self, "Success", f"Report generated successfully: {report_file}")
                except Exception as e:
                    error_msg = f"Error generating PDF: {e}"
                    print(error_msg)
                    QMessageBox.critical(self, "Report Error", error_msg)
        except Exception as e:
            error_msg = f"Error in generate_report: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Report Error", error_msg)

    def manage_categories(self):
        self.categories_dialog = QDialog()
        self.categories_dialog.setWindowTitle('مدیریت دسته‌بندی‌ها')
        self.categories_dialog.setMinimumSize(500, 400)
        self.categories_dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-weight: bold;
            }
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 6px 12px;
                min-width: 80px;
                font-weight: bold;
            }
            QPushButton:hover {
                background-color: #00559b;
            }
            QPushButton:pressed {
                background-color: #003c6c;
            }
            QLineEdit {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 5px;
                background-color: white;
            }
            QLineEdit:focus {
                border: 1px solid #0078d7;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # عنوان صفحه
        title_label = QLabel("مدیریت دسته‌بندی‌های محصولات")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #0078d7;
            margin-bottom: 10px;
        """)
        layout.addWidget(title_label)

        # گروه دسته‌بندی‌های فعلی
        categories_group = QGroupBox("دسته‌بندی‌های موجود")
        categories_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 15px;
            }
        """)

        categories_layout = QVBoxLayout()
        categories_layout.setContentsMargins(10, 15, 10, 10)

        self.categories_table = QTableWidget()
        self.categories_table.setColumnCount(2)
        self.categories_table.setHorizontalHeaderLabels(['شناسه', 'نام'])
        self.categories_table.setAlternatingRowColors(True)
        self.categories_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
        self.categories_table.horizontalHeader().setStretchLastSection(True)
        self.categories_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

        categories_layout.addWidget(self.categories_table)
        categories_group.setLayout(categories_layout)
        layout.addWidget(categories_group)

        self.load_categories_table()

        # گروه افزودن دسته‌بندی جدید
        add_category_group = QGroupBox("افزودن دسته‌بندی جدید")
        add_category_group.setStyleSheet("""
            QGroupBox {
                font-size: 14px;
                font-weight: bold;
                padding-top: 15px;
            }
        """)

        add_category_layout = QVBoxLayout()
        add_category_layout.setContentsMargins(10, 15, 10, 10)

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        name_label = QLabel("نام دسته‌بندی:")
        name_label.setStyleSheet("font-weight: bold;")
        self.category_name_input = QLineEdit()
        self.category_name_input.setPlaceholderText("نام دسته‌بندی جدید را وارد کنید")

        form_layout.addRow(name_label, self.category_name_input)
        add_category_layout.addLayout(form_layout)

        # دکمه‌های عملیات
        buttons_layout = QHBoxLayout()

        add_button = QPushButton("افزودن دسته‌بندی")
        add_button.setIcon(QtGui.QIcon.fromTheme("list-add", QtGui.QIcon()))
        add_button.clicked.connect(self.add_category)

        delete_button = QPushButton("حذف انتخاب شده")
        delete_button.setIcon(QtGui.QIcon.fromTheme("edit-delete", QtGui.QIcon()))
        delete_button.setStyleSheet("""
            QPushButton {
                background-color: #d9534f;
                color: white;
            }
            QPushButton:hover {
                background-color: #c9302c;
            }
            QPushButton:pressed {
                background-color: #ac2925;
            }
        """)
        delete_button.clicked.connect(self.delete_selected_category)

        close_button = QPushButton("بستن")
        close_button.clicked.connect(self.categories_dialog.reject)

        buttons_layout.addWidget(add_button)
        buttons_layout.addWidget(delete_button)
        buttons_layout.addStretch()
        buttons_layout.addWidget(close_button)

        add_category_layout.addLayout(buttons_layout)
        add_category_group.setLayout(add_category_layout)
        layout.addWidget(add_category_group)

        self.categories_dialog.setLayout(layout)
        self.categories_dialog.exec_()

    def delete_selected_category(self):
        """حذف الفئة المحددة"""
        try:
            selected_row = self.categories_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Selection Error", "Please select a category to delete")
                return

            category_id = self.categories_table.item(selected_row, 0).text()
            category_name = self.categories_table.item(selected_row, 1).text()

            # التحقق من وجود منتجات في هذه الفئة
            self.cursor.execute("SELECT COUNT(*) FROM products WHERE category = ?", (category_name,))
            product_count = self.cursor.fetchone()[0]

            if product_count > 0:
                QMessageBox.warning(
                    self, "Cannot Delete",
                    f"Cannot delete category '{category_name}' because it contains {product_count} products.\n"
                    "Please reassign or delete these products first."
                )
                return

            # تأكيد الحذف
            response = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete the category '{category_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )

            if response == QMessageBox.Yes:
                self.cursor.execute("DELETE FROM categories WHERE id = ?", (category_id,))
                self.conn.commit()
                self.load_categories_table()
                self.load_categories()
                QMessageBox.information(self, "Success", f"Category '{category_name}' deleted successfully")

        except Exception as e:
            error_msg = f"Error deleting category: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            self.conn.rollback()

    def load_categories(self):
        try:
            # دریافت دسته‌بندی‌ها از پایگاه داده
            self.cursor.execute("SELECT name FROM categories")
            categories = self.cursor.fetchall()
            category_names = [cat[0] for cat in categories]

            # به‌روزرسانی کنترل‌ها اگر وجود داشته باشند
            if hasattr(self, 'category_input'):
                current_text = self.category_input.currentText() if self.category_input.count() > 0 else ""
                self.category_input.clear()
                self.category_input.addItems(category_names)

                # Try to restore the previous selection if it still exists
                if current_text and current_text in category_names:
                    self.category_input.setCurrentText(current_text)

            if hasattr(self, 'filter_input'):
                current_filter = self.filter_input.currentText() if self.filter_input.count() > 0 else "All"
                self.filter_input.clear()
                self.filter_input.addItems(['All'] + category_names)

                # Try to restore the previous filter if it still exists
                if current_filter in ['All'] + category_names:
                    self.filter_input.setCurrentText(current_filter)

            print(f"Loaded {len(categories)} categories")
        except Exception as e:
            print(f"Error in load_categories: {e}")
            if hasattr(self, 'category_input') or hasattr(self, 'filter_input'):
                QMessageBox.warning(self, "Category Error", f"Error loading categories: {str(e)}")

    def load_categories_table(self):
        try:
            # دریافت دسته‌بندی‌ها از پایگاه داده
            self.cursor.execute("SELECT id, name FROM categories")
            categories = self.cursor.fetchall()

            # به‌روزرسانی جدول اگر وجود داشته باشد
            if hasattr(self, 'categories_table'):
                self.categories_table.setRowCount(len(categories))
                for i, category in enumerate(categories):
                    self.categories_table.setItem(i, 0, QTableWidgetItem(str(category[0])))
                    self.categories_table.setItem(i, 1, QTableWidgetItem(category[1]))

            print(f"Loaded {len(categories)} categories in table")
        except Exception as e:
            print(f"Error in load_categories_table: {e}")

    def add_category(self):
        try:
            name = self.category_name_input.text()
            if not name.strip():
                print("Category name cannot be empty")
                return

            self.cursor.execute("INSERT INTO categories (name) VALUES (?)", (name,))
            self.conn.commit()
            self.load_categories()
            self.load_categories_table()
            self.category_name_input.clear()
            self.categories_dialog.accept()

            print(f"Category '{name}' added successfully")
        except Exception as e:
            print(f"Error in add_category: {e}")

    def show_dashboard(self):
        try:
            # ایجاد دیالوگ داشبورد
            dashboard_dialog = QDialog(self)
            dashboard_dialog.setWindowTitle('داشبورد آماری')
            dashboard_dialog.setMinimumSize(900, 700)
            dashboard_dialog.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                }
                QLabel {
                    color: #333333;
                }
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    margin-top: 20px;
                    font-weight: bold;
                    background-color: white;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 10px;
                    color: #0078d7;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00559b;
                }
                QTabWidget::pane {
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    background-color: white;
                }
                QTabBar::tab {
                    background-color: #f0f0f0;
                    border: 1px solid #cccccc;
                    border-bottom: none;
                    border-top-left-radius: 4px;
                    border-top-right-radius: 4px;
                    padding: 8px 16px;
                    margin-right: 2px;
                    font-weight: bold;
                }
                QTabBar::tab:selected {
                    background-color: white;
                    border-bottom: 2px solid #0078d7;
                }
            """)

            # ایجاد لایه اصلی
            main_layout = QVBoxLayout()
            main_layout.setSpacing(15)
            main_layout.setContentsMargins(20, 20, 20, 20)

            # عنوان داشبورد
            title_label = QLabel("داشبورد آماری محصولات")
            title_label.setStyleSheet("""
                font-size: 22px;
                font-weight: bold;
                color: #0078d7;
                margin-bottom: 10px;
                padding: 5px;
                border-bottom: 2px solid #0078d7;
            """)
            title_label.setAlignment(QtCore.Qt.AlignCenter)
            main_layout.addWidget(title_label)

            # ایجاد تب‌ها
            tab_widget = QTabWidget()
            tab_widget.setStyleSheet("""
                QTabWidget::tab-bar {
                    alignment: center;
                }
            """)

            # تب آمار کلی
            summary_tab = QWidget()
            summary_layout = QVBoxLayout()
            summary_layout.setSpacing(15)
            summary_layout.setContentsMargins(15, 15, 15, 15)

            # دریافت آمار کلی
            stats = self.get_product_stats()

            # نمایش آمار کلی در کارت‌های جذاب
            stats_cards_layout = QHBoxLayout()

            # کارت تعداد محصولات
            products_card = QGroupBox("تعداد کل محصولات")
            products_card.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                    background-color: #e8f4fc;
                    padding: 10px;
                    min-height: 100px;
                }
                QGroupBox::title {
                    color: #0078d7;
                    font-size: 14px;
                }
            """)
            products_layout = QVBoxLayout()
            products_value = QLabel(str(stats['total_products']))
            products_value.setStyleSheet("""
                font-size: 36px;
                font-weight: bold;
                color: #0078d7;
            """)
            products_value.setAlignment(QtCore.Qt.AlignCenter)
            products_layout.addWidget(products_value)
            products_card.setLayout(products_layout)
            stats_cards_layout.addWidget(products_card)

            # کارت تعداد دسته‌بندی‌ها
            categories_card = QGroupBox("تعداد دسته‌بندی‌ها")
            categories_card.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                    background-color: #e8fcef;
                    padding: 10px;
                    min-height: 100px;
                }
                QGroupBox::title {
                    color: #00a651;
                    font-size: 14px;
                }
            """)
            categories_layout = QVBoxLayout()
            categories_value = QLabel(str(stats['total_categories']))
            categories_value.setStyleSheet("""
                font-size: 36px;
                font-weight: bold;
                color: #00a651;
            """)
            categories_value.setAlignment(QtCore.Qt.AlignCenter)
            categories_layout.addWidget(categories_value)
            categories_card.setLayout(categories_layout)
            stats_cards_layout.addWidget(categories_card)

            # کارت متوسط قیمت
            avg_price_card = QGroupBox("میانگین قیمت")
            avg_price_card.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                    background-color: #fff8e8;
                    padding: 10px;
                    min-height: 100px;
                }
                QGroupBox::title {
                    color: #ff9800;
                    font-size: 14px;
                }
            """)
            avg_price_layout = QVBoxLayout()
            avg_price_value = QLabel(f"{stats['avg_price']:.2f}")
            avg_price_value.setStyleSheet("""
                font-size: 36px;
                font-weight: bold;
                color: #ff9800;
            """)
            avg_price_value.setAlignment(QtCore.Qt.AlignCenter)
            avg_price_layout.addWidget(avg_price_value)
            avg_price_card.setLayout(avg_price_layout)
            stats_cards_layout.addWidget(avg_price_card)

            summary_layout.addLayout(stats_cards_layout)

            # جدول آمار تفصیلی
            detailed_stats_group = QGroupBox("آمار تفصیلی")
            detailed_stats_group.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    margin-top: 20px;
                    font-weight: bold;
                    background-color: white;
                }
            """)

            detailed_stats_layout = QGridLayout()
            detailed_stats_layout.setSpacing(10)
            detailed_stats_layout.setContentsMargins(15, 15, 15, 15)

            # عناوین ستون‌ها
            header_style = "font-weight: bold; color: #0078d7; font-size: 13px;"
            value_style = "font-size: 13px; color: #333333;"

            detailed_stats_layout.addWidget(QLabel("معیار"), 0, 0)
            detailed_stats_layout.addWidget(QLabel("مقدار"), 0, 1)

            # مقادیر
            metrics = [
                ("تعداد کل محصولات", str(stats['total_products'])),
                ("تعداد دسته‌بندی‌ها", str(stats['total_categories'])),
                ("میانگین قیمت", f"{stats['avg_price']:.2f}"),
                ("کمترین قیمت", f"{stats['min_price']:.2f}"),
                ("بیشترین قیمت", f"{stats['max_price']:.2f}")
            ]

            for i, (metric, value) in enumerate(metrics, 1):
                metric_label = QLabel(metric)
                metric_label.setStyleSheet(header_style)

                value_label = QLabel(value)
                value_label.setStyleSheet(value_style)

                detailed_stats_layout.addWidget(metric_label, i, 0)
                detailed_stats_layout.addWidget(value_label, i, 1)

            detailed_stats_group.setLayout(detailed_stats_layout)
            summary_layout.addWidget(detailed_stats_group)

            # اضافه کردن نمودار توزیع قیمت
            price_chart_group = QGroupBox("توزیع قیمت")
            price_chart_layout = QVBoxLayout()
            price_canvas = MplCanvas(width=6, height=4, dpi=100)
            self.plot_price_distribution(price_canvas)
            price_chart_layout.addWidget(price_canvas)
            price_chart_group.setLayout(price_chart_layout)
            summary_layout.addWidget(price_chart_group)

            summary_tab.setLayout(summary_layout)
            tab_widget.addTab(summary_tab, "خلاصه")

            # تب دسته‌بندی‌ها
            categories_tab = QWidget()
            categories_layout = QVBoxLayout()
            categories_layout.setSpacing(15)
            categories_layout.setContentsMargins(15, 15, 15, 15)

            # عنوان تب دسته‌بندی‌ها
            cat_title = QLabel("محصولات بر اساس دسته‌بندی")
            cat_title.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #0078d7;
                margin-bottom: 10px;
            """)
            categories_layout.addWidget(cat_title)

            # نمودار دسته‌بندی‌ها
            category_chart_group = QGroupBox("توزیع دسته‌بندی‌ها")
            category_chart_layout = QVBoxLayout()
            category_canvas = MplCanvas(width=6, height=5, dpi=100)
            self.plot_category_distribution(category_canvas)
            category_chart_layout.addWidget(category_canvas)
            category_chart_group.setLayout(category_chart_layout)
            categories_layout.addWidget(category_chart_group)

            categories_tab.setLayout(categories_layout)
            tab_widget.addTab(categories_tab, "دسته‌بندی‌ها")

            # اضافه کردن تب‌ها به لایه اصلی
            main_layout.addWidget(tab_widget)

            # دکمه بستن
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            refresh_button = QPushButton("به‌روزرسانی داده‌ها")
            refresh_button.setIcon(QtGui.QIcon.fromTheme("view-refresh", QtGui.QIcon()))
            refresh_button.clicked.connect(lambda: self.refresh_dashboard(dashboard_dialog))

            close_button = QPushButton("بستن")
            close_button.setIcon(QtGui.QIcon.fromTheme("window-close", QtGui.QIcon()))
            close_button.clicked.connect(dashboard_dialog.accept)

            button_layout.addWidget(refresh_button)
            button_layout.addWidget(close_button)

            main_layout.addLayout(button_layout)

            dashboard_dialog.setLayout(main_layout)
            dashboard_dialog.exec_()

        except Exception as e:
            error_msg = f"Error showing dashboard: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Dashboard Error", error_msg)

    def refresh_dashboard(self, dialog):
        """تحديث بيانات لوحة المعلومات"""
        try:
            dialog.accept()
            self.show_dashboard()
        except Exception as e:
            print(f"Error refreshing dashboard: {e}")
            QMessageBox.critical(self, "Refresh Error", f"Error refreshing dashboard: {str(e)}")

    def load_settings(self):
        """بارگذاری تنظیمات از فایل"""
        try:
            settings_file = os.path.join('settings', 'app_settings.json')
            if os.path.exists(settings_file):
                with open(settings_file, 'r', encoding='utf-8') as f:
                    loaded_settings = json.load(f)
                    # به‌روزرسانی تنظیمات با مقادیر بارگذاری شده
                    self.app_settings.update(loaded_settings)
                print("Settings loaded successfully")
        except Exception as e:
            print(f"Error loading settings: {e}")
            # در صورت خطا، از تنظیمات پیش‌فرض استفاده می‌شود

    def save_settings(self):
        """ذخیره تنظیمات در فایل"""
        try:
            settings_file = os.path.join('settings', 'app_settings.json')
            with open(settings_file, 'w', encoding='utf-8') as f:
                json.dump(self.app_settings, f, ensure_ascii=False, indent=4)
            print("Settings saved successfully")
        except Exception as e:
            print(f"Error saving settings: {e}")
            QMessageBox.warning(self, "Settings Error", f"Error saving settings: {str(e)}")

    def apply_theme(self, theme_name):
        """اعمال تم انتخاب شده به برنامه"""
        if theme_name == "light":
            # تم روشن (پیش‌فرض)
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #f5f5f5;
                }
                QLabel {
                    color: #333333;
                }
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    margin-top: 20px;
                    font-weight: bold;
                    background-color: #fafafa;
                }
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                }
                QLineEdit, QComboBox {
                    background-color: #ffffcc;
                    border: 1px solid #e6e6b8;
                }
            """)
        elif theme_name == "dark":
            # تم تاریک
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #2d2d2d;
                }
                QLabel {
                    color: #e0e0e0;
                }
                QGroupBox {
                    border: 1px solid #555555;
                    border-radius: 4px;
                    margin-top: 20px;
                    font-weight: bold;
                    background-color: #3d3d3d;
                    color: #e0e0e0;
                }
                QLineEdit, QComboBox {
                    background-color: #ffffcc;
                    color: #333333;
                    border: 1px solid #e6e6b8;
                }
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                }
                QTableWidget {
                    background-color: #3d3d3d;
                    color: #e0e0e0;
                    gridline-color: #555555;
                    border: 1px solid #555555;
                }
                QHeaderView::section {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                    border: 1px solid #555555;
                }
                QMenuBar, QMenu {
                    background-color: #2d2d2d;
                    color: #e0e0e0;
                }
                QMenuBar::item:selected, QMenu::item:selected {
                    background-color: #0078d7;
                }
            """)
        elif theme_name == "blue":
            # تم آبی
            self.setStyleSheet("""
                QMainWindow, QDialog {
                    background-color: #e6f2ff;
                }
                QLabel {
                    color: #00366d;
                }
                QGroupBox {
                    border: 1px solid #99c2ff;
                    border-radius: 4px;
                    margin-top: 20px;
                    font-weight: bold;
                    background-color: #cce6ff;
                    color: #00366d;
                }
                QLineEdit, QComboBox {
                    background-color: #ffffcc;
                    border: 1px solid #e6e6b8;
                }
                QPushButton {
                    background-color: #005cb8;
                    color: white;
                }
                QTableWidget {
                    background-color: white;
                    gridline-color: #99c2ff;
                    border: 1px solid #99c2ff;
                }
                QHeaderView::section {
                    background-color: #cce6ff;
                    color: #00366d;
                    border: 1px solid #99c2ff;
                }
                QMenuBar, QMenu {
                    background-color: #cce6ff;
                    color: #00366d;
                }
                QMenuBar::item:selected, QMenu::item:selected {
                    background-color: #99c2ff;
                }
            """)

    def apply_font(self, font_family, font_size):
        """اعمال فونت انتخاب شده به برنامه"""
        font = QtGui.QFont(font_family, font_size)
        QApplication.setFont(font)

    def mobile_layout(self):
        """تغییر چیدمان به حالت عمودی برای گوشی‌های هوشمند"""
        try:
            # حذف ویجت مرکزی فعلی
            old_central_widget = self.centralWidget()
            if old_central_widget:
                old_central_widget.deleteLater()

            # ایجاد ویجت مرکزی جدید با لایه عمودی
            central_widget = QWidget()
            main_layout = QVBoxLayout()
            main_layout.setSpacing(5)
            main_layout.setContentsMargins(5, 5, 5, 5)

            # ایجاد تب‌ویجت برای دسترسی آسان‌تر به بخش‌های مختلف
            tab_widget = QTabWidget()
            tab_widget.setStyleSheet("""
                QTabWidget::pane {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                }
            """)

            # تب اول: فرم اطلاعات محصول
            form_tab = QWidget()
            form_layout = QVBoxLayout()
            form_layout.setSpacing(5)
            form_layout.setContentsMargins(5, 5, 5, 5)

            # اضافه کردن گروه اطلاعات محصول
            product_info_group = QGroupBox("اطلاعات محصول")
            product_form_layout = QFormLayout()
            product_form_layout.setSpacing(5)
            product_form_layout.setContentsMargins(5, 5, 5, 5)

            # تنظیم اندازه فیلدها برای گوشی
            self.name_input.setFixedHeight(32)
            self.price_input.setFixedHeight(32)
            self.category_input.setFixedHeight(32)
            self.stock_input.setFixedHeight(32)
            self.min_stock_input.setFixedHeight(32)
            self.image_path.setFixedHeight(32)
            self.image_browse.setFixedHeight(32)
            self.image_browse.setFixedWidth(60)

            product_form_layout.addRow(self.name_label, self.name_input)
            product_form_layout.addRow(self.price_label, self.price_input)
            product_form_layout.addRow(self.category_label, self.category_input)
            product_form_layout.addRow(self.stock_label, self.stock_input)
            product_form_layout.addRow(self.min_stock_label, self.min_stock_input)

            # بهبود فیلد تصویر
            image_layout = QHBoxLayout()
            image_layout.setSpacing(5)
            image_layout.addWidget(self.image_path)
            image_layout.addWidget(self.image_browse)
            product_form_layout.addRow(self.image_label, image_layout)

            product_info_group.setLayout(product_form_layout)
            form_layout.addWidget(product_info_group)

            # اضافه کردن دکمه‌های عملیات
            button_group = QGroupBox("عملیات")
            button_layout = QHBoxLayout()
            button_layout.setSpacing(5)
            button_layout.setContentsMargins(5, 5, 5, 5)

            # تنظیم اندازه دکمه‌ها
            self.add_button.setFixedHeight(36)
            self.update_button.setFixedHeight(36)
            self.delete_button.setFixedHeight(36)
            self.show_button.setFixedHeight(36)

            button_layout.addWidget(self.add_button)
            button_layout.addWidget(self.update_button)
            button_layout.addWidget(self.delete_button)
            button_layout.addWidget(self.show_button)

            button_group.setLayout(button_layout)
            form_layout.addWidget(button_group)

            form_tab.setLayout(form_layout)

            # تب دوم: جستجو و فیلتر
            search_tab = QWidget()
            search_layout = QVBoxLayout()
            search_layout.setSpacing(5)
            search_layout.setContentsMargins(5, 5, 5, 5)

            # گروه جستجو
            search_group = QGroupBox("جستجو")
            search_form_layout = QVBoxLayout()
            search_form_layout.setSpacing(5)
            search_form_layout.setContentsMargins(5, 5, 5, 5)

            # تنظیم اندازه فیلدهای جستجو
            self.search_input.setFixedHeight(32)
            self.search_button.setFixedHeight(32)
            self.filter_input.setFixedHeight(32)
            self.sort_input.setFixedHeight(32)

            # بخش جستجو
            search_input_layout = QHBoxLayout()
            search_input_layout.addWidget(self.search_label)
            search_input_layout.addWidget(self.search_input)
            search_input_layout.addWidget(self.search_button)

            # بخش فیلتر
            filter_layout = QHBoxLayout()
            filter_layout.addWidget(self.filter_label)
            filter_layout.addWidget(self.filter_input)

            # بخش مرتب‌سازی
            sort_layout = QHBoxLayout()
            sort_layout.addWidget(self.sort_label)
            sort_layout.addWidget(self.sort_input)

            search_form_layout.addLayout(search_input_layout)
            search_form_layout.addLayout(filter_layout)
            search_form_layout.addLayout(sort_layout)

            search_group.setLayout(search_form_layout)
            search_layout.addWidget(search_group)
            search_tab.setLayout(search_layout)

            # تب سوم: لیست محصولات
            list_tab = QWidget()
            list_layout = QVBoxLayout()
            list_layout.setSpacing(5)
            list_layout.setContentsMargins(5, 5, 5, 5)

            # عنوان جدول
            table_title = QLabel("لیست محصولات")
            table_title.setStyleSheet("""
                font-size: 13px;
                font-weight: bold;
                color: #0078d7;
                padding: 3px;
            """)
            table_title.setAlignment(QtCore.Qt.AlignCenter)

            # تنظیم جدول برای نمایش در گوشی
            self.products_table.setAlternatingRowColors(True)
            self.products_table.setSelectionBehavior(QtWidgets.QAbstractItemView.SelectRows)
            self.products_table.setSelectionMode(QtWidgets.QAbstractItemView.SingleSelection)
            self.products_table.horizontalHeader().setStretchLastSection(True)
            self.products_table.horizontalHeader().setSectionResizeMode(QtWidgets.QHeaderView.Stretch)

            list_layout.addWidget(table_title)
            list_layout.addWidget(self.products_table)
            list_tab.setLayout(list_layout)

            # اضافه کردن تب‌ها به تب‌ویجت
            tab_widget.addTab(form_tab, "اطلاعات محصول")
            tab_widget.addTab(search_tab, "جستجو و فیلتر")
            tab_widget.addTab(list_tab, "لیست محصولات")

            # اضافه کردن تب‌ویجت به لایه اصلی
            main_layout.addWidget(tab_widget)

            central_widget.setLayout(main_layout)
            self.setCentralWidget(central_widget)

        except Exception as e:
            print(f"Error in mobile layout: {e}")
            QMessageBox.critical(self, "Layout Error", f"Error setting mobile layout: {str(e)}")

    def apply_ui_scale(self, scale_mode):
        """اعمال سایز رابط کاربری بر اساس نوع دستگاه"""
        if scale_mode == "mobile":
            # تنظیمات برای نمایش در گوشی (جمع‌تر و کوچکتر برای گوشی‌های شیائومی و سامسونگ)
            self.setStyleSheet(self.styleSheet() + """
                QPushButton {
                    min-height: 36px;
                    min-width: 80px;
                    padding: 5px 8px;
                    font-size: 12px;
                }
                QLineEdit, QComboBox {
                    min-height: 32px;
                    padding: 4px;
                    font-size: 12px;
                    background-color: #ffffcc;
                }
                QTableWidget::item {
                    padding: 4px;
                    font-size: 11px;
                }
                QHeaderView::section {
                    padding: 5px;
                    font-size: 12px;
                }
                QGroupBox {
                    margin-top: 20px;
                    padding: 8px;
                    font-size: 12px;
                }
                QLabel {
                    font-size: 12px;
                }
                QMenuBar {
                    min-height: 32px;
                    font-size: 12px;
                }
                QMenuBar::item {
                    padding: 6px 10px;
                }
                QMenu::item {
                    padding: 6px 15px;
                    min-height: 24px;
                    font-size: 12px;
                }
                QTabBar::tab {
                    padding: 6px 10px;
                    min-height: 24px;
                    font-size: 12px;
                }
            """)
            # تغییر اندازه پنجره اصلی برای گوشی
            screen_size = QApplication.desktop().screenGeometry()
            self.setGeometry(0, 0, screen_size.width(), screen_size.height())
            self.showMaximized()

            # تغییر چیدمان به حالت عمودی برای گوشی
            self.mobile_layout()
        else:  # desktop
            # تنظیمات برای نمایش در کامپیوتر (اندازه‌های استاندارد - جمع‌تر)
            self.setGeometry(100, 100, 1000, 700)
            # رنگ زرد برای فیلدهای نوشتاری
            self.setStyleSheet(self.styleSheet() + """
                QLineEdit, QComboBox {
                    background-color: #ffffcc;
                }
            """)

    def show_settings(self):
        """نمایش پنجره تنظیمات برنامه"""
        try:
            settings_dialog = QDialog(self)
            settings_dialog.setWindowTitle('تنظیمات برنامه')
            settings_dialog.setMinimumSize(500, 400)
            settings_dialog.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                }
                QLabel {
                    font-weight: bold;
                }
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    margin-top: 20px;
                    font-weight: bold;
                    background-color: white;
                    padding: 10px;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 10px;
                    color: #0078d7;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00559b;
                }
                QComboBox {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 5px;
                    background-color: white;
                    min-height: 25px;
                }
            """)

            layout = QVBoxLayout()
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            # عنوان صفحه
            title_label = QLabel("تنظیمات برنامه")
            title_label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: #0078d7;
                margin-bottom: 10px;
                padding: 5px;
                border-bottom: 1px solid #cccccc;
            """)
            layout.addWidget(title_label)

            # تنظیمات تم
            theme_group = QGroupBox("تم برنامه")
            theme_layout = QVBoxLayout()

            theme_label = QLabel("انتخاب تم:")
            theme_combo = QComboBox()
            theme_combo.addItems(["روشن (پیش‌فرض)", "تاریک", "آبی"])

            # تنظیم مقدار پیش‌فرض کومبوباکس بر اساس تنظیمات فعلی
            if self.app_settings["theme"] == "light":
                theme_combo.setCurrentIndex(0)
            elif self.app_settings["theme"] == "dark":
                theme_combo.setCurrentIndex(1)
            elif self.app_settings["theme"] == "blue":
                theme_combo.setCurrentIndex(2)

            theme_layout.addWidget(theme_label)
            theme_layout.addWidget(theme_combo)
            theme_group.setLayout(theme_layout)
            layout.addWidget(theme_group)

            # تنظیمات زبان
            language_group = QGroupBox("زبان برنامه")
            language_layout = QVBoxLayout()

            language_label = QLabel("انتخاب زبان:")
            language_combo = QComboBox()
            language_combo.addItems(["فارسی", "انگلیسی"])

            # تنظیم مقدار پیش‌فرض کومبوباکس بر اساس تنظیمات فعلی
            if self.app_settings["language"] == "fa":
                language_combo.setCurrentIndex(0)
            elif self.app_settings["language"] == "en":
                language_combo.setCurrentIndex(1)

            language_layout.addWidget(language_label)
            language_layout.addWidget(language_combo)
            language_group.setLayout(language_layout)
            layout.addWidget(language_group)

            # تنظیمات فونت
            font_group = QGroupBox("فونت برنامه")
            font_layout = QFormLayout()

            font_family_label = QLabel("نوع فونت:")
            font_family_combo = QComboBox()
            # لیست فونت‌های سیستم
            font_families = QtGui.QFontDatabase().families()
            font_family_combo.addItems(font_families)

            # تنظیم مقدار پیش‌فرض کومبوباکس بر اساس تنظیمات فعلی
            current_font_index = font_family_combo.findText(self.app_settings["font_family"])
            if current_font_index >= 0:
                font_family_combo.setCurrentIndex(current_font_index)

            font_size_label = QLabel("اندازه فونت:")
            font_size_combo = QComboBox()
            font_size_combo.addItems(["8", "9", "10", "11", "12", "14", "16", "18"])

            # تنظیم مقدار پیش‌فرض کومبوباکس بر اساس تنظیمات فعلی
            font_size_index = font_size_combo.findText(str(self.app_settings["font_size"]))
            if font_size_index >= 0:
                font_size_combo.setCurrentIndex(font_size_index)

            font_layout.addRow(font_family_label, font_family_combo)
            font_layout.addRow(font_size_label, font_size_combo)
            font_group.setLayout(font_layout)
            layout.addWidget(font_group)

            # تنظیمات سایز رابط کاربری
            ui_scale_group = QGroupBox("سایز رابط کاربری")
            ui_scale_layout = QVBoxLayout()

            ui_scale_label = QLabel("انتخاب سایز رابط کاربری:")
            ui_scale_combo = QComboBox()
            ui_scale_combo.addItems(["نمایش استاندارد (کامپیوتر)", "نمایش بزرگ (گوشی و تبلت)"])

            # تنظیم مقدار پیش‌فرض کومبوباکس بر اساس تنظیمات فعلی
            if self.app_settings["ui_scale"] == "desktop":
                ui_scale_combo.setCurrentIndex(0)
            elif self.app_settings["ui_scale"] == "mobile":
                ui_scale_combo.setCurrentIndex(1)

            ui_scale_description = QLabel("نمایش بزرگ برای دستگاه‌های لمسی مانند گوشی و تبلت مناسب است.")
            ui_scale_description.setWordWrap(True)
            ui_scale_description.setStyleSheet("font-size: 11px; color: #666666;")

            ui_scale_layout.addWidget(ui_scale_label)
            ui_scale_layout.addWidget(ui_scale_combo)
            ui_scale_layout.addWidget(ui_scale_description)
            ui_scale_group.setLayout(ui_scale_layout)
            layout.addWidget(ui_scale_group)

            # اطلاعات نسخه
            version_group = QGroupBox("اطلاعات برنامه")
            version_layout = QVBoxLayout()

            version_label = QLabel(f"نسخه برنامه: {self.app_version}")
            version_label.setStyleSheet("""
                font-size: 14px;
                color: #555555;
                padding: 5px;
            """)

            version_layout.addWidget(version_label)
            version_group.setLayout(version_layout)
            layout.addWidget(version_group)

            # دکمه‌های تأیید و لغو
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            cancel_button = QPushButton("انصراف")
            cancel_button.setIcon(QtGui.QIcon.fromTheme("dialog-cancel", QtGui.QIcon()))
            cancel_button.clicked.connect(settings_dialog.reject)

            save_button = QPushButton("ذخیره تنظیمات")
            save_button.setIcon(QtGui.QIcon.fromTheme("document-save", QtGui.QIcon()))

            # ذخیره تنظیمات
            def save_settings_and_apply():
                # ذخیره تم
                theme_index = theme_combo.currentIndex()
                if theme_index == 0:
                    self.app_settings["theme"] = "light"
                elif theme_index == 1:
                    self.app_settings["theme"] = "dark"
                elif theme_index == 2:
                    self.app_settings["theme"] = "blue"

                # ذخیره زبان
                language_index = language_combo.currentIndex()
                if language_index == 0:
                    self.app_settings["language"] = "fa"
                elif language_index == 1:
                    self.app_settings["language"] = "en"

                # ذخیره فونت
                self.app_settings["font_family"] = font_family_combo.currentText()
                self.app_settings["font_size"] = int(font_size_combo.currentText())

                # ذخیره سایز رابط کاربری
                ui_scale_index = ui_scale_combo.currentIndex()
                if ui_scale_index == 0:
                    self.app_settings["ui_scale"] = "desktop"
                elif ui_scale_index == 1:
                    self.app_settings["ui_scale"] = "mobile"

                # ذخیره تنظیمات در فایل
                self.save_settings()

                # اعمال تنظیمات
                self.apply_theme(self.app_settings["theme"])
                self.apply_font(self.app_settings["font_family"], self.app_settings["font_size"])
                self.apply_ui_scale(self.app_settings["ui_scale"])

                # نمایش پیام موفقیت
                QMessageBox.information(self, "ذخیره تنظیمات", "تنظیمات با موفقیت ذخیره شد.\nبرخی تغییرات پس از راه‌اندازی مجدد برنامه اعمال می‌شوند.")

                settings_dialog.accept()

            save_button.clicked.connect(save_settings_and_apply)

            button_layout.addWidget(cancel_button)
            button_layout.addWidget(save_button)

            layout.addLayout(button_layout)
            settings_dialog.setLayout(layout)

            # نمایش دیالوگ
            settings_dialog.exec_()

        except Exception as e:
            print(f"Error showing settings: {e}")
            QMessageBox.critical(self, "Settings Error", f"Error showing settings: {str(e)}")

    def open_product_manager_fixed(self):
        """باز کردن فرم مدیریت محصولات (نسخه جدید) و بستن فرم فعلی"""
        try:
            # ثبت فعالیت
            self.log_activity("application", "باز کردن فرم مدیریت محصولات (نسخه جدید)")

            # بررسی وجود ماژول
            try:
                import sys
                import os

                # اجرای فایل به صورت مستقل
                python_executable = sys.executable
                script_path = os.path.join(os.path.dirname(os.path.abspath(__file__)), 'product_manager_fixed.py')

                if os.path.exists(script_path):
                    # اجرای فایل به صورت یک پروسه جدید
                    import subprocess
                    subprocess.Popen([python_executable, script_path])

                    # نمایش پیام موفقیت
                    QMessageBox.information(self, "اتصال موفق", "فرم مدیریت محصولات (نسخه جدید) در حال اجرا است. فرم فعلی بسته خواهد شد.")

                    # بستن فرم فعلی
                    self.close()
                else:
                    QMessageBox.critical(self, "خطا", f"فایل product_manager_fixed.py در مسیر {script_path} یافت نشد.")

            except ImportError as e:
                QMessageBox.critical(self, "خطا", f"خطا در وارد کردن ماژول‌های مورد نیاز: {str(e)}")
            except Exception as e:
                QMessageBox.critical(self, "خطا", f"خطا در باز کردن فرم مدیریت محصولات (نسخه جدید): {str(e)}")
        except Exception as e:
            QMessageBox.critical(self, "خطا", f"خطا در اجرای عملیات: {str(e)}")

    def show_about(self):
        """نمایش اطلاعات درباره برنامه"""
        try:
            about_dialog = QDialog(self)
            about_dialog.setWindowTitle('درباره برنامه')
            about_dialog.setMinimumSize(400, 300)
            about_dialog.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                }
                QLabel {
                    color: #333333;
                }
            """)

            layout = QVBoxLayout()
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            # لوگوی برنامه
            logo_label = QLabel()
            try:
                logo_pixmap = QtGui.QPixmap('product_images/app_icon.png')
                logo_label.setPixmap(logo_pixmap.scaled(100, 100, QtCore.Qt.KeepAspectRatio))
                logo_label.setAlignment(QtCore.Qt.AlignCenter)
            except:
                logo_label.setText("مدیریت محصولات")
                logo_label.setStyleSheet("""
                    font-size: 24px;
                    font-weight: bold;
                    color: #0078d7;
                """)
                logo_label.setAlignment(QtCore.Qt.AlignCenter)

            layout.addWidget(logo_label)

            # عنوان برنامه
            title_label = QLabel("سیستم مدیریت محصولات")
            title_label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: #0078d7;
            """)
            title_label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(title_label)

            # نسخه برنامه
            version_label = QLabel(f"نسخه: {self.app_version}")
            version_label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(version_label)

            # توضیحات برنامه
            description_label = QLabel(
                "این برنامه یک سیستم مدیریت محصولات است که به شما امکان می‌دهد "
                "محصولات خود را مدیریت کنید، موجودی را کنترل کنید، "
                "گزارش‌های مختلف تهیه کنید و بارکدها را مدیریت نمایید."
            )
            description_label.setWordWrap(True)
            description_label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(description_label)

            # اطلاعات سازنده
            developer_label = QLabel("توسعه‌دهنده: تیم توسعه نرم‌افزار")
            developer_label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(developer_label)

            # سال ساخت
            year_label = QLabel(f"سال ساخت: {datetime.datetime.now().year}")
            year_label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(year_label)

            # دکمه بستن
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            close_button = QPushButton("بستن")
            close_button.clicked.connect(about_dialog.accept)

            button_layout.addWidget(close_button)
            button_layout.addStretch()

            layout.addLayout(button_layout)
            about_dialog.setLayout(layout)

            # نمایش دیالوگ
            about_dialog.exec_()

        except Exception as e:
            print(f"Error showing about: {e}")
            QMessageBox.critical(self, "About Error", f"Error showing about dialog: {str(e)}")

    def get_product_stats(self):
        """دریافت آمار کلی محصولات"""
        stats = {
            'total_products': 0,
            'total_categories': 0,
            'avg_price': 0,
            'min_price': 0,
            'max_price': 0
        }

        try:
            # تعداد کل محصولات
            self.cursor.execute("SELECT COUNT(*) FROM products")
            stats['total_products'] = self.cursor.fetchone()[0]

            # تعداد کل دسته‌بندی‌ها
            self.cursor.execute("SELECT COUNT(*) FROM categories")
            stats['total_categories'] = self.cursor.fetchone()[0]

            # آمار قیمت‌ها
            if stats['total_products'] > 0:
                self.cursor.execute("SELECT AVG(price), MIN(price), MAX(price) FROM products")
                avg, min_price, max_price = self.cursor.fetchone()
                stats['avg_price'] = avg or 0
                stats['min_price'] = min_price or 0
                stats['max_price'] = max_price or 0

        except Exception as e:
            print(f"Error getting product stats: {e}")

        return stats

    def plot_price_distribution(self, canvas):
        """رسم نمودار توزیع قیمت"""
        try:
            self.cursor.execute("SELECT price FROM products ORDER BY price")
            prices = [row[0] for row in self.cursor.fetchall() if row[0] is not None]

            if not prices:
                canvas.axes.text(0.5, 0.5, "No price data available",
                                ha='center', va='center', fontsize=12)
                return

            canvas.axes.hist(prices, bins=10, alpha=0.7, color='skyblue')
            canvas.axes.set_title('Price Distribution')
            canvas.axes.set_xlabel('Price')
            canvas.axes.set_ylabel('Number of Products')
            canvas.fig.tight_layout()
            canvas.draw()

        except Exception as e:
            print(f"Error plotting price distribution: {e}")
            canvas.axes.text(0.5, 0.5, f"Error: {str(e)}",
                            ha='center', va='center', fontsize=10)
            canvas.draw()

    def plot_category_distribution(self, canvas):
        """رسم نمودار توزیع دسته‌بندی‌ها"""
        try:
            self.cursor.execute("""
                SELECT c.name, COUNT(p.id)
                FROM categories c
                LEFT JOIN products p ON c.name = p.category
                GROUP BY c.name
                ORDER BY COUNT(p.id) DESC
            """)
            result = self.cursor.fetchall()

            if not result:
                canvas.axes.text(0.5, 0.5, "No category data available",
                                ha='center', va='center', fontsize=12)
                return

            categories = [row[0] for row in result]
            counts = [row[1] for row in result]

            # رسم نمودار میله‌ای
            bars = canvas.axes.bar(categories, counts, color='lightgreen')
            canvas.axes.set_title('Products by Category')
            canvas.axes.set_xlabel('Category')
            canvas.axes.set_ylabel('Number of Products')

            # چرخش برچسب‌ها برای خوانایی بهتر
            canvas.axes.set_xticklabels(categories, rotation=45, ha='right')

            # اضافه کردن مقادیر روی نمودار
            for bar in bars:
                height = bar.get_height()
                canvas.axes.text(bar.get_x() + bar.get_width()/2., height + 0.1,
                                f'{height:.0f}', ha='center', va='bottom')

            canvas.fig.tight_layout()
            canvas.draw()

        except Exception as e:
            print(f"Error plotting category distribution: {e}")
            canvas.axes.text(0.5, 0.5, f"Error: {str(e)}",
                            ha='center', va='center', fontsize=10)
            canvas.draw()

    def manage_stock(self):
        """مدیریت موجودی محصولات"""
        try:
            # ابتدا بررسی می‌کنیم که آیا محصولی انتخاب شده است
            selected_row = self.products_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Selection Error", "Please select a product to manage its stock")
                return

            product_id = self.products_table.item(selected_row, 0).text()
            product_name = self.products_table.item(selected_row, 1).text()
            current_stock = self.products_table.item(selected_row, 5).text()  # تصحیح شماره ستون موجودی

            # ایجاد دیالوگ مدیریت موجودی
            stock_dialog = QDialog(self)
            stock_dialog.setWindowTitle(f'مدیریت موجودی: {product_name}')
            stock_dialog.setMinimumWidth(500)
            stock_dialog.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                }
                QLabel {
                    color: #333333;
                }
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    margin-top: 20px;
                    font-weight: bold;
                    background-color: white;
                }
                QGroupBox::title {
                    subcontrol-origin: margin;
                    subcontrol-position: top center;
                    padding: 0 10px;
                    color: #0078d7;
                    font-size: 14px;
                }
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 8px 16px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00559b;
                }
                QLineEdit {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: white;
                }
                QLineEdit:focus {
                    border: 1px solid #0078d7;
                }
                QComboBox {
                    border: 1px solid #cccccc;
                    border-radius: 4px;
                    padding: 8px;
                    background-color: white;
                    min-height: 30px;
                }
                QComboBox:focus {
                    border: 1px solid #0078d7;
                }
            """)

            layout = QVBoxLayout()
            layout.setSpacing(15)
            layout.setContentsMargins(20, 20, 20, 20)

            # عنوان صفحه
            title_label = QLabel(f"مدیریت موجودی برای: {product_name}")
            title_label.setStyleSheet("""
                font-size: 18px;
                font-weight: bold;
                color: #0078d7;
                margin-bottom: 10px;
                padding: 5px;
                border-bottom: 1px solid #cccccc;
            """)
            layout.addWidget(title_label)

            # نمایش موجودی فعلی در کارت
            stock_info_group = QGroupBox("اطلاعات موجودی فعلی")
            stock_info_group.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 10px;
                    background-color: #e8f4fc;
                    padding: 10px;
                }
                QGroupBox::title {
                    color: #0078d7;
                    font-size: 14px;
                }
            """)

            stock_info_layout = QVBoxLayout()

            current_stock_label = QLabel(f"{current_stock}")
            current_stock_label.setStyleSheet("""
                font-size: 36px;
                font-weight: bold;
                color: #0078d7;
            """)
            current_stock_label.setAlignment(QtCore.Qt.AlignCenter)

            stock_text_label = QLabel("میزان موجودی فعلی")
            stock_text_label.setStyleSheet("""
                font-size: 14px;
                color: #555555;
            """)
            stock_text_label.setAlignment(QtCore.Qt.AlignCenter)

            stock_info_layout.addWidget(current_stock_label)
            stock_info_layout.addWidget(stock_text_label)
            stock_info_group.setLayout(stock_info_layout)
            layout.addWidget(stock_info_group)

            # فرم تغییر موجودی
            stock_change_group = QGroupBox("به‌روزرسانی موجودی")
            stock_change_layout = QVBoxLayout()
            stock_change_layout.setSpacing(15)

            form_layout = QFormLayout()
            form_layout.setSpacing(10)
            form_layout.setLabelAlignment(QtCore.Qt.AlignRight)

            # مقدار تغییر
            amount_label = QLabel("مقدار:")
            amount_label.setStyleSheet("font-weight: bold;")
            amount_input = QLineEdit()
            amount_input.setValidator(QtGui.QIntValidator(1, 999999))
            amount_input.setPlaceholderText("مقدار افزایش یا کاهش را وارد کنید")
            form_layout.addRow(amount_label, amount_input)

            # نوع تغییر
            type_label = QLabel("عملیات:")
            type_label.setStyleSheet("font-weight: bold;")
            type_combo = QComboBox()
            type_combo.addItems(["افزودن به موجودی", "کاهش از موجودی"])
            form_layout.addRow(type_label, type_combo)

            # توضیحات
            notes_label = QLabel("توضیحات:")
            notes_label.setStyleSheet("font-weight: bold;")
            notes_input = QLineEdit()
            notes_input.setPlaceholderText("توضیحات اختیاری درباره این تغییر")
            form_layout.addRow(notes_label, notes_input)

            stock_change_layout.addLayout(form_layout)

            # پیش‌نمایش تغییرات
            preview_group = QGroupBox("پیش‌نمایش")
            preview_group.setStyleSheet("""
                QGroupBox {
                    border: 1px solid #cccccc;
                    border-radius: 6px;
                    background-color: #f9f9f9;
                }
            """)

            preview_layout = QVBoxLayout()

            preview_label = QLabel("میزان موجودی جدید اینجا نمایش داده می‌شود")
            preview_label.setStyleSheet("""
                font-size: 14px;
                font-weight: bold;
                color: #555555;
                padding: 10px;
            """)
            preview_label.setAlignment(QtCore.Qt.AlignCenter)

            preview_layout.addWidget(preview_label)
            preview_group.setLayout(preview_layout)
            stock_change_layout.addWidget(preview_group)

            # به‌روزرسانی پیش‌نمایش
            def update_preview():
                try:
                    amount = int(amount_input.text() or "0")
                    current = int(current_stock)

                    if type_combo.currentText() == "افزودن به موجودی":
                        new_stock = current + amount
                        preview_label.setText(f"میزان موجودی جدید: {new_stock} (+{amount})")
                        preview_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #00a651; padding: 10px;")
                    else:
                        new_stock = max(0, current - amount)
                        preview_label.setText(f"میزان موجودی جدید: {new_stock} (-{amount})")
                        if new_stock < current:
                            preview_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #d9534f; padding: 10px;")
                        else:
                            preview_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #555555; padding: 10px;")
                except ValueError:
                    preview_label.setText("لطفاً یک مقدار معتبر وارد کنید")
                    preview_label.setStyleSheet("font-size: 14px; font-weight: bold; color: #d9534f; padding: 10px;")

            amount_input.textChanged.connect(update_preview)
            type_combo.currentIndexChanged.connect(update_preview)

            stock_change_group.setLayout(stock_change_layout)
            layout.addWidget(stock_change_group)

            # دکمه‌های تأیید و لغو
            button_layout = QHBoxLayout()
            button_layout.addStretch()

            cancel_button = QPushButton("انصراف")
            cancel_button.setIcon(QtGui.QIcon.fromTheme("dialog-cancel", QtGui.QIcon()))
            cancel_button.clicked.connect(stock_dialog.reject)

            save_button = QPushButton("به‌روزرسانی موجودی")
            save_button.setIcon(QtGui.QIcon.fromTheme("document-save", QtGui.QIcon()))
            save_button.clicked.connect(stock_dialog.accept)

            button_layout.addWidget(cancel_button)
            button_layout.addWidget(save_button)

            layout.addLayout(button_layout)
            stock_dialog.setLayout(layout)

            # نمایش دیالوگ و پردازش نتیجه
            if stock_dialog.exec_() == QDialog.Accepted:
                try:
                    amount = int(amount_input.text())
                    if amount <= 0:
                        QMessageBox.warning(self, "Invalid Amount", "Amount must be a positive number")
                        return

                    change_type = "increase" if type_combo.currentText() == "Add to Stock" else "decrease"
                    notes = notes_input.text()

                    # دریافت موجودی فعلی
                    self.cursor.execute("SELECT stock FROM products WHERE id = ?", (product_id,))
                    current_stock = self.cursor.fetchone()[0] or 0

                    # محاسبه موجودی جدید
                    if change_type == "increase":
                        new_stock = current_stock + amount
                    else:
                        if current_stock < amount:
                            QMessageBox.warning(self, "Invalid Amount",
                                              f"Cannot remove {amount} items. Current stock is only {current_stock}")
                            return
                        new_stock = current_stock - amount

                    # به‌روزرسانی موجودی
                    self.cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))

                    # ثبت در تاریخچه
                    self.add_inventory_history(product_id, amount, change_type, notes)

                    self.conn.commit()

                    # به‌روزرسانی نمایش
                    self.load_products()

                    QMessageBox.information(self, "Success",
                                          f"Stock updated successfully. New stock: {new_stock}")

                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for amount")
                except Exception as e:
                    self.conn.rollback()
                    QMessageBox.critical(self, "Error", f"Error updating stock: {str(e)}")

        except Exception as e:
            error_msg = f"Error in manage_stock: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def view_inventory_history(self):
        """نمایش تاریخچه تغییرات موجودی"""
        try:
            # ابتدا بررسی می‌کنیم که آیا محصولی انتخاب شده است
            selected_row = self.products_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Selection Error", "Please select a product to view its inventory history")
                return

            product_id = self.products_table.item(selected_row, 0).text()
            product_name = self.products_table.item(selected_row, 1).text()

            # دریافت تاریخچه موجودی
            self.cursor.execute("""
                SELECT change_amount, change_type, change_date, notes
                FROM inventory_history
                WHERE product_id = ?
                ORDER BY change_date DESC
            """, (product_id,))
            history = self.cursor.fetchall()

            if not history:
                QMessageBox.information(self, "No History", f"No inventory history found for {product_name}")
                return

            # ایجاد دیالوگ نمایش تاریخچه
            history_dialog = QDialog(self)
            history_dialog.setWindowTitle(f'Inventory History: {product_name}')
            history_dialog.setMinimumSize(600, 400)

            layout = QVBoxLayout()

            # جدول تاریخچه
            history_table = QTableWidget()
            history_table.setColumnCount(4)
            history_table.setHorizontalHeaderLabels(['Date', 'Type', 'Amount', 'Notes'])
            history_table.setRowCount(len(history))

            for i, record in enumerate(history):
                # تبدیل نوع تغییر به متن فارسی
                change_type = "Increase" if record[1] == "increase" else "Decrease"
                if record[1] == "initial":
                    change_type = "Initial Stock"

                history_table.setItem(i, 0, QTableWidgetItem(record[2]))
                history_table.setItem(i, 1, QTableWidgetItem(change_type))
                history_table.setItem(i, 2, QTableWidgetItem(str(record[0])))
                history_table.setItem(i, 3, QTableWidgetItem(record[3]))

                # رنگ‌بندی سطرها بر اساس نوع تغییر
                if record[1] == "increase":
                    for j in range(4):
                        history_table.item(i, j).setBackground(QtGui.QColor(200, 255, 200))  # سبز کمرنگ
                elif record[1] == "decrease":
                    for j in range(4):
                        history_table.item(i, j).setBackground(QtGui.QColor(255, 200, 200))  # قرمز کمرنگ

            # تنظیم عرض ستون‌ها
            history_table.horizontalHeader().setStretchLastSection(True)
            history_table.resizeColumnsToContents()

            layout.addWidget(history_table)

            # دکمه بستن
            close_button = QPushButton("Close")
            close_button.clicked.connect(history_dialog.accept)
            layout.addWidget(close_button)

            history_dialog.setLayout(layout)
            history_dialog.exec_()

        except Exception as e:
            error_msg = f"Error in view_inventory_history: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def show_low_stock_alert(self):
        """نمایش هشدار برای محصولات با موجودی کم"""
        try:
            self.cursor.execute("""
                SELECT id, name, stock, min_stock
                FROM products
                WHERE stock < min_stock
                ORDER BY (min_stock - stock) DESC
            """)
            low_stock_products = self.cursor.fetchall()

            if not low_stock_products:
                QMessageBox.information(self, "Stock Status", "All products have sufficient stock levels.")
                return

            # ایجاد دیالوگ نمایش محصولات با موجودی کم
            low_stock_dialog = QDialog(self)
            low_stock_dialog.setWindowTitle('Low Stock Alert')
            low_stock_dialog.setMinimumSize(500, 400)

            layout = QVBoxLayout()

            # برچسب هشدار
            alert_label = QLabel(f"⚠️ {len(low_stock_products)} products have low stock!")
            alert_label.setStyleSheet("font-weight: bold; color: red; font-size: 16px;")
            layout.addWidget(alert_label)

            # جدول محصولات با موجودی کم
            low_stock_table = QTableWidget()
            low_stock_table.setColumnCount(4)
            low_stock_table.setHorizontalHeaderLabels(['ID', 'Name', 'Current Stock', 'Minimum Stock'])
            low_stock_table.setRowCount(len(low_stock_products))

            for i, product in enumerate(low_stock_products):
                low_stock_table.setItem(i, 0, QTableWidgetItem(str(product[0])))
                low_stock_table.setItem(i, 1, QTableWidgetItem(product[1]))

                # نمایش موجودی فعلی با رنگ قرمز
                stock_item = QTableWidgetItem(str(product[2]))
                stock_item.setForeground(QtGui.QBrush(QtGui.QColor(255, 0, 0)))
                low_stock_table.setItem(i, 2, stock_item)

                low_stock_table.setItem(i, 3, QTableWidgetItem(str(product[3])))

            # تنظیم عرض ستون‌ها
            low_stock_table.horizontalHeader().setStretchLastSection(True)
            low_stock_table.resizeColumnsToContents()

            layout.addWidget(low_stock_table)

            # دکمه‌های عملیات
            button_layout = QHBoxLayout()

            restock_button = QPushButton("Restock Selected")
            restock_button.clicked.connect(lambda: self.restock_product(low_stock_table, low_stock_dialog))

            close_button = QPushButton("Close")
            close_button.clicked.connect(low_stock_dialog.accept)

            button_layout.addWidget(restock_button)
            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)

            low_stock_dialog.setLayout(layout)
            low_stock_dialog.exec_()

        except Exception as e:
            error_msg = f"Error in show_low_stock_alert: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def restock_product(self, table, parent_dialog):
        """افزایش موجودی محصول انتخاب شده"""
        try:
            selected_row = table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Selection Error", "Please select a product to restock")
                return

            product_id = table.item(selected_row, 0).text()
            product_name = table.item(selected_row, 1).text()
            current_stock = int(table.item(selected_row, 2).text())
            min_stock = int(table.item(selected_row, 3).text())

            # محاسبه مقدار پیشنهادی برای افزایش موجودی
            suggested_amount = max(min_stock - current_stock, 10)  # حداقل 10 واحد یا به اندازه رسیدن به حداقل موجودی

            # دریافت مقدار افزایش موجودی از کاربر
            amount, ok = QtWidgets.QInputDialog.getInt(
                self, f"Restock {product_name}",
                "Enter amount to add to stock:",
                suggested_amount, 1, 1000, 1
            )

            if ok:
                # به‌روزرسانی موجودی
                new_stock = current_stock + amount
                self.cursor.execute("UPDATE products SET stock = ? WHERE id = ?", (new_stock, product_id))

                # ثبت در تاریخچه
                self.add_inventory_history(
                    product_id, amount, "increase",
                    f"Restocked from low stock alert ({current_stock} to {new_stock})"
                )

                self.conn.commit()

                # به‌روزرسانی نمایش
                self.load_products()

                # بستن دیالوگ والد
                parent_dialog.accept()

                QMessageBox.information(
                    self, "Success",
                    f"Stock for {product_name} updated successfully. New stock: {new_stock}"
                )

        except Exception as e:
            error_msg = f"Error in restock_product: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            self.conn.rollback()

    def generate_barcode(self):
        """تولید بارکد برای محصول انتخاب شده"""
        try:
            # ابتدا بررسی می‌کنیم که آیا محصولی انتخاب شده است
            selected_row = self.products_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Selection Error", "Please select a product to generate barcode")
                return

            product_id = self.products_table.item(selected_row, 0).text()
            product_name = self.products_table.item(selected_row, 1).text()

            # بررسی وجود بارکد قبلی
            self.cursor.execute("SELECT barcode FROM products WHERE id = ?", (product_id,))
            existing_barcode = self.cursor.fetchone()[0]

            if existing_barcode:
                response = QMessageBox.question(
                    self, "Barcode Exists",
                    f"Product '{product_name}' already has barcode: {existing_barcode}\nDo you want to generate a new one?",
                    QMessageBox.Yes | QMessageBox.No
                )
                if response == QMessageBox.No:
                    self.show_barcode(product_id, existing_barcode)
                    return

            # تولید بارکد جدید
            # از شناسه محصول و یک عدد تصادفی برای تولید بارکد استفاده می‌کنیم
            import random
            barcode_number = f"{product_id}{int(time.time())%10000}{random.randint(1000, 9999)}"
            barcode_number = barcode_number[:12]  # محدود کردن به 12 رقم برای EAN13

            # ذخیره بارکد در پایگاه داده
            self.cursor.execute("UPDATE products SET barcode = ? WHERE id = ?", (barcode_number, product_id))
            self.conn.commit()

            # نمایش بارکد
            self.show_barcode(product_id, barcode_number)

        except Exception as e:
            error_msg = f"Error generating barcode: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            self.conn.rollback()

    def show_barcode(self, product_id, barcode_number):
        """نمایش بارکد تولید شده"""
        try:
            # دریافت اطلاعات محصول
            self.cursor.execute("SELECT name, price FROM products WHERE id = ?", (product_id,))
            product = self.cursor.fetchone()
            product_name = product[0]
            product_price = product[1]

            # تولید فایل بارکد
            barcode_path = os.path.join('barcodes', f"barcode_{product_id}.png")

            # تولید بارکد EAN13
            try:
                # اگر بارکد دقیقاً 12 رقم نباشد، آن را به 12 رقم تبدیل می‌کنیم
                if len(barcode_number) < 12:
                    barcode_number = barcode_number.zfill(12)
                elif len(barcode_number) > 12:
                    barcode_number = barcode_number[:12]

                # تولید بارکد EAN13
                ean = barcode.get('ean13', barcode_number, writer=ImageWriter())
                ean.save(barcode_path)
            except Exception as e:
                print(f"Error generating EAN13 barcode: {e}")
                # اگر EAN13 با خطا مواجه شد، از Code128 استفاده می‌کنیم
                code128 = barcode.get('code128', barcode_number, writer=ImageWriter())
                code128.save(barcode_path)

            # نمایش بارکد در یک دیالوگ
            barcode_dialog = QDialog(self)
            barcode_dialog.setWindowTitle(f'Barcode: {product_name}')
            barcode_dialog.setMinimumSize(400, 500)

            layout = QVBoxLayout()

            # نمایش اطلاعات محصول
            info_label = QLabel(f"<h2>{product_name}</h2><p>Price: {product_price}</p><p>Barcode: {barcode_number}</p>")
            info_label.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(info_label)

            # نمایش تصویر بارکد
            barcode_image = QLabel()
            pixmap = QtGui.QPixmap(barcode_path)
            barcode_image.setPixmap(pixmap)
            barcode_image.setAlignment(QtCore.Qt.AlignCenter)
            layout.addWidget(barcode_image)

            # دکمه‌های عملیات
            button_layout = QHBoxLayout()

            print_button = QPushButton("Print")
            print_button.clicked.connect(lambda: self.print_single_barcode(barcode_path, product_name, product_price, barcode_number))

            close_button = QPushButton("Close")
            close_button.clicked.connect(barcode_dialog.accept)

            button_layout.addWidget(print_button)
            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)

            barcode_dialog.setLayout(layout)
            barcode_dialog.exec_()

        except Exception as e:
            error_msg = f"Error showing barcode: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def print_single_barcode(self, barcode_path, product_name, product_price, barcode_number):
        """چاپ یک بارکد"""
        try:
            # ایجاد فایل PDF برای چاپ
            pdf_path = os.path.join('barcodes', f"print_{barcode_number}.pdf")
            c = canvas.Canvas(pdf_path, pagesize=letter)

            # تنظیم فونت و اندازه
            c.setFont("Helvetica-Bold", 14)

            # موقعیت چاپ در صفحه
            x, y = 100, 700

            # چاپ اطلاعات محصول
            c.drawString(x, y, product_name)
            c.setFont("Helvetica", 12)
            c.drawString(x, y-20, f"Price: {product_price}")
            c.drawString(x, y-40, f"Barcode: {barcode_number}")

            # چاپ تصویر بارکد
            c.drawImage(barcode_path, x, y-180, width=300, height=120)

            c.save()

            # باز کردن فایل PDF
            import webbrowser
            webbrowser.open(pdf_path)

            QMessageBox.information(self, "Print", f"Barcode saved to {pdf_path} and opened for printing")

        except Exception as e:
            error_msg = f"Error printing barcode: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def scan_barcode(self):
        """اسکن بارکد برای جستجوی محصول"""
        try:
            # در یک برنامه واقعی، اینجا از دوربین یا اسکنر بارکد استفاده می‌شود
            # اما در اینجا فقط یک دیالوگ ورودی نمایش می‌دهیم
            barcode_number, ok = QtWidgets.QInputDialog.getText(
                self, "Scan Barcode",
                "Enter or scan barcode number:"
            )

            if ok and barcode_number:
                # جستجوی محصول با بارکد وارد شده
                self.cursor.execute("SELECT id FROM products WHERE barcode = ?", (barcode_number,))
                result = self.cursor.fetchone()

                if result:
                    product_id = result[0]

                    # پیدا کردن محصول در جدول و انتخاب آن
                    for row in range(self.products_table.rowCount()):
                        if self.products_table.item(row, 0).text() == str(product_id):
                            self.products_table.selectRow(row)
                            self.load_product(row, 0)
                            QMessageBox.information(self, "Barcode Found", f"Product found with barcode: {barcode_number}")
                            return

                QMessageBox.warning(self, "Barcode Not Found", f"No product found with barcode: {barcode_number}")

        except Exception as e:
            error_msg = f"Error scanning barcode: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def print_barcodes(self):
        """چاپ بارکد برای همه محصولات یا محصولات انتخاب شده"""
        try:
            # دریافت لیست محصولات دارای بارکد
            self.cursor.execute("SELECT id, name, price, barcode FROM products WHERE barcode IS NOT NULL")
            products_with_barcode = self.cursor.fetchall()

            if not products_with_barcode:
                QMessageBox.warning(self, "No Barcodes", "No products with barcodes found. Generate barcodes first.")
                return

            # ایجاد دیالوگ انتخاب محصولات برای چاپ
            print_dialog = QDialog(self)
            print_dialog.setWindowTitle('Print Barcodes')
            print_dialog.setMinimumSize(500, 400)

            layout = QVBoxLayout()

            # جدول محصولات
            products_table = QTableWidget()
            products_table.setColumnCount(4)
            products_table.setHorizontalHeaderLabels(['ID', 'Name', 'Price', 'Barcode'])
            products_table.setRowCount(len(products_with_barcode))
            products_table.setSelectionMode(QTableWidget.MultiSelection)

            for i, product in enumerate(products_with_barcode):
                products_table.setItem(i, 0, QTableWidgetItem(str(product[0])))
                products_table.setItem(i, 1, QTableWidgetItem(product[1]))
                products_table.setItem(i, 2, QTableWidgetItem(str(product[2])))
                products_table.setItem(i, 3, QTableWidgetItem(product[3]))

            layout.addWidget(products_table)

            # دکمه‌های عملیات
            button_layout = QHBoxLayout()

            select_all_button = QPushButton("Select All")
            select_all_button.clicked.connect(lambda: products_table.selectAll())

            print_selected_button = QPushButton("Print Selected")
            print_selected_button.clicked.connect(lambda: self.print_selected_barcodes(products_table, print_dialog))

            close_button = QPushButton("Close")
            close_button.clicked.connect(print_dialog.reject)

            button_layout.addWidget(select_all_button)
            button_layout.addWidget(print_selected_button)
            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)

            print_dialog.setLayout(layout)
            print_dialog.exec_()

        except Exception as e:
            error_msg = f"Error in print_barcodes: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def print_selected_barcodes(self, table, parent_dialog):
        """چاپ بارکدهای انتخاب شده"""
        try:
            selected_rows = table.selectionModel().selectedRows()

            if not selected_rows:
                QMessageBox.warning(self, "No Selection", "Please select at least one product")
                return

            # ایجاد فایل PDF برای چاپ
            pdf_path = os.path.join('barcodes', f"print_multiple_{int(time.time())}.pdf")
            c = canvas.Canvas(pdf_path, pagesize=letter)

            # تنظیمات صفحه
            margin = 50
            width, height = letter

            # تعداد بارکد در هر ردیف و ستون
            cols = 2
            rows = 4

            # اندازه هر بارکد
            barcode_width = (width - 2*margin) / cols
            barcode_height = (height - 2*margin) / rows

            # چاپ بارکدها
            page_count = 0
            for i, row in enumerate(selected_rows):
                # محاسبه موقعیت در صفحه
                col = i % cols
                row_pos = (i // cols) % rows

                # اگر به انتهای صفحه رسیدیم، صفحه جدید ایجاد می‌کنیم
                if i > 0 and i % (cols * rows) == 0:
                    c.showPage()
                    page_count += 1

                # دریافت اطلاعات محصول
                product_id = table.item(row.row(), 0).text()
                product_name = table.item(row.row(), 1).text()
                product_price = table.item(row.row(), 2).text()
                barcode_number = table.item(row.row(), 3).text()

                # محاسبه موقعیت دقیق
                x = margin + col * barcode_width
                y = height - margin - (row_pos + 1) * barcode_height

                # تولید فایل بارکد اگر وجود نداشته باشد
                barcode_path = os.path.join('barcodes', f"barcode_{product_id}.png")
                if not os.path.exists(barcode_path):
                    try:
                        # اگر بارکد دقیقاً 12 رقم نباشد، آن را به 12 رقم تبدیل می‌کنیم
                        if len(barcode_number) < 12:
                            barcode_number = barcode_number.zfill(12)
                        elif len(barcode_number) > 12:
                            barcode_number = barcode_number[:12]

                        # تولید بارکد EAN13
                        ean = barcode.get('ean13', barcode_number, writer=ImageWriter())
                        ean.save(barcode_path)
                    except Exception as e:
                        print(f"Error generating EAN13 barcode: {e}")
                        # اگر EAN13 با خطا مواجه شد، از Code128 استفاده می‌کنیم
                        code128 = barcode.get('code128', barcode_number, writer=ImageWriter())
                        code128.save(barcode_path)

                # چاپ اطلاعات محصول
                c.setFont("Helvetica-Bold", 10)
                c.drawString(x + 10, y + barcode_height - 20, product_name[:20])
                c.setFont("Helvetica", 8)
                c.drawString(x + 10, y + barcode_height - 35, f"Price: {product_price}")
                c.drawString(x + 10, y + barcode_height - 50, f"ID: {product_id}")

                # چاپ تصویر بارکد
                c.drawImage(barcode_path, x + 10, y + 10, width=barcode_width - 20, height=barcode_height - 70)

                # چاپ شماره بارکد زیر تصویر
                c.setFont("Helvetica", 8)
                c.drawString(x + 10, y + 5, barcode_number)

            c.save()

            # باز کردن فایل PDF
            import webbrowser
            webbrowser.open(pdf_path)

            # بستن دیالوگ والد
            parent_dialog.accept()

            QMessageBox.information(
                self, "Print",
                f"Barcodes saved to {pdf_path} and opened for printing.\nTotal pages: {page_count + 1}"
            )

        except Exception as e:
            error_msg = f"Error printing selected barcodes: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def manage_discounts(self):
        """مدیریت تخفیف‌ها"""
        try:
            # ایجاد دیالوگ مدیریت تخفیف‌ها
            discounts_dialog = QDialog(self)
            discounts_dialog.setWindowTitle('Manage Discounts')
            discounts_dialog.setMinimumSize(800, 600)

            layout = QVBoxLayout()

            # جدول تخفیف‌ها
            discounts_table = QTableWidget()
            discounts_table.setColumnCount(8)
            discounts_table.setHorizontalHeaderLabels(['ID', 'Name', 'Type', 'Value', 'Start Date', 'End Date', 'Status', 'Applies To'])

            # بارگذاری تخفیف‌ها
            self.cursor.execute("""
                SELECT id, name, discount_type, discount_value, start_date, end_date, is_active, applies_to, target_id
                FROM discounts
                ORDER BY id DESC
            """)
            discounts = self.cursor.fetchall()

            discounts_table.setRowCount(len(discounts))
            for i, discount in enumerate(discounts):
                discounts_table.setItem(i, 0, QTableWidgetItem(str(discount[0])))
                discounts_table.setItem(i, 1, QTableWidgetItem(discount[1]))

                # نوع تخفیف (درصدی یا مبلغی)
                discount_type = "Percentage" if discount[2] == "percentage" else "Fixed Amount"
                discounts_table.setItem(i, 2, QTableWidgetItem(discount_type))

                # مقدار تخفیف
                value_text = f"{discount[3]}%" if discount[2] == "percentage" else f"{discount[3]}"
                discounts_table.setItem(i, 3, QTableWidgetItem(value_text))

                # تاریخ شروع و پایان
                discounts_table.setItem(i, 4, QTableWidgetItem(discount[4]))
                discounts_table.setItem(i, 5, QTableWidgetItem(discount[5]))

                # وضعیت (فعال یا غیرفعال)
                status = "Active" if discount[6] == 1 else "Inactive"
                status_item = QTableWidgetItem(status)
                if discount[6] == 1:
                    status_item.setBackground(QtGui.QColor(200, 255, 200))  # سبز کمرنگ
                else:
                    status_item.setBackground(QtGui.QColor(255, 200, 200))  # قرمز کمرنگ
                discounts_table.setItem(i, 6, status_item)

                # نوع اعمال (محصول یا دسته‌بندی)
                applies_to = discount[7]
                target_id = discount[8]

                if applies_to == "product":
                    # دریافت نام محصول
                    self.cursor.execute("SELECT name FROM products WHERE id = ?", (target_id,))
                    product = self.cursor.fetchone()
                    if product:
                        applies_text = f"Product: {product[0]}"
                    else:
                        applies_text = f"Product ID: {target_id} (Not Found)"
                elif applies_to == "category":
                    # دریافت نام دسته‌بندی
                    self.cursor.execute("SELECT name FROM categories WHERE id = ?", (target_id,))
                    category = self.cursor.fetchone()
                    if category:
                        applies_text = f"Category: {category[0]}"
                    else:
                        applies_text = f"Category ID: {target_id} (Not Found)"
                else:
                    applies_text = applies_to

                discounts_table.setItem(i, 7, QTableWidgetItem(applies_text))

            # تنظیم عرض ستون‌ها
            discounts_table.horizontalHeader().setStretchLastSection(True)
            discounts_table.resizeColumnsToContents()

            layout.addWidget(discounts_table)

            # فرم افزودن تخفیف جدید
            form_group = QGroupBox("Add New Discount")
            form_layout = QFormLayout()

            # نام تخفیف
            name_input = QLineEdit()
            form_layout.addRow("Name:", name_input)

            # نوع تخفیف
            type_combo = QComboBox()
            type_combo.addItems(["Percentage", "Fixed Amount"])
            form_layout.addRow("Type:", type_combo)

            # مقدار تخفیف
            value_input = QLineEdit()
            value_input.setValidator(QtGui.QDoubleValidator(0, 100, 2))
            form_layout.addRow("Value:", value_input)

            # تاریخ شروع
            start_date_input = QLineEdit()
            start_date_input.setText(datetime.datetime.now().strftime("%Y-%m-%d"))
            form_layout.addRow("Start Date (YYYY-MM-DD):", start_date_input)

            # تاریخ پایان
            end_date_input = QLineEdit()
            # تاریخ پایان پیش‌فرض: یک ماه بعد
            end_date = datetime.datetime.now() + datetime.timedelta(days=30)
            end_date_input.setText(end_date.strftime("%Y-%m-%d"))
            form_layout.addRow("End Date (YYYY-MM-DD):", end_date_input)

            # نوع اعمال
            applies_combo = QComboBox()
            applies_combo.addItems(["Product", "Category"])
            form_layout.addRow("Applies To:", applies_combo)

            # هدف (محصول یا دسته‌بندی)
            target_combo = QComboBox()
            form_layout.addRow("Target:", target_combo)

            # به‌روزرسانی لیست هدف‌ها بر اساس نوع اعمال
            def update_targets():
                target_combo.clear()
                if applies_combo.currentText() == "Product":
                    self.cursor.execute("SELECT id, name FROM products ORDER BY name")
                    products = self.cursor.fetchall()
                    for product in products:
                        target_combo.addItem(f"{product[1]} (ID: {product[0]})", product[0])
                else:
                    self.cursor.execute("SELECT id, name FROM categories ORDER BY name")
                    categories = self.cursor.fetchall()
                    for category in categories:
                        target_combo.addItem(f"{category[1]} (ID: {category[0]})", category[0])

            applies_combo.currentIndexChanged.connect(update_targets)
            update_targets()  # بارگذاری اولیه

            form_group.setLayout(form_layout)
            layout.addWidget(form_group)

            # دکمه‌های عملیات
            button_layout = QHBoxLayout()

            add_button = QPushButton("Add Discount")
            delete_button = QPushButton("Delete Selected")
            toggle_button = QPushButton("Toggle Active/Inactive")
            close_button = QPushButton("Close")

            button_layout.addWidget(add_button)
            button_layout.addWidget(delete_button)
            button_layout.addWidget(toggle_button)
            button_layout.addWidget(close_button)

            layout.addLayout(button_layout)

            # اتصال عملکردها به دکمه‌ها
            add_button.clicked.connect(lambda: self.add_discount(
                name_input.text(),
                type_combo.currentText().lower().replace(" ", "_"),
                value_input.text(),
                start_date_input.text(),
                end_date_input.text(),
                applies_combo.currentText().lower(),
                target_combo.currentData(),
                discounts_dialog
            ))

            delete_button.clicked.connect(lambda: self.delete_discount(
                discounts_table.currentRow(),
                discounts_table,
                discounts_dialog
            ))

            toggle_button.clicked.connect(lambda: self.toggle_discount_status(
                discounts_table.currentRow(),
                discounts_table,
                discounts_dialog
            ))

            close_button.clicked.connect(discounts_dialog.accept)

            discounts_dialog.setLayout(layout)
            discounts_dialog.exec_()

            # به‌روزرسانی قیمت‌های تخفیف‌دار پس از بستن دیالوگ
            self.update_discounted_prices()
            self.load_products()

        except Exception as e:
            error_msg = f"Error in manage_discounts: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def add_discount(self, name, discount_type, value, start_date, end_date, applies_to, target_id, parent_dialog):
        """افزودن تخفیف جدید"""
        try:
            # اعتبارسنجی ورودی‌ها
            if not name:
                QMessageBox.warning(self, "Validation Error", "Please enter a name for the discount")
                return

            try:
                discount_value = float(value)
                if discount_value <= 0:
                    QMessageBox.warning(self, "Validation Error", "Discount value must be positive")
                    return

                if discount_type == "percentage" and discount_value > 100:
                    QMessageBox.warning(self, "Validation Error", "Percentage discount cannot exceed 100%")
                    return
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Please enter a valid number for discount value")
                return

            # اعتبارسنجی تاریخ‌ها
            try:
                start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

                if end < start:
                    QMessageBox.warning(self, "Validation Error", "End date cannot be before start date")
                    return
            except ValueError:
                QMessageBox.warning(self, "Validation Error", "Please enter valid dates in YYYY-MM-DD format")
                return

            if target_id is None:
                QMessageBox.warning(self, "Validation Error", "Please select a target product or category")
                return

            # افزودن تخفیف به پایگاه داده
            self.cursor.execute("""
                INSERT INTO discounts (name, discount_type, discount_value, start_date, end_date, is_active, applies_to, target_id)
                VALUES (?, ?, ?, ?, ?, ?, ?, ?)
            """, (name, discount_type, discount_value, start_date, end_date, 1, applies_to, target_id))
            self.conn.commit()

            # به‌روزرسانی قیمت‌های تخفیف‌دار
            self.update_discounted_prices()

            # بستن دیالوگ و نمایش پیام موفقیت
            parent_dialog.accept()
            QMessageBox.information(self, "Success", f"Discount '{name}' added successfully")

            # باز کردن مجدد دیالوگ مدیریت تخفیف‌ها
            self.manage_discounts()

        except Exception as e:
            error_msg = f"Error adding discount: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            self.conn.rollback()

    def delete_discount(self, row, table, parent_dialog):
        """حذف تخفیف انتخاب شده"""
        try:
            if row < 0:
                QMessageBox.warning(self, "Selection Error", "Please select a discount to delete")
                return

            discount_id = table.item(row, 0).text()
            discount_name = table.item(row, 1).text()

            # تأیید حذف
            response = QMessageBox.question(
                self, "Confirm Deletion",
                f"Are you sure you want to delete the discount '{discount_name}'?",
                QMessageBox.Yes | QMessageBox.No
            )

            if response == QMessageBox.Yes:
                self.cursor.execute("DELETE FROM discounts WHERE id = ?", (discount_id,))
                self.conn.commit()

                # به‌روزرسانی قیمت‌های تخفیف‌دار
                self.update_discounted_prices()

                # بستن دیالوگ و نمایش پیام موفقیت
                parent_dialog.accept()
                QMessageBox.information(self, "Success", f"Discount '{discount_name}' deleted successfully")

                # باز کردن مجدد دیالوگ مدیریت تخفیف‌ها
                self.manage_discounts()

        except Exception as e:
            error_msg = f"Error deleting discount: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            self.conn.rollback()

    def toggle_discount_status(self, row, table, parent_dialog):
        """تغییر وضعیت فعال/غیرفعال تخفیف"""
        try:
            if row < 0:
                QMessageBox.warning(self, "Selection Error", "Please select a discount to toggle status")
                return

            discount_id = table.item(row, 0).text()
            discount_name = table.item(row, 1).text()
            current_status = table.item(row, 6).text()

            # تغییر وضعیت
            new_status = 0 if current_status == "Active" else 1
            status_text = "active" if new_status == 1 else "inactive"

            self.cursor.execute("UPDATE discounts SET is_active = ? WHERE id = ?", (new_status, discount_id))
            self.conn.commit()

            # به‌روزرسانی قیمت‌های تخفیف‌دار
            self.update_discounted_prices()

            # بستن دیالوگ و نمایش پیام موفقیت
            parent_dialog.accept()
            QMessageBox.information(self, "Success", f"Discount '{discount_name}' is now {status_text}")

            # باز کردن مجدد دیالوگ مدیریت تخفیف‌ها
            self.manage_discounts()

        except Exception as e:
            error_msg = f"Error toggling discount status: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            self.conn.rollback()

    def update_discounted_prices(self):
        """به‌روزرسانی قیمت‌های تخفیف‌دار برای همه محصولات"""
        try:
            # ابتدا همه قیمت‌های تخفیف‌دار را پاک می‌کنیم
            self.cursor.execute("UPDATE products SET discount_price = NULL")

            # تاریخ امروز
            today = datetime.datetime.now().strftime("%Y-%m-%d")

            # دریافت تخفیف‌های فعال
            self.cursor.execute("""
                SELECT id, discount_type, discount_value, applies_to, target_id
                FROM discounts
                WHERE is_active = 1
                AND start_date <= ?
                AND end_date >= ?
            """, (today, today))

            active_discounts = self.cursor.fetchall()

            for discount in active_discounts:
                discount_id, discount_type, discount_value, applies_to, target_id = discount

                if applies_to == "product":
                    # اعمال تخفیف به یک محصول خاص
                    self.apply_discount_to_single_product(target_id, discount_type, discount_value)
                elif applies_to == "category":
                    # اعمال تخفیف به همه محصولات یک دسته‌بندی
                    self.cursor.execute("SELECT id FROM products WHERE category IN (SELECT name FROM categories WHERE id = ?)", (target_id,))
                    products = self.cursor.fetchall()

                    for product in products:
                        self.apply_discount_to_single_product(product[0], discount_type, discount_value)

            self.conn.commit()
            print("Discounted prices updated successfully")

        except Exception as e:
            error_msg = f"Error updating discounted prices: {e}"
            print(error_msg)
            self.conn.rollback()

    def apply_discount_to_single_product(self, product_id, discount_type, discount_value):
        """اعمال تخفیف به یک محصول"""
        try:
            # دریافت قیمت اصلی محصول
            self.cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
            result = self.cursor.fetchone()

            if not result:
                return

            original_price = result[0]

            # محاسبه قیمت با تخفیف
            if discount_type == "percentage":
                discount_amount = original_price * (discount_value / 100)
                discounted_price = original_price - discount_amount
            else:  # fixed_amount
                discounted_price = max(0, original_price - discount_value)

            # به‌روزرسانی قیمت با تخفیف
            self.cursor.execute("UPDATE products SET discount_price = ? WHERE id = ?", (discounted_price, product_id))

        except Exception as e:
            print(f"Error applying discount to product {product_id}: {e}")

    def apply_discount_to_product(self):
        """اعمال تخفیف به محصول انتخاب شده"""
        try:
            # ابتدا بررسی می‌کنیم که آیا محصولی انتخاب شده است
            selected_row = self.products_table.currentRow()
            if selected_row < 0:
                QMessageBox.warning(self, "Selection Error", "Please select a product to apply discount")
                return

            product_id = self.products_table.item(selected_row, 0).text()
            product_name = self.products_table.item(selected_row, 1).text()

            # دریافت قیمت اصلی محصول
            self.cursor.execute("SELECT price FROM products WHERE id = ?", (product_id,))
            original_price = self.cursor.fetchone()[0]

            # ایجاد دیالوگ تخفیف
            discount_dialog = QDialog(self)
            discount_dialog.setWindowTitle(f'Apply Discount to {product_name}')
            discount_dialog.setMinimumWidth(400)

            layout = QVBoxLayout()

            # نمایش قیمت اصلی
            price_label = QLabel(f"Original Price: {original_price}")
            price_label.setStyleSheet("font-weight: bold; font-size: 14px;")
            layout.addWidget(price_label)

            # فرم تخفیف
            form_layout = QFormLayout()

            # نام تخفیف
            name_input = QLineEdit()
            name_input.setText(f"Discount for {product_name}")
            form_layout.addRow("Discount Name:", name_input)

            # نوع تخفیف
            type_combo = QComboBox()
            type_combo.addItems(["Percentage", "Fixed Amount"])
            form_layout.addRow("Discount Type:", type_combo)

            # مقدار تخفیف
            value_input = QLineEdit()
            value_input.setValidator(QtGui.QDoubleValidator(0, 100, 2))
            form_layout.addRow("Discount Value:", value_input)

            # تاریخ شروع
            start_date_input = QLineEdit()
            start_date_input.setText(datetime.datetime.now().strftime("%Y-%m-%d"))
            form_layout.addRow("Start Date (YYYY-MM-DD):", start_date_input)

            # تاریخ پایان
            end_date_input = QLineEdit()
            # تاریخ پایان پیش‌فرض: یک ماه بعد
            end_date = datetime.datetime.now() + datetime.timedelta(days=30)
            end_date_input.setText(end_date.strftime("%Y-%m-%d"))
            form_layout.addRow("End Date (YYYY-MM-DD):", end_date_input)

            # پیش‌نمایش قیمت با تخفیف
            preview_label = QLabel("Discounted Price: -")
            preview_label.setStyleSheet("color: green; font-weight: bold;")
            form_layout.addRow("", preview_label)

            # به‌روزرسانی پیش‌نمایش قیمت با تخفیف
            def update_preview():
                try:
                    discount_type = type_combo.currentText()
                    discount_value = float(value_input.text() or "0")

                    if discount_type == "Percentage":
                        discount_amount = original_price * (discount_value / 100)
                        discounted_price = original_price - discount_amount
                    else:  # Fixed Amount
                        discounted_price = max(0, original_price - discount_value)

                    preview_label.setText(f"Discounted Price: {discounted_price:.2f} (Save {original_price - discounted_price:.2f})")
                except ValueError:
                    preview_label.setText("Discounted Price: -")

            value_input.textChanged.connect(update_preview)
            type_combo.currentIndexChanged.connect(update_preview)

            layout.addLayout(form_layout)

            # دکمه‌های تأیید و لغو
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(discount_dialog.accept)
            button_box.rejected.connect(discount_dialog.reject)
            layout.addWidget(button_box)

            discount_dialog.setLayout(layout)

            # نمایش دیالوگ و پردازش نتیجه
            if discount_dialog.exec_() == QDialog.Accepted:
                try:
                    name = name_input.text()
                    discount_type = type_combo.currentText().lower().replace(" ", "_")
                    discount_value = float(value_input.text() or "0")
                    start_date = start_date_input.text()
                    end_date = end_date_input.text()

                    # اعتبارسنجی ورودی‌ها
                    if not name:
                        QMessageBox.warning(self, "Validation Error", "Please enter a name for the discount")
                        return

                    if discount_value <= 0:
                        QMessageBox.warning(self, "Validation Error", "Discount value must be positive")
                        return

                    if discount_type == "percentage" and discount_value > 100:
                        QMessageBox.warning(self, "Validation Error", "Percentage discount cannot exceed 100%")
                        return

                    # اعتبارسنجی تاریخ‌ها
                    try:
                        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

                        if end < start:
                            QMessageBox.warning(self, "Validation Error", "End date cannot be before start date")
                            return
                    except ValueError:
                        QMessageBox.warning(self, "Validation Error", "Please enter valid dates in YYYY-MM-DD format")
                        return

                    # افزودن تخفیف به پایگاه داده
                    self.cursor.execute("""
                        INSERT INTO discounts (name, discount_type, discount_value, start_date, end_date, is_active, applies_to, target_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (name, discount_type, discount_value, start_date, end_date, 1, "product", product_id))
                    self.conn.commit()

                    # به‌روزرسانی قیمت‌های تخفیف‌دار
                    self.update_discounted_prices()

                    # به‌روزرسانی نمایش محصولات
                    self.load_products()

                    QMessageBox.information(self, "Success", f"Discount applied to {product_name} successfully")

                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for discount value")
                except Exception as e:
                    self.conn.rollback()
                    QMessageBox.critical(self, "Error", f"Error applying discount: {str(e)}")

        except Exception as e:
            error_msg = f"Error in apply_discount_to_product: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def apply_discount_to_category(self):
        """اعمال تخفیف به یک دسته‌بندی"""
        try:
            # دریافت لیست دسته‌بندی‌ها
            self.cursor.execute("SELECT id, name FROM categories ORDER BY name")
            categories = self.cursor.fetchall()

            if not categories:
                QMessageBox.warning(self, "No Categories", "No categories found. Please add categories first.")
                return

            # ایجاد دیالوگ انتخاب دسته‌بندی
            category_dialog = QDialog(self)
            category_dialog.setWindowTitle('Apply Discount to Category')
            category_dialog.setMinimumWidth(500)

            layout = QVBoxLayout()

            # انتخاب دسته‌بندی
            category_label = QLabel("Select Category:")
            layout.addWidget(category_label)

            category_combo = QComboBox()
            for category in categories:
                category_combo.addItem(f"{category[1]} (ID: {category[0]})", category[0])
            layout.addWidget(category_combo)

            # فرم تخفیف
            form_layout = QFormLayout()

            # نام تخفیف
            name_input = QLineEdit()
            name_input.setText(f"Category Discount")
            form_layout.addRow("Discount Name:", name_input)

            # نوع تخفیف
            type_combo = QComboBox()
            type_combo.addItems(["Percentage", "Fixed Amount"])
            form_layout.addRow("Discount Type:", type_combo)

            # مقدار تخفیف
            value_input = QLineEdit()
            value_input.setValidator(QtGui.QDoubleValidator(0, 100, 2))
            form_layout.addRow("Discount Value:", value_input)

            # تاریخ شروع
            start_date_input = QLineEdit()
            start_date_input.setText(datetime.datetime.now().strftime("%Y-%m-%d"))
            form_layout.addRow("Start Date (YYYY-MM-DD):", start_date_input)

            # تاریخ پایان
            end_date_input = QLineEdit()
            # تاریخ پایان پیش‌فرض: یک ماه بعد
            end_date = datetime.datetime.now() + datetime.timedelta(days=30)
            end_date_input.setText(end_date.strftime("%Y-%m-%d"))
            form_layout.addRow("End Date (YYYY-MM-DD):", end_date_input)

            layout.addLayout(form_layout)

            # دکمه‌های تأیید و لغو
            button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
            button_box.accepted.connect(category_dialog.accept)
            button_box.rejected.connect(category_dialog.reject)
            layout.addWidget(button_box)

            category_dialog.setLayout(layout)

            # نمایش دیالوگ و پردازش نتیجه
            if category_dialog.exec_() == QDialog.Accepted:
                try:
                    category_id = category_combo.currentData()
                    category_name = category_combo.currentText().split(" (ID:")[0]

                    name = name_input.text()
                    if not name:
                        name = f"Discount for {category_name}"

                    discount_type = type_combo.currentText().lower().replace(" ", "_")
                    discount_value = float(value_input.text() or "0")
                    start_date = start_date_input.text()
                    end_date = end_date_input.text()

                    # اعتبارسنجی ورودی‌ها
                    if discount_value <= 0:
                        QMessageBox.warning(self, "Validation Error", "Discount value must be positive")
                        return

                    if discount_type == "percentage" and discount_value > 100:
                        QMessageBox.warning(self, "Validation Error", "Percentage discount cannot exceed 100%")
                        return

                    # اعتبارسنجی تاریخ‌ها
                    try:
                        start = datetime.datetime.strptime(start_date, "%Y-%m-%d")
                        end = datetime.datetime.strptime(end_date, "%Y-%m-%d")

                        if end < start:
                            QMessageBox.warning(self, "Validation Error", "End date cannot be before start date")
                            return
                    except ValueError:
                        QMessageBox.warning(self, "Validation Error", "Please enter valid dates in YYYY-MM-DD format")
                        return

                    # افزودن تخفیف به پایگاه داده
                    self.cursor.execute("""
                        INSERT INTO discounts (name, discount_type, discount_value, start_date, end_date, is_active, applies_to, target_id)
                        VALUES (?, ?, ?, ?, ?, ?, ?, ?)
                    """, (name, discount_type, discount_value, start_date, end_date, 1, "category", category_id))
                    self.conn.commit()

                    # به‌روزرسانی قیمت‌های تخفیف‌دار
                    self.update_discounted_prices()

                    # به‌روزرسانی نمایش محصولات
                    self.load_products()

                    QMessageBox.information(self, "Success", f"Discount applied to category '{category_name}' successfully")

                except ValueError:
                    QMessageBox.warning(self, "Invalid Input", "Please enter a valid number for discount value")
                except Exception as e:
                    self.conn.rollback()
                    QMessageBox.critical(self, "Error", f"Error applying discount: {str(e)}")

        except Exception as e:
            error_msg = f"Error in apply_discount_to_category: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def clear_all_discounts(self):
        """حذف همه تخفیف‌ها"""
        try:
            # تأیید حذف
            response = QMessageBox.question(
                self, "Confirm Deletion",
                "Are you sure you want to delete ALL discounts?\nThis action cannot be undone.",
                QMessageBox.Yes | QMessageBox.No
            )

            if response == QMessageBox.Yes:
                self.cursor.execute("DELETE FROM discounts")
                self.cursor.execute("UPDATE products SET discount_price = NULL")
                self.conn.commit()

                # به‌روزرسانی نمایش محصولات
                self.load_products()

                QMessageBox.information(self, "Success", "All discounts have been cleared")

        except Exception as e:
            error_msg = f"Error clearing discounts: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)
            self.conn.rollback()

    def show_dashboard(self):
        """نمایش داشبورد آماری"""
        try:
            # ایجاد دیالوگ داشبورد
            dashboard = QDialog(self)
            dashboard.setWindowTitle("آمار و اطلاعات محصولات")
            dashboard.setMinimumSize(900, 700)

            # ایجاد تب‌ها برای دسته‌بندی آمارها
            tabs = QTabWidget()

            # تب آمار کلی
            overview_tab = QWidget()
            overview_layout = QVBoxLayout()

            # آمار کلی در قالب کارت‌ها
            stats_layout = QHBoxLayout()

            # تعداد کل محصولات
            self.cursor.execute("SELECT COUNT(*) FROM products")
            total_products = self.cursor.fetchone()[0]

            # تعداد دسته‌بندی‌ها
            self.cursor.execute("SELECT COUNT(DISTINCT category) FROM products")
            total_categories = self.cursor.fetchone()[0]

            # مجموع موجودی
            self.cursor.execute("SELECT SUM(stock) FROM products")
            total_stock = self.cursor.fetchone()[0] or 0

            # تعداد محصولات با موجودی کم
            self.cursor.execute("SELECT COUNT(*) FROM products WHERE stock < min_stock")
            low_stock_count = self.cursor.fetchone()[0]

            # تعداد محصولات دارای تخفیف
            self.cursor.execute("SELECT COUNT(*) FROM products WHERE discount_price IS NOT NULL")
            discounted_count = self.cursor.fetchone()[0]

            # ایجاد کارت‌های آماری
            stats_cards = [
                {"title": "تعداد کل محصولات", "value": total_products, "color": "#3498db"},
                {"title": "تعداد دسته‌بندی‌ها", "value": total_categories, "color": "#2ecc71"},
                {"title": "مجموع موجودی", "value": total_stock, "color": "#9b59b6"},
                {"title": "محصولات با موجودی کم", "value": low_stock_count, "color": "#e74c3c"},
                {"title": "محصولات دارای تخفیف", "value": discounted_count, "color": "#f39c12"}
            ]

            for card in stats_cards:
                # ایجاد گروه برای هر کارت
                card_group = QGroupBox(card["title"])
                card_group.setStyleSheet(f"QGroupBox {{ border: 2px solid {card['color']}; border-radius: 5px; }}")

                # مقدار آماری
                value_label = QLabel(str(card["value"]))
                value_label.setAlignment(QtCore.Qt.AlignCenter)
                value_label.setStyleSheet(f"font-size: 24pt; color: {card['color']}; font-weight: bold;")

                # چیدمان کارت
                card_layout = QVBoxLayout()
                card_layout.addWidget(value_label)
                card_group.setLayout(card_layout)

                # افزودن به چیدمان آمار
                stats_layout.addWidget(card_group)

            overview_layout.addLayout(stats_layout)

            # نمودار توزیع قیمت
            price_chart_group = QGroupBox("توزیع قیمت محصولات")
            price_chart_layout = QVBoxLayout()

            # دریافت داده‌های قیمت
            self.cursor.execute("SELECT price FROM products WHERE price > 0")
            prices = [row[0] for row in self.cursor.fetchall()]

            if prices:
                # ایجاد نمودار
                price_canvas = MplCanvas(width=8, height=4)

                # تعیین بازه‌های قیمتی
                max_price = max(prices)
                if max_price > 0:
                    # تعیین تعداد و اندازه بازه‌ها بر اساس محدوده قیمت
                    if max_price <= 100:
                        bins = 10
                    elif max_price <= 1000:
                        bins = 20
                    else:
                        bins = 30

                    # رسم هیستوگرام
                    price_canvas.axes.hist(prices, bins=bins, color='#3498db', alpha=0.7)
                    price_canvas.axes.set_xlabel('قیمت')
                    price_canvas.axes.set_ylabel('تعداد محصولات')
                    price_canvas.axes.set_title('توزیع قیمت محصولات')
                    price_canvas.axes.grid(True, linestyle='--', alpha=0.7)

                    price_chart_layout.addWidget(price_canvas)
                else:
                    price_chart_layout.addWidget(QLabel("داده‌های کافی برای نمایش نمودار وجود ندارد"))
            else:
                price_chart_layout.addWidget(QLabel("داده‌های کافی برای نمایش نمودار وجود ندارد"))

            price_chart_group.setLayout(price_chart_layout)
            overview_layout.addWidget(price_chart_group)

            # نمودار موجودی
            stock_chart_group = QGroupBox("وضعیت موجودی محصولات")
            stock_chart_layout = QVBoxLayout()

            # دریافت داده‌های موجودی
            self.cursor.execute("""
                SELECT
                    CASE
                        WHEN stock = 0 THEN 'بدون موجودی'
                        WHEN stock < min_stock THEN 'موجودی کم'
                        WHEN stock < min_stock * 2 THEN 'موجودی متوسط'
                        ELSE 'موجودی کافی'
                    END as stock_status,
                    COUNT(*) as count
                FROM products
                GROUP BY stock_status
            """)
            stock_data = self.cursor.fetchall()

            if stock_data:
                # ایجاد نمودار
                stock_canvas = MplCanvas(width=8, height=4)

                # آماده‌سازی داده‌ها برای نمودار دایره‌ای
                labels = [row[0] for row in stock_data]
                sizes = [row[1] for row in stock_data]
                colors = ['#e74c3c', '#f39c12', '#3498db', '#2ecc71']

                # رسم نمودار دایره‌ای
                wedges, texts, autotexts = stock_canvas.axes.pie(
                    sizes,
                    labels=labels,
                    colors=colors,
                    autopct='%1.1f%%',
                    startangle=90,
                    shadow=True
                )

                # تنظیم فونت برچسب‌ها
                for text in texts + autotexts:
                    text.set_fontsize(9)

                stock_canvas.axes.axis('equal')  # نمودار دایره‌ای به صورت دایره کامل نمایش داده شود
                stock_canvas.axes.set_title('وضعیت موجودی محصولات')

                stock_chart_layout.addWidget(stock_canvas)
            else:
                stock_chart_layout.addWidget(QLabel("داده‌های کافی برای نمایش نمودار وجود ندارد"))

            stock_chart_group.setLayout(stock_chart_layout)
            overview_layout.addWidget(stock_chart_group)

            overview_tab.setLayout(overview_layout)
            tabs.addTab(overview_tab, "آمار کلی")

            # تب آمار دسته‌بندی‌ها
            categories_tab = QWidget()
            categories_layout = QVBoxLayout()

            # نمودار توزیع محصولات بر اساس دسته‌بندی
            category_chart_group = QGroupBox("توزیع محصولات بر اساس دسته‌بندی")
            category_chart_layout = QVBoxLayout()

            # دریافت داده‌های دسته‌بندی
            self.cursor.execute("""
                SELECT category, COUNT(*) as count
                FROM products
                WHERE category IS NOT NULL AND category != ''
                GROUP BY category
                ORDER BY count DESC
            """)
            category_data = self.cursor.fetchall()

            if category_data:
                # ایجاد نمودار
                category_canvas = MplCanvas(width=8, height=5)

                # آماده‌سازی داده‌ها برای نمودار میله‌ای
                categories = [row[0] if row[0] else 'بدون دسته‌بندی' for row in category_data]
                counts = [row[1] for row in category_data]

                # محدود کردن تعداد دسته‌بندی‌ها برای نمایش بهتر
                max_categories = 10
                if len(categories) > max_categories:
                    other_count = sum(counts[max_categories-1:])
                    categories = categories[:max_categories-1] + ['سایر']
                    counts = counts[:max_categories-1] + [other_count]

                # رسم نمودار میله‌ای
                bars = category_canvas.axes.bar(categories, counts, color='#3498db')

                # افزودن برچسب مقدار روی هر میله
                for bar in bars:
                    height = bar.get_height()
                    category_canvas.axes.text(
                        bar.get_x() + bar.get_width()/2.,
                        height + 0.1,
                        str(int(height)),
                        ha='center',
                        va='bottom',
                        fontsize=9
                    )

                category_canvas.axes.set_xlabel('دسته‌بندی')
                category_canvas.axes.set_ylabel('تعداد محصولات')
                category_canvas.axes.set_title('توزیع محصولات بر اساس دسته‌بندی')
                category_canvas.axes.set_xticklabels(categories, rotation=45, ha='right')
                category_canvas.axes.grid(True, linestyle='--', alpha=0.7, axis='y')
                category_canvas.fig.tight_layout()

                category_chart_layout.addWidget(category_canvas)

                # جدول آمار دسته‌بندی‌ها
                category_table = QTableWidget()
                category_table.setColumnCount(4)
                category_table.setHorizontalHeaderLabels(['دسته‌بندی', 'تعداد محصولات', 'میانگین قیمت', 'مجموع موجودی'])

                # دریافت آمار تفصیلی دسته‌بندی‌ها
                self.cursor.execute("""
                    SELECT
                        category,
                        COUNT(*) as product_count,
                        AVG(price) as avg_price,
                        SUM(stock) as total_stock
                    FROM products
                    WHERE category IS NOT NULL AND category != ''
                    GROUP BY category
                    ORDER BY product_count DESC
                """)
                detailed_category_data = self.cursor.fetchall()

                category_table.setRowCount(len(detailed_category_data))
                for i, row in enumerate(detailed_category_data):
                    category_name = row[0] if row[0] else 'بدون دسته‌بندی'
                    product_count = row[1]
                    avg_price = row[2] if row[2] else 0
                    total_stock = row[3] if row[3] else 0

                    category_table.setItem(i, 0, QTableWidgetItem(category_name))
                    category_table.setItem(i, 1, QTableWidgetItem(str(product_count)))
                    category_table.setItem(i, 2, QTableWidgetItem(f"{avg_price:,.0f}"))
                    category_table.setItem(i, 3, QTableWidgetItem(str(total_stock)))

                category_table.horizontalHeader().setStretchLastSection(True)
                category_table.resizeColumnsToContents()

                category_chart_layout.addWidget(category_table)
            else:
                category_chart_layout.addWidget(QLabel("داده‌های کافی برای نمایش نمودار وجود ندارد"))

            category_chart_group.setLayout(category_chart_layout)
            categories_layout.addWidget(category_chart_group)

            categories_tab.setLayout(categories_layout)
            tabs.addTab(categories_tab, "آمار دسته‌بندی‌ها")

            # تب آمار تخفیف‌ها
            discounts_tab = QWidget()
            discounts_layout = QVBoxLayout()

            # آمار تخفیف‌ها
            discount_stats_group = QGroupBox("آمار تخفیف‌ها")
            discount_stats_layout = QVBoxLayout()

            # دریافت آمار تخفیف‌ها
            self.cursor.execute("""
                SELECT
                    COUNT(*) as total_discounts,
                    SUM(CASE WHEN is_active = 1 THEN 1 ELSE 0 END) as active_discounts,
                    SUM(CASE WHEN discount_type = 'percent' THEN 1 ELSE 0 END) as percent_discounts,
                    SUM(CASE WHEN discount_type = 'amount' THEN 1 ELSE 0 END) as amount_discounts,
                    AVG(CASE WHEN discount_type = 'percent' THEN discount_value ELSE NULL END) as avg_percent,
                    AVG(CASE WHEN discount_type = 'amount' THEN discount_value ELSE NULL END) as avg_amount
                FROM discounts
            """)
            discount_stats = self.cursor.fetchone()

            if discount_stats and discount_stats[0] > 0:
                total_discounts = discount_stats[0]
                active_discounts = discount_stats[1] or 0
                percent_discounts = discount_stats[2] or 0
                amount_discounts = discount_stats[3] or 0
                avg_percent = discount_stats[4] or 0
                avg_amount = discount_stats[5] or 0

                # نمایش آمار تخفیف‌ها
                discount_stats_text = f"""
                <html>
                <body>
                <p><b>تعداد کل تخفیف‌ها:</b> {total_discounts}</p>
                <p><b>تخفیف‌های فعال:</b> {active_discounts} ({active_discounts/total_discounts*100:.1f}%)</p>
                <p><b>تخفیف‌های درصدی:</b> {percent_discounts} ({percent_discounts/total_discounts*100:.1f}%)</p>
                <p><b>تخفیف‌های مبلغی:</b> {amount_discounts} ({amount_discounts/total_discounts*100:.1f}%)</p>
                <p><b>میانگین تخفیف درصدی:</b> {avg_percent:.1f}%</p>
                <p><b>میانگین تخفیف مبلغی:</b> {avg_amount:,.0f} تومان</p>
                </body>
                </html>
                """

                discount_stats_label = QLabel(discount_stats_text)
                discount_stats_layout.addWidget(discount_stats_label)

                # نمودار تأثیر تخفیف‌ها بر قیمت‌ها
                discount_canvas = MplCanvas(width=8, height=4)

                # دریافت داده‌های قیمت اصلی و قیمت با تخفیف
                self.cursor.execute("""
                    SELECT
                        price,
                        discount_price,
                        (price - discount_price) / price * 100 as discount_percent
                    FROM products
                    WHERE discount_price IS NOT NULL AND price > 0
                    ORDER BY discount_percent DESC
                """)
                discount_data = self.cursor.fetchall()

                if discount_data:
                    # آماده‌سازی داده‌ها برای نمودار
                    original_prices = [row[0] for row in discount_data]
                    discounted_prices = [row[1] for row in discount_data]
                    discount_percents = [row[2] for row in discount_data]

                    # محدود کردن تعداد محصولات برای نمایش بهتر
                    max_products = 10
                    if len(original_prices) > max_products:
                        original_prices = original_prices[:max_products]
                        discounted_prices = discounted_prices[:max_products]
                        discount_percents = discount_percents[:max_products]

                    # ایجاد محور X برای نمودار
                    x = np.arange(len(original_prices))
                    width = 0.35

                    # رسم نمودار میله‌ای مقایسه‌ای
                    bar1 = discount_canvas.axes.bar(x - width/2, original_prices, width, label='قیمت اصلی', color='#3498db')
                    bar2 = discount_canvas.axes.bar(x + width/2, discounted_prices, width, label='قیمت با تخفیف', color='#e74c3c')

                    # افزودن برچسب درصد تخفیف
                    for i, (b1, b2, percent) in enumerate(zip(bar1, bar2, discount_percents)):
                        discount_canvas.axes.text(
                            i,
                            b1.get_height() + 5,
                            f"{percent:.1f}%",
                            ha='center',
                            va='bottom',
                            fontsize=8,
                            color='green',
                            rotation=90
                        )

                    discount_canvas.axes.set_ylabel('قیمت')
                    discount_canvas.axes.set_title('مقایسه قیمت اصلی و قیمت با تخفیف')
                    discount_canvas.axes.set_xticks(x)
                    discount_canvas.axes.set_xticklabels([f"محصول {i+1}" for i in range(len(original_prices))], rotation=45)
                    discount_canvas.axes.legend()
                    discount_canvas.axes.grid(True, linestyle='--', alpha=0.7, axis='y')
                    discount_canvas.fig.tight_layout()

                    discount_stats_layout.addWidget(discount_canvas)
                else:
                    discount_stats_layout.addWidget(QLabel("هیچ محصولی با تخفیف فعال وجود ندارد"))
            else:
                discount_stats_layout.addWidget(QLabel("هیچ تخفیفی تعریف نشده است"))

            discount_stats_group.setLayout(discount_stats_layout)
            discounts_layout.addWidget(discount_stats_group)

            discounts_tab.setLayout(discounts_layout)
            tabs.addTab(discounts_tab, "آمار تخفیف‌ها")

            # چیدمان کلی
            main_layout = QVBoxLayout()
            main_layout.addWidget(tabs)

            # دکمه بستن
            close_button = QPushButton("بستن")
            close_button.clicked.connect(dashboard.accept)

            # دکمه به‌روزرسانی
            refresh_button = QPushButton("به‌روزرسانی")
            refresh_button.clicked.connect(lambda: self.show_dashboard() or dashboard.accept())

            # چیدمان دکمه‌ها
            button_layout = QHBoxLayout()
            button_layout.addWidget(refresh_button)
            button_layout.addWidget(close_button)

            main_layout.addLayout(button_layout)

            dashboard.setLayout(main_layout)
            dashboard.exec_()

        except Exception as e:
            error_msg = f"Error in show_dashboard: {e}"
            print(error_msg)
            QMessageBox.critical(self, "Error", error_msg)

    def browse_image(self):
        """انتخاب تصویر از فایل‌های سیستم"""
        try:
            file_path, _ = QFileDialog.getOpenFileName(
                self, 'انتخاب تصویر', '', 'Image Files (*.png *.jpg *.jpeg *.bmp *.gif)'
            )

            if file_path:
                # نمایش مسیر فایل در فیلد مربوطه
                self.image_path.setText(file_path)

                # ثبت فعالیت
                self.log_activity("product", "انتخاب تصویر برای محصول")
        except Exception as e:
            print(f"Error in browse_image: {e}")
            QMessageBox.critical(self, "Error", f"Error selecting image: {str(e)}")

    def manage_product_images(self):
        """مدیریت تصاویر محصول"""
        try:
            # بررسی انتخاب محصول
            selected_row = self.products_table.currentRow()
            if selected_row < 0:
                # اگر محصولی انتخاب نشده باشد، ابتدا باید محصول را ذخیره کنیم
                QMessageBox.information(self, "اطلاعات", "لطفاً ابتدا محصول را ذخیره کنید تا بتوانید تصاویر آن را مدیریت کنید.")
                return

            product_id = self.products_table.item(selected_row, 0).text()
            product_name = self.products_table.item(selected_row, 1).text()

            # ایجاد دیالوگ مدیریت تصاویر
            images_dialog = QDialog(self)
            images_dialog.setWindowTitle(f'مدیریت تصاویر محصول: {product_name}')
            images_dialog.setMinimumSize(800, 600)
            images_dialog.setStyleSheet("""
                QDialog {
                    background-color: #f5f5f5;
                }
                QLabel {
                    color: #333333;
                }
                QPushButton {
                    background-color: #0078d7;
                    color: white;
                    border: none;
                    border-radius: 4px;
                    padding: 6px 12px;
                    font-weight: bold;
                }
                QPushButton:hover {
                    background-color: #00559b;
                }
                QPushButton#deleteBtn {
                    background-color: #d9534f;
                }
                QPushButton#deleteBtn:hover {
                    background-color: #c9302c;
                }
            """)

            # لایه اصلی
            main_layout = QVBoxLayout()
            main_layout.setSpacing(10)
            main_layout.setContentsMargins(15, 15, 15, 15)

            # عنوان
            title_label = QLabel(f"مدیریت تصاویر محصول: {product_name}")
            title_label.setStyleSheet("""
                font-size: 16px;
                font-weight: bold;
                color: #0078d7;
                margin-bottom: 10px;
                padding-bottom: 5px;
                border-bottom: 1px solid #cccccc;
            """)
            main_layout.addWidget(title_label)

            # بخش افزودن تصویر جدید
            add_image_group = QGroupBox("افزودن تصویر جدید")
            add_image_layout = QVBoxLayout()

            # فرم افزودن تصویر
            add_form_layout = QFormLayout()

            # مسیر تصویر
            new_image_path = QLineEdit()
            new_image_browse = QPushButton("انتخاب تصویر")

            path_layout = QHBoxLayout()
            path_layout.addWidget(new_image_path)
            path_layout.addWidget(new_image_browse)

            add_form_layout.addRow("مسیر تصویر:", path_layout)

            # توضیحات تصویر
            new_image_desc = QLineEdit()
            add_form_layout.addRow("توضیحات:", new_image_desc)

            # تصویر اصلی
            new_image_primary = QCheckBox("تصویر اصلی محصول")
            add_form_layout.addRow("", new_image_primary)

            add_image_layout.addLayout(add_form_layout)

            # دکمه افزودن
            add_image_button = QPushButton("افزودن تصویر")
            add_image_layout.addWidget(add_image_button)

            add_image_group.setLayout(add_image_layout)
            main_layout.addWidget(add_image_group)

            # جدول تصاویر موجود
            images_table = QTableWidget()
            images_table.setColumnCount(5)
            images_table.setHorizontalHeaderLabels(['شناسه', 'مسیر تصویر', 'توضیحات', 'تصویر اصلی', 'پیش‌نمایش'])
            images_table.setSelectionBehavior(QTableWidget.SelectRows)
            images_table.setSelectionMode(QTableWidget.SingleSelection)
            images_table.horizontalHeader().setStretchLastSection(True)
            images_table.setEditTriggers(QTableWidget.NoEditTriggers)

            main_layout.addWidget(images_table)

            # بخش پیش‌نمایش تصویر انتخاب شده
            preview_group = QGroupBox("پیش‌نمایش تصویر انتخاب شده")
            preview_layout = QVBoxLayout()

            preview_label = QLabel()
            preview_label.setAlignment(QtCore.Qt.AlignCenter)
            preview_label.setMinimumHeight(200)
            preview_label.setStyleSheet("""
                border: 1px solid #cccccc;
                background-color: white;
            """)

            preview_layout.addWidget(preview_label)
            preview_group.setLayout(preview_layout)

            main_layout.addWidget(preview_group)

            # دکمه‌های عملیات
            buttons_layout = QHBoxLayout()

            edit_image_button = QPushButton("ویرایش تصویر")
            delete_image_button = QPushButton("حذف تصویر")
            delete_image_button.setObjectName("deleteBtn")
            set_primary_button = QPushButton("تنظیم به عنوان تصویر اصلی")

            buttons_layout.addWidget(edit_image_button)
            buttons_layout.addWidget(delete_image_button)
            buttons_layout.addWidget(set_primary_button)

            buttons_layout.addStretch()

            close_button = QPushButton("بستن")
            buttons_layout.addWidget(close_button)

            main_layout.addLayout(buttons_layout)

            images_dialog.setLayout(main_layout)

            # تعریف توابع مورد نیاز
            def load_product_images():
                """بارگذاری تصاویر محصول در جدول"""
                try:
                    self.cursor.execute("""
                        SELECT id, image_path, description, is_primary, created_at
                        FROM product_images
                        WHERE product_id = ?
                        ORDER BY sort_order, id
                    """, (product_id,))

                    images = self.cursor.fetchall()
                    images_table.setRowCount(len(images))

                    for i, image in enumerate(images):
                        # شناسه
                        images_table.setItem(i, 0, QTableWidgetItem(str(image[0])))

                        # مسیر تصویر
                        images_table.setItem(i, 1, QTableWidgetItem(image[1]))

                        # توضیحات
                        images_table.setItem(i, 2, QTableWidgetItem(image[2] if image[2] else ""))

                        # تصویر اصلی
                        is_primary = "بله" if image[3] == 1 else "خیر"
                        primary_item = QTableWidgetItem(is_primary)
                        if image[3] == 1:
                            primary_item.setForeground(QtGui.QColor(0, 128, 0))  # سبز
                        images_table.setItem(i, 3, primary_item)

                        # پیش‌نمایش (دکمه نمایش)
                        preview_button = QPushButton("نمایش")
                        preview_button.clicked.connect(lambda checked, path=image[1]: show_preview(path))
                        images_table.setCellWidget(i, 4, preview_button)

                except Exception as e:
                    print(f"Error loading product images: {e}")
                    QMessageBox.critical(images_dialog, "خطا", f"خطا در بارگذاری تصاویر: {str(e)}")

            def show_preview(image_path):
                """نمایش پیش‌نمایش تصویر انتخاب شده"""
                try:
                    if os.path.exists(image_path):
                        pixmap = QtGui.QPixmap(image_path)
                        pixmap = pixmap.scaled(preview_label.width(), preview_label.height(),
                                              QtCore.Qt.KeepAspectRatio, QtCore.Qt.SmoothTransformation)
                        preview_label.setPixmap(pixmap)
                    else:
                        preview_label.setText("تصویر یافت نشد")
                except Exception as e:
                    print(f"Error showing preview: {e}")
                    preview_label.setText(f"خطا در نمایش تصویر: {str(e)}")

            def browse_new_image():
                """انتخاب تصویر جدید"""
                try:
                    file_path, _ = QFileDialog.getOpenFileName(
                        images_dialog, 'انتخاب تصویر', '', 'Image Files (*.png *.jpg *.jpeg *.bmp *.gif)'
                    )

                    if file_path:
                        new_image_path.setText(file_path)
                        show_preview(file_path)
                except Exception as e:
                    print(f"Error browsing new image: {e}")
                    QMessageBox.critical(images_dialog, "خطا", f"خطا در انتخاب تصویر: {str(e)}")

            def add_new_image():
                """افزودن تصویر جدید به محصول"""
                try:
                    image_path = new_image_path.text().strip()
                    description = new_image_desc.text().strip()
                    is_primary = 1 if new_image_primary.isChecked() else 0

                    if not image_path:
                        QMessageBox.warning(images_dialog, "خطا", "لطفاً یک تصویر انتخاب کنید.")
                        return

                    if not os.path.exists(image_path):
                        QMessageBox.warning(images_dialog, "خطا", "فایل تصویر انتخاب شده وجود ندارد.")
                        return

                    # کپی تصویر به پوشه product_images
                    file_name = os.path.basename(image_path)
                    timestamp = int(time.time())
                    new_file_name = f"{product_id}_{timestamp}_{file_name}"
                    new_path = os.path.join('product_images', new_file_name)

                    # اطمینان از وجود پوشه
                    if not os.path.exists('product_images'):
                        os.makedirs('product_images')

                    # کپی فایل
                    import shutil
                    shutil.copy2(image_path, new_path)

                    # اگر این تصویر به عنوان تصویر اصلی انتخاب شده، تصاویر دیگر را غیر اصلی کنیم
                    if is_primary == 1:
                        self.cursor.execute("""
                            UPDATE product_images
                            SET is_primary = 0
                            WHERE product_id = ?
                        """, (product_id,))

                        # همچنین فیلد image در جدول products را به‌روزرسانی کنیم
                        self.cursor.execute("""
                            UPDATE products
                            SET image = ?
                            WHERE id = ?
                        """, (new_path, product_id))

                    # تعیین ترتیب نمایش
                    self.cursor.execute("""
                        SELECT MAX(sort_order) FROM product_images WHERE product_id = ?
                    """, (product_id,))
                    max_order = self.cursor.fetchone()[0]
                    sort_order = (max_order or 0) + 10  # افزایش با گام 10

                    # ثبت تصویر در پایگاه داده
                    created_at = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
                    self.cursor.execute("""
                        INSERT INTO product_images
                        (product_id, image_path, is_primary, sort_order, description, created_at)
                        VALUES (?, ?, ?, ?, ?, ?)
                    """, (product_id, new_path, is_primary, sort_order, description, created_at))

                    self.conn.commit()

                    # پاک کردن فیلدها
                    new_image_path.clear()
                    new_image_desc.clear()
                    new_image_primary.setChecked(False)

                    # به‌روزرسانی جدول
                    load_product_images()

                    # ثبت فعالیت
                    self.log_activity("product", f"افزودن تصویر جدید به محصول {product_name}")

                    QMessageBox.information(images_dialog, "موفقیت", "تصویر با موفقیت اضافه شد.")

                except Exception as e:
                    self.conn.rollback()
                    print(f"Error adding new image: {e}")
                    QMessageBox.critical(images_dialog, "خطا", f"خطا در افزودن تصویر: {str(e)}")

            def delete_image():
                """حذف تصویر انتخاب شده"""
                try:
                    selected_row = images_table.currentRow()
                    if selected_row < 0:
                        QMessageBox.warning(images_dialog, "خطا", "لطفاً یک تصویر را انتخاب کنید.")
                        return

                    image_id = images_table.item(selected_row, 0).text()
                    image_path = images_table.item(selected_row, 1).text()
                    is_primary = images_table.item(selected_row, 3).text() == "بله"

                    # تأیید حذف
                    reply = QMessageBox.question(
                        images_dialog,
                        'تأیید حذف',
                        'آیا از حذف این تصویر اطمینان دارید؟',
                        QMessageBox.Yes | QMessageBox.No,
                        QMessageBox.No
                    )

                    if reply == QMessageBox.Yes:
                        # حذف فایل تصویر
                        if os.path.exists(image_path):
                            try:
                                os.remove(image_path)
                            except:
                                print(f"Warning: Could not delete file {image_path}")

                        # حذف از پایگاه داده
                        self.cursor.execute("DELETE FROM product_images WHERE id = ?", (image_id,))

                        # اگر تصویر اصلی بوده، یک تصویر دیگر را به عنوان اصلی تنظیم کنیم
                        if is_primary:
                            self.cursor.execute("""
                                SELECT id, image_path FROM product_images
                                WHERE product_id = ?
                                ORDER BY sort_order, id
                                LIMIT 1
                            """, (product_id,))

                            next_primary = self.cursor.fetchone()
                            if next_primary:
                                self.cursor.execute("""
                                    UPDATE product_images
                                    SET is_primary = 1
                                    WHERE id = ?
                                """, (next_primary[0],))

                                # به‌روزرسانی فیلد image در جدول products
                                self.cursor.execute("""
                                    UPDATE products
                                    SET image = ?
                                    WHERE id = ?
                                """, (next_primary[1], product_id))
                            else:
                                # اگر تصویر دیگری وجود ندارد، فیلد image را خالی کنیم
                                self.cursor.execute("""
                                    UPDATE products
                                    SET image = NULL
                                    WHERE id = ?
                                """, (product_id,))

                        self.conn.commit()

                        # به‌روزرسانی جدول
                        load_product_images()

                        # پاک کردن پیش‌نمایش
                        preview_label.clear()

                        # ثبت فعالیت
                        self.log_activity("product", f"حذف تصویر از محصول {product_name}")

                        QMessageBox.information(images_dialog, "موفقیت", "تصویر با موفقیت حذف شد.")

                except Exception as e:
                    self.conn.rollback()
                    print(f"Error deleting image: {e}")
                    QMessageBox.critical(images_dialog, "خطا", f"خطا در حذف تصویر: {str(e)}")

            def set_as_primary():
                """تنظیم تصویر انتخاب شده به عنوان تصویر اصلی"""
                try:
                    selected_row = images_table.currentRow()
                    if selected_row < 0:
                        QMessageBox.warning(images_dialog, "خطا", "لطفاً یک تصویر را انتخاب کنید.")
                        return

                    image_id = images_table.item(selected_row, 0).text()
                    image_path = images_table.item(selected_row, 1).text()

                    # تنظیم همه تصاویر به غیر اصلی
                    self.cursor.execute("""
                        UPDATE product_images
                        SET is_primary = 0
                        WHERE product_id = ?
                    """, (product_id,))

                    # تنظیم تصویر انتخاب شده به عنوان اصلی
                    self.cursor.execute("""
                        UPDATE product_images
                        SET is_primary = 1
                        WHERE id = ?
                    """, (image_id,))

                    # به‌روزرسانی فیلد image در جدول products
                    self.cursor.execute("""
                        UPDATE products
                        SET image = ?
                        WHERE id = ?
                    """, (image_path, product_id))

                    self.conn.commit()

                    # به‌روزرسانی جدول
                    load_product_images()

                    # ثبت فعالیت
                    self.log_activity("product", f"تغییر تصویر اصلی محصول {product_name}")

                    QMessageBox.information(images_dialog, "موفقیت", "تصویر اصلی با موفقیت تغییر کرد.")

                except Exception as e:
                    self.conn.rollback()
                    print(f"Error setting primary image: {e}")
                    QMessageBox.critical(images_dialog, "خطا", f"خطا در تنظیم تصویر اصلی: {str(e)}")

            def edit_image():
                """ویرایش و برش تصویر انتخاب شده"""
                try:
                    selected_row = images_table.currentRow()
                    if selected_row < 0:
                        QMessageBox.warning(images_dialog, "خطا", "لطفاً یک تصویر را انتخاب کنید.")
                        return

                    image_id = images_table.item(selected_row, 0).text()
                    image_path = images_table.item(selected_row, 1).text()

                    if not os.path.exists(image_path):
                        QMessageBox.warning(images_dialog, "خطا", "فایل تصویر یافت نشد.")
                        return

                    # ایجاد دیالوگ ویرایش تصویر
                    edit_dialog = QDialog(images_dialog)
                    edit_dialog.setWindowTitle("ویرایش تصویر")
                    edit_dialog.setMinimumSize(800, 600)

                    edit_layout = QVBoxLayout()

                    # بارگذاری تصویر با PIL
                    img = Image.open(image_path)

                    # تبدیل به QPixmap برای نمایش
                    img_qt = toqimage(img)
                    pixmap = QtGui.QPixmap.fromImage(img_qt)

                    # ایجاد QLabel برای نمایش تصویر
                    image_label = QLabel()
                    image_label.setAlignment(QtCore.Qt.AlignCenter)
                    image_label.setPixmap(pixmap.scaled(
                        700, 500,
                        QtCore.Qt.KeepAspectRatio,
                        QtCore.Qt.SmoothTransformation
                    ))

                    edit_layout.addWidget(image_label)

                    # دکمه‌های ویرایش
                    buttons_layout = QHBoxLayout()

                    rotate_left_button = QPushButton("چرخش به چپ")
                    rotate_right_button = QPushButton("چرخش به راست")
                    crop_button = QPushButton("برش تصویر")
                    save_button = QPushButton("ذخیره تغییرات")
                    cancel_button = QPushButton("انصراف")

                    buttons_layout.addWidget(rotate_left_button)
                    buttons_layout.addWidget(rotate_right_button)
                    buttons_layout.addWidget(crop_button)
                    buttons_layout.addWidget(save_button)
                    buttons_layout.addWidget(cancel_button)

                    edit_layout.addLayout(buttons_layout)

                    edit_dialog.setLayout(edit_layout)

                    # متغیرهای مورد نیاز برای ویرایش
                    current_img = img.copy()
                    crop_mode = False
                    crop_start = None
                    crop_rect = None

                    # تابع به‌روزرسانی نمایش تصویر
                    def update_image_display():
                        img_qt = toqimage(current_img)
                        pixmap = QtGui.QPixmap.fromImage(img_qt)
                        image_label.setPixmap(pixmap.scaled(
                            700, 500,
                            QtCore.Qt.KeepAspectRatio,
                            QtCore.Qt.SmoothTransformation
                        ))

                    # توابع ویرایش تصویر
                    def rotate_left():
                        nonlocal current_img
                        current_img = current_img.rotate(90, expand=True)
                        update_image_display()

                    def rotate_right():
                        nonlocal current_img
                        current_img = current_img.rotate(-90, expand=True)
                        update_image_display()

                    def start_crop():
                        nonlocal crop_mode
                        crop_mode = True
                        QMessageBox.information(edit_dialog, "برش تصویر",
                                              "برای برش تصویر، با ماوس روی تصویر کلیک کنید و بکشید.")

                    def save_changes():
                        try:
                            # ذخیره تصویر ویرایش شده
                            file_name = os.path.basename(image_path)
                            timestamp = int(time.time())
                            new_file_name = f"{product_id}_{timestamp}_{file_name}"
                            new_path = os.path.join('product_images', new_file_name)

                            # اطمینان از وجود پوشه
                            if not os.path.exists('product_images'):
                                os.makedirs('product_images')

                            # ذخیره تصویر جدید
                            current_img.save(new_path)

                            # به‌روزرسانی مسیر در پایگاه داده
                            is_primary = 0
                            self.cursor.execute("SELECT is_primary FROM product_images WHERE id = ?", (image_id,))
                            result = self.cursor.fetchone()
                            if result:
                                is_primary = result[0]

                            self.cursor.execute("""
                                UPDATE product_images
                                SET image_path = ?
                                WHERE id = ?
                            """, (new_path, image_id))

                            # اگر تصویر اصلی است، جدول products را هم به‌روزرسانی کنیم
                            if is_primary == 1:
                                self.cursor.execute("""
                                    UPDATE products
                                    SET image = ?
                                    WHERE id = ?
                                """, (new_path, product_id))

                            self.conn.commit()

                            # حذف فایل قدیمی
                            if os.path.exists(image_path) and image_path != new_path:
                                try:
                                    os.remove(image_path)
                                except:
                                    print(f"Warning: Could not delete old file {image_path}")

                            # ثبت فعالیت
                            self.log_activity("product", f"ویرایش تصویر محصول {product_name}")

                            QMessageBox.information(edit_dialog, "موفقیت", "تصویر با موفقیت ویرایش شد.")
                            edit_dialog.accept()

                            # به‌روزرسانی جدول تصاویر
                            load_product_images()

                        except Exception as e:
                            self.conn.rollback()
                            print(f"Error saving edited image: {e}")
                            QMessageBox.critical(edit_dialog, "خطا", f"خطا در ذخیره تصویر: {str(e)}")

                    # اتصال توابع به دکمه‌ها
                    rotate_left_button.clicked.connect(rotate_left)
                    rotate_right_button.clicked.connect(rotate_right)
                    crop_button.clicked.connect(start_crop)
                    save_button.clicked.connect(save_changes)
                    cancel_button.clicked.connect(edit_dialog.reject)

                    # کلاس برای پیاده‌سازی برش تصویر
                    class CropLabel(QLabel):
                        def __init__(self, parent=None):
                            super().__init__(parent)
                            self.setMouseTracking(True)
                            self.rubberBand = QtWidgets.QRubberBand(QtWidgets.QRubberBand.Rectangle, self)
                            self.origin = QtCore.QPoint()
                            self.crop_start = None
                            self.crop_end = None

                        def mousePressEvent(self, event):
                            if crop_mode and event.button() == QtCore.Qt.LeftButton:
                                self.origin = event.pos()
                                self.rubberBand.setGeometry(QtCore.QRect(self.origin, QtCore.QSize()))
                                self.rubberBand.show()
                                self.crop_start = event.pos()

                        def mouseMoveEvent(self, event):
                            if crop_mode and not self.origin.isNull():
                                self.rubberBand.setGeometry(QtCore.QRect(self.origin, event.pos()).normalized())

                        def mouseReleaseEvent(self, event):
                            if crop_mode and event.button() == QtCore.Qt.LeftButton:
                                self.crop_end = event.pos()
                                self.rubberBand.hide()
                                self.perform_crop()

                        def perform_crop(self):
                            nonlocal current_img

                            if not self.crop_start or not self.crop_end:
                                return

                            # تبدیل مختصات پیکسل‌های انتخاب شده به مختصات واقعی تصویر
                            pixmap = self.pixmap()
                            if not pixmap:
                                return

                            # محاسبه نسبت مقیاس
                            img_rect = self.pixmap().rect()
                            label_rect = self.rect()

                            scale_x = img_rect.width() / label_rect.width()
                            scale_y = img_rect.height() / label_rect.height()

                            # محاسبه مختصات واقعی در تصویر اصلی
                            x1 = int(min(self.crop_start.x(), self.crop_end.x()) * scale_x)
                            y1 = int(min(self.crop_start.y(), self.crop_end.y()) * scale_y)
                            x2 = int(max(self.crop_start.x(), self.crop_end.x()) * scale_x)
                            y2 = int(max(self.crop_start.y(), self.crop_end.y()) * scale_y)

                            # برش تصویر
                            current_img = current_img.crop((x1, y1, x2, y2))
                            update_image_display()

                            # خروج از حالت برش
                            nonlocal crop_mode
                            crop_mode = False

                    # جایگزینی QLabel با CropLabel
                    crop_label = CropLabel()
                    crop_label.setAlignment(QtCore.Qt.AlignCenter)
                    crop_label.setPixmap(pixmap.scaled(
                        700, 500,
                        QtCore.Qt.KeepAspectRatio,
                        QtCore.Qt.SmoothTransformation
                    ))

                    # حذف QLabel قبلی و اضافه کردن CropLabel
                    edit_layout.removeWidget(image_label)
                    image_label.deleteLater()
                    edit_layout.insertWidget(0, crop_label)

                    # به‌روزرسانی تابع نمایش تصویر
                    def update_image_display():
                        img_qt = toqimage(current_img)
                        pixmap = QtGui.QPixmap.fromImage(img_qt)
                        crop_label.setPixmap(pixmap.scaled(
                            700, 500,
                            QtCore.Qt.KeepAspectRatio,
                            QtCore.Qt.SmoothTransformation
                        ))

                    edit_dialog.exec_()

                except Exception as e:
                    print(f"Error editing image: {e}")
                    QMessageBox.critical(images_dialog, "خطا", f"خطا در ویرایش تصویر: {str(e)}")

            # اتصال توابع به رویدادها
            new_image_browse.clicked.connect(browse_new_image)
            add_image_button.clicked.connect(add_new_image)
            delete_image_button.clicked.connect(delete_image)
            set_primary_button.clicked.connect(set_as_primary)
            edit_image_button.clicked.connect(edit_image)
            close_button.clicked.connect(images_dialog.accept)

            # بارگذاری تصاویر محصول
            load_product_images()

            # نمایش دیالوگ
            images_dialog.exec_()

            # ثبت فعالیت
            self.log_activity("product", f"مدیریت تصاویر محصول {product_name}")

        except Exception as e:
            print(f"Error in manage_product_images: {e}")
            QMessageBox.critical(self, "خطا", f"خطا در مدیریت تصاویر: {str(e)}")

if __name__ == '__main__':
    try:
        app = QApplication(sys.argv)
        window = ProductManager()
        window.show()
        sys.exit(app.exec_())
    except Exception as e:
        print(f"Fatal error: {e}")
        # در صورت بروز خطای جدی، یک پیام خطا نمایش می‌دهیم
        if QApplication.instance():
            QMessageBox.critical(None, "Fatal Error", f"A critical error occurred: {str(e)}")
        sys.exit(1)