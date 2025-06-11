import 'package:flutter/material.dart';
import 'admin/category_management_screen.dart';
import 'admin/product_management_screen.dart';
import 'admin/article_management_screen.dart';
import 'admin/admin_dashboard_screen.dart';
import 'admin/user_management_screen.dart'; // Import the new user management screen

class AdminPanelScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('پنل مدیریت (Admin Panel)'),
      ),
      body: ListView(
        padding: EdgeInsets.symmetric(vertical: 8.0),
        children: <Widget>[
          ListTile(
            leading: Icon(Icons.dashboard_outlined, color: Theme.of(context).primaryColor),
            title: Text('داشبورد آماری', style: TextStyle(fontWeight: FontWeight.w500)),
            trailing: Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => AdminDashboardScreen()),
              );
            },
          ),
          Divider(),
          ListTile(
            leading: Icon(Icons.category_outlined, color: Theme.of(context).primaryColor),
            title: Text('مدیریت دسته‌بندی‌ها', style: TextStyle(fontWeight: FontWeight.w500)),
            trailing: Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => CategoryManagementScreen()),
              );
            },
          ),
          ListTile(
            leading: Icon(Icons.shopping_bag_outlined, color: Theme.of(context).primaryColor),
            title: Text('مدیریت محصولات', style: TextStyle(fontWeight: FontWeight.w500)),
            trailing: Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => ProductManagementScreen()),
              );
            },
          ),
          ListTile(
            leading: Icon(Icons.article_outlined, color: Theme.of(context).primaryColor),
            title: Text('مدیریت مقالات', style: TextStyle(fontWeight: FontWeight.w500)),
            trailing: Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => ArticleManagementScreen()),
              );
            },
          ),
           Divider(),
           ListTile(
            leading: Icon(Icons.people_alt_outlined, color: Theme.of(context).primaryColor), // Updated color
            title: Text('مدیریت کاربران', style: TextStyle(fontWeight: FontWeight.w500)), // Updated text
            trailing: Icon(Icons.arrow_forward_ios, size: 16),
            onTap: () {
                 Navigator.push(
                    context,
                    MaterialPageRoute(builder: (context) => UserManagementScreen()),
                 );
            },
          ),
        ],
      ),
    );
  }
}
