import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import 'package:provider/provider.dart'; // To potentially provide AuthService if needed, or instantiate directly
import '../../../core/services/auth_service.dart'; // Import AuthService
import '../../home/screens/home_screen.dart'; // Import HomeScreen
import '../screens/authentication_screen.dart'; // Placeholder for AuthenticationScreen

class AuthWrapper extends StatelessWidget {
  const AuthWrapper({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    // Using a direct instance of AuthService here for simplicity.
    // In a larger app, you might provide this using Provider higher up the widget tree.
    final authService = AuthService();

    return StreamBuilder<User?>(
      stream: authService.authStateChanges,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Scaffold(
            body: Center(child: CircularProgressIndicator()),
          );
        }
        if (snapshot.hasData && snapshot.data != null) {
          // User is logged in
          return const HomeScreen();
        } else {
          // User is logged out
          return const AuthenticationScreen(); // This screen will be created next
        }
      },
    );
  }
}
