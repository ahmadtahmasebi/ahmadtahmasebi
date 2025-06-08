import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import 'package:cloud_firestore/cloud_firestore.dart'; // For Timestamp
import '../../../../core/models/product_model.dart';
import '../../../../core/models/category_model.dart'; // For category dropdown
import '../../../../core/services/firestore_service.dart';
import '../../../../core/services/product_service_interface.dart';
import '../../../../core/services/category_service_interface.dart';

class AdminAddEditProductScreen extends StatefulWidget {
  final Product? productToEdit;

  const AdminAddEditProductScreen({Key? key, this.productToEdit}) : super(key: key);

  @override
  _AdminAddEditProductScreenState createState() => _AdminAddEditProductScreenState();
}

class _AdminAddEditProductScreenState extends State<AdminAddEditProductScreen> {
  final _formKey = GlobalKey<FormState>();
  final IProductService _productService = FirestoreService();
  final ICategoryService _categoryService = FirestoreService(); // For category dropdown

  // Form field controllers
  late TextEditingController _nameController;
  late TextEditingController _descriptionController;
  late TextEditingController _imageUrlController;
  late TextEditingController _priceController;
  late TextEditingController _brandController;
  late TextEditingController _countryOfOriginController;
  // For specificFeatures, a simple approach for now: manage as a list of key-value pairs
  List<MapEntry<String, String>> _specificFeaturesList = [];
  final _featureKeyController = TextEditingController();
  final _featureValueController = TextEditingController();


  String? _selectedCategoryId;
  List<Category> _categories = [];
  bool _isLoadingCategories = true;
  bool _isSaving = false;

  @override
  void initState() {
    super.initState();
    _nameController = TextEditingController(text: widget.productToEdit?.name);
    _descriptionController = TextEditingController(text: widget.productToEdit?.description);
    _imageUrlController = TextEditingController(text: widget.productToEdit?.imageUrl);
    _priceController = TextEditingController(text: widget.productToEdit?.price.toString());
    _selectedCategoryId = widget.productToEdit?.categoryId;
    _brandController = TextEditingController(text: widget.productToEdit?.brand);
    _countryOfOriginController = TextEditingController(text: widget.productToEdit?.countryOfOrigin);

    if (widget.productToEdit?.specificFeatures != null) {
      _specificFeaturesList = widget.productToEdit!.specificFeatures!.entries.toList();
    }
    _fetchCategories();
  }

