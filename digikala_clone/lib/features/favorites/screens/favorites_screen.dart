import 'package:flutter/material.dart';
import '../../../core/models/product_model.dart';
import '../../../core/services/auth_service.dart'; // Import AuthService
import '../../../core/services/favorites_service.dart';
import '../../../core/services/firestore_service.dart';
import '../../../core/services/product_service_interface.dart';
import '../../products/widgets/product_card.dart';
import '../../auth/screens/authentication_screen.dart'; // For redirecting if not logged in

class FavoritesScreen extends StatefulWidget {
  const FavoritesScreen({Key? key}) : super(key: key);

  @override
  _FavoritesScreenState createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends State<FavoritesScreen> {
  final FavoritesService _favoritesService = FavoritesService();
  final IProductService _productService = FirestoreService();
  final AuthService _authService = AuthService(); // Instantiate AuthService
  String? _currentUserId;
  Future<List<Product>>? _favoriteProductsFuture; // Make it nullable

  @override
  void initState() {
    super.initState();
    _currentUserId = _authService.currentUser?.uid;
    if (_currentUserId != null) {
      _loadFavoriteProducts();
    }
  }

  Future<void> _loadFavoriteProducts() async {
    if (_currentUserId == null) {
      // This should ideally not be reached if UI prevents access, but as a safeguard:
      setState(() {
        _favoriteProductsFuture = Future.value([]); // Empty list if no user
      });
      return;
    }
    // Assign the future directly for FutureBuilder to handle states
    setState(() {
      _favoriteProductsFuture = _fetchFavoriteProducts(_currentUserId!);
    });
  }

  Future<List<Product>> _fetchFavoriteProducts(String userId) async {
    final List<String> favIds = await _favoritesService.getFavoriteProductIds(userId);
    if (favIds.isEmpty) {
      return [];
    }

    final List<Product?> productList = await Future.wait(
      favIds.map((id) => _productService.getProductById(id)).toList(),
    );

    return productList.where((product) => product != null).cast<Product>().toList();
  }

  @override
  Widget build(BuildContext context) {
    if (_currentUserId == null) {
      return Scaffold(
        appBar: AppBar(
          title: const Text('علاقه‌مندی‌ها', style: TextStyle(fontFamily: 'IranYekan')),
          backgroundColor: Colors.red[700],
        ),
        body: Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              const Text('برای مشاهده علاقه‌مندی‌ها ابتدا وارد شوید.', style: TextStyle(fontFamily: 'IranYekan', fontSize: 16)),
              const SizedBox(height: 20),
              ElevatedButton(
                onPressed: () {
                  Navigator.of(context).pushReplacement(MaterialPageRoute(
                    builder: (_) => const AuthenticationScreen(),
                  ));
                },
                style: ElevatedButton.styleFrom(backgroundColor: Colors.red[700]),
                child: const Text('ورود / ثبت نام', style: TextStyle(fontFamily: 'IranYekan', color: Colors.white)),
              )
            ],
          ),
        ),
      );
    }

    return Scaffold(
      appBar: AppBar(
        title: const Text('علاقه‌مندی‌ها', style: TextStyle(fontFamily: 'IranYekan')),
        backgroundColor: Colors.red[700],
      ),
      body: RefreshIndicator(
        onRefresh: _loadFavoriteProducts,
        child: FutureBuilder<List<Product>>(
          future: _favoriteProductsFuture,
          builder: (context, snapshot) {
            if (snapshot.connectionState == ConnectionState.waiting) {
              return const Center(child: CircularProgressIndicator());
            }
            if (snapshot.hasError) {
              return Center(
                child: Text(
                  'خطا در بارگذاری علاقه‌مندی‌ها: ${snapshot.error}',
                  style: const TextStyle(fontFamily: 'IranYekan'),
                ),
              );
            }
            if (!snapshot.hasData || snapshot.data!.isEmpty) {
              return const Center(
                child: Text(
                  'هنوز محصولی به علاقه‌مندی‌ها اضافه نشده است.',
                  style: TextStyle(fontFamily: 'IranYekan', fontSize: 16),
                ),
              );
            }

            final favoriteProducts = snapshot.data!;
            return GridView.builder(
              padding: const EdgeInsets.all(8.0),
              gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                crossAxisCount: 2,
                crossAxisSpacing: 8.0,
                mainAxisSpacing: 8.0,
                childAspectRatio: 0.7,
              ),
              itemCount: favoriteProducts.length,
              itemBuilder: (context, index) {
                return ProductCard(product: favoriteProducts[index]);
              },
            );
          },
        ),
      ),
    );
  }
}
