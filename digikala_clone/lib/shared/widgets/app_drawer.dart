import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../../core/services/auth_service.dart';
import '../../features/favorites/screens/favorites_screen.dart';
import '../../features/settings/screens/settings_screen.dart';
import '../../features/user_profile/screens/user_profile_screen.dart';
import '../../features/admin/screens/admin_home_screen.dart'; // Import AdminHomeScreen

class AppDrawer extends StatefulWidget {
  const AppDrawer({Key? key}) : super(key: key);

  @override
  _AppDrawerState createState() => _AppDrawerState();
}

class _AppDrawerState extends State<AppDrawer> {
  final AuthService _authService = AuthService();
  User? _currentUser;
  bool _isAdmin = false;

  @override
  void initState() {
    super.initState();
    _currentUser = _authService.currentUser;
    if (_currentUser != null) {
      _checkAdminStatus();
    }
  }

  Future<void> _checkAdminStatus() async {
    bool isAdmin = await _authService.isAdminCheck();
    if (mounted) {
      setState(() {
        _isAdmin = isAdmin;
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    // Listen to auth state changes to update drawer if user logs in/out while drawer is open or for next open
    // This can also be handled by a top-level provider if AuthService state is managed there.
    // For simplicity here, we re-check on build if currentUser changed.
    final User? latestUser = _authService.currentUser;
    if (_currentUser?.uid != latestUser?.uid) {
      _currentUser = latestUser;
      if (_currentUser != null) {
        _checkAdminStatus();
      } else {
        _isAdmin = false; // Reset if user logged out
      }
    }


    return Drawer(
      child: ListView(
        padding: EdgeInsets.zero,
        children: <Widget>[
          UserAccountsDrawerHeader(
            decoration: BoxDecoration(
              color: Colors.red[700],
            ),
            accountName: Text(
              _currentUser?.displayName ?? 'کاربر مهمان',
              style: const TextStyle(fontFamily: 'IranYekan', color: Colors.white, fontSize: 18),
            ),
            accountEmail: Text(
              _currentUser?.email ?? 'وارد نشده',
              style: const TextStyle(fontFamily: 'IranYekan', color: Colors.white70),
            ),
            currentAccountPicture: CircleAvatar(
              backgroundColor: Colors.white,
              backgroundImage: _currentUser?.photoURL != null ? NetworkImage(_currentUser!.photoURL!) : null,
              child: _currentUser?.photoURL == null
                  ? Icon(Icons.person, size: 40, color: Colors.red[700])
                  : null,
            ),
            onDetailsPressed: _currentUser != null ? () {
              Navigator.pop(context);
              Navigator.push(context, MaterialPageRoute(builder: (_) => const UserProfileScreen()));
            } : null,
          ),
          _buildListTile(
            context: context,
            icon: Icons.home_outlined,
            title: 'صفحه اصلی',
            onTapAction: () {
              // Usually, just closing drawer is enough if already on home, or use Navigator.pushNamed('/')
            },
          ),
          _buildListTile(
            context: context,
            icon: Icons.category_outlined,
            title: 'دسته بندی ها',
            onTapAction: () {
               print('Tapped on دسته بندی ها');
            },
          ),
          const Divider(),
          _buildListTile(
            context: context,
            icon: Icons.favorite_border,
            title: 'علاقه‌مندی‌ها',
            onTapAction: () {
              if (_currentUser != null) {
                Navigator.push(
                  context,
                  MaterialPageRoute(builder: (_) => const FavoritesScreen()),
                );
              } else {
                 ScaffoldMessenger.of(context).showSnackBar(
                  const SnackBar(content: Text('برای مشاهده علاقه‌مندی‌ها ابتدا وارد شوید.', style: TextStyle(fontFamily: 'IranYekan'))),
                );
              }
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
          if (_isAdmin) ...[ // Conditionally show Admin Panel link
            const Divider(),
            _buildListTile(
              context: context,
              icon: Icons.admin_panel_settings_outlined,
              title: 'پنل مدیریت',
              onTapAction: () {
                Navigator.push(context, MaterialPageRoute(builder: (_) => const AdminHomeScreen()));
              },
            ),
          ],
          if (_currentUser != null) ...[
            const Divider(),
            _buildListTile(
              context: context,
              icon: Icons.exit_to_app,
              title: 'خروج از حساب',
              onTapAction: () async {
                await _authService.signOut();
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
        Navigator.pop(context);
        onTapAction();
      },
    );
  }
}
