import 'package:flutter/material.dart';
import '../../../core/models/product_model.dart';
import '../../../core/services/favorites_service.dart';
import '../../../core/services/firestore_service.dart';
import '../../../core/services/product_service_interface.dart';
import '../../products/widgets/product_card.dart'; // Assuming ProductCard can be reused

class FavoritesScreen extends StatefulWidget {
  const FavoritesScreen({Key? key}) : super(key: key);

  @override
  _FavoritesScreenState createState() => _FavoritesScreenState();
}

class _FavoritesScreenState extends State<FavoritesScreen> {
  final FavoritesService _favoritesService = FavoritesService();
  final IProductService _productService = FirestoreService();
  late Future<List<Product>> _favoriteProductsFuture;

  @override
  void initState() {
    super.initState();
    _loadFavoriteProducts();
  }

  Future<void> _loadFavoriteProducts() async {
    setState(() { // Ensure UI rebuilds when future is assigned
      _favoriteProductsFuture = _fetchFavoriteProducts();
    });
  }

  Future<List<Product>> _fetchFavoriteProducts() async {
    final List<String> favIds = await _favoritesService.getFavoriteProductIds();
    if (favIds.isEmpty) {
      return [];
    }

    final List<Product?> productFutures = await Future.wait(
      favIds.map((id) => _productService.getProductById(id)).toList(),
    );

    // Filter out nulls (if a product was deleted or ID was invalid) and cast
    return productFutures.where((product) => product != null).cast<Product>().toList();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('علاقه‌مندی‌ها', style: TextStyle(fontFamily: 'IranYekan')),
        backgroundColor: Colors.red[700],
      ),
      body: RefreshIndicator(
        onRefresh: _loadFavoriteProducts, // Allow pull-to-refresh
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
