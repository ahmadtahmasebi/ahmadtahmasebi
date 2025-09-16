import '../models/category.dart';
import 'dart:math'; // For Random

class CategoryService {
  final List<Category> _categories = [
    // Cosmetics Categories
    Category(id: 'cat_cos_1', name: 'کرم صورت', description: 'انواع کرم های مخصوص پوست صورت', masterTabType: 'cosmetics'),
    Category(id: 'cat_cos_2', name: 'رژ لب', description: 'انواع رژ لب جامد و مایع', masterTabType: 'cosmetics'),
    Category(id: 'cat_cos_3', name: 'مراقبت مو', description: 'شامپو، نرم کننده و ماسک مو', masterTabType: 'cosmetics'),

    // Medicines Categories
    Category(id: 'cat_med_1', name: 'مسکن ها', description: 'داروهای تسکین دهنده درد', masterTabType: 'medicines'),
    Category(id: 'cat_med_2', name: 'ویتامین ها', description: 'انواع ویتامین های ضروری بدن', masterTabType: 'medicines'),
    Category(id: 'cat_med_3', name: 'ضد حساسیت', description: 'داروهای مربوط به آلرژی', masterTabType: 'medicines'),

    // Herbal Categories
    Category(id: 'cat_herb_1', name: 'دمنوش های گیاهی', description: 'ترکیبات گیاهی برای دم کردن', masterTabType: 'herbal'),
    Category(id: 'cat_herb_2', name: 'عرقیات سنتی', description: 'عرقیات گرفته شده از گیاهان دارویی', masterTabType: 'herbal'),

    // Supplements Categories
    Category(id: 'cat_sup_1', name: 'مکمل های ورزشی', description: 'پروتئین، کراتین و سایر مکمل ها', masterTabType: 'supplements'),
    Category(id: 'cat_sup_2', name: 'مکمل های غذایی', description: 'تقویت کننده های عمومی بدن', masterTabType: 'supplements')
  ];
  final Random _random = Random();

  List<Category> getAllCategories() {
    return List.from(_categories);
  }

  void addCategory(String name, String description, {String masterTabType = 'general'}) { // Added masterTabType
    if (_categories.any((cat) => cat.name.toLowerCase() == name.toLowerCase())) {
      print('Category with name "$name" already exists.');
      return;
    }
    final newCategory = Category(
      id: 'cat_user_${(_random.nextInt(99999) + _categories.length + 1).toString()}',
      name: name,
      description: description,
      masterTabType: masterTabType, // Assign masterTabType
    );
    _categories.add(newCategory);
  }

  void updateCategory(Category category) {
    final index = _categories.indexWhere((c) => c.id == category.id);
    if (index != -1) {
      _categories[index] = category; // Ensure the passed category object has masterTabType
    }
  }

  void deleteCategory(String categoryId) {
    _categories.removeWhere((c) => c.id == categoryId);
  }

  Category? getCategoryById(String categoryId) {
    try {
      return _categories.firstWhere((c) => c.id == categoryId);
    } catch (e) {
      return null;
    }
  }
}
