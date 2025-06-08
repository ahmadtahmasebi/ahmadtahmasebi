import 'package:flutter/material.dart';
import '../../../core/services/auth_service.dart';
import 'forgot_password_screen.dart'; // Import ForgotPasswordScreen

class AuthenticationScreen extends StatefulWidget {
  const AuthenticationScreen({Key? key}) : super(key: key);

  @override
  _AuthenticationScreenState createState() => _AuthenticationScreenState();
}

enum AuthMode { signIn, signUp }

class _AuthenticationScreenState extends State<AuthenticationScreen> {
  final _formKey = GlobalKey<FormState>();
  final AuthService _authService = AuthService();
  AuthMode _authMode = AuthMode.signIn;
  bool _isLoading = false;

  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  @override
  void dispose() {
    _emailController.dispose();
    _passwordController.dispose();
    _confirmPasswordController.dispose();
    super.dispose();
  }

  void _switchAuthMode() {
    setState(() {
      _authMode = _authMode == AuthMode.signIn ? AuthMode.signUp : AuthMode.signIn;
      _formKey.currentState?.reset();
    });
  }

  Future<void> _submitForm() async {
    if (!(_formKey.currentState?.validate() ?? false)) {
      return;
    }
    _formKey.currentState?.save();
    setState(() => _isLoading = true);

    try {
      if (_authMode == AuthMode.signIn) {
        await _authService.signInWithEmailPassword(
          _emailController.text.trim(),
          _passwordController.text.trim(),
        );
      } else {
        await _authService.signUpWithEmailPassword(
          _emailController.text.trim(),
          _passwordController.text.trim(),
        );
      }
      // Navigation is handled by AuthWrapper's stream
    } on FirebaseAuthException catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.message ?? 'خطای احراز هویت', style: const TextStyle(fontFamily: 'IranYekan'))),
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

  Future<void> _signInWithGoogle() async {
    setState(() => _isLoading = true);
    try {
      await _authService.signInWithGoogle();
      // Navigation handled by AuthWrapper
    } on FirebaseAuthException catch (e) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text(e.message ?? 'خطای ورود با گوگل', style: const TextStyle(fontFamily: 'IranYekan'))),
      );
    } catch (e) {
       ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('خطایی در ورود با گوگل رخ داد: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
      );
    } finally {
      if (mounted) {
        setState(() => _isLoading = false);
      }
    }
  }


  @override
  Widget build(BuildContext context) {
    final deviceSize = MediaQuery.of(context).size;
    return Scaffold(
      body: Center(
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(24.0),
          child: Form(
            key: _formKey,
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              crossAxisAlignment: CrossAxisAlignment.stretch,
              children: <Widget>[
                Text(
                  _authMode == AuthMode.signIn ? 'ورود به حساب کاربری' : 'ایجاد حساب کاربری',
                  textAlign: TextAlign.center,
                  style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontFamily: 'IranYekan', fontWeight: FontWeight.bold),
                ),
                const SizedBox(height: 24),
                TextFormField(
                  controller: _emailController,
                  decoration: const InputDecoration(labelText: 'ایمیل', border: OutlineInputBorder()),
                  keyboardType: TextInputType.emailAddress,
                  validator: (value) {
                    if (value == null || value.isEmpty || !value.contains('@')) {
                      return 'لطفا ایمیل معتبر وارد کنید.';
                    }
                    return null;
                  },
                ),
                const SizedBox(height: 12),
                TextFormField(
                  controller: _passwordController,
                  decoration: const InputDecoration(labelText: 'رمز عبور', border: OutlineInputBorder()),
                  obscureText: true,
                  validator: (value) {
                    if (value == null || value.isEmpty || value.length < 6) {
                      return 'رمز عبور باید حداقل ۶ کاراکتر باشد.';
                    }
                    return null;
                  },
                ),
                if (_authMode == AuthMode.signUp) ...[
                  const SizedBox(height: 12),
                  TextFormField(
                    controller: _confirmPasswordController,
                    decoration: const InputDecoration(labelText: 'تکرار رمز عبور', border: OutlineInputBorder()),
                    obscureText: true,
                    validator: (value) {
                      if (value != _passwordController.text) {
                        return 'رمزهای عبور یکسان نیستند.';
                      }
                      return null;
                    },
                  ),
                ],
                const SizedBox(height: 24),
                if (_isLoading)
                  const Center(child: CircularProgressIndicator())
                else
                  ElevatedButton(
                    onPressed: _submitForm,
                    style: ElevatedButton.styleFrom(
                      backgroundColor: Colors.red[700],
                      padding: const EdgeInsets.symmetric(vertical: 12),
                      textStyle: const TextStyle(fontSize: 18, fontFamily: 'IranYekan', color: Colors.white)
                    ),
                    child: Text(_authMode == AuthMode.signIn ? 'ورود' : 'ثبت نام', style: const TextStyle(color: Colors.white)),
                  ),
                TextButton(
                  onPressed: _switchAuthMode,
                  child: Text(
                    _authMode == AuthMode.signIn ? 'حساب کاربری ندارید؟ ثبت نام کنید' : 'قبلا ثبت نام کرده‌اید؟ وارد شوید',
                     style: const TextStyle(fontFamily: 'IranYekan', color: Colors.red),
                  ),
                ),
                if (_authMode == AuthMode.signIn)
                  TextButton(
                    onPressed: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(builder: (_) => const ForgotPasswordScreen()),
                      );
                    },
                    child: const Text('فراموشی رمز عبور؟', style: TextStyle(fontFamily: 'IranYekan', color: Colors.grey)),
                  ),
                const SizedBox(height: 16),
                const Row(
                  children: <Widget>[
                    Expanded(child: Divider()),
                    Padding(
                      padding: EdgeInsets.symmetric(horizontal: 8.0),
                      child: Text("یا", style: TextStyle(fontFamily: 'IranYekan', color: Colors.grey)),
                    ),
                    Expanded(child: Divider()),
                  ],
                ),
                const SizedBox(height: 16),
                ElevatedButton.icon(
                  icon: const Icon(Icons.g_mobiledata_outlined, color: Colors.white), // Placeholder for Google icon
                  label: const Text('ورود با گوگل', style: TextStyle(fontFamily: 'IranYekan', color: Colors.white)),
                  onPressed: _isLoading ? null : _signInWithGoogle,
                  style: ElevatedButton.styleFrom(
                    backgroundColor: Colors.blue, // Google blue
                    padding: const EdgeInsets.symmetric(vertical: 12),
                     textStyle: const TextStyle(fontSize: 16)
                  ),
                ),
              ],
            ),
          ),
        ),
      ),
    );
  }
}
