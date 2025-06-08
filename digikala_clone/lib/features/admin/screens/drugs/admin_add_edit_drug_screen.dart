import 'package:flutter/material.dart';
import 'package:uuid/uuid.dart';
import 'package:cloud_firestore/cloud_firestore.dart'; // For Timestamp
import '../../../../core/models/drug_model.dart';
import '../../../../core/models/category_model.dart'; // For category dropdown
import '../../../../core/services/firestore_service.dart';
import '../../../../core/services/drug_service_interface.dart';
import '../../../../core/services/category_service_interface.dart';

class AdminAddEditDrugScreen extends StatefulWidget {
  final Drug? drugToEdit;

  const AdminAddEditDrugScreen({Key? key, this.drugToEdit}) : super(key: key);

  @override
  _AdminAddEditDrugScreenState createState() => _AdminAddEditDrugScreenState();
}

class _AdminAddEditDrugScreenState extends State<AdminAddEditDrugScreen> {
  final _formKey = GlobalKey<FormState>();
  final IDrugService _drugService = FirestoreService();
  final ICategoryService _categoryService = FirestoreService();

  // Form field controllers
  late TextEditingController _idController;
  late TextEditingController _genericNameController;
  late TextEditingController _brandNamesController; // Comma-separated
  late TextEditingController _dosageFormsController;
  late TextEditingController _strengthController;
  late TextEditingController _pharmacologyController;
  late TextEditingController _indicationsController;
  late TextEditingController _contraindicationsController;
  late TextEditingController _sideEffectsController;
  late TextEditingController _drugInteractionsController;
  late TextEditingController _priceController;
  late TextEditingController _imageUrlController;

  String? _selectedCategoryId; // For internal drug categorization
  List<Category> _categories = []; // For the dropdown
  bool _isLoadingCategories = true;
  bool _isSaving = false;
  bool _isEditing = false;

  @override
  void initState() {
    super.initState();
    _isEditing = widget.drugToEdit != null;

    _idController = TextEditingController(text: widget.drugToEdit?.id ?? 'در صورت افزودن، خودکار ایجاد می‌شود');
    _genericNameController = TextEditingController(text: widget.drugToEdit?.genericName);
    _brandNamesController = TextEditingController(text: widget.drugToEdit?.brandNames.join(', '));
    _dosageFormsController = TextEditingController(text: widget.drugToEdit?.dosageForms);
    _strengthController = TextEditingController(text: widget.drugToEdit?.strength);
    _pharmacologyController = TextEditingController(text: widget.drugToEdit?.pharmacology);
    _indicationsController = TextEditingController(text: widget.drugToEdit?.indications);
    _contraindicationsController = TextEditingController(text: widget.drugToEdit?.contraindications);
    _sideEffectsController = TextEditingController(text: widget.drugToEdit?.sideEffects);
    _drugInteractionsController = TextEditingController(text: widget.drugToEdit?.drugInteractions);
    _priceController = TextEditingController(text: widget.drugToEdit?.price?.toString());
    _imageUrlController = TextEditingController(text: widget.drugToEdit?.imageUrl);
    _selectedCategoryId = widget.drugToEdit?.categoryId;

    _fetchCategories();
  }

