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
  String _selectedRole = 'user'; // Default role for new users
  User? _selectedUser;

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
    _selectedUser = user;
    _usernameController.text = user?.username ?? '';
    _emailController.text = user?.email ?? '';
    _selectedRole = user?.role ?? 'user';

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return StatefulBuilder(builder: (context, setDialogState) {
          return AlertDialog(
            title: Text(user == null ? 'افزودن کاربر جدید' : 'ویرایش کاربر'),
            content: SingleChildScrollView(
              child: Column(
                mainAxisSize: MainAxisSize.min,
                children: <Widget>[
                  TextField(
                    controller: _usernameController,
                    decoration: InputDecoration(labelText: 'نام کاربری'),
                  ),
                  TextField(
                    controller: _emailController,
                    decoration: InputDecoration(labelText: 'ایمیل (اختیاری)'),
                    keyboardType: TextInputType.emailAddress,
                  ),
                  SizedBox(height: 10),
                  DropdownButtonFormField<String>(
                    decoration: InputDecoration(labelText: 'نقش کاربر'),
                    value: _selectedRole,
                    items: ['user', 'admin'].map((String role) {
                      return DropdownMenuItem<String>(
                        value: role,
                        child: Text(role),
                      );
                    }).toList(),
                    onChanged: (String? newValue) {
                      if (newValue != null) {
                        setDialogState(() {
                           _selectedRole = newValue;
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
                  final String actionMessage;
                  if (user == null) {
                    // Placeholder for adding user
                    actionMessage = 'User Add (Placeholder): ${_usernameController.text}';
                    // User newUser = User(id: DateTime.now().millisecondsSinceEpoch.toString(), username: _usernameController.text, email: _emailController.text, role: _selectedRole);
                    // _userService.addUser(newUser); // This service method is a placeholder
                  } else {
                    // Placeholder for updating user
                    actionMessage = 'User Update (Placeholder): ${_usernameController.text}';
                    // User updatedUser = User(id: _selectedUser!.id, username: _usernameController.text, email: _emailController.text, role: _selectedRole);
                    // _userService.updateUser(updatedUser); // This service method is a placeholder
                  }
                  ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('$actionMessage - Data not saved.')),
                  );
                  // _loadUsers(); // Call this if service actually modified data
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
    _selectedRole = 'user';
    _selectedUser = null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('مدیریت کاربران'),
        actions: [
          IconButton(
            icon: Icon(Icons.person_add_alt_1),
            onPressed: () => _showUserForm(),
            tooltip: 'افزودن کاربر جدید',
          ),
        ],
      ),
      body: _users.isEmpty
          ? Center(child: Text('کاربری برای نمایش وجود ندارد.'))
          : ListView.builder(
              itemCount: _users.length,
              itemBuilder: (context, index) {
                final user = _users[index];
                return Card(
                  margin: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  child: ListTile(
                    leading: Icon(user.role == 'admin' ? Icons.shield_alt_outlined : Icons.person_outline, color: user.role == 'admin' ? Colors.amber : Colors.blue),
                    title: Text(user.username, style: TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text('نقش: ${user.role} - ایمیل: ${user.email ?? "وارد نشده"}'),
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(
                          icon: Icon(Icons.edit_outlined, color: Colors.grey[700]),
                          onPressed: () => _showUserForm(user: user),
                        ),
                        IconButton(
                          icon: Icon(Icons.delete_outline, color: Colors.red[700]),
                          onPressed: () {
                            _userService.deleteUser(user.id); // This is a placeholder
                            ScaffoldMessenger.of(context).showSnackBar(
                              SnackBar(content: Text('حذف کاربر ${user.username} به صورت نمایشی انجام شد (ذخیره نمی‌شود).')),
                            );
                            // _loadUsers(); // To reflect change if deleteUser was functional
                          },
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
