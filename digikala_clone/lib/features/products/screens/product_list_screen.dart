import 'package:flutter/material.dart';
import '../../../core/models/category_model.dart';
import '../../../core/models/product_model.dart';
import '../../../core/services/firestore_service.dart'; // Import FirestoreService
import '../../../core/services/product_service_interface.dart';
import '../../../core/services/category_service_interface.dart';
import '../widgets/product_card.dart';
import '../../../shared/widgets/app_drawer.dart'; // Import AppDrawer

class ProductListScreen extends StatefulWidget {
  ProductListScreen({Key? key}) : super(key: key);

  @override
  _ProductListScreenState createState() => _ProductListScreenState();
}

class _ProductListScreenState extends State<ProductListScreen> {
  late Stream<List<Product>> _productsStream;
  late Stream<List<Category>> _categoriesStream;
  String? _selectedCategoryId;

  // Use interfaces for service declaration, instantiate with FirestoreService
  final IProductService _productService = FirestoreService();
  final ICategoryService _categoryService = FirestoreService();


  // Mock data for initial Firestore seeding (if needed, can be done via Firestore console too)
  // For this subtask, we assume data is either already in Firestore or will be added manually.
  // The old _mockCategoriesSeed and _mockProductsSeed are removed as per task.

  @override
  void initState() {
    super.initState();
    _initializeStreams();
  }

  void _initializeStreams() {
    _categoriesStream = _categoryService.getCategories();
    _updateProductStream(); // Initial product stream
  }

  void _updateProductStream() {
    if (_selectedCategoryId == null || _selectedCategoryId == 'all') {
      _productsStream = _productService.getProducts();
    } else {
      _productsStream = _productService.getProductsByCategory(_selectedCategoryId!);
    }
  }

  void _onCategorySelected(String? categoryId) {
    setState(() {
      _selectedCategoryId = categoryId;
      _updateProductStream(); // Update the product stream based on new selection
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('محصولات'),
        backgroundColor: Colors.red[700],
      ),
      drawer: const AppDrawer(), // Add the AppDrawer to the Scaffold
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildCategoryChips(),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(8.0),
              child: StreamBuilder<List<Product>>(
                stream: _productsStream,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  } else if (snapshot.hasError) {
                    print('Product Stream Error: ${snapshot.error}');
                    print('Stack trace: ${snapshot.stackTrace}');
                    return Center(child: Text('خطا در بارگذاری محصولات: ${snapshot.error}'));
                  } else if (snapshot.hasData && snapshot.data != null && snapshot.data!.isNotEmpty) {
                    final products = snapshot.data!;
                    return SizedBox(
                      height: 250,
                      child: ListView.builder(
                        scrollDirection: Axis.horizontal,
                        itemCount: products.length,
                        itemBuilder: (context, index) {
                          return Padding(
                            padding: const EdgeInsets.symmetric(horizontal: 4.0),
                            child: ProductCard(product: products[index]),
                          );
                        },
                      ),
                    );
                  } else if (snapshot.hasData && (snapshot.data == null || snapshot.data!.isEmpty)) {
                     return const Center(child: Text('محصولی در این دسته بندی یافت نشد.'));
                  } else {
                    return const Center(child: Text('محصولی یافت نشد یا در حال بارگذاری...')); // Default message
                  }
                },
              ),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildCategoryChips() {
    return StreamBuilder<List<Category>>(
      stream: _categoriesStream,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting && !snapshot.hasData) { // Show loader only if no data yet
          return const Padding(
            padding: EdgeInsets.all(8.0),
            child: Center(child: SizedBox(height: 30, width: 30, child: CircularProgressIndicator())),
          );
        } else if (snapshot.hasError) {
          print('Category Stream Error: ${snapshot.error}');
          return Padding(
            padding: const EdgeInsets.all(8.0),
            child: Text('خطا در بارگذاری دسته بندی ها: ${snapshot.error}'),
          );
        } else if (snapshot.hasData && snapshot.data != null && snapshot.data!.isNotEmpty) {
          List<Category> categories = snapshot.data!;
          return Padding(
            padding: const EdgeInsets.symmetric(vertical: 8.0, horizontal: 4.0),
            child: SizedBox(
              height: 50,
              child: ListView(
                scrollDirection: Axis.horizontal,
                children: [
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 4.0),
                    child: ChoiceChip(
                      label: const Text('همه'),
                      selected: _selectedCategoryId == null || _selectedCategoryId == 'all',
                      onSelected: (selected) {
                        _onCategorySelected('all');
                      },
                      selectedColor: Colors.red[100],
                      backgroundColor: Colors.grey[200],
                    ),
                  ),
                  ...categories.map((category) {
                    return Padding(
                      padding: const EdgeInsets.symmetric(horizontal: 4.0),
                      child: ChoiceChip(
                        label: Text(category.name),
                        selected: _selectedCategoryId == category.id,
                        onSelected: (selected) {
                           // If unselecting a chip, it means "all" unless another is selected immediately
                          _onCategorySelected(selected ? category.id : 'all');
                        },
                        selectedColor: Colors.red[100],
                        backgroundColor: Colors.grey[200],
                      ),
                    );
                  }).toList(),
                ],
              ),
            ),
          );
        } else {
          return const Padding(
            padding: EdgeInsets.all(8.0),
            child: Text('دسته بندی یافت نشد.'), // Or a quiet loader
          );
        }
      },
    );
  }
}
