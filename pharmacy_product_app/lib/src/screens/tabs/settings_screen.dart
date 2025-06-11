import 'package:flutter/material.dart';
import '../admin_panel_screen.dart';
import '../auth/login_screen.dart'; // Import LoginScreen
import '../auth/registration_screen.dart'; // Import RegistrationScreen

class SettingsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('تنظیمات')),
      body: ListView( // Changed to ListView for more items
        padding: EdgeInsets.all(8.0),
        children: <Widget>[
          ListTile(
            leading: Icon(Icons.admin_panel_settings),
            title: Text('Admin Panel'),
            trailing: Icon(Icons.arrow_forward_ios),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => AdminPanelScreen()),
              );
            },
          ),
          Divider(),
          ListTile(
            leading: Icon(Icons.login),
            title: Text('ورود کاربر (Login)'),
            trailing: Icon(Icons.arrow_forward_ios),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => LoginScreen()),
              );
            },
          ),
          ListTile(
            leading: Icon(Icons.person_add_alt_1),
            title: Text('ثبت نام کاربر (Register)'),
            trailing: Icon(Icons.arrow_forward_ios),
            onTap: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (context) => RegistrationScreen()),
              );
            },
          ),
          Divider(),
          // Add other settings items here later
          ListTile(
            title: Text('نسخه برنامه: 1.0.0 (in-memory)'),
            enabled: false,
          ),
        ],
      ),
    );
  }
}
