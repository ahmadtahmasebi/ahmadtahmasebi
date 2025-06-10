import 'package:flutter/material.dart';
import '../admin_panel_screen.dart'; // Corrected import path

class SettingsScreen extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('تنظیمات')),
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: <Widget>[
            Text('Settings Screen Content'),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: () {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (context) => AdminPanelScreen())
                );
              },
              child: Text('Open Admin Panel'),
            ),
          ],
        ),
      ),
    );
  }
}
