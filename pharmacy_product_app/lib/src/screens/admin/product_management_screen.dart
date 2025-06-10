import 'package:flutter/material.dart';
import 'package:flutter/services.dart'; // For TextInputFormatter
import '../../models/product.dart';
import '../../models/category.dart';
import '../../services/product_service.dart';
import '../../services/category_service.dart'; // To fetch categories for dropdown

// Initialize services (simple global instances for now)
final ProductService _productService = ProductService();
final CategoryService _categoryService = CategoryService(); // Already used in category_management_screen

class ProductManagementScreen extends StatefulWidget {
  @override
  _ProductManagementScreenState createState() => _ProductManagementScreenState();
}

class _ProductManagementScreenState extends State<ProductManagementScreen> {
  List<Product> _products = [];
  List<Category> _categories = [];
  String? _selectedCategoryId;
  Product? _selectedProduct; // For editing

  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController();
  final _priceController = TextEditingController();
  final _descriptionController = TextEditingController();
  final _imagePathController = TextEditingController(); // Simple text input for now
  final _stockController = TextEditingController();
  final _minStockController = TextEditingController();

  @override
  void initState() {
    super.initState();
    _loadProducts();
    _loadCategories();
  }

  void _loadProducts() {
    setState(() {
      _products = _productService.getAllProducts();
    });
  }

  void _loadCategories() {
    setState(() {
      _categories = _categoryService.getAllCategories();
      if (_categories.isNotEmpty && _selectedCategoryId == null) {
        //_selectedCategoryId = _categories.first.id; // Default to first category if none selected
      }
    });
  }

