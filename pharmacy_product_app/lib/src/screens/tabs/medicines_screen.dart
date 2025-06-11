import 'package:flutter/material.dart';
import '../../models/product.dart';
import '../../models/category.dart';
import '../../services/product_service.dart';
import '../../services/category_service.dart';
import '../details/product_detail_screen.dart';

final ProductService _productService = ProductService();
final CategoryService _categoryService = CategoryService();

class MedicinesScreen extends StatefulWidget {
  @override
  createState() => _MedicinesScreenState();
}

class _MedicinesScreenState extends State<MedicinesScreen> {
  List<Category> _categories = [];
  List<Product> _products = []; // All products fetched
  List<Product> _filteredProducts = []; // Products for the selected category
  String? _selectedCategoryId;

  // Define a fixed height for product cards for consistent row height
  final double _productCardHeight = 280.0; // Increased height for better content visibility
  final double _productCardWidth = 180.0;

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
      _filteredProducts = [];
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
    if (_categories.isEmpty) {
      return Padding(
        padding: const EdgeInsets.all(8.0),
        child: Text("No categories available.", textAlign: TextAlign.center),
      );
    }
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
          backgroundColor: isSelected ? Colors.blue[100] : Colors.grey[200],
          selectedColor: Colors.blue,
          labelStyle: TextStyle(color: isSelected ? Colors.white : Colors.black),
        ),
      );
    }).toList();
    filterChips.insert(
      0,
      Padding(
        padding: const EdgeInsets.symmetric(horizontal: 4.0),
        child: FilterChip(
          label: Text("All Categories"),
          selected: _selectedCategoryId == null,
          onSelected: (bool selected) {
            _onCategorySelected(null);
          },
          backgroundColor: _selectedCategoryId == null ? Colors.blue[100] : Colors.grey[200],
          selectedColor: Colors.blue,
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

  Widget _buildProductCard(Product product) {
    final category = _categoryService.getCategoryById(product.categoryId);
    return Container(
      width: _productCardWidth,
      child: Card(
        margin: EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: () {
            Navigator.push(
              context,
              MaterialPageRoute(
                builder: (context) => ProductDetailScreen(product: product),
              ),
            );
          },
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              if (product.imagePath.isNotEmpty)
                Container(height: 120, width: double.infinity, color: Colors.grey[300], alignment: Alignment.center, child: Icon(Icons.image, size: 40, color: Colors.grey[600]))
              else
                Container(height: 120, width: double.infinity, color: Colors.grey[200], alignment: Alignment.center, child: Icon(Icons.image_not_supported, size: 40, color: Colors.grey[500])),
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(product.name, style: Theme.of(context).textTheme.subtitle1?.copyWith(fontWeight: FontWeight.bold), maxLines: 1, overflow: TextOverflow.ellipsis,),
                    SizedBox(height: 2),
                    Text(category?.name ?? 'Uncategorized', style: TextStyle(color: Colors.grey[600], fontSize: 10)),
                    SizedBox(height: 4),
                    Text(product.description.isNotEmpty ? product.description : 'No description.', maxLines: 2, overflow: TextOverflow.ellipsis, style: TextStyle(fontSize: 12)),
                    SizedBox(height: 6),
                    Text('\$${product.price.toStringAsFixed(2)}', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Colors.blue)),
                  ],
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildHorizontalProductList(String title, List<Product> productsInRow) {
    if (productsInRow.isEmpty) {
      return SizedBox.shrink();
    }
    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(
          padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
          child: Text(title, style: Theme.of(context).textTheme.headline6),
        ),
        Container(
          height: _productCardHeight,
          child: ListView.builder(
            scrollDirection: Axis.horizontal,
            itemCount: productsInRow.length,
            itemBuilder: (context, index) {
              return _buildProductCard(productsInRow[index]);
            },
            padding: EdgeInsets.symmetric(horizontal: 8.0),
          ),
        ),
      ],
    );
  }

  Widget _buildProductDisplay() {
    if (_selectedCategoryId != null) {
      if (_filteredProducts.isEmpty) {
        return Center(child: Padding(padding: const EdgeInsets.all(16.0), child: Text("No products found in this category.", textAlign: TextAlign.center)));
      }
      final categoryName = _categoryService.getCategoryById(_selectedCategoryId!)?.name ?? "Selected Category";
      return _buildHorizontalProductList(categoryName, _filteredProducts);
    } else {
      if (_categories.isEmpty) {
         return Center(child: Padding(padding: const EdgeInsets.all(16.0), child: Text("No categories found. Please add categories in Admin panel.", textAlign: TextAlign.center)));
      }
      List<Widget> categoryRows = _categories.map((category) {
        List<Product> productsForThisCategory = _productService.getProductsByCategoryId(category.id);
        if (productsForThisCategory.isNotEmpty) {
          return _buildHorizontalProductList(category.name, productsForThisCategory);
        }
        return SizedBox.shrink();
      }).toList();

      bool hasContent = categoryRows.any((widget) => widget is! SizedBox);
      if (!hasContent && _products.isEmpty) {
         return Center(child: Padding(padding: const EdgeInsets.all(16.0), child: Text("No products found. Please add products in Admin panel.", textAlign: TextAlign.center)));
      }
      if (!hasContent && _products.isNotEmpty) { // Products exist but not in any of the current categories
         return Center(child: Padding(padding: const EdgeInsets.all(16.0), child: Text("No products found for the available categories. Check product category assignments.", textAlign: TextAlign.center)));
      }

      return ListView(children: categoryRows);
    }
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('دارو (Medicines)'),
        actions: [IconButton(icon: Icon(Icons.refresh), onPressed: _loadData, tooltip: 'Refresh Data')],
      ),
      body: Column(
        children: [
          _buildCategoryFilters(),
          Expanded(child: _buildProductDisplay()),
        ],
      ),
    );
  }
}
