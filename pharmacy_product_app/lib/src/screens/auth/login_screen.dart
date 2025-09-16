import 'package:flutter/material.dart';

class LoginScreen extends StatefulWidget {
  @override
  _LoginScreenState createState() => _LoginScreenState();
}

class _LoginScreenState extends State<LoginScreen> {
  final _formKey = GlobalKey<FormState>();
  final _emailController = TextEditingController();
  final _passwordController = TextEditingController();

  void _loginUser() {
    if (_formKey.currentState!.validate()) {
      // No actual login logic for now
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Login functionality not implemented yet.')),
      );
      print('Login attempt: ${_emailController.text}, ${_passwordController.text}');
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text('ورود کاربر (Login)')),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              Text('خوش آمدید!', style: Theme.of(context).textTheme.headline5, textAlign: TextAlign.center),
              SizedBox(height: 24),
              TextFormField(
                controller: _emailController,
                decoration: InputDecoration(labelText: 'ایمیل یا نام کاربری', border: OutlineInputBorder()),
                keyboardType: TextInputType.emailAddress,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'لطفا ایمیل یا نام کاربری را وارد کنید';
                  }
                  return null;
                },
              ),
              SizedBox(height: 16),
              TextFormField(
                controller: _passwordController,
                decoration: InputDecoration(labelText: 'رمز عبور', border: OutlineInputBorder()),
                obscureText: true,
                validator: (value) {
                  if (value == null || value.isEmpty) {
                    return 'لطفا رمز عبور را وارد کنید';
                  }
                  return null;
                },
              ),
              SizedBox(height: 24),
              ElevatedButton(
                onPressed: _loginUser,
                child: Text('ورود'),
                style: ElevatedButton.styleFrom(padding: EdgeInsets.symmetric(vertical: 12)),
              ),
              TextButton(
                onPressed: () {
                  // Navigate to Registration Screen
                  // Assuming RegistrationScreen is available and imported
                  // For now, show a message if direct navigation isn't set up from here
                  // dynamic registrationScreenRoute = ModalRoute.of(context)?.settings.arguments; // Example, not used
                  // Check if navigator can pop, to prevent issues if it's the first screen
                  // if (Navigator.canPop(context)) {
                     // This is just an example, actual navigation will be from settings or dedicated button
                  // }
                   ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Navigate to Registration Screen (placeholder)')),
                      );
                },
                child: Text('حساب کاربری ندارید؟ ثبت نام کنید'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