  void _addOrUpdateProduct() {
    if (_formKey.currentState!.validate()) {
      if (_selectedCategoryId == null && _categories.isNotEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Please select a category!')),
          );
          return;
      }
       if (_categories.isEmpty) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('Please add a category first!')),
          );
          return;
      }


      final productData = Product(
        id: _selectedProduct?.id ?? DateTime.now().millisecondsSinceEpoch.toString(), // Simple unique ID
        name: _nameController.text,
        categoryId: _selectedCategoryId!,
        price: double.tryParse(_priceController.text) ?? 0.0,
        description: _descriptionController.text,
        imagePath: _imagePathController.text,
        stock: int.tryParse(_stockController.text) ?? 0,
        minStock: int.tryParse(_minStockController.text) ?? 5,
        likes: _selectedProduct?.likes ?? 0,
        viewCount: _selectedProduct?.viewCount ?? 0,
      );

      if (_selectedProduct == null) { // Add new
        _productService.addProduct(productData);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Product added!')),
        );
      } else { // Update existing
        _productService.updateProduct(productData);
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('Product updated!')),
        );
      }
      _clearForm();
      _loadProducts();
    }
  }

  void _deleteProduct(String productId) {
    _productService.deleteProduct(productId);
    _loadProducts();
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Product deleted!')),
    );
  }

  void _selectProductForEditing(Product product) {
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

  void _clearForm() {
    setState(() {
      _selectedProduct = null;
      _formKey.currentState?.reset();
      _nameController.clear();
      _priceController.clear();
      _descriptionController.clear();
      _imagePathController.clear();
      _stockController.clear();
      _minStockController.clear();
      // _selectedCategoryId = _categories.isNotEmpty ? _categories.first.id : null; // Reset dropdown
      _selectedCategoryId = null;
       // If you want to reset the dropdown to the first item or null:
      if (_categories.isNotEmpty) {
       // _selectedCategoryId = _categories.first.id; // Or null to show hint text
      } else {
        _selectedCategoryId = null;
      }
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Manage Products'),
        actions: [
          IconButton(
            icon: Icon(Icons.clear_all),
            onPressed: _clearForm,
            tooltip: 'Clear Form',
          )
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Form(
          key: _formKey,
          child: Column(
            children: [
              // Form fields
              TextFormField(
                controller: _nameController,
                decoration: InputDecoration(labelText: 'Product Name'),
                validator: (value) => value == null || value.isEmpty ? 'Name is required' : null,
              ),
              if (_categories.isNotEmpty) // Only show dropdown if categories exist
                DropdownButtonFormField<String>(
                  value: _selectedCategoryId,
                  hint: Text('Select Category'),
                  isExpanded: true,
                  items: _categories.map((Category category) {
                    return DropdownMenuItem<String>(
                      value: category.id,
                      child: Text(category.name),
                    );
                  }).toList(),
                  onChanged: (String? newValue) {
                    setState(() {
                      _selectedCategoryId = newValue;
                    });
                  },
                  validator: (value) => value == null ? 'Category is required' : null,
                )
              else
                Padding(
                  padding: const EdgeInsets.symmetric(vertical: 8.0),
                  child: Text('No categories available. Please add categories first.', style: TextStyle(color: Colors.red)),
                ),
              TextFormField(
                controller: _priceController,
                decoration: InputDecoration(labelText: 'Price'),
                keyboardType: TextInputType.numberWithOptions(decimal: true),
                inputFormatters: <TextInputFormatter>[
                    FilteringTextInputFormatter.allow(RegExp(r'^\d*\.?\d*')),
                ],
                validator: (value) {
                  if (value == null || value.isEmpty) return 'Price is required';
                  if (double.tryParse(value) == null) return 'Invalid price';
                  return null;
                },
              ),
              TextFormField(
                controller: _stockController,
                decoration: InputDecoration(labelText: 'Stock Quantity'),
                keyboardType: TextInputType.number,
                inputFormatters: <TextInputFormatter>[FilteringTextInputFormatter.digitsOnly],
                 validator: (value) {
                  if (value == null || value.isEmpty) return 'Stock is required';
                  if (int.tryParse(value) == null) return 'Invalid stock quantity';
                  return null;
                }
              ),
              TextFormField(
                controller: _minStockController,
                decoration: InputDecoration(labelText: 'Min Stock (Alert Level)'),
                keyboardType: TextInputType.number,
                inputFormatters: <TextInputFormatter>[FilteringTextInputFormatter.digitsOnly],
                 validator: (value) {
                  if (value == null || value.isEmpty) return 'Min stock is required';
                  if (int.tryParse(value) == null) return 'Invalid min stock quantity';
                  return null;
                }
              ),
              TextFormField(
                controller: _descriptionController,
                decoration: InputDecoration(labelText: 'Description'),
                maxLines: 2,
              ),
              TextFormField(
                controller: _imagePathController,
                decoration: InputDecoration(labelText: 'Image Path (e.g., assets/image.png or URL)'),
              ),
              SizedBox(height: 20),
              ElevatedButton(
                onPressed: _addOrUpdateProduct,
                child: Text(_selectedProduct == null ? 'Add Product' : 'Update Product'),
              ),
              SizedBox(height: 10),
              Text('Existing Products', style: Theme.of(context).textTheme.headline6),
              Expanded(
                child: _products.isEmpty
                    ? Center(child: Text('No products found.'))
                    : ListView.builder(
                        itemCount: _products.length,
                        itemBuilder: (context, index) {
                          final product = _products[index];
                          final categoryName = _categoryService.getCategoryById(product.categoryId)?.name ?? 'Unknown Category';
                          return Card(
                            child: ListTile(
                              title: Text(product.name),
                              subtitle: Text('Category: $categoryName - Price: ${product.price} - Stock: ${product.stock}'),
                              trailing: Row(
                                mainAxisSize: MainAxisSize.min,
                                children: [
                                  IconButton(
                                    icon: Icon(Icons.edit, color: Colors.blue),
                                    onPressed: () => _selectProductForEditing(product),
                                  ),
                                  IconButton(
                                    icon: Icon(Icons.delete, color: Colors.red),
                                    onPressed: () => _deleteProduct(product.id),
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
      ),
    );
  }
}