  Future<void> _fetchCategories() async {
    setState(() => _isLoadingCategories = true);
    try {
      // Using a stream and taking the first event for initial load
      final categories = await _categoryService.getCategories().first;
      if (mounted) {
        setState(() {
          _categories = categories;
          // Ensure _selectedCategoryId is valid if product is being edited
          if (widget.productToEdit != null && !_categories.any((cat) => cat.id == _selectedCategoryId)) {
            _selectedCategoryId = null;
          }
          _isLoadingCategories = false;
        });
      }
    } catch (e) {
      if (mounted) {
        setState(() => _isLoadingCategories = false);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطا در بارگذاری دسته‌بندی‌ها: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
        );
      }
    }
  }

  @override
  void dispose() {
    _nameController.dispose();
    _descriptionController.dispose();
    _imageUrlController.dispose();
    _priceController.dispose();
    _brandController.dispose();
    _countryOfOriginController.dispose();
    _featureKeyController.dispose();
    _featureValueController.dispose();
    super.dispose();
  }

  void _addFeature() {
    if (_featureKeyController.text.isNotEmpty && _featureValueController.text.isNotEmpty) {
      setState(() {
        _specificFeaturesList.add(MapEntry(_featureKeyController.text, _featureValueController.text));
        _featureKeyController.clear();
        _featureValueController.clear();
      });
    }
  }

  void _removeFeature(int index) {
    setState(() {
      _specificFeaturesList.removeAt(index);
    });
  }

  Future<void> _saveProduct() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    if (_selectedCategoryId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('لطفا یک دسته‌بندی انتخاب کنید.', style: TextStyle(fontFamily: 'IranYekan'))),
      );
      return;
    }
    _formKey.currentState?.save();
    setState(() => _isSaving = true);

    final String id = widget.productToEdit?.id ?? const Uuid().v4();
    final Map<String, String> specificFeaturesMap = Map.fromEntries(_specificFeaturesList);

    final Product product = Product(
      id: id,
      name: _nameController.text.trim(),
      description: _descriptionController.text.trim(),
      imageUrl: _imageUrlController.text.trim(),
      price: double.tryParse(_priceController.text.trim()) ?? 0.0,
      categoryId: _selectedCategoryId!,
      brand: _brandController.text.trim().isNotEmpty ? _brandController.text.trim() : null,
      countryOfOrigin: _countryOfOriginController.text.trim().isNotEmpty ? _countryOfOriginController.text.trim() : null,
      specificFeatures: specificFeaturesMap.isNotEmpty ? specificFeaturesMap : null,
      views: widget.productToEdit?.views ?? 0,
      likes: widget.productToEdit?.likes ?? 0,
      likedBy: widget.productToEdit?.likedBy ?? [],
      createdAt: widget.productToEdit?.createdAt, // Will be set by serverTimestamp in toJson if null
      updatedAt: null, // Will be set by serverTimestamp in toJson
    );

    try {
      if (widget.productToEdit == null) {
        await _productService.addProduct(product);
      } else {
        await _productService.updateProduct(product);
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('محصول با موفقیت ذخیره شد.', style: const TextStyle(fontFamily: 'IranYekan'))),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطا در ذخیره محصول: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
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
          widget.productToEdit == null ? 'افزودن محصول' : 'ویرایش محصول',
          style: const TextStyle(fontFamily: 'IranYekan'),
        ),
      ),
      body: _isLoadingCategories
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16.0),
              child: Form(
                key: _formKey,
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.stretch,
                  children: <Widget>[
                    TextFormField(
                      controller: _nameController,
                      decoration: const InputDecoration(labelText: 'نام محصول', border: OutlineInputBorder()),
                      validator: (value) => (value == null || value.isEmpty) ? 'نام محصول الزامی است' : null,
                      style: const TextStyle(fontFamily: 'IranYekan'),
                    ),
                    const SizedBox(height: 12),
                    DropdownButtonFormField<String>(
                      value: _selectedCategoryId,
                      decoration: const InputDecoration(labelText: 'دسته‌بندی', border: OutlineInputBorder()),
                      isExpanded: true,
                      hint: const Text('انتخاب دسته‌بندی', style: TextStyle(fontFamily: 'IranYekan')),
                      items: _categories.map((Category category) {
                        return DropdownMenuItem<String>(
                          value: category.id,
                          child: Text(category.name, style: const TextStyle(fontFamily: 'IranYekan')),
                        );
                      }).toList(),
                      onChanged: (String? newValue) {
                        setState(() {
                          _selectedCategoryId = newValue;
                        });
                      },
                      validator: (value) => value == null ? 'انتخاب دسته‌بندی الزامی است' : null,
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _descriptionController,
                      decoration: const InputDecoration(labelText: 'توضیحات', border: OutlineInputBorder()),
                      maxLines: 3,
                      style: const TextStyle(fontFamily: 'IranYekan'),
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _imageUrlController,
                      decoration: const InputDecoration(labelText: 'URL تصویر محصول', border: OutlineInputBorder()),
                      keyboardType: TextInputType.url,
                      style: const TextStyle(fontFamily: 'IranYekan'),
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _priceController,
                      decoration: const InputDecoration(labelText: 'قیمت (تومان)', border: OutlineInputBorder()),
                      keyboardType: TextInputType.number,
                      validator: (value) {
                        if (value == null || value.isEmpty) return 'قیمت الزامی است';
                        if (double.tryParse(value) == null) return 'قیمت معتبر نیست';
                        return null;
                      },
                      style: const TextStyle(fontFamily: 'IranYekan'),
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _brandController,
                      decoration: const InputDecoration(labelText: 'برند (اختیاری)', border: OutlineInputBorder()),
                      style: const TextStyle(fontFamily: 'IranYekan'),
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _countryOfOriginController,
                      decoration: const InputDecoration(labelText: 'کشور سازنده (اختیاری)', border: OutlineInputBorder()),
                      style: const TextStyle(fontFamily: 'IranYekan'),
                    ),
                    const SizedBox(height: 16),
                    Text('ویژگی‌های خاص (اختیاری):', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontFamily: 'IranYekan')),
                    ListView.builder(
                      shrinkWrap: true,
                      physics: const NeverScrollableScrollPhysics(),
                      itemCount: _specificFeaturesList.length,
                      itemBuilder: (context, index) {
                        return Row(
                          children: [
                            Expanded(child: Text('${_specificFeaturesList[index].key}: ${_specificFeaturesList[index].value}', style: const TextStyle(fontFamily: 'IranYekan'))),
                            IconButton(icon: const Icon(Icons.remove_circle_outline, color: Colors.red), onPressed: () => _removeFeature(index))
                          ],
                        );
                      },
                    ),
                    Row(children: [
                      Expanded(child: TextFormField(controller: _featureKeyController, decoration: const InputDecoration(labelText: 'نام ویژگی', hintStyle: TextStyle(fontFamily: 'IranYekan')))),
                      const SizedBox(width: 8),
                      Expanded(child: TextFormField(controller: _featureValueController, decoration: const InputDecoration(labelText: 'مقدار ویژگی', hintStyle: TextStyle(fontFamily: 'IranYekan')))),
                      IconButton(icon: const Icon(Icons.add_circle_outline, color: Colors.green), onPressed: _addFeature)
                    ]),
                    const SizedBox(height: 24),
                    if (_isSaving)
                      const Center(child: CircularProgressIndicator())
                    else
                      ElevatedButton(
                        onPressed: _saveProduct,
                        style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 12)),
                        child: Text(widget.productToEdit == null ? 'افزودن محصول' : 'ذخیره تغییرات', style: const TextStyle(fontFamily: 'IranYekan', fontSize: 18)),
                      ),
                  ],
                ),
              ),
            ),
    );
  }
}
