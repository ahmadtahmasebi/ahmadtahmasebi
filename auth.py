from PyQt5.QtWidgets import (QDialog, QVBoxLayout, QHBoxLayout, QLabel, QLineEdit,
                            QPushButton, QMessageBox, QFormLayout, QComboBox, QTableWidget,
                            QTableWidgetItem, QTabWidget, QWidget, QGroupBox, QGridLayout,
                            QCheckBox, QDialogButtonBox, QScrollArea)
from PyQt5.QtCore import Qt, QDateTime
from PyQt5.QtGui import QIcon, QPixmap, QFont
from database import DatabaseManager
import datetime
import socket

class AuthManager:
    def __init__(self):
        self.db = DatabaseManager()
        self.login_dialog = None
        self.register_dialog = None
        self.current_user = None
        self.user_management_dialog = None

    def show_login_dialog(self):
        self.login_dialog = QDialog()
        self.login_dialog.setWindowTitle('ورود به سیستم')
        self.login_dialog.setGeometry(100, 100, 400, 300)
        self.login_dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
                font-weight: bold;
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
            QPushButton {
                background-color: #0078d7;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #00559b;
            }
            QPushButton:pressed {
                background-color: #003c6c;
            }
            QPushButton#registerBtn {
                background-color: #5cb85c;
            }
            QPushButton#registerBtn:hover {
                background-color: #449d44;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # عنوان فرم
        title_label = QLabel("ورود به سیستم مدیریت محصولات")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #0078d7;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #cccccc;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # فرم ورود
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(0, 10, 0, 10)

        self.login_username_label = QLabel('نام کاربری:')
        self.login_username_input = QLineEdit()
        self.login_username_input.setPlaceholderText("نام کاربری خود را وارد کنید")
        form_layout.addRow(self.login_username_label, self.login_username_input)

        self.login_password_label = QLabel('رمز عبور:')
        self.login_password_input = QLineEdit()
        self.login_password_input.setEchoMode(QLineEdit.Password)
        self.login_password_input.setPlaceholderText("رمز عبور خود را وارد کنید")
        form_layout.addRow(self.login_password_label, self.login_password_input)

        layout.addLayout(form_layout)

        # دکمه‌های عملیات
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.login_button = QPushButton('ورود')
        self.login_button.clicked.connect(self.login)
        buttons_layout.addWidget(self.login_button)

        self.register_button = QPushButton('ثبت‌نام')
        self.register_button.setObjectName("registerBtn")
        self.register_button.clicked.connect(self.show_register_dialog)
        buttons_layout.addWidget(self.register_button)

        layout.addLayout(buttons_layout)

        # اطلاعات راهنما
        info_label = QLabel("برای ورود به عنوان مدیر سیستم از نام کاربری 'admin' و رمز عبور 'admin123' استفاده کنید.")
        info_label.setStyleSheet("""
            font-size: 11px;
            color: #666666;
            margin-top: 15px;
        """)
        info_label.setWordWrap(True)
        layout.addWidget(info_label)

        self.login_dialog.setLayout(layout)
        return self.login_dialog.exec_()

    def show_register_dialog(self):
        self.register_dialog = QDialog()
        self.register_dialog.setWindowTitle('ثبت‌نام کاربر جدید')
        self.register_dialog.setGeometry(100, 100, 450, 400)
        self.register_dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
                font-weight: bold;
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
            QPushButton {
                background-color: #5cb85c;
                color: white;
                border: none;
                border-radius: 4px;
                padding: 8px 16px;
                font-weight: bold;
                min-height: 30px;
            }
            QPushButton:hover {
                background-color: #449d44;
            }
            QPushButton:pressed {
                background-color: #398439;
            }
            QPushButton#cancelBtn {
                background-color: #d9534f;
            }
            QPushButton#cancelBtn:hover {
                background-color: #c9302c;
            }
        """)

        layout = QVBoxLayout()
        layout.setSpacing(15)
        layout.setContentsMargins(20, 20, 20, 20)

        # عنوان فرم
        title_label = QLabel("ثبت‌نام کاربر جدید")
        title_label.setStyleSheet("""
            font-size: 18px;
            font-weight: bold;
            color: #5cb85c;
            margin-bottom: 10px;
            padding-bottom: 10px;
            border-bottom: 1px solid #cccccc;
        """)
        title_label.setAlignment(Qt.AlignCenter)
        layout.addWidget(title_label)

        # فرم ثبت‌نام
        form_layout = QFormLayout()
        form_layout.setSpacing(10)
        form_layout.setContentsMargins(0, 10, 0, 10)

        self.register_username_label = QLabel('نام کاربری:')
        self.register_username_input = QLineEdit()
        self.register_username_input.setPlaceholderText("نام کاربری منحصر به فرد")
        form_layout.addRow(self.register_username_label, self.register_username_input)

        self.register_password_label = QLabel('رمز عبور:')
        self.register_password_input = QLineEdit()
        self.register_password_input.setEchoMode(QLineEdit.Password)
        self.register_password_input.setPlaceholderText("رمز عبور امن")
        form_layout.addRow(self.register_password_label, self.register_password_input)

        self.register_fullname_label = QLabel('نام کامل:')
        self.register_fullname_input = QLineEdit()
        self.register_fullname_input.setPlaceholderText("نام و نام خانوادگی")
        form_layout.addRow(self.register_fullname_label, self.register_fullname_input)

        self.register_email_label = QLabel('ایمیل:')
        self.register_email_input = QLineEdit()
        self.register_email_input.setPlaceholderText("example@domain.com")
        form_layout.addRow(self.register_email_label, self.register_email_input)

        layout.addLayout(form_layout)

        # دکمه‌های عملیات
        buttons_layout = QHBoxLayout()
        buttons_layout.setSpacing(10)

        self.register_submit_button = QPushButton('ثبت‌نام')
        self.register_submit_button.clicked.connect(self.register)
        buttons_layout.addWidget(self.register_submit_button)

        self.register_cancel_button = QPushButton('انصراف')
        self.register_cancel_button.setObjectName("cancelBtn")
        self.register_cancel_button.clicked.connect(self.register_dialog.reject)
        buttons_layout.addWidget(self.register_cancel_button)

        layout.addLayout(buttons_layout)

        self.register_dialog.setLayout(layout)
        self.register_dialog.exec_()

    def login(self):
        username = self.login_username_input.text().strip()
        password = self.login_password_input.text().strip()

        if not username or not password:
            QMessageBox.warning(self.login_dialog, 'خطا', 'لطفاً نام کاربری و رمز عبور را وارد کنید.')
            return

        user = self.db.fetch_query("SELECT id, username, role, is_active FROM users WHERE username = ? AND password = ?", (username, password))

        if not user:
            QMessageBox.warning(self.login_dialog, 'خطا', 'نام کاربری یا رمز عبور اشتباه است.')
            return

        user = user[0]  # اولین نتیجه را انتخاب می‌کنیم

        # بررسی فعال بودن کاربر
        if user[3] != 1:
            QMessageBox.warning(self.login_dialog, 'خطا', 'حساب کاربری شما غیرفعال شده است. لطفاً با مدیر سیستم تماس بگیرید.')
            return

        # ذخیره اطلاعات کاربر جاری
        self.current_user = {
            'id': user[0],
            'username': user[1],
            'role': user[2]
        }

        # به‌روزرسانی زمان آخرین ورود
        last_login = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        self.db.execute_query("UPDATE users SET last_login = ? WHERE id = ?", (last_login, user[0]))

        # ثبت فعالیت ورود
        ip_address = socket.gethostbyname(socket.gethostname())
        self.db.log_activity(
            user_id=user[0],
            activity_type="login",
            description=f"ورود به سیستم با نام کاربری {username}",
            ip_address=ip_address
        )

        self.login_dialog.accept()

    def register(self):
        username = self.register_username_input.text().strip()
        password = self.register_password_input.text().strip()
        full_name = self.register_fullname_input.text().strip()
        email = self.register_email_input.text().strip()

        # اعتبارسنجی ورودی‌ها
        if not username or not password:
            QMessageBox.warning(self.register_dialog, 'خطا', 'نام کاربری و رمز عبور الزامی هستند.')
            return

        if len(password) < 6:
            QMessageBox.warning(self.register_dialog, 'خطا', 'رمز عبور باید حداقل 6 کاراکتر باشد.')
            return

        # بررسی تکراری نبودن نام کاربری
        user = self.db.fetch_query("SELECT * FROM users WHERE username = ?", (username,))
        if user:
            QMessageBox.warning(self.register_dialog, 'خطا', 'این نام کاربری قبلاً ثبت شده است.')
            return

        # ثبت کاربر جدید
        current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
        try:
            self.db.execute_query(
                "INSERT INTO users (username, password, full_name, email, role, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                (username, password, full_name, email, 'user', 1, current_time)
            )

            # دریافت شناسه کاربر جدید
            user = self.db.fetch_query("SELECT id FROM users WHERE username = ?", (username,))
            if user:
                user_id = user[0][0]

                # ثبت فعالیت ثبت‌نام
                ip_address = socket.gethostbyname(socket.gethostname())
                self.db.log_activity(
                    user_id=user_id,
                    activity_type="register",
                    description="ثبت‌نام کاربر جدید",
                    ip_address=ip_address
                )

            self.register_dialog.accept()
            QMessageBox.information(self.register_dialog, 'موفقیت', 'ثبت‌نام با موفقیت انجام شد. اکنون می‌توانید وارد سیستم شوید.')

        except Exception as e:
            QMessageBox.critical(self.register_dialog, 'خطا', f'خطا در ثبت‌نام: {str(e)}')

    def show_user_management(self):
        """نمایش فرم مدیریت کاربران (فقط برای مدیران)"""
        if not self.current_user or self.current_user['role'] != 'admin':
            QMessageBox.warning(None, 'خطا', 'شما دسترسی لازم برای مدیریت کاربران را ندارید.')
            return

        self.user_management_dialog = QDialog()
        self.user_management_dialog.setWindowTitle('مدیریت کاربران')
        self.user_management_dialog.setGeometry(100, 100, 900, 600)
        self.user_management_dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                color: #333333;
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
            QTableWidget {
                border: 1px solid #cccccc;
                border-radius: 4px;
                background-color: white;
                alternate-background-color: #f9f9f9;
            }
            QTableWidget::item {
                padding: 4px;
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

        # ایجاد تب‌ها
        tab_widget = QTabWidget()

        # تب لیست کاربران
        users_tab = QWidget()
        users_layout = QVBoxLayout()

        # جدول کاربران
        self.users_table = QTableWidget()
        self.users_table.setColumnCount(8)
        self.users_table.setHorizontalHeaderLabels(['شناسه', 'نام کاربری', 'نام کامل', 'ایمیل', 'نقش', 'وضعیت', 'آخرین ورود', 'تاریخ ثبت‌نام'])
        self.users_table.setAlternatingRowColors(True)
        self.users_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.users_table.setSelectionMode(QTableWidget.SingleSelection)
        self.users_table.horizontalHeader().setStretchLastSection(True)

        # دکمه‌های عملیات
        buttons_layout = QHBoxLayout()

        add_user_button = QPushButton('افزودن کاربر')
        add_user_button.clicked.connect(self.show_add_user_dialog)
        buttons_layout.addWidget(add_user_button)

        edit_user_button = QPushButton('ویرایش کاربر')
        edit_user_button.clicked.connect(self.show_edit_user_dialog)
        buttons_layout.addWidget(edit_user_button)

        delete_user_button = QPushButton('حذف کاربر')
        delete_user_button.setObjectName("deleteBtn")
        delete_user_button.clicked.connect(self.delete_user)
        buttons_layout.addWidget(delete_user_button)

        toggle_status_button = QPushButton('تغییر وضعیت')
        toggle_status_button.clicked.connect(self.toggle_user_status)
        buttons_layout.addWidget(toggle_status_button)

        buttons_layout.addStretch()

        refresh_button = QPushButton('به‌روزرسانی')
        refresh_button.clicked.connect(self.load_users)
        buttons_layout.addWidget(refresh_button)

        users_layout.addWidget(self.users_table)
        users_layout.addLayout(buttons_layout)
        users_tab.setLayout(users_layout)

        # تب فعالیت‌های کاربران
        activities_tab = QWidget()
        activities_layout = QVBoxLayout()

        # جدول فعالیت‌ها
        self.activities_table = QTableWidget()
        self.activities_table.setColumnCount(6)
        self.activities_table.setHorizontalHeaderLabels(['شناسه', 'کاربر', 'نوع فعالیت', 'توضیحات', 'زمان', 'آدرس IP'])
        self.activities_table.setAlternatingRowColors(True)
        self.activities_table.setSelectionBehavior(QTableWidget.SelectRows)
        self.activities_table.horizontalHeader().setStretchLastSection(True)

        # دکمه‌های عملیات فعالیت‌ها
        activities_buttons_layout = QHBoxLayout()

        activities_buttons_layout.addStretch()

        refresh_activities_button = QPushButton('به‌روزرسانی')
        refresh_activities_button.clicked.connect(self.load_activities)
        activities_buttons_layout.addWidget(refresh_activities_button)

        activities_layout.addWidget(self.activities_table)
        activities_layout.addLayout(activities_buttons_layout)
        activities_tab.setLayout(activities_layout)

        # افزودن تب‌ها
        tab_widget.addTab(users_tab, 'لیست کاربران')
        tab_widget.addTab(activities_tab, 'فعالیت‌های کاربران')

        # لایه اصلی
        main_layout = QVBoxLayout()
        main_layout.addWidget(tab_widget)

        # دکمه بستن
        close_button = QPushButton('بستن')
        close_button.clicked.connect(self.user_management_dialog.accept)

        close_layout = QHBoxLayout()
        close_layout.addStretch()
        close_layout.addWidget(close_button)

        main_layout.addLayout(close_layout)

        self.user_management_dialog.setLayout(main_layout)

        # بارگذاری داده‌ها
        self.load_users()
        self.load_activities()

        self.user_management_dialog.exec_()

    def load_users(self):
        """بارگذاری لیست کاربران در جدول"""
        try:
            users = self.db.fetch_query("""
                SELECT id, username, full_name, email, role, is_active, last_login, created_at
                FROM users
                ORDER BY id
            """)

            self.users_table.setRowCount(len(users))

            for i, user in enumerate(users):
                self.users_table.setItem(i, 0, QTableWidgetItem(str(user[0])))
                self.users_table.setItem(i, 1, QTableWidgetItem(user[1]))
                self.users_table.setItem(i, 2, QTableWidgetItem(user[2] if user[2] else ""))
                self.users_table.setItem(i, 3, QTableWidgetItem(user[3] if user[3] else ""))
                self.users_table.setItem(i, 4, QTableWidgetItem(user[4]))

                # وضعیت کاربر
                status_item = QTableWidgetItem("فعال" if user[5] == 1 else "غیرفعال")
                if user[5] != 1:
                    status_item.setForeground(Qt.red)
                self.users_table.setItem(i, 5, status_item)

                # آخرین ورود
                self.users_table.setItem(i, 6, QTableWidgetItem(user[6] if user[6] else ""))

                # تاریخ ثبت‌نام
                self.users_table.setItem(i, 7, QTableWidgetItem(user[7] if user[7] else ""))

        except Exception as e:
            QMessageBox.critical(self.user_management_dialog, 'خطا', f'خطا در بارگذاری کاربران: {str(e)}')

    def load_activities(self):
        """بارگذاری فعالیت‌های کاربران در جدول"""
        try:
            activities = self.db.fetch_query("""
                SELECT a.id, u.username, a.activity_type, a.description, a.timestamp, a.ip_address
                FROM user_activities a
                JOIN users u ON a.user_id = u.id
                ORDER BY a.timestamp DESC
                LIMIT 100
            """)

            self.activities_table.setRowCount(len(activities))

            for i, activity in enumerate(activities):
                self.activities_table.setItem(i, 0, QTableWidgetItem(str(activity[0])))
                self.activities_table.setItem(i, 1, QTableWidgetItem(activity[1]))
                self.activities_table.setItem(i, 2, QTableWidgetItem(activity[2]))
                self.activities_table.setItem(i, 3, QTableWidgetItem(activity[3]))
                self.activities_table.setItem(i, 4, QTableWidgetItem(activity[4]))
                self.activities_table.setItem(i, 5, QTableWidgetItem(activity[5]))

        except Exception as e:
            QMessageBox.critical(self.user_management_dialog, 'خطا', f'خطا در بارگذاری فعالیت‌ها: {str(e)}')

    def show_add_user_dialog(self):
        """نمایش فرم افزودن کاربر جدید"""
        dialog = QDialog(self.user_management_dialog)
        dialog.setWindowTitle('افزودن کاربر جدید')
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
        """)

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        username_input = QLineEdit()
        username_input.setPlaceholderText("نام کاربری منحصر به فرد")
        form_layout.addRow('نام کاربری:', username_input)

        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setPlaceholderText("رمز عبور")
        form_layout.addRow('رمز عبور:', password_input)

        fullname_input = QLineEdit()
        fullname_input.setPlaceholderText("نام و نام خانوادگی")
        form_layout.addRow('نام کامل:', fullname_input)

        email_input = QLineEdit()
        email_input.setPlaceholderText("example@domain.com")
        form_layout.addRow('ایمیل:', email_input)

        role_combo = QComboBox()
        role_combo.addItems(['user', 'admin', 'manager'])
        form_layout.addRow('نقش:', role_combo)

        is_active_check = QCheckBox("کاربر فعال است")
        is_active_check.setChecked(True)
        form_layout.addRow('وضعیت:', is_active_check)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            username = username_input.text().strip()
            password = password_input.text().strip()
            full_name = fullname_input.text().strip()
            email = email_input.text().strip()
            role = role_combo.currentText()
            is_active = 1 if is_active_check.isChecked() else 0

            if not username or not password:
                QMessageBox.warning(self.user_management_dialog, 'خطا', 'نام کاربری و رمز عبور الزامی هستند.')
                return

            # بررسی تکراری نبودن نام کاربری
            user = self.db.fetch_query("SELECT * FROM users WHERE username = ?", (username,))
            if user:
                QMessageBox.warning(self.user_management_dialog, 'خطا', 'این نام کاربری قبلاً ثبت شده است.')
                return

            # ثبت کاربر جدید
            current_time = datetime.datetime.now().strftime("%Y-%m-%d %H:%M:%S")
            try:
                self.db.execute_query(
                    "INSERT INTO users (username, password, full_name, email, role, is_active, created_at) VALUES (?, ?, ?, ?, ?, ?, ?)",
                    (username, password, full_name, email, role, is_active, current_time)
                )

                # ثبت فعالیت
                self.db.log_activity(
                    user_id=self.current_user['id'],
                    activity_type="user_management",
                    description=f"افزودن کاربر جدید: {username}"
                )

                self.load_users()
                QMessageBox.information(self.user_management_dialog, 'موفقیت', 'کاربر جدید با موفقیت اضافه شد.')

            except Exception as e:
                QMessageBox.critical(self.user_management_dialog, 'خطا', f'خطا در افزودن کاربر: {str(e)}')

    def show_edit_user_dialog(self):
        """نمایش فرم ویرایش کاربر"""
        selected_row = self.users_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self.user_management_dialog, 'خطا', 'لطفاً یک کاربر را انتخاب کنید.')
            return

        user_id = self.users_table.item(selected_row, 0).text()

        # دریافت اطلاعات کاربر
        user = self.db.fetch_query("SELECT * FROM users WHERE id = ?", (user_id,))
        if not user:
            QMessageBox.warning(self.user_management_dialog, 'خطا', 'کاربر مورد نظر یافت نشد.')
            return

        user = user[0]

        dialog = QDialog(self.user_management_dialog)
        dialog.setWindowTitle('ویرایش کاربر')
        dialog.setMinimumWidth(400)
        dialog.setStyleSheet("""
            QDialog {
                background-color: #f5f5f5;
            }
            QLabel {
                font-weight: bold;
            }
            QLineEdit, QComboBox {
                border: 1px solid #cccccc;
                border-radius: 4px;
                padding: 6px;
                background-color: white;
            }
        """)

        layout = QVBoxLayout()

        form_layout = QFormLayout()
        form_layout.setSpacing(10)

        username_input = QLineEdit()
        username_input.setText(user[1])  # username
        username_input.setReadOnly(True)  # نام کاربری قابل تغییر نیست
        username_input.setStyleSheet("background-color: #f0f0f0;")
        form_layout.addRow('نام کاربری:', username_input)

        password_input = QLineEdit()
        password_input.setEchoMode(QLineEdit.Password)
        password_input.setPlaceholderText("برای تغییر رمز عبور، رمز جدید را وارد کنید")
        form_layout.addRow('رمز عبور جدید:', password_input)

        fullname_input = QLineEdit()
        fullname_input.setText(user[3] if user[3] else "")  # full_name
        form_layout.addRow('نام کامل:', fullname_input)

        email_input = QLineEdit()
        email_input.setText(user[4] if user[4] else "")  # email
        form_layout.addRow('ایمیل:', email_input)

        role_combo = QComboBox()
        role_combo.addItems(['user', 'admin', 'manager'])
        role_combo.setCurrentText(user[5] if user[5] else "user")  # role
        form_layout.addRow('نقش:', role_combo)

        is_active_check = QCheckBox("کاربر فعال است")
        is_active_check.setChecked(user[6] == 1)  # is_active
        form_layout.addRow('وضعیت:', is_active_check)

        layout.addLayout(form_layout)

        button_box = QDialogButtonBox(QDialogButtonBox.Ok | QDialogButtonBox.Cancel)
        button_box.accepted.connect(dialog.accept)
        button_box.rejected.connect(dialog.reject)
        layout.addWidget(button_box)

        dialog.setLayout(layout)

        if dialog.exec_() == QDialog.Accepted:
            password = password_input.text().strip()
            full_name = fullname_input.text().strip()
            email = email_input.text().strip()
            role = role_combo.currentText()
            is_active = 1 if is_active_check.isChecked() else 0

            try:
                if password:
                    # اگر رمز عبور وارد شده باشد، آن را نیز به‌روزرسانی می‌کنیم
                    self.db.execute_query(
                        "UPDATE users SET password = ?, full_name = ?, email = ?, role = ?, is_active = ? WHERE id = ?",
                        (password, full_name, email, role, is_active, user_id)
                    )
                else:
                    # در غیر این صورت، رمز عبور را تغییر نمی‌دهیم
                    self.db.execute_query(
                        "UPDATE users SET full_name = ?, email = ?, role = ?, is_active = ? WHERE id = ?",
                        (full_name, email, role, is_active, user_id)
                    )

                # ثبت فعالیت
                self.db.log_activity(
                    user_id=self.current_user['id'],
                    activity_type="user_management",
                    description=f"ویرایش کاربر: {user[1]}"
                )

                self.load_users()
                QMessageBox.information(self.user_management_dialog, 'موفقیت', 'اطلاعات کاربر با موفقیت به‌روزرسانی شد.')

            except Exception as e:
                QMessageBox.critical(self.user_management_dialog, 'خطا', f'خطا در به‌روزرسانی کاربر: {str(e)}')

    def delete_user(self):
        """حذف کاربر انتخاب شده"""
        selected_row = self.users_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self.user_management_dialog, 'خطا', 'لطفاً یک کاربر را انتخاب کنید.')
            return

        user_id = self.users_table.item(selected_row, 0).text()
        username = self.users_table.item(selected_row, 1).text()

        # اطمینان از عدم حذف کاربر جاری
        if int(user_id) == self.current_user['id']:
            QMessageBox.warning(self.user_management_dialog, 'خطا', 'شما نمی‌توانید حساب کاربری خود را حذف کنید.')
            return

        # اطمینان از عدم حذف آخرین مدیر سیستم
        if self.users_table.item(selected_row, 4).text() == 'admin':
            admin_count = 0
            for row in range(self.users_table.rowCount()):
                if self.users_table.item(row, 4).text() == 'admin':
                    admin_count += 1

            if admin_count <= 1:
                QMessageBox.warning(self.user_management_dialog, 'خطا', 'حذف آخرین مدیر سیستم مجاز نیست.')
                return

        # تأیید حذف
        reply = QMessageBox.question(
            self.user_management_dialog,
            'تأیید حذف',
            f'آیا از حذف کاربر "{username}" اطمینان دارید؟\nاین عمل قابل بازگشت نیست.',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            try:
                # حذف فعالیت‌های کاربر
                self.db.execute_query("DELETE FROM user_activities WHERE user_id = ?", (user_id,))

                # حذف کاربر
                self.db.execute_query("DELETE FROM users WHERE id = ?", (user_id,))

                # ثبت فعالیت
                self.db.log_activity(
                    user_id=self.current_user['id'],
                    activity_type="user_management",
                    description=f"حذف کاربر: {username}"
                )

                self.load_users()
                self.load_activities()
                QMessageBox.information(self.user_management_dialog, 'موفقیت', 'کاربر با موفقیت حذف شد.')

            except Exception as e:
                QMessageBox.critical(self.user_management_dialog, 'خطا', f'خطا در حذف کاربر: {str(e)}')

    def toggle_user_status(self):
        """تغییر وضعیت فعال/غیرفعال کاربر"""
        selected_row = self.users_table.currentRow()
        if selected_row < 0:
            QMessageBox.warning(self.user_management_dialog, 'خطا', 'لطفاً یک کاربر را انتخاب کنید.')
            return

        user_id = self.users_table.item(selected_row, 0).text()
        username = self.users_table.item(selected_row, 1).text()
        current_status = self.users_table.item(selected_row, 5).text()

        # اطمینان از عدم غیرفعال‌سازی کاربر جاری
        if int(user_id) == self.current_user['id']:
            QMessageBox.warning(self.user_management_dialog, 'خطا', 'شما نمی‌توانید حساب کاربری خود را غیرفعال کنید.')
            return

        # اطمینان از عدم غیرفعال‌سازی آخرین مدیر سیستم
        if current_status == 'فعال' and self.users_table.item(selected_row, 4).text() == 'admin':
            active_admin_count = 0
            for row in range(self.users_table.rowCount()):
                if (self.users_table.item(row, 4).text() == 'admin' and
                    self.users_table.item(row, 5).text() == 'فعال'):
                    active_admin_count += 1

            if active_admin_count <= 1:
                QMessageBox.warning(self.user_management_dialog, 'خطا', 'غیرفعال‌سازی آخرین مدیر فعال سیستم مجاز نیست.')
                return

        # تغییر وضعیت
        new_status = 0 if current_status == 'فعال' else 1
        status_text = 'غیرفعال' if new_status == 0 else 'فعال'

        try:
            self.db.execute_query("UPDATE users SET is_active = ? WHERE id = ?", (new_status, user_id))

            # ثبت فعالیت
            self.db.log_activity(
                user_id=self.current_user['id'],
                activity_type="user_management",
                description=f"تغییر وضعیت کاربر {username} به {status_text}"
            )

            self.load_users()
            QMessageBox.information(self.user_management_dialog, 'موفقیت', f'وضعیت کاربر به {status_text} تغییر یافت.')

        except Exception as e:
            QMessageBox.critical(self.user_management_dialog, 'خطا', f'خطا در تغییر وضعیت کاربر: {str(e)}')

    def get_current_user(self):
        """دریافت اطلاعات کاربر جاری"""
        return self.current_user

    def log_user_activity(self, activity_type, description):
        """ثبت فعالیت کاربر جاری"""
        if self.current_user:
            try:
                self.db.log_activity(
                    user_id=self.current_user['id'],
                    activity_type=activity_type,
                    description=description
                )
            except Exception as e:
                print(f"Error logging user activity: {e}")