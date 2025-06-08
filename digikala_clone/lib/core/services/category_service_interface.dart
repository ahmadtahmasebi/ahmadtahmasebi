import '../models/category_model.dart';

abstract class ICategoryService {
  Future<void> addCategory(Category category);
  Future<void> updateCategory(Category category);
  Future<void> deleteCategory(String categoryId);
  Stream<List<Category>> getCategories();
  Future<Category?> getCategoryById(String categoryId);
}
