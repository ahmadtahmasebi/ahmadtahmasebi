import 'package:flutter/material.dart';
import 'package:firebase_auth/firebase_auth.dart';
import '../../../core/services/auth_service.dart'; // Assuming AuthService is in core/services

class UserProfileScreen extends StatefulWidget {
  const UserProfileScreen({Key? key}) : super(key: key);

  @override
  _UserProfileScreenState createState() => _UserProfileScreenState();
}

class _UserProfileScreenState extends State<UserProfileScreen> {
  final AuthService _authService = AuthService();
  User? _currentUser;
  bool _isLoading = false;

  final _displayNameController = TextEditingController();
  final _formKey = GlobalKey<FormState>();

  @override
  void initState() {
    super.initState();
    _currentUser = _authService.currentUser;
    if (_currentUser != null) {
      _displayNameController.text = _currentUser!.displayName ?? '';
    }
  }

  @override
  void dispose() {
    _displayNameController.dispose();
    super.dispose();
  }

  Future<void> _updateDisplayName() async {
    if (!(_formKey.currentState?.validate() ?? false) || _currentUser == null) {
      return;
    }
    _formKey.currentState?.save();
    setState(() => _isLoading = true);

    try {
      await _currentUser!.updateDisplayName(_displayNameController.text.trim());
      // Refresh user data
      await _currentUser!.reload();
      _currentUser = _authService.currentUser; // Re-fetch to get updated user

      if (mounted) {
        setState(() {}); // Update UI with new display name
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('نام نمایشی با موفقیت بروزرسانی شد.', style: TextStyle(fontFamily: 'IranYekan'))),
        );
      }
    } on FirebaseAuthException catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('خطا در بروزرسانی نام: ${e.message}', style: const TextStyle(fontFamily: 'IranYekan'))),
      );
    } catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('خطایی رخ داد: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
      );
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('پروفایل کاربری', style: TextStyle(fontFamily: 'IranYekan')),
      ),
      body: _currentUser == null
          ? const Center(child: Text('کاربری یافت نشد. لطفا ابتدا وارد شوید.', style: TextStyle(fontFamily: 'IranYekan')))
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.center,
                  children: <Widget>[
                    CircleAvatar(
                      radius: 50,
                      backgroundImage: _currentUser!.photoURL != null
                          ? NetworkImage(_currentUser!.photoURL!)
                          : null,
                      child: _currentUser!.photoURL == null
                          ? const Icon(Icons.person, size: 50)
                          : null,
                    ),
                    const SizedBox(height: 16),
                    Text(
                      'ایمیل: ${_currentUser!.email ?? "نامشخص"}',
                      style: const TextStyle(fontSize: 16, fontFamily: 'IranYekan'),
                    ),
                    const SizedBox(height: 24),
                    TextFormField(
                      controller: _displayNameController,
                      decoration: const InputDecoration(
                        labelText: 'نام نمایشی',
                        border: OutlineInputBorder(),
                        hintText: 'نامی که به دیگران نمایش داده می‌شود',
                        hintStyle: TextStyle(fontFamily: 'IranYekan', fontSize: 14)
                      ),
                      style: const TextStyle(fontFamily: 'IranYekan'),
                      validator: (value) {
                        if (value == null || value.trim().isEmpty) {
                          return 'نام نمایشی نمی‌تواند خالی باشد.';
                        }
                        return null;
                      },
                    ),
                    const SizedBox(height: 20),
                    if (_isLoading)
                      const CircularProgressIndicator()
                    else
                      ElevatedButton(
                        onPressed: _updateDisplayName,
                        child: const Text('ذخیره نام نمایشی', style: TextStyle(fontFamily: 'IranYekan')),
                      ),
                    // TODO: Add more profile fields if needed (e.g., change password, etc.)
                  ],
                ),
              ),
            ),
    );
  }
}
