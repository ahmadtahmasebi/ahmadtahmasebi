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
      title: 'داروخانه آنلاین', // Online Pharmacy
      theme: ThemeData(
        primarySwatch: Colors.blue,
        scaffoldBackgroundColor: Colors.white,
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.blue, // Primary color for AppBar
          foregroundColor: Colors.white, // Text/icon color on AppBar
          elevation: 1.0,
          titleTextStyle: TextStyle(fontFamily: 'Vazir', fontSize: 20, color: Colors.white, fontWeight: FontWeight.bold),
        ),
        bottomNavigationBarTheme: BottomNavigationBarThemeData(
          selectedItemColor: Colors.blue, // Selected item color
          unselectedItemColor: Colors.grey[600], // Unselected item color
          backgroundColor: Colors.white,
          elevation: 4.0,
          selectedLabelStyle: TextStyle(fontFamily: 'Vazir', fontWeight: FontWeight.normal, fontSize: 12),
          unselectedLabelStyle: TextStyle(fontFamily: 'Vazir', fontWeight: FontWeight.normal, fontSize: 12),
        ),
        colorScheme: ColorScheme.light(
          primary: Colors.blue, // Main primary color
          secondary: Colors.blueAccent, // Accent color
          onPrimary: Colors.white, // Text on primary color
          surface: Colors.white, // Card backgrounds, dialogs etc.
          onSurface: Colors.black87, // Text on surface
          background: Colors.white, // Overall background
        ),
        fontFamily: 'Vazir', // Default font for the app
        visualDensity: VisualDensity.adaptivePlatformDensity,
        chipTheme: ChipThemeData(
          backgroundColor: Colors.grey[200],
          disabledColor: Colors.grey.withOpacity(0.38),
          selectedColor: Colors.blue, // Selected FilterChips will be blue
          secondarySelectedColor: Colors.blueAccent,
          padding: EdgeInsets.symmetric(horizontal: 12.0, vertical: 8.0),
          labelStyle: TextStyle(color: Colors.black87, fontWeight: FontWeight.normal, fontFamily: 'Vazir'),
          secondaryLabelStyle: TextStyle(color: Colors.white, fontWeight: FontWeight.normal, fontFamily: 'Vazir'),
          brightness: Brightness.light,
        ),
        textTheme: TextTheme(
          headline5: TextStyle(fontFamily: 'Vazir', fontSize: 24, fontWeight: FontWeight.bold, color: Colors.black87),
          headline6: TextStyle(fontFamily: 'Vazir', fontSize: 20, fontWeight: FontWeight.bold, color: Colors.black87),
          subtitle1: TextStyle(fontFamily: 'Vazir', fontSize: 16, fontWeight: FontWeight.normal, color: Colors.black87),
          bodyText1: TextStyle(fontFamily: 'Vazir', fontSize: 14, color: Colors.black87, height: 1.5),
          bodyText2: TextStyle(fontFamily: 'Vazir', fontSize: 14, color: Colors.grey[700], height: 1.5),
          button: TextStyle(fontFamily: 'Vazir', fontWeight: FontWeight.bold, color: Colors.white, fontSize: 14),
        ),
        elevatedButtonTheme: ElevatedButtonThemeData(
            style: ElevatedButton.styleFrom(
                backgroundColor: Colors.blue, // Button background
                foregroundColor: Colors.white, // Button text/icon color
                textStyle: TextStyle(fontFamily: 'Vazir', fontWeight: FontWeight.bold, fontSize: 14),
                padding: EdgeInsets.symmetric(horizontal: 16, vertical: 12),
                shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8)),
            ),
        ),
        textButtonTheme: TextButtonThemeData(
            style: TextButton.styleFrom(
                foregroundColor: Colors.blue, // TextButton color
                textStyle: TextStyle(fontFamily: 'Vazir', fontWeight: FontWeight.bold),
            ),
        ),
        inputDecorationTheme: InputDecorationTheme(
            labelStyle: TextStyle(fontFamily: 'Vazir', color: Colors.blue),
            hintStyle: TextStyle(fontFamily: 'Vazir', color: Colors.grey[500]),
            border: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8.0),
                borderSide: BorderSide(color: Colors.grey[400]!),
            ),
            enabledBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8.0),
                borderSide: BorderSide(color: Colors.grey[400]!),
            ),
            focusedBorder: OutlineInputBorder(
                borderRadius: BorderRadius.circular(8.0),
                borderSide: BorderSide(color: Colors.blue, width: 2.0),
            ),
            filled: false, // Changed to false for a cleaner look, or use very light grey
            // fillColor: Colors.grey[50],
        ),
        cardTheme: CardTheme(
          elevation: 1.5,
          shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(8.0)),
          margin: EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
        )
      ),
      home: MainAppShell(),
      debugShowCheckedModeBanner: false,
      // localizationsDelegates: [
      //   GlobalMaterialLocalizations.delegate,
      //   GlobalWidgetsLocalizations.delegate,
      //   GlobalCupertinoLocalizations.delegate,
      // ],
      // supportedLocales: [
      //   const Locale('fa', ''), // Farsi
      //   const Locale('en', ''), // English
      // ],
      // locale: const Locale('fa', ''), // Default to Farsi
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
    if (mounted) {
      setState(() {
        _selectedIndex = index;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: _widgetOptions.elementAt(_selectedIndex),
      ),
      bottomNavigationBar: BottomNavigationBar(
        items: const <BottomNavigationBarItem>[
          BottomNavigationBarItem(icon: Icon(Icons.medical_services_outlined), activeIcon: Icon(Icons.medical_services), label: 'دارو'),
          BottomNavigationBarItem(icon: Icon(Icons.face_retouching_natural_outlined), activeIcon: Icon(Icons.face_retouching_natural), label: 'آرایشی'),
          BottomNavigationBarItem(icon: Icon(Icons.eco_outlined), activeIcon: Icon(Icons.eco), label: 'گیاهی'),
          BottomNavigationBarItem(icon: Icon(Icons.health_and_safety_outlined), activeIcon: Icon(Icons.health_and_safety), label: 'مکمل ها'),
          BottomNavigationBarItem(icon: Icon(Icons.article_outlined), activeIcon: Icon(Icons.article), label: 'اخبار'),
          BottomNavigationBarItem(icon: Icon(Icons.settings_outlined), activeIcon: Icon(Icons.settings), label: 'تنظیمات'),
        ],
        currentIndex: _selectedIndex,
        showUnselectedLabels: true, // Ensure labels are always visible
        onTap: _onItemTapped,
        type: BottomNavigationBarType.fixed, // Good for 3-5 items. If more, consider scrolling or other patterns.
      ),
    );
  }
}
