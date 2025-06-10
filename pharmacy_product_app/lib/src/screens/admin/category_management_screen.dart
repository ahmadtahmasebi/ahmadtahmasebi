import 'package:flutter/material.dart';
import '../../models/category.dart';
import '../../services/category_service.dart'; // Assuming global instance or accessible

// Initialize CategoryService (simple global instance for now)
// This is not ideal for larger apps but works given current constraints.
final CategoryService _categoryService = CategoryService();

class CategoryManagementScreen extends StatefulWidget {
  @override
  _CategoryManagementScreenState createState() => _CategoryManagementScreenState();
}

class _CategoryManagementScreenState extends State<CategoryManagementScreen> {
  List<Category> _categories = [];
  final _nameController = TextEditingController();
  final _descriptionController = TextEditingController();
  Category? _selectedCategory; // For editing

  @override
  void initState() {
    super.initState();
    _loadCategories();
  }

  void _loadCategories() {
    setState(() {
      _categories = _categoryService.getAllCategories();
    });
  }

  void _addOrUpdateCategory() {
    if (_nameController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Category name cannot be empty!')),
      );
      return;
    }

    if (_selectedCategory == null) { // Add new
      _categoryService.addCategory(_nameController.text, _descriptionController.text);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Category added!')),
      );
    } else { // Update existing
      final updatedCategory = Category(
        id: _selectedCategory!.id,
        name: _nameController.text,
        description: _descriptionController.text,
      );
      _categoryService.updateCategory(updatedCategory);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Category updated!')),
      );
    }
    _clearForm();
    _loadCategories();
  }

  void _deleteCategory(String categoryId) {
    _categoryService.deleteCategory(categoryId);
    _loadCategories();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Category deleted!')),
    );
  }

  void _selectCategoryForEditing(Category category) {
    setState(() {
      _selectedCategory = category;
      _nameController.text = category.name;
      _descriptionController.text = category.description;
    });
  }

  void _clearForm() {
    setState(() {
      _selectedCategory = null;
      _nameController.clear();
      _descriptionController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Manage Categories'),
        actions: [
          IconButton(
            icon: Icon(Icons.clear),
            onPressed: _clearForm,
            tooltip: 'Clear Form',
          )
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _nameController,
              decoration: InputDecoration(labelText: 'Category Name'),
            ),
            SizedBox(height: 10),
            TextField(
              controller: _descriptionController,
              decoration: InputDecoration(labelText: 'Description (Optional)'),
              maxLines: 2,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _addOrUpdateCategory,
              child: Text(_selectedCategory == null ? 'Add Category' : 'Update Category'),
            ),
            SizedBox(height: 20),
            Text('Existing Categories', style: Theme.of(context).textTheme.headline6),
            Expanded(
              child: _categories.isEmpty
                  ? Center(child: Text('No categories found.'))
                  : ListView.builder(
                      itemCount: _categories.length,
                      itemBuilder: (context, index) {
                        final category = _categories[index];
                        return Card(
                          margin: EdgeInsets.symmetric(vertical: 4.0),
                          child: ListTile(
                            title: Text(category.name),
                            subtitle: Text(category.description.isNotEmpty ? category.description : 'No description'),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(
                                  icon: Icon(Icons.edit, color: Colors.blue),
                                  onPressed: () => _selectCategoryForEditing(category),
                                ),
                                IconButton(
                                  icon: Icon(Icons.delete, color: Colors.red),
                                  onPressed: () => _deleteCategory(category.id),
                                ),
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