  Future<void> _fetchCategories() async {
    setState(() => _isLoadingCategories = true);
    try {
      final categories = await _categoryService.getCategories().first;
      if (mounted) {
        setState(() {
          _categories = categories;
          if (_isEditing && widget.drugToEdit?.categoryId != null && !_categories.any((cat) => cat.id == _selectedCategoryId)) {
            // Category might have been deleted, or it's an old/invalid ID
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
    _idController.dispose();
    _genericNameController.dispose();
    _brandNamesController.dispose();
    _dosageFormsController.dispose();
    _strengthController.dispose();
    _pharmacologyController.dispose();
    _indicationsController.dispose();
    _contraindicationsController.dispose();
    _sideEffectsController.dispose();
    _drugInteractionsController.dispose();
    _priceController.dispose();
    _imageUrlController.dispose();
    super.dispose();
  }

  Future<void> _saveDrug() async {
    if (!(_formKey.currentState?.validate() ?? false)) return;
    _formKey.currentState?.save();
    setState(() => _isSaving = true);

    final String id = widget.drugToEdit?.id ?? const Uuid().v4();
    final List<String> brandNamesList = _brandNamesController.text.trim().split(',').map((s) => s.trim()).where((s) => s.isNotEmpty).toList();

    final Drug drug = Drug(
      id: id,
      genericName: _genericNameController.text.trim(),
      brandNames: brandNamesList,
      dosageForms: _dosageFormsController.text.trim(),
      strength: _strengthController.text.trim(),
      pharmacology: _pharmacologyController.text.trim(),
      indications: _indicationsController.text.trim(),
      contraindications: _contraindicationsController.text.trim(),
      sideEffects: _sideEffectsController.text.trim(),
      drugInteractions: _drugInteractionsController.text.trim(),
      price: double.tryParse(_priceController.text.trim()),
      categoryId: _selectedCategoryId,
      imageUrl: _imageUrlController.text.trim().isNotEmpty ? _imageUrlController.text.trim() : null,
      views: widget.drugToEdit?.views ?? 0,
      likes: widget.drugToEdit?.likes ?? 0,
      createdAt: widget.drugToEdit?.createdAt, // Handled by model/Firestore on create
      updatedAt: null, // Handled by model/Firestore on update
    );

    try {
      if (_isEditing) {
        await _drugService.updateDrug(drug);
      } else {
        await _drugService.addDrug(drug);
      }
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
           SnackBar(content: Text('دارو با موفقیت ذخیره شد.', style: const TextStyle(fontFamily: 'IranYekan'))),
        );
        Navigator.of(context).pop();
      }
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطا در ذخیره دارو: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
        );
      }
    } finally {
      if (mounted) {
        setState(() => _isSaving = false);
      }
    }
  }

  Widget _buildMultiLineFormField(TextEditingController controller, String label) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: TextFormField(
        controller: controller,
        decoration: InputDecoration(labelText: label, border: const OutlineInputBorder(), hintStyle: const TextStyle(fontFamily: 'IranYekan')),
        maxLines: null, // Allows multiple lines
        keyboardType: TextInputType.multiline,
        style: const TextStyle(fontFamily: 'IranYekan'),
      ),
    );
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(
          _isEditing ? 'ویرایش دارو' : 'افزودن دارو',
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
                      controller: _idController,
                      decoration: const InputDecoration(labelText: 'شناسه (ID)', border: OutlineInputBorder()),
                      readOnly: true,
                      style: TextStyle(fontFamily: 'IranYekan', color: _isEditing ? Colors.grey : null),
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _genericNameController,
                      decoration: const InputDecoration(labelText: 'نام ژنریک', border: OutlineInputBorder()),
                      validator: (value) => (value == null || value.trim().isEmpty) ? 'نام ژنریک الزامی است' : null,
                      style: const TextStyle(fontFamily: 'IranYekan'),
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _brandNamesController,
                      decoration: const InputDecoration(labelText: 'نام‌های تجاری (جدا شده با ویرگول)', border: OutlineInputBorder()),
                       style: const TextStyle(fontFamily: 'IranYekan'),
                    ),
                     const SizedBox(height: 12),
                    TextFormField(
                      controller: _dosageFormsController,
                      decoration: const InputDecoration(labelText: 'اشکال دارویی (مثال: قرص، شربت)', border: OutlineInputBorder()),
                      validator: (value) => (value == null || value.trim().isEmpty) ? 'اشکال دارویی الزامی است' : null,
                       style: const TextStyle(fontFamily: 'IranYekan'),
                    ),
                     const SizedBox(height: 12),
                    TextFormField(
                      controller: _strengthController,
                      decoration: const InputDecoration(labelText: 'قدرت دوز (مثال: 500mg)', border: OutlineInputBorder()),
                      validator: (value) => (value == null || value.trim().isEmpty) ? 'قدرت دوز الزامی است' : null,
                       style: const TextStyle(fontFamily: 'IranYekan'),
                    ),
                    const SizedBox(height: 12),
                     DropdownButtonFormField<String>(
                      value: _selectedCategoryId,
                      decoration: const InputDecoration(labelText: 'دسته‌بندی داخلی (اختیاری)', border: OutlineInputBorder()),
                      isExpanded: true,
                      hint: const Text('انتخاب دسته‌بندی', style: TextStyle(fontFamily: 'IranYekan')),
                      items: [
                        const DropdownMenuItem<String>(
                          value: null, // Option for no category
                          child: Text("هیچکدام", style: TextStyle(fontFamily: 'IranYekan', fontStyle: FontStyle.italic)),
                        ),
                        ..._categories.map((Category category) {
                        return DropdownMenuItem<String>(
                          value: category.id,
                          child: Text(category.name, style: const TextStyle(fontFamily: 'IranYekan')),
                        );
                      })],
                      onChanged: (String? newValue) {
                        setState(() {
                          _selectedCategoryId = newValue;
                        });
                      },
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _priceController,
                      decoration: const InputDecoration(labelText: 'قیمت (تومان - اختیاری)', border: OutlineInputBorder()),
                      keyboardType: TextInputType.number,
                       style: const TextStyle(fontFamily: 'IranYekan'),
                    ),
                    const SizedBox(height: 12),
                    TextFormField(
                      controller: _imageUrlController,
                      decoration: const InputDecoration(labelText: 'URL تصویر (اختیاری)', border: OutlineInputBorder()),
                      keyboardType: TextInputType.url,
                       style: const TextStyle(fontFamily: 'IranYekan'),
                    ),
                    const SizedBox(height: 12),
                    _buildMultiLineFormField(_pharmacologyController, 'فارماکولوژی (اختیاری)'),
                    _buildMultiLineFormField(_indicationsController, 'موارد مصرف (اختیاری)'),
                    _buildMultiLineFormField(_contraindicationsController, 'موارد منع مصرف (اختیاری)'),
                    _buildMultiLineFormField(_sideEffectsController, 'عوارض جانبی (اختیاری)'),
                    _buildMultiLineFormField(_drugInteractionsController, 'تداخلات دارویی (اختیاری)'),

                    const SizedBox(height: 24),
                    if (_isSaving)
                      const Center(child: CircularProgressIndicator())
                    else
                      ElevatedButton(
                        onPressed: _saveDrug,
                        style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 12)),
                        child: Text(_isEditing ? 'ذخیره تغییرات دارو' : 'افزودن دارو', style: const TextStyle(fontFamily: 'IranYekan', fontSize: 18)),
                      ),
                  ],
                ),
              ),
            ),
    );
  }
}
