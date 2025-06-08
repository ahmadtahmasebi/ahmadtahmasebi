import 'package:flutter/material.dart';
import '../../../../core/models/category_model.dart';
import '../../../../core/services/firestore_service.dart';
import '../../../../core/services/category_service_interface.dart';
import 'admin_add_edit_category_screen.dart'; // Will be created next

class AdminCategoryListScreen extends StatefulWidget {
  const AdminCategoryListScreen({Key? key}) : super(key: key);

  @override
  _AdminCategoryListScreenState createState() => _AdminCategoryListScreenState();
}

class _AdminCategoryListScreenState extends State<AdminCategoryListScreen> {
  final ICategoryService _categoryService = FirestoreService();

  void _navigateToAddEditScreen({Category? category}) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => AdminAddEditCategoryScreen(categoryToEdit: category),
      ),
    ).then((_) {
      // Optional: could refresh or listen to a stream if needed,
      // but StreamBuilder below should handle UI updates automatically.
    });
  }

  Future<void> _deleteCategory(String categoryId, String categoryName) async {
    final bool? confirmDelete = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('تایید حذف', style: TextStyle(fontFamily: 'IranYekan')),
          content: Text('آیا از حذف دسته‌بندی "$categoryName" مطمئن هستید؟\nتوجه: این کار ممکن است بر محصولاتی که از این دسته‌بندی استفاده می‌کنند تاثیر بگذارد.', style: TextStyle(fontFamily: 'IranYekan')),
          actions: <Widget>[
            TextButton(
              child: const Text('لغو', style: TextStyle(fontFamily: 'IranYekan')),
              onPressed: () => Navigator.of(context).pop(false),
            ),
            TextButton(
              child: const Text('حذف', style: TextStyle(fontFamily: 'IranYekan', color: Colors.red)),
              onPressed: () => Navigator.of(context).pop(true),
            ),
          ],
        );
      },
    );

    if (confirmDelete == true) {
      try {
        await _categoryService.deleteCategory(categoryId);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('دسته‌بندی "$categoryName" با موفقیت حذف شد.', style: const TextStyle(fontFamily: 'IranYekan'))),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('خطا در حذف دسته‌بندی: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('مدیریت دسته‌بندی‌ها', style: TextStyle(fontFamily: 'IranYekan')),
      ),
      body: StreamBuilder<List<Category>>(
        stream: _categoryService.getCategories(), // Assumes getCategories orders them or add .orderBy('name') in service
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('خطا: ${snapshot.error}', style: const TextStyle(fontFamily: 'IranYekan')));
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('دسته‌بندی‌ای یافت نشد. برای افزودن روی + کلیک کنید.', style: TextStyle(fontFamily: 'IranYekan')));
          }

          final categories = snapshot.data!;

          return ListView.separated(
            itemCount: categories.length,
            separatorBuilder: (context, index) => const Divider(),
            itemBuilder: (context, index) {
              final category = categories[index];
              return ListTile(
                title: Text(category.name, style: const TextStyle(fontFamily: 'IranYekan', fontWeight: FontWeight.bold)),
                subtitle: Text('ID: ${category.id}', style: const TextStyle(fontFamily: 'IranYekan', fontSize: 12, color: Colors.grey)),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.edit, color: Colors.blue),
                      tooltip: 'ویرایش',
                      onPressed: () => _navigateToAddEditScreen(category: category),
                    ),
                    IconButton(
                      icon: const Icon(Icons.delete, color: Colors.red),
                      tooltip: 'حذف',
                      onPressed: () => _deleteCategory(category.id, category.name),
                    ),
                  ],
                ),
                onTap: () => _navigateToAddEditScreen(category: category),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _navigateToAddEditScreen(),
        tooltip: 'افزودن دسته‌بندی جدید',
        child: const Icon(Icons.add),
      ),
    );
  }
}
