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

  // Placeholder methods - no actual data modification for now
  void addUser(User user) {
    // Simulate adding for UI feedback, but not persisting in this placeholder version
    // To make it persist for the session:
    // final newUser = User(
    //   id: user.id.isEmpty ? 'user_gen_${_random.nextInt(9999)}' : user.id,
    //   username: user.username,
    //   email: user.email,
    //   role: user.role
    // );
    // _users.add(newUser);
    print('Attempted to add user (placeholder): ${user.username}');
  }

  void updateUser(User user) {
    print('Attempted to update user (placeholder): ${user.username}');
    // final index = _users.indexWhere((u) => u.id == user.id);
    // if (index != -1) {
    //   _users[index] = user;
    // }
  }

  void deleteUser(String userId) {
    print('Attempted to delete user (placeholder): $userId');
    // _users.removeWhere((u) => u.id == userId);
  }

  User? getUserById(String userId) {
    try {
      return _users.firstWhere((u) => u.id == userId);
    } catch (e) {
      return null;
    }
  }
}
