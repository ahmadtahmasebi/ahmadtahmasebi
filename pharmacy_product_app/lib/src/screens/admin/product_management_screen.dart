import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; // For TextInputFormatter
import '../../models/product.dart';
import '../../models/category.dart';
import '../../services/product_service.dart';
import '../../services/category_service.dart';

final ProductService _productService = ProductService();
final CategoryService _categoryService = CategoryService();

class ProductManagementScreen extends StatefulWidget {
  @override
  _ProductManagementScreenState createState() => _ProductManagementScreenState();
}

class _ProductManagementScreenState extends State<ProductManagementScreen> {
  List<Product> _allProducts = [];
  List<Product> _filteredProducts = [];
  List<Category> _categories = [];
  String? _selectedCategoryId;
  Product? _selectedProduct;

  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _priceController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _imagePathController = TextEditingController();
  final _stockController = TextEditingController();
  final _minStockController = TextEditingController();
  final _searchController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadInitialData();
    _searchController.addListener(_filterProducts);
  }

  @override
  void dispose() {
    _searchController.removeListener(_filterProducts);
    _searchController.dispose();
    _nameController.dispose();
    _priceController.dispose();
    _descriptionController.dispose();
    _imagePathController.dispose();
    _stockController.dispose();
    _minStockController.dispose();
    super.dispose();
  }

  void _loadInitialData() {
    if (mounted) {
      setState(() {
        _allProducts = _productService.getAllProducts();
        _filteredProducts = List.from(_allProducts);
        _categories = _categoryService.getAllCategories();
      });
    }
  }

  void _filterProducts() {
    String searchTerm = _searchController.text.toLowerCase();
    if (mounted) {
      setState(() {
        if (searchTerm.isEmpty) {
          _filteredProducts = List.from(_allProducts);
        } else {
          _filteredProducts = _allProducts
              .where((product) =>
                  product.name.toLowerCase().contains(searchTerm))
              .toList();
        }
      });
    }
  }

  void _showExcelImportInfo() {
    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text('قابلیت وارد کردن از اکسل'),
          content: Text(
            'متاسفانه این قابلیت در حال حاضر به دلیل محدودیت‌های محیطی (عدم امکان افزودن پکیج‌های پردازش فایل) در دسترس نیست. در آینده این امکان اضافه خواهد شد.',
            textAlign: TextAlign.right, // For Farsi
            style: TextStyle(fontFamily: 'Vazir', height: 1.5),
          ),
          actions: <Widget>[
            TextButton(
              child: Text('متوجه شدم', style: TextStyle(fontFamily: 'Vazir')),
              onPressed: () {
                Navigator.of(context).pop();
              },
            ),
          ],
        );
      },
    );
  }

  void _addOrUpdateProduct() {
    if (_formKey.currentState!.validate()) {
      if (_selectedCategoryId == null && _categories.isNotEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('لطفا دسته‌بندی را انتخاب کنید!')));
        return;
      }
      if (_categories.isEmpty) {
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('ابتدا یک دسته‌بندی اضافه کنید!')));
        return;
      }

      final productData = Product(
        id: _selectedProduct?.id ?? DateTime.now().millisecondsSinceEpoch.toString(),
        name: _nameController.text,
        categoryId: _selectedCategoryId!,
        price: double.tryParse(_priceController.text) ?? 0.0,
        description: _descriptionController.text,
        imagePath: _imagePathController.text,
        stock: int.tryParse(_stockController.text) ?? 0,
        minStock: int.tryParse(_minStockController.text) ?? 5,
        likes: _selectedProduct?.likes ?? 0,
        viewCount: _selectedProduct?.viewCount ?? 0,
        comments: _selectedProduct?.comments ?? [], // Ensure comments list is preserved
      );

      if (_selectedProduct == null) {
        _productService.addProduct(productData);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('محصول اضافه شد!')));
      } else {
        _productService.updateProduct(productData);
        ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('محصول به‌روزرسانی شد!')));
      }
      _clearForm();
      _loadInitialData();
      _filterProducts();
    }
  }

  void _deleteProduct(String productId) {
    _productService.deleteProduct(productId);
    _loadInitialData();
    _filterProducts();
    ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('محصول حذف شد!')));
  }

  void _selectProductForEditing(Product product) {
    if (mounted) {
      setState(() {
        _selectedProduct = product;
        _nameController.text = product.name;
        _priceController.text = product.price.toString();
        _selectedCategoryId = product.categoryId;
        _descriptionController.text = product.description;
        _imagePathController.text = product.imagePath;
        _stockController.text = product.stock.toString();
        _minStockController.text = product.minStock.toString();
      });
    }
  }

  void _clearForm() {
    if (mounted) {
      setState(() {
        _selectedProduct = null;
        _formKey.currentState?.reset();
        _nameController.clear();
        _priceController.clear();
        _descriptionController.clear();
        _imagePathController.clear();
        _stockController.clear();
        _minStockController.clear();
        // _selectedCategoryId = _categories.isNotEmpty && _categories.any((c) => c.id == _selectedCategoryId) ? _selectedCategoryId : null;
         if (_categories.isNotEmpty) {
            bool currentCategoryStillValid = _categories.any((c) => c.id == _selectedCategoryId);
            if(!currentCategoryStillValid) _selectedCategoryId = null;
         } else {
             _selectedCategoryId = null;
         }
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('مدیریت محصولات'),
        actions: [
          IconButton(icon: Icon(Icons.clear_all), onPressed: _clearForm, tooltip: 'پاک کردن فرم'),
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            Card(
              elevation: 2,
              margin: EdgeInsets.only(bottom: 16),
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Form(
                  key: _formKey,
                  child: Column(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      TextFormField(controller: _nameController, decoration: InputDecoration(labelText: 'نام محصول'), validator: (value) => value == null || value.isEmpty ? 'نام محصول الزامی است' : null),
                      SizedBox(height: 10),
                      if (_categories.isNotEmpty)
                        DropdownButtonFormField<String>(value: _selectedCategoryId, hint: Text('انتخاب دسته‌بندی'), isExpanded: true, decoration: InputDecoration(border: OutlineInputBorder()), items: _categories.map((Category category) => DropdownMenuItem<String>(value: category.id, child: Text(category.name))).toList(), onChanged: (String? newValue) { if (mounted) setState(() => _selectedCategoryId = newValue); }, validator: (value) => value == null ? 'دسته‌بندی الزامی است' : null)
                      else
                        Padding(padding: const EdgeInsets.symmetric(vertical: 8.0), child: Text('دسته‌بندی موجود نیست. ابتدا دسته‌بندی اضافه کنید.', style: TextStyle(color: Colors.red))),
                      SizedBox(height: 10),
                      Row(children: [
                        Expanded(child: TextFormField(controller: _priceController, decoration: InputDecoration(labelText: 'قیمت'), keyboardType: TextInputType.numberWithOptions(decimal: true), inputFormatters: <TextInputFormatter>[FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*'))], validator: (value) => (value == null || value.isEmpty) ? 'قیمت الزامی است' : (double.tryParse(value) == null ? 'قیمت نامعتبر' : null))), SizedBox(width: 10),
                        Expanded(child: TextFormField(controller: _stockController, decoration: InputDecoration(labelText: 'موجودی'), keyboardType: TextInputType.number, inputFormatters: <TextInputFormatter>[FilteringTextInputFormatter.digitsOnly], validator: (value) => (value == null || value.isEmpty) ? 'موجودی الزامی است' : (int.tryParse(value) == null ? 'موجودی نامعتبر' : null))), SizedBox(width: 10),
                        Expanded(child: TextFormField(controller: _minStockController, decoration: InputDecoration(labelText: 'حداقل موجودی'), keyboardType: TextInputType.number, inputFormatters: <TextInputFormatter>[FilteringTextInputFormatter.digitsOnly], validator: (value) => (value == null || value.isEmpty) ? 'حداقل موجودی الزامی است' : (int.tryParse(value) == null ? 'حداقل موجودی نامعتبر' : null))),
                      ]),
                      SizedBox(height: 10),
                      TextFormField(controller: _descriptionController, decoration: InputDecoration(labelText: 'توضیحات محصول'), maxLines: 3),
                      SizedBox(height: 10),
                      TextFormField(controller: _imagePathController, decoration: InputDecoration(labelText: 'مسیر عکس (نمایشی)')),
                      SizedBox(height: 16),
                      ElevatedButton(onPressed: _addOrUpdateProduct, child: Text(_selectedProduct == null ? 'افزودن محصول' : 'ذخیره تغییرات محصول'), style: ElevatedButton.styleFrom(minimumSize: Size(double.infinity, 40))),
                      SizedBox(height: 10),
                      OutlinedButton.icon(
                        icon: Icon(Icons.upload_file_outlined, color: Colors.grey[700]),
                        label: Text('وارد کردن از اکسل (راهنما)', style: TextStyle(color: Colors.grey[700], fontFamily: 'Vazir')),
                        onPressed: _showExcelImportInfo,
                        style: OutlinedButton.styleFrom(
                          minimumSize: Size(double.infinity, 36),
                          side: BorderSide(color: Colors.grey[400]!),
                        ),
                      ),
                    ],
                  ),
                ),
              ),
            ),
            Padding(
              padding: const EdgeInsets.symmetric(vertical: 8.0),
              child: TextField(controller: _searchController, decoration: InputDecoration(labelText: 'جستجو بر اساس نام محصول...', hintText: 'نام محصول را وارد کنید', prefixIcon: Icon(Icons.search), border: OutlineInputBorder(borderRadius: BorderRadius.circular(8.0)))),
            ),
            Text('لیست محصولات موجود', style: Theme.of(context).textTheme.subtitle1?.copyWith(fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Expanded(
              child: _filteredProducts.isEmpty
                  ? Center(child: Text(_searchController.text.isEmpty ? 'محصولی یافت نشد.' : 'نتیجه‌ای برای جستجوی شما یافت نشد.'))
                  : ListView.builder(
                      itemCount: _filteredProducts.length,
                      itemBuilder: (context, index) {
                        final product = _filteredProducts[index];
                        final categoryName = _categoryService.getCategoryById(product.categoryId)?.name ?? 'نامشخص';
                        return Card(
                          elevation: 1.5,
                          margin: EdgeInsets.symmetric(vertical: 4.0),
                          child: ListTile(
                            leading: Container(width: 50, height: 50, color: Colors.grey[200], child: product.imagePath.isNotEmpty ? Icon(Icons.image_outlined, color: Colors.grey[500]) : Icon(Icons.image_not_supported_outlined, color: Colors.grey[400])),
                            title: Text(product.name, style: TextStyle(fontWeight: FontWeight.bold)),
                            subtitle: Column(crossAxisAlignment: CrossAxisAlignment.start, children: [Text('دسته: $categoryName'), Text('قیمت: ${product.price.toStringAsFixed(0)} ت - موجودی: ${product.stock}')]),
                            trailing: Row(mainAxisSize: MainAxisSize.min, children: [IconButton(icon: Icon(Icons.edit_outlined, color: Colors.blueAccent, size: 20), onPressed: () => _selectProductForEditing(product), tooltip: 'ویرایش'), IconButton(icon: Icon(Icons.delete_outline, color: Colors.redAccent, size: 20), onPressed: () => _deleteProduct(product.id), tooltip: 'حذف')]),
                            onTap: () => _selectProductForEditing(product),
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
