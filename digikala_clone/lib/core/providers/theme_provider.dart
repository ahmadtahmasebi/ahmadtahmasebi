import 'package:flutter/material.dart';
import 'package:shared_preferences/shared_preferences.dart';

class ThemeProvider extends ChangeNotifier {
  static const String _kThemePreference = 'theme_preference';
  ThemeMode _themeMode = ThemeMode.system;

  ThemeMode get themeMode => _themeMode;

  ThemeProvider() {
    loadThemeMode();
  }

  Future<void> loadThemeMode() async {
    final prefs = await SharedPreferences.getInstance();
    final themePreference = prefs.getString(_kThemePreference);
    switch (themePreference) {
      case 'light':
        _themeMode = ThemeMode.light;
        break;
      case 'dark':
        _themeMode = ThemeMode.dark;
        break;
      case 'system':
      default:
        _themeMode = ThemeMode.system;
        break;
    }
    notifyListeners();
  }

  Future<void> setThemeMode(ThemeMode mode) async {
    if (_themeMode == mode) return;
    _themeMode = mode;

    final prefs = await SharedPreferences.getInstance();
    String themePreference;
    switch (mode) {
      case ThemeMode.light:
        themePreference = 'light';
        break;
      case ThemeMode.dark:
        themePreference = 'dark';
        break;
      case ThemeMode.system:
      default:
        themePreference = 'system';
        break;
    }
    await prefs.setString(_kThemePreference, themePreference);
    notifyListeners();
  }
}
