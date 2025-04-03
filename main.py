from PyQt5.QtWidgets import QApplication, QMainWindow, QAction, QMenu, QMessageBox
from PyQt5.QtGui import QIcon
from PyQt5.QtCore import Qt
import sys
from auth import AuthManager
from product_manager import ProductManager

class MainWindow(QMainWindow):
    def __init__(self, auth_manager):
        super().__init__()
        self.auth_manager = auth_manager
        self.current_user = auth_manager.get_current_user()
        self.product_manager = ProductManager()

        # تنظیم عنوان پنجره
        self.setWindowTitle(f"سیستم مدیریت محصولات - کاربر: {self.current_user['username']}")

        # ایجاد منوی کاربر
        self.create_user_menu()

        # تنظیم ویجت مرکزی
        self.setCentralWidget(self.product_manager)

        # ثبت فعالیت باز کردن برنامه
        self.auth_manager.log_user_activity(
            activity_type="application",
            description="باز کردن برنامه مدیریت محصولات"
        )

    def create_user_menu(self):
        """ایجاد منوی کاربر در نوار منو"""
        menubar = self.menuBar()

        # منوی کاربر
        user_menu = menubar.addMenu('کاربر')

        # گزینه مدیریت کاربران (فقط برای مدیران)
        if self.current_user['role'] == 'admin':
            user_management_action = QAction('مدیریت کاربران', self)
            user_management_action.triggered.connect(self.auth_manager.show_user_management)
            user_menu.addAction(user_management_action)

            user_menu.addSeparator()

        # گزینه خروج
        logout_action = QAction('خروج از حساب کاربری', self)
        logout_action.triggered.connect(self.logout)
        user_menu.addAction(logout_action)

        # اضافه کردن منوی کاربر به منوهای موجود در ProductManager

    def logout(self):
        """خروج از حساب کاربری"""
        reply = QMessageBox.question(
            self,
            'تأیید خروج',
            'آیا مطمئن هستید که می‌خواهید از حساب کاربری خود خارج شوید؟',
            QMessageBox.Yes | QMessageBox.No,
            QMessageBox.No
        )

        if reply == QMessageBox.Yes:
            # ثبت فعالیت خروج
            self.auth_manager.log_user_activity(
                activity_type="logout",
                description="خروج از حساب کاربری"
            )

            # بستن پنجره اصلی
            self.close()

            # نمایش مجدد فرم ورود
            if self.auth_manager.show_login_dialog():
                # به‌روزرسانی کاربر جاری
                self.current_user = self.auth_manager.get_current_user()

                # به‌روزرسانی عنوان پنجره
                self.setWindowTitle(f"سیستم مدیریت محصولات - کاربر: {self.current_user['username']}")

                # نمایش مجدد پنجره
                self.show()
            else:
                # خروج از برنامه در صورت انصراف از ورود
                sys.exit(0)

    def closeEvent(self, event):
        """رویداد بستن پنجره"""
        # ثبت فعالیت بستن برنامه
        if self.current_user:
            self.auth_manager.log_user_activity(
                activity_type="application",
                description="بستن برنامه مدیریت محصولات"
            )

        event.accept()

def main():
    app = QApplication(sys.argv)

    # تنظیم جهت راست به چپ برای زبان فارسی
    app.setLayoutDirection(Qt.RightToLeft)

    # نمایش فرم ورود
    auth_manager = AuthManager()
    if auth_manager.show_login_dialog():
        # در صورت موفقیت در ورود، نمایش فرم مدیریت محصولات
        window = MainWindow(auth_manager)
        window.show()
        sys.exit(app.exec_())
    else:
        sys.exit(1)

if __name__ == '__main__':
    main()