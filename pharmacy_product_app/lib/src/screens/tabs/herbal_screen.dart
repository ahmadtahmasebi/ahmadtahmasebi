import 'package:flutter/material.dart';
import '../../models/product.dart';
import '../../models/category.dart';
import '../../services/product_service.dart';
import '../../services/category_service.dart';

final ProductService _productService = ProductService();
final CategoryService _categoryService = CategoryService();

class HerbalScreen extends StatefulWidget {
  @override
  _HerbalScreenState createState() => _HerbalScreenState();
}

class _HerbalScreenState extends State<HerbalScreen> {
  List<Category> _categories = [];
  List<Product> _products = [];
  List<Product> _filteredProducts = [];
  String? _selectedCategoryId;

  @override
  void initState() {
    super.initState();
    _loadData();
  }

  void _loadData() {
    setState(() {
      _categories = _categoryService.getAllCategories();
      _products = _productService.getAllProducts();
      _applyFilter();
    });
  }

  void _applyFilter() {
    if (_selectedCategoryId == null) {
      _filteredProducts = List.from(_products);
    } else {
      _filteredProducts = _productService.getProductsByCategoryId(_selectedCategoryId!);
    }
  }

  void _onCategorySelected(String? categoryId) {
    setState(() {
      _selectedCategoryId = categoryId;
      _applyFilter();
    });
  }

  Widget _buildCategoryFilters() {
    if (_categories.isEmpty) return Padding(padding: const EdgeInsets.all(8.0), child: Text("No categories available.", textAlign: TextAlign.center));
    List<Widget> filterChips = _categories.map((category) {
      bool isSelected = _selectedCategoryId == category.id;
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 4.0),
        child: FilterChip(
          label: Text(category.name),
          selected: isSelected,
          onSelected: (bool selected) {
            _onCategorySelected(selected ? category.id : null);
          },
          backgroundColor: isSelected ? Colors.green[100] : Colors.grey[200],
          selectedColor: Colors.green, // Theme color for Herbal
          labelStyle: TextStyle(color: isSelected ? Colors.white : Colors.black),
        ),
      );
    }).toList();
    filterChips.insert(
      0,
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 4.0),
        child: FilterChip(
          label: Text("All"),
          selected: _selectedCategoryId == null,
          onSelected: (bool selected) {
            _onCategorySelected(null);
          },
          backgroundColor: _selectedCategoryId == null ? Colors.green[100] : Colors.grey[200],
          selectedColor: Colors.green,
          labelStyle: TextStyle(color: _selectedCategoryId == null ? Colors.white : Colors.black),
        ),
      )
    );
    return Container(
      height: 60,
      child: ListView(
        scrollDirection: Axis.horizontal,
        padding: EdgeInsets.symmetric(vertical: 8.0, horizontal: 8.0),
        children: filterChips,
      ),
    );
  }

  Widget _buildProductList() {
    if (_filteredProducts.isEmpty) return Center(child: Padding(padding: const EdgeInsets.all(16.0), child: Text("No products found.", textAlign: TextAlign.center)));
    return ListView.builder(
      itemCount: _filteredProducts.length,
      itemBuilder: (context, index) {
        final product = _filteredProducts[index];
        final category = _categoryService.getCategoryById(product.categoryId);
        return Card(
          margin: EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          child: Padding(
            padding: const EdgeInsets.all(12.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                if (product.imagePath.isNotEmpty)
                  Container(height: 150, width: double.infinity, color: Colors.grey[300], alignment: Alignment.center, child: Icon(Icons.image, size: 50, color: Colors.grey[600]))
                else
                  Container(height: 150, width: double.infinity, color: Colors.grey[200], alignment: Alignment.center, child: Icon(Icons.image_not_supported, size: 50, color: Colors.grey[500])),
                SizedBox(height: 10),
                Text(product.name, style: Theme.of(context).textTheme.headline6),
                SizedBox(height: 4),
                Text(category?.name ?? 'Uncategorized', style: TextStyle(color: Colors.grey[600], fontSize: 12)),
                SizedBox(height: 8),
                Text(product.description.isNotEmpty ? product.description : 'No description.', maxLines: 2, overflow: TextOverflow.ellipsis),
                SizedBox(height: 8),
                Row(
                  mainAxisAlignment: MainAxisAlignment.spaceBetween,
                  children: [
                    Text('\$${product.price.toStringAsFixed(2)}', style: TextStyle(fontSize: 18, fontWeight: FontWeight.bold, color: Colors.green)),
                    Text('Stock: \${product.stock}', style: TextStyle(fontSize: 12)),
                  ],
                ),
              ],
            ),
          ),
        );
      },
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('گیاهی (Herbal)'),
        actions: [IconButton(icon: Icon(Icons.refresh), onPressed: _loadData, tooltip: 'Refresh Data')],
      ),
      body: Column(
        children: [
          _buildCategoryFilters(),
          Expanded(child: _buildProductList()),
        ],
      ),
    );
  }
}
