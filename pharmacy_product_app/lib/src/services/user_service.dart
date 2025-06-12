import '../models/user_model.dart';
import 'dart:math';

class UserService {
  final List<User> _users = [
    User(id: 'user_1', username: 'admin_user', email: 'admin@example.com', role: 'admin'),
    User(id: 'user_2', username: 'sample_user_1', email: 'user1@example.com', role: 'user'),
    User(id: 'user_3', username: 'sample_user_2', email: 'user2@example.com', role: 'user'),
  ];
  final Random _random = Random();

  List<User> getAllUsers() {
    return List.from(_users);
  }

  // Actually add user to the in-memory list
  void addUser(User user) {
    // Ensure unique ID
    String newId = user.id;
    if (newId.isEmpty || _users.any((u) => u.id == newId)) {
      newId = 'user_mem_${(_random.nextInt(99999) + _users.length + 1).toString()}';
    }

    // Check for duplicate username (optional, good practice)
    if (_users.any((u) => u.username.toLowerCase() == user.username.toLowerCase())) {
      print('UserService: Username "${user.username}" already exists.');
      // Optionally throw an error or return a status to be handled by UI
      return;
    }

    final newUser = User(
      id: newId,
      username: user.username,
      email: user.email,
      role: user.role,
    );
    _users.add(newUser);
    print('UserService: User "${newUser.username}" added to in-memory list.');
  }

  // Actually update user in the in-memory list
  void updateUser(User user) {
    final index = _users.indexWhere((u) => u.id == user.id);
    if (index != -1) {
      // Check if new username conflicts with another existing user (excluding self)
      if (_users.any((u) => u.username.toLowerCase() == user.username.toLowerCase() && u.id != user.id)) {
          print('UserService: Updated username "${user.username}" conflicts with another user.');
          // Optionally throw an error or return a status to be handled by UI
          return;
      }
      _users[index] = user;
      print('UserService: User "${user.username}" updated in in-memory list.');
    } else {
      print('UserService: User with ID "${user.id}" not found for update.');
    }
  }

  // Actually delete user from the in-memory list
  void deleteUser(String userId) {
    final initialLength = _users.length;
    _users.removeWhere((u) => u.id == userId);
    if (_users.length < initialLength) {
      print('UserService: User with ID "$userId" deleted from in-memory list.');
    } else {
      print('UserService: User with ID "$userId" not found for deletion.');
    }
  }

  User? getUserById(String userId) {
    try {
      return _users.firstWhere((u) => u.id == userId);
    } catch (e) {
      return null;
    }
  }
}
