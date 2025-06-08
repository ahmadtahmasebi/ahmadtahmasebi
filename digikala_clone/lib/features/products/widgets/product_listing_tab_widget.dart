import 'package:flutter/material.dart';
import '../../../core/models/category_model.dart';
import '../../../core/models/product_model.dart';
import '../../../core/services/firestore_service.dart';
import '../../../core/services/product_service_interface.dart';
import '../../../core/services/category_service_interface.dart';
import './product_card.dart'; // Assuming ProductCard is in the same directory

class ProductListingTabWidget extends StatefulWidget {
  final String mainCategoryIdentifier; // e.g., "cosmetics", "electronics" - for future use

  const ProductListingTabWidget({Key? key, required this.mainCategoryIdentifier}) : super(key: key);

  @override
  _ProductListingTabWidgetState createState() => _ProductListingTabWidgetState();
}

class _ProductListingTabWidgetState extends State<ProductListingTabWidget> {
  late Stream<List<Category>> _subCategoriesStream;
  late Stream<List<Product>> _productsStream;
  String? _selectedSubCategoryId;

  final IProductService _productService = FirestoreService();
  final ICategoryService _categoryService = FirestoreService();

  @override
  void initState() {
    super.initState();
    // For now, _subCategoriesStream fetches ALL categories.
    // TODO: Later, filter sub-categories based on widget.mainCategoryIdentifier if needed
    _subCategoriesStream = _categoryService.getCategories();
    _updateProductsStream();
  }

  void _updateProductsStream() {
    if (mounted) { // Check if the widget is still in the tree
      setState(() {
        if (_selectedSubCategoryId == null || _selectedSubCategoryId == 'all') {
          // TODO: Potentially filter by widget.mainCategoryIdentifier if products have such a field
          // For now, shows all products if no sub-category is selected.
          _productsStream = _productService.getProducts();
        } else {
          _productsStream = _productService.getProductsByCategory(_selectedSubCategoryId!);
        }
      });
    }
  }

  void _onSubCategorySelected(String? categoryId) {
    // If the same chip is tapped again and it's already selected, treat as deselecting (show all)
    // Otherwise, set the new categoryId
    _selectedSubCategoryId = (_selectedSubCategoryId == categoryId) ? 'all' : categoryId;
    _updateProductsStream();
  }

  @override
  Widget build(BuildContext context) {
    return Column(
      crossAxisAlignment: CrossAxisAlignment.stretch,
      children: [
        _buildSubCategoryChips(),
        Expanded(
          child: StreamBuilder<List<Product>>(
            stream: _productsStream,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snapshot.hasError) {
                print("Error loading products in tab: ${snapshot.error}");
                return Center(child: Text('خطا در بارگذاری محصولات: ${snapshot.error}', style: const TextStyle(fontFamily: 'IranYekan')));
              }
              if (!snapshot.hasData || snapshot.data!.isEmpty) {
                return const Center(child: Text('محصولی یافت نشد.', style: TextStyle(fontFamily: 'IranYekan')));
              }
              final products = snapshot.data!;
              // Using GridView for better layout of product cards
              return GridView.builder(
                padding: const EdgeInsets.all(8.0),
                gridDelegate: const SliverGridDelegateWithFixedCrossAxisCount(
                  crossAxisCount: 2, // Number of columns
                  crossAxisSpacing: 8.0,
                  mainAxisSpacing: 8.0,
                  childAspectRatio: 0.7, // Adjust for desired card height/width ratio
                ),
                itemCount: products.length,
                itemBuilder: (context, index) {
                  return ProductCard(product: products[index]);
                },
              );
            },
          ),
        ),
      ],
    );
  }

  Widget _buildSubCategoryChips() {
    return StreamBuilder<List<Category>>(
      stream: _subCategoriesStream,
      builder: (context, snapshot) {
        if (!snapshot.hasData && snapshot.connectionState == ConnectionState.waiting) {
          return const Center(child: Padding(padding: EdgeInsets.all(8.0), child: CircularProgressIndicator()));
        }
        if (snapshot.hasError) {
          print("Error loading sub-categories: ${snapshot.error}");
          return Center(child: Text('خطا در بارگذاری دسته بندی های فرعی.', style: const TextStyle(fontFamily: 'IranYekan')));
        }
        if (!snapshot.hasData || snapshot.data!.isEmpty) {
          return const SizedBox(height: 50, child: Center(child: Text('دسته بندی فرعی یافت نشد.', style: TextStyle(fontFamily: 'IranYekan'))));
        }

        final categories = snapshot.data!;
        return Padding(
          padding: const EdgeInsets.symmetric(vertical: 8.0),
          child: SizedBox(
            height: 50,
            child: ListView(
              scrollDirection: Axis.horizontal,
              padding: const EdgeInsets.symmetric(horizontal: 8.0),
              children: [
                Padding(
                  padding: const EdgeInsets.symmetric(horizontal: 4.0),
                  child: ChoiceChip(
                    label: const Text('همه', style: TextStyle(fontFamily: 'IranYekan')),
                    selected: _selectedSubCategoryId == null || _selectedSubCategoryId == 'all',
                    onSelected: (selected) => _onSubCategorySelected('all'),
                    selectedColor: Colors.red[100],
                    backgroundColor: Colors.grey[200],
                  ),
                ),
                ...categories.map((category) {
                  return Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4.0),
                    child: ChoiceChip(
                      label: Text(category.name, style: const TextStyle(fontFamily: 'IranYekan')),
                      selected: _selectedSubCategoryId == category.id,
                      onSelected: (selected) => _onSubCategorySelected(category.id),
                      selectedColor: Colors.red[100],
                      backgroundColor: Colors.grey[200],
                    ),
                  );
                }).toList(),
              ],
            ),
          ),
        );
      },
    );
  }
}
