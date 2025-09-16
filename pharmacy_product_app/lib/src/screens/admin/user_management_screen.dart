import 'package:flutter/material.dart';
import '../../models/user_model.dart';
import '../../services/user_service.dart';

final UserService _userService = UserService();

class UserManagementScreen extends StatefulWidget {
  @override
  _UserManagementScreenState createState() => _UserManagementScreenState();
}

class _UserManagementScreenState extends State<UserManagementScreen> {
  List<User> _users = [];
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  // String _selectedRole = 'user'; // This will be managed by dialog's local state
  User? _editingUser;

  @override
  void initState() {
    super.initState();
    _loadUsers();
  }

  void _loadUsers() {
    if (mounted) {
      setState(() {
        _users = _userService.getAllUsers();
      });
    }
  }

  void _showUserForm({User? user}) {
    _editingUser = user;
    _usernameController.text = user?.username ?? '';
    _emailController.text = user?.email ?? '';
    // Use user's role for dialog, or default to 'user' for new.
    String dialogSelectedRole = user?.role ?? 'user';

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(builder: (context, setDialogState) { // Use StatefulBuilder for dialog's own state
          return AlertDialog(
            title: Text(user == null ? 'افزودن کاربر جدید' : 'ویرایش کاربر: ${user!.username}'),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: <Widget>[
                  TextField(
                    controller: _usernameController,
                    decoration: InputDecoration(labelText: 'نام کاربری'),
                  ),
                  SizedBox(height: 10),
                  TextField(
                    controller: _emailController,
                    decoration: InputDecoration(labelText: 'ایمیل (اختیاری)'),
                    keyboardType: TextInputType.emailAddress,
                  ),
                  SizedBox(height: 10),
                  DropdownButtonFormField<String>(
                    decoration: InputDecoration(labelText: 'نقش کاربر'),
                    value: dialogSelectedRole,
                    items: ['user', 'admin'].map((String role) {
                      return DropdownMenuItem<String>(
                        value: role,
                        child: Text(role),
                      );
                    }).toList(),
                    onChanged: (String? newValue) {
                      if (newValue != null) {
                        setDialogState(() {
                           dialogSelectedRole = newValue;
                        });
                      }
                    },
                  ),
                ],
              ),
            ),
            actions: <Widget>[
              TextButton(
                child: Text('انصراف'),
                onPressed: () {
                  Navigator.of(context).pop();
                  _clearForm();
                },
              ),
              ElevatedButton(
                child: Text(user == null ? 'افزودن' : 'ذخیره تغییرات'),
                onPressed: () {
                  if (_usernameController.text.isEmpty) {
                     ScaffoldMessenger.of(context).showSnackBar(
                       SnackBar(content: Text('نام کاربری نمی‌تواند خالی باشد!')),
                     );
                     return;
                  }

                  final String finalRole = dialogSelectedRole;

                  if (_editingUser == null) {
                    final newUser = User(
                      id: '',
                      username: _usernameController.text,
                      email: _emailController.text.isNotEmpty ? _emailController.text : null,
                      role: finalRole,
                    );
                    _userService.addUser(newUser);
                    ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('کاربر "${newUser.username}" اضافه شد.')),
                    );
                  } else {
                    final updatedUser = User(
                      id: _editingUser!.id,
                      username: _usernameController.text,
                      email: _emailController.text.isNotEmpty ? _emailController.text : null,
                      role: finalRole,
                    );
                    _userService.updateUser(updatedUser);
                     ScaffoldMessenger.of(context).showSnackBar(
                      SnackBar(content: Text('کاربر "${updatedUser.username}" به‌روزرسانی شد.')),
                    );
                  }
                  _loadUsers();
                  Navigator.of(context).pop();
                  _clearForm();
                },
              ),
            ],
          );
        });
      },
    );
  }

  void _clearForm() {
    _usernameController.clear();
    _emailController.clear();
    // _selectedRole = 'user'; // No longer needed here, dialog manages its own role state
    _editingUser = null;
  }

  void _confirmDeleteUser(User user) {
    showDialog(
        context: context,
        builder: (BuildContext context) {
          return AlertDialog(
            title: Text('تایید حذف'),
            content: Text('آیا از حذف کاربر "${user.username}" اطمینان دارید؟ این عمل قابل بازگشت نیست.'),
            actions: <Widget>[
              TextButton(child: Text('انصراف'), onPressed: () => Navigator.of(context).pop()),
              TextButton(
                child: Text('حذف', style: TextStyle(color: Colors.red)),
                onPressed: () {
                  _userService.deleteUser(user.id);
                  _loadUsers();
                  Navigator.of(context).pop();
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('کاربر "${user.username}" حذف شد.')),
                  );
                },
              ),
            ],
          );
        });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('مدیریت کاربران'),
        actions: [
          IconButton(
            icon: Icon(Icons.person_add_alt_1_outlined),
            onPressed: () => _showUserForm(),
            tooltip: 'افزودن کاربر جدید',
          ),
        ],
      ),
      body: _users.isEmpty
          ? Center(child: Text('کاربری برای نمایش وجود ندارد. برای افزودن، روی + کلیک کنید.'))
          : ListView.builder(
              padding: EdgeInsets.all(8.0),
              itemCount: _users.length,
              itemBuilder: (context, index) {
                final user = _users[index];
                return Card(
                  elevation: 1.5,
                  margin: EdgeInsets.symmetric(vertical: 4),
                  child: ListTile(
                    leading: Icon(
                      user.role == 'admin' ? Icons.shield_outlined : Icons.person_outline,
                      color: user.role == 'admin' ? Colors.amber.shade700 : Theme.of(context).primaryColor,
                      size: 30,
                    ),
                    title: Text(user.username, style: TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text('نقش: ${user.role}  |  ایمیل: ${user.email ?? "ثبت نشده"}'),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: Icon(Icons.edit_outlined, color: Colors.grey[700], size: 20),
                          onPressed: () => _showUserForm(user: user),
                          tooltip: 'ویرایش کاربر',
                        ),
                        IconButton(
                          icon: Icon(Icons.delete_outline, color: Colors.red.shade700, size: 20),
                          onPressed: () => _confirmDeleteUser(user),
                          tooltip: 'حذف کاربر',
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showUserForm(),
        tooltip: 'افزودن کاربر جدید',
        child: Icon(Icons.add),
      ),
    );
  }
}
