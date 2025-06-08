import 'package:flutter/material.dart';
import 'package:provider/provider.dart';
import '../../../core/providers/theme_provider.dart';

class SettingsScreen extends StatelessWidget {
  const SettingsScreen({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('تنظیمات', style: TextStyle(fontFamily: 'IranYekan')),
        // backgroundColor will be inherited from ThemeData.appBarTheme
      ),
      body: ListView(
        children: <Widget>[
          ListTile(
            title: const Text('حالت تم', style: TextStyle(fontFamily: 'IranYekan')),
            trailing: DropdownButton<ThemeMode>(
              value: themeProvider.themeMode,
              items: const [
                DropdownMenuItem(
                  value: ThemeMode.system,
                  child: Text('سیستم', style: TextStyle(fontFamily: 'IranYekan')),
                ),
                DropdownMenuItem(
                  value: ThemeMode.light,
                  child: Text('روشن', style: TextStyle(fontFamily: 'IranYekan')),
                ),
                DropdownMenuItem(
                  value: ThemeMode.dark,
                  child: Text('تیره', style: TextStyle(fontFamily: 'IranYekan')),
                ),
              ],
              onChanged: (ThemeMode? mode) {
                if (mode != null) {
                  themeProvider.setThemeMode(mode);
                }
              },
            ),
          ),
          const Divider(),
          _buildPlaceholderTile(context, 'تنظیمات اعلان‌ها', Icons.notifications_outlined),
          _buildPlaceholderTile(context, 'زبان', Icons.language_outlined),
          _buildPlaceholderTile(context, 'درباره ما', Icons.info_outline_rounded),
        ],
      ),
    );
  }

  Widget _buildPlaceholderTile(BuildContext context, String title, IconData icon) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title, style: const TextStyle(fontFamily: 'IranYekan')),
      onTap: () {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(
            content: Text('$title - هنوز پیاده‌سازی نشده است', style: const TextStyle(fontFamily: 'IranYekan')),
            duration: const Duration(seconds: 1),
          ),
        );
      },
    );
  }
}
