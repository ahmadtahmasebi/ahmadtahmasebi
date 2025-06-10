import 'package:flutter/material.dart';
import 'admin/category_management_screen.dart';
import 'admin/product_management_screen.dart';
import 'admin/article_management_screen.dart'; // Import new screen

class AdminPanelScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Admin Panel'),
      ),
      body: ListView(
        children: <Widget>[
          ListTile(
            leading: Icon(Icons.category),
            title: Text('Manage Categories'),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => CategoryManagementScreen()),
              );
            },
          ),
          ListTile(
            leading: Icon(Icons.shopping_bag),
            title: Text('Manage Products'),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => ProductManagementScreen()),
              );
            },
          ),
          ListTile(
            leading: Icon(Icons.article),
            title: Text('Manage Articles'),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => ArticleManagementScreen()),
              );
            },
          ),
        ],
      ),
    );
  }
}
