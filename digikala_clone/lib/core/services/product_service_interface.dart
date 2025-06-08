import '../models/product_model.dart';
import '../models/user_comment_model.dart'; // Import UserComment model

abstract class IProductService {
  Future<void> addProduct(Product product);
  Future<void> updateProduct(Product product);
  Future<void> deleteProduct(String productId);
  Stream<List<Product>> getProducts();
  Stream<List<Product>> getProductsByCategory(String categoryId);
  Future<Product?> getProductById(String productId);

  // New methods for views, likes, and comments
  Future<void> incrementProductView(String productId);
  Future<void> likeProduct(String productId, String userId);
  Future<void> unlikeProduct(String productId, String userId);
  Stream<List<UserComment>> getProductComments(String productId);
  Future<void> addProductComment(UserComment comment);
}
