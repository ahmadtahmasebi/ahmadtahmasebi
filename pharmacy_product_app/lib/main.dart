import 'package:flutter/material.dart';
import 'src/screens/tabs/medicines_screen.dart';
import 'src/screens/tabs/cosmetics_screen.dart';
import 'src/screens/tabs/herbal_screen.dart';
import 'src/screens/tabs/supplements_screen.dart';
import 'src/screens/tabs/news_articles_screen.dart';
import 'src/screens/tabs/settings_screen.dart';

void main() {
  runApp(MyApp());
}

class MyApp extends StatelessWidget {
  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Pharmacy App',
      theme: ThemeData(
        primarySwatch: Colors.teal,
        visualDensity: VisualDensity.adaptivePlatformDensity,
        fontFamily: 'Vazir', // Assuming a Persian font might be needed
      ),
      home: MainAppShell(),
      debugShowCheckedModeBanner: false,
    );
  }
}

class MainAppShell extends StatefulWidget {
  @override
  _MainAppShellState createState() => _MainAppShellState();
}

class _MainAppShellState extends State<MainAppShell> {
  int _selectedIndex = 0;

  static List<Widget> _widgetOptions = <Widget>[
    MedicinesScreen(),
    CosmeticsScreen(),
    HerbalScreen(),
    SupplementsScreen(),
    NewsArticlesScreen(),
    SettingsScreen(),
  ];

  void _onItemTapped(int index) {
    setState(() {
      _selectedIndex = index;
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: _widgetOptions.elementAt(_selectedIndex),
      ),
      bottomNavigationBar: BottomNavigationBar(
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(
            icon: Icon(Icons.medical_services),
            label: 'دارو',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.face_retouching_natural),
            label: 'آرایشی',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.eco),
            label: 'گیاهی',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.health_and_safety),
            label: 'مکمل ها',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.article),
            label: 'اخبار',
          ),
          BottomNavigationBarItem(
            icon: Icon(Icons.settings),
            label: 'تنظیمات',
          ),
        ],
        currentIndex: _selectedIndex,
        selectedItemColor: Colors.teal,
        unselectedItemColor: Colors.grey,
        showUnselectedLabels: true,
        onTap: _onItemTapped,
        type: BottomNavigationBarType.fixed, // Ensures all labels are visible
      ),
    );
  }
}
