import '../models/product.dart';
import 'dart:math'; // For Random

class ProductService {
  final List<Product> _products = [];
  final Random _random = Random();

  List<Product> getAllProducts() {
    return List.from(_products);
  }

  void addProduct(Product product) {
    // Assign a simple random ID if not provided (though product constructor requires it)
    final newProduct = Product(
      id: product.id.isEmpty ? (_random.nextInt(999999) + 1).toString() : product.id,
      name: product.name,
      categoryId: product.categoryId,
      price: product.price,
      description: product.description,
      imagePath: product.imagePath,
      stock: product.stock,
      minStock: product.minStock,
      likes: product.likes,
      viewCount: product.viewCount,
    );
    _products.add(newProduct);
  }

  void updateProduct(Product product) {
    final index = _products.indexWhere((p) => p.id == product.id);
    if (index != -1) {
      _products[index] = product;
    }
  }

  void deleteProduct(String productId) {
    _products.removeWhere((p) => p.id == productId);
  }

  List<Product> getProductsByCategoryId(String categoryId) {
    return _products.where((p) => p.categoryId == categoryId).toList();
  }

  Product? getProductById(String productId) {
    try {
      return _products.firstWhere((p) => p.id == productId);
    } catch (e) {
      return null;
    }
  }
}
