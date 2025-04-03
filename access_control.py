"""
ماژول کنترل دسترسی برای سیستم مدیریت محصولات
این ماژول امکان تعریف و بررسی سطوح دسترسی مختلف را فراهم می‌کند
"""

class AccessControl:
    """کلاس مدیریت دسترسی‌ها"""
    
    # تعریف سطوح دسترسی
    ROLES = {
        'admin': {
            'description': 'مدیر سیستم',
            'permissions': [
                'user_management',  # مدیریت کاربران
                'product_management',  # مدیریت محصولات
                'category_management',  # مدیریت دسته‌بندی‌ها
                'report_management',  # مدیریت گزارش‌ها
                'discount_management',  # مدیریت تخفیف‌ها
                'inventory_management',  # مدیریت موجودی
                'barcode_management',  # مدیریت بارکدها
                'settings_management',  # مدیریت تنظیمات
                'view_dashboard',  # مشاهده داشبورد
                'view_activities'  # مشاهده فعالیت‌ها
            ]
        },
        'manager': {
            'description': 'مدیر فروشگاه',
            'permissions': [
                'product_management',
                'category_management',
                'report_management',
                'discount_management',
                'inventory_management',
                'barcode_management',
                'view_dashboard'
            ]
        },
        'user': {
            'description': 'کاربر عادی',
            'permissions': [
                'product_view',  # مشاهده محصولات
                'inventory_view',  # مشاهده موجودی
                'barcode_view'  # مشاهده بارکدها
            ]
        }
    }
    
    @staticmethod
    def has_permission(user_role, permission):
        """بررسی دسترسی کاربر به یک عملیات خاص
        
        Args:
            user_role (str): نقش کاربر (admin, manager, user)
            permission (str): دسترسی مورد نظر
            
        Returns:
            bool: True اگر کاربر دسترسی داشته باشد، False در غیر این صورت
        """
        if user_role not in AccessControl.ROLES:
            return False
            
        return permission in AccessControl.ROLES[user_role]['permissions']
    
    @staticmethod
    def get_role_permissions(role):
        """دریافت لیست دسترسی‌های یک نقش
        
        Args:
            role (str): نقش کاربر
            
        Returns:
            list: لیست دسترسی‌های نقش
        """
        if role not in AccessControl.ROLES:
            return []
            
        return AccessControl.ROLES[role]['permissions']
    
    @staticmethod
    def get_role_description(role):
        """دریافت توضیحات یک نقش
        
        Args:
            role (str): نقش کاربر
            
        Returns:
            str: توضیحات نقش
        """
        if role not in AccessControl.ROLES:
            return "نقش نامشخص"
            
        return AccessControl.ROLES[role]['description']
    
    @staticmethod
    def get_all_roles():
        """دریافت لیست تمام نقش‌ها
        
        Returns:
            dict: دیکشنری نقش‌ها
        """
        return AccessControl.ROLES