import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart'; // Import FirebaseAuth
import '../../core/services/auth_service.dart'; // Import AuthService
import '../../features/favorites/screens/favorites_screen.dart';
import '../../features/settings/screens/settings_screen.dart';

class AppDrawer extends StatelessWidget {
  const AppDrawer({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Using AuthService directly for currentUser.
    // In a larger app, this might be accessed via Provider.
    final AuthService authService = AuthService();
    final User? currentUser = authService.currentUser;

    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: <Widget>[
          DrawerHeader(
            decoration: BoxDecoration(
              color: Colors.red[700],
            ),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              mainAxisAlignment: MainAxisAlignment.end,
              children: [
                const Text(
                  'داروخانه آنلاین',
                  style: TextStyle(
                    color: Colors.white,
                    fontSize: 24,
                    fontFamily: 'IranYekan',
                  ),
                ),
                if (currentUser != null) ...[
                  const SizedBox(height: 4),
                  Text(
                    currentUser.email ?? currentUser.displayName ?? 'کاربر وارد شده',
                    style: const TextStyle(
                      color: Colors.white70,
                      fontSize: 14,
                      fontFamily: 'IranYekan',
                    ),
                  ),
                ],
              ],
            )
          ),
          _buildListTile(
            context: context,
            icon: Icons.home_outlined, // Changed for Home
            title: 'صفحه اصلی',
            onTapAction: () {
              // Assuming HomeScreen is the main page after login (handled by AuthWrapper)
              // If already on HomeScreen, just close drawer.
              // If not, and we want explicit navigation:
              // Navigator.pushReplacement(context, MaterialPageRoute(builder: (_) => const HomeScreen()));
              print('Tapped on صفحه اصلی');
            },
          ),
          _buildListTile(
            context: context,
            icon: Icons.local_pharmacy_outlined,
            title: 'دارویی',
            onTapAction: () {
              print('Tapped on دارویی - Navigating to /pharmaceuticals');
              // TODO: Navigate to relevant tab or screen
            },
          ),
          _buildListTile(
            context: context,
            icon: Icons.brush_outlined,
            title: 'آرایشی',
            onTapAction: () {
              print('Tapped on آرایشی - Navigating to /cosmetics');
              // TODO: Navigate to relevant tab or screen
            },
          ),
          // ... other category ListTiles ...
          const Divider(),
          _buildListTile(
            context: context,
            icon: Icons.favorite_border,
            title: 'علاقه‌مندی‌ها',
            onTapAction: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const FavoritesScreen()),
              );
            },
          ),
          _buildListTile(
            context: context,
            icon: Icons.settings_outlined,
            title: 'تنظیمات',
            onTapAction: () {
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const SettingsScreen()),
              );
            },
          ),
          if (currentUser != null) ...[
            const Divider(),
            _buildListTile(
              context: context,
              icon: Icons.exit_to_app,
              title: 'خروج از حساب',
              onTapAction: () async {
                await authService.signOut();
                // AuthWrapper will handle navigation to AuthenticationScreen
              },
            ),
          ],
        ],
      ),
    );
  }

  Widget _buildListTile({
    required BuildContext context,
    required IconData icon,
    required String title,
    required VoidCallback onTapAction,
  }) {
    return ListTile(
      leading: Icon(icon),
      title: Text(title, style: const TextStyle(fontFamily: 'IranYekan')),
      onTap: () {
        Navigator.pop(context); // Close the drawer first
        onTapAction();
      },
    );
  }
}
