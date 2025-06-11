import '../models/category.dart';
import 'dart:math'; // For Random

class CategoryService {
  // In-memory list to store categories, pre-populated with sample data
  final List<Category> _categories = [
    // Cosmetics Categories
    Category(id: 'cat_cos_1', name: 'کرم صورت', description: 'انواع کرم های مخصوص پوست صورت'),
    Category(id: 'cat_cos_2', name: 'رژ لب', description: 'انواع رژ لب جامد و مایع'),
    Category(id: 'cat_cos_3', name: 'مراقبت مو', description: 'شامپو، نرم کننده و ماسک مو'),

    // Medicines Categories
    Category(id: 'cat_med_1', name: 'مسکن ها', description: 'داروهای تسکین دهنده درد'),
    Category(id: 'cat_med_2', name: 'ویتامین ها', description: 'انواع ویتامین های ضروری بدن'),
    Category(id: 'cat_med_3', name: 'ضد حساسیت', description: 'داروهای مربوط به آلرژی'),

    // Herbal Categories
    Category(id: 'cat_herb_1', name: 'دمنوش های گیاهی', description: 'ترکیبات گیاهی برای دم کردن'),
    Category(id: 'cat_herb_2', name: 'عرقیات سنتی', description: 'عرقیات گرفته شده از گیاهان دارویی'),

    // Supplements Categories
    Category(id: 'cat_sup_1', name: 'مکمل های ورزشی', description: 'پروتئین، کراتین و سایر مکمل ها'),
    Category(id: 'cat_sup_2', name: 'مکمل های غذایی', description: 'تقویت کننده های عمومی بدن')
  ];
  final Random _random = Random();

  // Get all categories
  List<Category> getAllCategories() {
    return List.from(_categories); // Return a copy
  }

  // Add a new category
  void addCategory(String name, String description) {
    // Check if category with the same name already exists to avoid duplicates from admin panel
    if (_categories.any((cat) => cat.name.toLowerCase() == name.toLowerCase())) {
      print('Category with name "$name" already exists.'); // Using double quotes for print
      return;
    }
    final newCategory = Category(
      id: 'cat_user_${(_random.nextInt(99999) + _categories.length + 1).toString()}', // Simple random ID for user-added
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

  Category? getCategoryById(String categoryId) {
    try {
      return _categories.firstWhere((c) => c.id == categoryId);
    } catch (e) {
      return null; // Not found
    }
  }
}
