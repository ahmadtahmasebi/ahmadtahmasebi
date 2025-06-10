import '../models/category.dart';
import 'dart:math'; // For Random

class CategoryService {
  // In-memory list to store categories
  final List<Category> _categories = [];
  final Random _random = Random();

  // Get all categories
  List<Category> getAllCategories() {
    return List.from(_categories); // Return a copy
  }

  // Add a new category
  void addCategory(String name, String description) {
    final newCategory = Category(
      id: (_random.nextInt(999999) + 1).toString(), // Simple random ID
      name: name,
      description: description,
    );
    _categories.add(newCategory);
  }

  // Update an existing category
  void updateCategory(Category category) {
    final index = _categories.indexWhere((c) => c.id == category.id);
    if (index != -1) {
      _categories[index] = category;
    }
  }

  // Delete a category
  void deleteCategory(String categoryId) {
    _categories.removeWhere((c) => c.id == categoryId);
    // TODO: Consider what happens to products in this category
  }

  // Get a category by ID (optional, but good to have)
  Category? getCategoryById(String categoryId) {
    try {
      return _categories.firstWhere((c) => c.id == categoryId);
    } catch (e) {
      return null;
    }
  }
}
