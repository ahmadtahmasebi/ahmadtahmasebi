import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import '../../../../core/models/category_model.dart';
import '../../../../core/services/firestore_service.dart';
import '../../../../core/services/category_service_interface.dart';

class AdminAddEditCategoryScreen extends StatefulWidget {
  final Category? categoryToEdit;

  const AdminAddEditCategoryScreen({Key? key, this.categoryToEdit}) : super(key: key);

  @override
  _AdminAddEditCategoryScreenState createState() => _AdminAddEditCategoryScreenState();
}

class _AdminAddEditCategoryScreenState extends State<AdminAddEditCategoryScreen> {
  final _formKey = GlobalKey<FormState>();
  final ICategoryService _categoryService = FirestoreService();

  late TextEditingController _nameController;
  late TextEditingController _idController; // For displaying ID, not editable for existing
  bool _isSaving = false;
  bool _isEditing = false;

  @override
  void initState() {
    super.initState();
    _isEditing = widget.categoryToEdit != null;
    _nameController = TextEditingController(text: widget.categoryToEdit?.name);
    _idController = TextEditingController(text: widget.categoryToEdit?.id ?? 'در صورت افزودن، خودکار ایجاد می‌شود');
  }

  @override
  void dispose() {
    _nameController.dispose();
    _idController.dispose();
    super.dispose();
  }

  Future<void> _saveCategory() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    _formKey.currentState?.save();
    setState(() => _isSaving = true);

    final String id = widget.categoryToEdit?.id ?? const Uuid().v4();
    final Category category = Category(
      id: id,
      name: _nameController.text.trim(),
    );

    try {
      if (_isEditing) {
        await _categoryService.updateCategory(category);
      } else {
        await _categoryService.addCategory(category);
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('دسته‌بندی با موفقیت ذخیره شد.', style: const TextStyle(fontFamily: 'IranYekan'))),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطا در ذخیره دسته‌بندی: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          _isEditing ? 'ویرایش دسته‌بندی' : 'افزودن دسته‌بندی',
          style: const TextStyle(fontFamily: 'IranYekan'),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: <Widget>[
              TextFormField(
                controller: _idController,
                decoration: const InputDecoration(
                  labelText: 'شناسه (ID)',
                  border: OutlineInputBorder(),
                  hintStyle: TextStyle(fontFamily: 'IranYekan')
                ),
                readOnly: true, // ID is not editable
                style: TextStyle(fontFamily: 'IranYekan', color: _isEditing ? Colors.grey : null),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'نام دسته‌بندی',
                  border: OutlineInputBorder(),
                  hintStyle: TextStyle(fontFamily: 'IranYekan')
                ),
                validator: (value) => (value == null || value.trim().isEmpty) ? 'نام دسته‌بندی الزامی است' : null,
                style: const TextStyle(fontFamily: 'IranYekan'),
              ),
              const SizedBox(height: 24),
              if (_isSaving)
                const Center(child: CircularProgressIndicator())
              else
                ElevatedButton(
                  onPressed: _saveCategory,
                  style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 12)),
                  child: Text(_isEditing ? 'ذخیره تغییرات' : 'افزودن دسته‌بندی', style: const TextStyle(fontFamily: 'IranYekan', fontSize: 18)),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
