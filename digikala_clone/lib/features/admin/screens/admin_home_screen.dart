import 'package:flutter/material.dart';
import 'products/admin_product_list_screen.dart';
import 'categories/admin_category_list_screen.dart';
import 'drugs/admin_drug_list_screen.dart';
import 'news_items/admin_news_item_list_screen.dart';
import 'users/admin_user_list_screen.dart';
import 'products/admin_product_excel_upload_screen.dart'; // Import the Excel upload screen

class AdminHomeScreen extends StatelessWidget {
  const AdminHomeScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('پنل مدیریت', style: TextStyle(fontFamily: 'IranYekan')),
        backgroundColor: Colors.indigo,
      ),
      body: ListView(
        padding: const EdgeInsets.all(16.0),
        children: <Widget>[
          const Center(
            child: Padding(
              padding: EdgeInsets.only(bottom: 20.0),
              child: Text(
                'به پنل مدیریت خوش آمدید!',
                style: TextStyle(fontSize: 20, fontFamily: 'IranYekan', fontWeight: FontWeight.bold),
              ),
            ),
          ),
          _buildAdminMenuItem(
            context: context,
            title: 'مدیریت محصولات',
            icon: Icons.shopping_bag_outlined,
            color: Colors.indigo,
            screen: const AdminProductListScreen(),
          ),
          _buildAdminMenuItem( // Added for Excel Upload
            context: context,
            title: 'آپلود محصولات با اکسل',
            icon: Icons.file_upload_outlined,
            color: Colors.blueGrey, // Different color
            screen: const AdminProductExcelUploadScreen(),
          ),
          _buildAdminMenuItem(
            context: context,
            title: 'مدیریت دسته‌بندی‌ها',
            icon: Icons.category_outlined,
            color: Colors.orange,
            screen: const AdminCategoryListScreen(),
          ),
          _buildAdminMenuItem(
            context: context,
            title: 'مدیریت داروها',
            icon: Icons.local_pharmacy_outlined,
            color: Colors.green,
            screen: const AdminDrugListScreen(),
          ),
          _buildAdminMenuItem(
            context: context,
            title: 'مدیریت اخبار و مقالات',
            icon: Icons.article_outlined,
            color: Colors.teal,
            screen: const AdminNewsItemListScreen(),
          ),
           _buildAdminMenuItem(
            context: context,
            title: 'مدیریت کاربران',
            icon: Icons.people_alt_outlined,
            color: Colors.purple,
            screen: const AdminUserListScreen(),
          ),
          // TODO: Add more admin sections here later
        ],
      ),
    );
  }

  Widget _buildAdminMenuItem({
    required BuildContext context,
    required String title,
    required IconData icon,
    required Color color,
    required Widget screen,
  }) {
    return Card(
      elevation: 2.0,
      margin: const EdgeInsets.symmetric(vertical: 6.0),
      child: ListTile(
        leading: Icon(icon, color: color, size: 30),
        title: Text(title, style: const TextStyle(fontFamily: 'IranYekan', fontSize: 18)),
        trailing: const Icon(Icons.arrow_forward_ios),
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(builder: (_) => screen),
          );
        },
      ),
    );
  }
}
