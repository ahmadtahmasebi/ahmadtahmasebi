import 'package:flutter/material.dart';
import 'package:firebase_core/firebase_core.dart';
import 'package:provider/provider.dart';
import 'firebase_options.dart';
// import 'features/home/screens/home_screen.dart'; // HomeScreen will be navigated to by AuthWrapper
import 'core/providers/theme_provider.dart';
import 'features/auth/widgets/auth_wrapper.dart'; // Import AuthWrapper

Future<void> main() async {
  WidgetsFlutterBinding.ensureInitialized();

  final themeProvider = ThemeProvider();
  await themeProvider.loadThemeMode();

  try {
    await Firebase.initializeApp(
      options: DefaultFirebaseOptions.currentPlatform,
    );
  } catch (e) {
    print('Firebase initialization error: $e');
  }

  runApp(
    ChangeNotifierProvider(
      create: (_) => themeProvider,
      child: const MyApp(),
    ),
  );
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final themeProvider = Provider.of<ThemeProvider>(context);

    return MaterialApp(
      title: 'داروخانه آنلاین',
      themeMode: themeProvider.themeMode,
      theme: ThemeData(
        brightness: Brightness.light,
        primarySwatch: Colors.red,
        fontFamily: 'IranYekan',
        appBarTheme: AppBarTheme(
          backgroundColor: Colors.red[700],
          foregroundColor: Colors.white,
        ),
        textTheme: const TextTheme(
          bodyLarge: TextStyle(fontFamily: 'IranYekan'),
          bodyMedium: TextStyle(fontFamily: 'IranYekan'),
          displayLarge: TextStyle(fontFamily: 'IranYekan'),
          displayMedium: TextStyle(fontFamily: 'IranYekan'),
          displaySmall: TextStyle(fontFamily: 'IranYekan'),
          headlineMedium: TextStyle(fontFamily: 'IranYekan'),
          headlineSmall: TextStyle(fontFamily: 'IranYekan'),
          titleLarge: TextStyle(fontFamily: 'IranYekan'),
          titleMedium: TextStyle(fontFamily: 'IranYekan'),
          titleSmall: TextStyle(fontFamily: 'IranYekan'),
          bodySmall: TextStyle(fontFamily: 'IranYekan'),
          labelLarge: TextStyle(fontFamily: 'IranYekan'),
          labelSmall: TextStyle(fontFamily: 'IranYekan'),
        ),
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      darkTheme: ThemeData(
        brightness: Brightness.dark,
        primarySwatch: Colors.red,
        fontFamily: 'IranYekan',
         appBarTheme: AppBarTheme(
          backgroundColor: Colors.red[900],
          foregroundColor: Colors.white,
        ),
        textTheme: const TextTheme(
          bodyLarge: TextStyle(fontFamily: 'IranYekan', color: Colors.white),
          bodyMedium: TextStyle(fontFamily: 'IranYekan', color: Colors.white70),
          displayLarge: TextStyle(fontFamily: 'IranYekan', color: Colors.white),
          displayMedium: TextStyle(fontFamily: 'IranYekan', color: Colors.white70),
          displaySmall: TextStyle(fontFamily: 'IranYekan', color: Colors.white70),
          headlineMedium: TextStyle(fontFamily: 'IranYekan', color: Colors.white),
          headlineSmall: TextStyle(fontFamily: 'IranYekan', color: Colors.white),
          titleLarge: TextStyle(fontFamily: 'IranYekan', color: Colors.white),
          titleMedium: TextStyle(fontFamily: 'IranYekan', color: Colors.white),
          titleSmall: TextStyle(fontFamily: 'IranYekan', color: Colors.white70),
          bodySmall: TextStyle(fontFamily: 'IranYekan', color: Colors.white70),
          labelLarge: TextStyle(fontFamily: 'IranYekan', color: Colors.white),
          labelSmall: TextStyle(fontFamily: 'IranYekan', color: Colors.white70),
        ),
        visualDensity: VisualDensity.adaptivePlatformDensity,
      ),
      home: const AuthWrapper(), // Set AuthWrapper as home
      debugShowCheckedModeBanner: false,
    );
  }
}
