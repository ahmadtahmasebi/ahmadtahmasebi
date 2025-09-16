import 'package:flutter/material.dart';

class RegistrationScreen extends StatefulWidget {
  @override
  _RegistrationScreenState createState() => _RegistrationScreenState();
}

class _RegistrationScreenState extends State<RegistrationScreen> {
  final _formKey = GlobalKey<FormState>();
  final _usernameController = TextEditingController();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();
  final _confirmPasswordController = TextEditingController();

  void _registerUser() {
    if (_formKey.currentState!.validate()) {
      if (_passwordController.text != _confirmPasswordController.text) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('رمزهای عبور مطابقت ندارند!')),
        );
        return;
      }
      // No actual registration logic for now
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Registration functionality not implemented yet.')),
      );
      print('Registration attempt: ${_usernameController.text}, ${_emailController.text}');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('ثبت نام کاربر (Register)')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: ListView( // Use ListView for longer forms that might need scrolling
            children: <Widget>[
              Text('ایجاد حساب کاربری جدید', style: Theme.of(context).textTheme.headline5, textAlign: TextAlign.center),
              SizedBox(height: 24),
              TextFormField(
                controller: _usernameController,
                decoration: InputDecoration(labelText: 'نام کاربری', border: OutlineInputBorder()),
                validator: (value) {
                  if (value == null || value.isEmpty) return 'نام کاربری الزامی است';
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _emailController,
                decoration: InputDecoration(labelText: 'ایمیل', border: OutlineInputBorder()),
                keyboardType: TextInputType.emailAddress,
                validator: (value) {
                  if (value == null || value.isEmpty) return 'ایمیل الزامی است';
                  if (!value.contains('@')) return 'ایمیل معتبر نیست';
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _passwordController,
                decoration: InputDecoration(labelText: 'رمز عبور', border: OutlineInputBorder()),
                obscureText: true,
                validator: (value) {
                  if (value == null || value.isEmpty) return 'رمز عبور الزامی است';
                  if (value.length < 6) return 'رمز عبور باید حداقل ۶ کاراکتر باشد';
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _confirmPasswordController,
                decoration: InputDecoration(labelText: 'تکرار رمز عبور', border: OutlineInputBorder()),
                obscureText: true,
                validator: (value) {
                  if (value == null || value.isEmpty) return 'تکرار رمز عبور الزامی است';
                  if (value != _passwordController.text) return 'رمزهای عبور مطابقت ندارند';
                  return null;
                },
              ),
              SizedBox(height: 24),
              ElevatedButton(
                onPressed: _registerUser,
                child: Text('ثبت نام'),
                style: ElevatedButton.styleFrom(padding: EdgeInsets.symmetric(vertical: 12)),
              ),
               TextButton(
                onPressed: () {
                  if (Navigator.canPop(context)) {
                    Navigator.pop(context); // Go back to Login or previous screen
                  }
                },
                child: Text('قبلاً ثبت نام کرده‌اید؟ وارد شوید'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
