import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import 'package:cloud_firestore/cloud_firestore.dart';
import '../../../../core/models/news_item_model.dart';
import '../../../../core/services/firestore_service.dart';
import '../../../../core/services/news_service_interface.dart';

class AdminAddEditNewsItemScreen extends StatefulWidget {
  final NewsItem? itemToEdit;

  const AdminAddEditNewsItemScreen({Key? key, this.itemToEdit}) : super(key: key);

  @override
  _AdminAddEditNewsItemScreenState createState() => _AdminAddEditNewsItemScreenState();
}

class _AdminAddEditNewsItemScreenState extends State<AdminAddEditNewsItemScreen> {
  final _formKey = GlobalKey<FormState>();
  final INewsService _newsService = FirestoreService();

  // Form field controllers
  late TextEditingController _idController;
  late TextEditingController _titleController;
  late TextEditingController _contentController;
  late TextEditingController _authorController;
  late TextEditingController _categoryController; // For news/article category e.g., "Health", "Tech"
  late TextEditingController _imageUrlController;

  NewsItemType _selectedType = NewsItemType.news; // Default type
  bool _isSaving = false;
  bool _isEditing = false;

  @override
  void initState() {
    super.initState();
    _isEditing = widget.itemToEdit != null;

    _idController = TextEditingController(text: widget.itemToEdit?.id ?? 'در صورت افزودن، خودکار ایجاد می‌شود');
    _titleController = TextEditingController(text: widget.itemToEdit?.title);
    _contentController = TextEditingController(text: widget.itemToEdit?.content);
    _authorController = TextEditingController(text: widget.itemToEdit?.author);
    _categoryController = TextEditingController(text: widget.itemToEdit?.category);
    _imageUrlController = TextEditingController(text: widget.itemToEdit?.imageUrl);
    _selectedType = widget.itemToEdit?.type ?? NewsItemType.news;
  }

  @override
  void dispose() {
    _idController.dispose();
    _titleController.dispose();
    _contentController.dispose();
    _authorController.dispose();
    _categoryController.dispose();
    _imageUrlController.dispose();
    super.dispose();
  }

  Future<void> _saveItem() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    _formKey.currentState?.save();
    setState(() => _isSaving = true);

    final String id = widget.itemToEdit?.id ?? const Uuid().v4();

    // For new items, createdAt should be set. For existing, it should be preserved.
    // updatedAt is always set by Firestore.
    final Timestamp createdAt = widget.itemToEdit?.createdAt ?? Timestamp.now();

    final NewsItem item = NewsItem(
      id: id,
      title: _titleController.text.trim(),
      content: _contentController.text.trim(),
      author: _authorController.text.trim().isNotEmpty ? _authorController.text.trim() : null,
      type: _selectedType,
      category: _categoryController.text.trim().isNotEmpty ? _categoryController.text.trim() : null,
      imageUrl: _imageUrlController.text.trim().isNotEmpty ? _imageUrlController.text.trim() : null,
      createdAt: createdAt, // Use existing or new Timestamp
      // updatedAt is handled by Firestore via FieldValue.serverTimestamp() in toJson
      views: widget.itemToEdit?.views ?? 0, // Preserve existing views
    );

    try {
      if (_isEditing) {
        await _newsService.updateNewsItem(item);
      } else {
        await _newsService.addNewsItem(item);
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('مورد با موفقیت ذخیره شد.', style: const TextStyle(fontFamily: 'IranYekan'))),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطا در ذخیره مورد: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
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
          _isEditing ? 'ویرایش مورد' : 'افزودن مورد جدید',
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
                decoration: const InputDecoration(labelText: 'شناسه (ID)', border: OutlineInputBorder()),
                readOnly: true,
                style: TextStyle(fontFamily: 'IranYekan', color: _isEditing ? Colors.grey : null),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _titleController,
                decoration: const InputDecoration(labelText: 'عنوان', border: OutlineInputBorder()),
                validator: (value) => (value == null || value.trim().isEmpty) ? 'عنوان الزامی است' : null,
                style: const TextStyle(fontFamily: 'IranYekan'),
              ),
              const SizedBox(height: 12),
              DropdownButtonFormField<NewsItemType>(
                value: _selectedType,
                decoration: const InputDecoration(labelText: 'نوع', border: OutlineInputBorder()),
                items: NewsItemType.values.map((NewsItemType type) {
                  return DropdownMenuItem<NewsItemType>(
                    value: type,
                    child: Text(newsItemTypeToString(type) == 'news' ? 'خبر' : 'مقاله', style: const TextStyle(fontFamily: 'IranYekan')),
                  );
                }).toList(),
                onChanged: (NewsItemType? newValue) {
                  if (newValue != null) {
                    setState(() {
                      _selectedType = newValue;
                    });
                  }
                },
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _contentController,
                decoration: const InputDecoration(labelText: 'محتوا', border: OutlineInputBorder(), alignLabelWithHint: true),
                maxLines: 10, // For longer content
                keyboardType: TextInputType.multiline,
                validator: (value) => (value == null || value.trim().isEmpty) ? 'محتوا الزامی است' : null,
                style: const TextStyle(fontFamily: 'IranYekan'),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _authorController,
                decoration: const InputDecoration(labelText: 'نویسنده (اختیاری)', border: OutlineInputBorder()),
                style: const TextStyle(fontFamily: 'IranYekan'),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _categoryController,
                decoration: const InputDecoration(labelText: 'دسته بندی (اختیاری)', border: OutlineInputBorder()),
                style: const TextStyle(fontFamily: 'IranYekan'),
              ),
              const SizedBox(height: 12),
              TextFormField(
                controller: _imageUrlController,
                decoration: const InputDecoration(labelText: 'URL تصویر (اختیاری)', border: OutlineInputBorder()),
                keyboardType: TextInputType.url,
                style: const TextStyle(fontFamily: 'IranYekan'),
              ),
              const SizedBox(height: 24),
              if (_isSaving)
                const Center(child: CircularProgressIndicator())
              else
                ElevatedButton(
                  onPressed: _saveItem,
                  style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 12)),
                  child: Text(_isEditing ? 'ذخیره تغییرات' : 'افزودن مورد', style: const TextStyle(fontFamily: 'IranYekan', fontSize: 18)),
                ),
            ],
          ),
        ),
      ),
    );
  }
}
