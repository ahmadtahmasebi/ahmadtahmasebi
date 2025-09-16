import 'package:flutter/material.dart';
import '../../models/category.dart';
import '../../services/category_service.dart';

final CategoryService _categoryService = CategoryService();

class CategoryManagementScreen extends StatefulWidget {
  @override
  _CategoryManagementScreenState createState() => _CategoryManagementScreenState();
}

class _CategoryManagementScreenState extends State<CategoryManagementScreen> {
  List<Category> _categories = [];
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  String _selectedMasterTabType = 'general'; // Default
  Category? _selectedCategory;

  final List<String> _masterTabTypes = ['general', 'cosmetics', 'medicines', 'herbal', 'supplements'];


  @override
  void initState() {
    super.initState();
    _loadCategories();
  }

  void _loadCategories() {
    if(mounted){
      setState(() {
        _categories = _categoryService.getAllCategories();
      });
    }
  }

  void _addOrUpdateCategory() {
    if (_nameController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('نام دسته‌بندی نمی‌تواند خالی باشد!')),
      );
      return;
    }

    if (_selectedCategory == null) {
      _categoryService.addCategory(
        _nameController.text,
        _descriptionController.text,
        masterTabType: _selectedMasterTabType,
      );
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('دسته‌بندی اضافه شد!')));
    } else {
      final updatedCategory = Category(
        id: _selectedCategory!.id,
        name: _nameController.text,
        description: _descriptionController.text,
        masterTabType: _selectedMasterTabType,
      );
      _categoryService.updateCategory(updatedCategory);
      ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('دسته‌بندی بروزرسانی شد!')));
    }
    _clearForm();
    _loadCategories();
  }

  void _deleteCategory(String categoryId) {
    _categoryService.deleteCategory(categoryId);
    _loadCategories();
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('دسته‌بندی حذف شد!')));
  }

  void _selectCategoryForEditing(Category category) {
    if(mounted){
      setState(() {
        _selectedCategory = category;
        _nameController.text = category.name;
        _descriptionController.text = category.description;
        _selectedMasterTabType = category.masterTabType;
      });
    }
  }

  void _clearForm() {
    if(mounted){
      setState(() {
        _selectedCategory = null;
        _nameController.clear();
        _descriptionController.clear();
        _selectedMasterTabType = 'general';
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('مدیریت دسته‌بندی‌ها'),
        actions: [
          IconButton(icon: Icon(Icons.clear), onPressed: _clearForm, tooltip: 'پاک کردن فرم')
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(controller: _nameController, decoration: InputDecoration(labelText: 'نام دسته‌بندی')),
            SizedBox(height: 10),
            TextField(controller: _descriptionController, decoration: InputDecoration(labelText: 'توضیحات (اختیاری)'), maxLines: 2),
            SizedBox(height: 10),
            DropdownButtonFormField<String>(
              decoration: InputDecoration(labelText: 'نوع تب اصلی'),
              value: _selectedMasterTabType,
              items: _masterTabTypes.map((String type) {
                return DropdownMenuItem<String>(value: type, child: Text(type));
              }).toList(),
              onChanged: (String? newValue) {
                if (newValue != null && mounted) {
                  setState(() => _selectedMasterTabType = newValue);
                }
              },
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _addOrUpdateCategory,
              child: Text(_selectedCategory == null ? 'افزودن دسته‌بندی' : 'ذخیره تغییرات'),
            ),
            SizedBox(height: 20),
            Text('دسته‌بندی‌های موجود', style: Theme.of(context).textTheme.headline6),
            Expanded(
              child: _categories.isEmpty
                  ? Center(child: Text('دسته‌بندی‌ای یافت نشد.'))
                  : ListView.builder(
                      itemCount: _categories.length,
                      itemBuilder: (context, index) {
                        final category = _categories[index];
                        return Card(
                          child: ListTile(
                            title: Text(category.name),
                            subtitle: Text(category.description.isNotEmpty ? 'توضیحات: \${category.description}\nتب اصلی: \${category.masterTabType}' : 'بدون توضیحات - تب: \${category.masterTabType}', style: TextStyle(color: Colors.grey[600])),
                            isThreeLine: category.description.isNotEmpty,
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(icon: Icon(Icons.edit, color: Colors.blue), onPressed: () => _selectCategoryForEditing(category)),
                                IconButton(icon: Icon(Icons.delete, color: Colors.red), onPressed: () => _deleteCategory(category.id)),
                              ],
                            ),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
