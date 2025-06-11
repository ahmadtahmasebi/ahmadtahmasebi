class User {
  String id;
  String username;
  String? email; // Optional
  String role; // e.g., 'admin', 'user'

  User({
    required this.id,
    required this.username,
    this.email,
    required this.role,
  });
}
