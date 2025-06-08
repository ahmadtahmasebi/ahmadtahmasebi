import 'package:flutter/material.dart';
import 'features/products/screens/product_list_screen.dart'; // Import the ProductListScreen

void main() {
  runApp(const MyApp());
}

class MyApp extends StatelessWidget {
  const MyApp({Key? key}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Digikala Clone',
      theme: ThemeData(
        primarySwatch: Colors.red, // Digikala's primary color is a shade of red
        fontFamily: 'IranYekan', // A common Persian font, assuming it would be added to assets
        textTheme: const TextTheme( // Basic TextTheme for right-to-left text direction
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
      home: ProductListScreen(), // Set ProductListScreen as home
      debugShowCheckedModeBanner: false, // Optional: to remove debug banner
      // For full RTL support, you might need to set LocalizationsDelegates and supportedLocales
      // localizationsDelegates: [
      //   GlobalMaterialLocalizations.delegate,
      //   GlobalWidgetsLocalizations.delegate,
      //   GlobalCupertinoLocalizations.delegate,
      // ],
      // supportedLocales: [
      //   const Locale('fa', ''), // Farsi
      //   // ... other locales your app supports
      // ],
      // locale: const Locale('fa', ''), // Default to Farsi
    );
  }
}
