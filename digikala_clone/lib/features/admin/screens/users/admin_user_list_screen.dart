import 'package:flutter/material.dart';
import '../../../../core/services/admin_user_service.dart';

// A simple data class to represent user data in the UI
class AdminUserView {
  final String uid;
  final String? email;
  final String? displayName;
  bool disabled;
  bool isAdmin;

  AdminUserView({
    required this.uid,
    this.email,
    this.displayName,
    required this.disabled,
    required this.isAdmin,
  });

  factory AdminUserView.fromMap(Map<String, dynamic> data) {
    return AdminUserView(
      uid: data['uid'] ?? '',
      email: data['email'] as String?,
      displayName: data['displayName'] as String?,
      disabled: data['disabled'] as bool? ?? false,
      isAdmin: (data['customClaims'] as Map<String, dynamic>?)?['isAdmin'] as bool? ?? false,
    );
  }
}

class AdminUserListScreen extends StatefulWidget {
  const AdminUserListScreen({Key? key}) : super(key: key);

  @override
  _AdminUserListScreenState createState() => _AdminUserListScreenState();
}

class _AdminUserListScreenState extends State<AdminUserListScreen> {
  final AdminUserService _adminUserService = AdminUserService();
  late Future<List<AdminUserView>> _usersFuture;

  @override
  void initState() {
    super.initState();
    _loadUsers();
  }

  void _loadUsers() {
    setState(() {
      _usersFuture = _adminUserService.listUsers().then(
        (usersData) => usersData.map((data) => AdminUserView.fromMap(data)).toList()
      );
    });
  }

  Future<void> _toggleDisabledStatus(AdminUserView user) async {
    bool newDisabledStatus = !user.disabled;
    // Optimistically update UI (optional, but good for responsiveness)
    // setState(() => user.disabled = newDisabledStatus);
    try {
      await _adminUserService.setUserDisabled(user.uid, newDisabledStatus);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('وضعیت کاربر ${user.email} به ${newDisabledStatus ? "غیرفعال" : "فعال"} تغییر کرد.', style: const TextStyle(fontFamily: 'IranYekan'))),
      );
    } catch (e) {
      // Revert optimistic update if error
      // setState(() => user.disabled = !newDisabledStatus);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('خطا در تغییر وضعیت کاربر: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
      );
    } finally {
       _loadUsers(); // Refresh list from source
    }
  }

  Future<void> _toggleAdminStatus(AdminUserView user) async {
    bool newAdminStatus = !user.isAdmin;
    // Optimistically update UI
    // setState(() => user.isAdmin = newAdminStatus);
    try {
      await _adminUserService.setUserAdminStatus(user.uid, newAdminStatus);
       ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('${user.email} ${newAdminStatus ? "به ادمین تبدیل شد" : "از ادمین بودن حذف شد"}.', style: const TextStyle(fontFamily: 'IranYekan'))),
      );
    } catch (e) {
      // Revert optimistic update if error
      // setState(() => user.isAdmin = !newAdminStatus);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('خطا در تغییر نقش ادمین: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
      );
    } finally {
      _loadUsers(); // Refresh list from source
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('مدیریت کاربران', style: TextStyle(fontFamily: 'IranYekan')),
      ),
      body: FutureBuilder<List<AdminUserView>>(
        future: _usersFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('خطا در بارگذاری کاربران: ${snapshot.error}', style: const TextStyle(fontFamily: 'IranYekan')));
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('کاربری یافت نشد.', style: TextStyle(fontFamily: 'IranYekan')));
          }

          final users = snapshot.data!;

          return ListView.separated(
            itemCount: users.length,
            separatorBuilder: (context, index) => const Divider(),
            itemBuilder: (context, index) {
              final user = users[index];
              return ListTile(
                title: Text(user.displayName ?? user.email ?? user.uid, style: const TextStyle(fontFamily: 'IranYekan', fontWeight: FontWeight.bold)),
                subtitle: Text('UID: ${user.uid}\nEmail: ${user.email ?? "N/A"}\nAdmin: ${user.isAdmin}, Disabled: ${user.disabled}', style: const TextStyle(fontFamily: 'IranYekan', fontSize: 12)),
                isThreeLine: true,
                trailing: PopupMenuButton<String>(
                  onSelected: (value) {
                    if (value == 'toggleDisabled') {
                      _toggleDisabledStatus(user);
                    } else if (value == 'toggleAdmin') {
                      _toggleAdminStatus(user);
                    }
                  },
                  itemBuilder: (BuildContext context) => <PopupMenuEntry<String>>[
                    PopupMenuItem<String>(
                      value: 'toggleDisabled',
                      child: Text(user.disabled ? 'فعال کردن' : 'غیرفعال کردن', style: const TextStyle(fontFamily: 'IranYekan')),
                    ),
                    PopupMenuItem<String>(
                      value: 'toggleAdmin',
                      child: Text(user.isAdmin ? 'حذف از ادمین' : 'اعطای نقش ادمین', style: const TextStyle(fontFamily: 'IranYekan')),
                    ),
                  ],
                ),
              );
            },
          );
        },
      ),
    );
  }
}
