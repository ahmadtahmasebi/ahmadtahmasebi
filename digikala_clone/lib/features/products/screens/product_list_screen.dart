import 'package:flutter/material.dart';
import '../../../core/models/category_model.dart'; // Import Category model
import '../../../core/models/product_model.dart';
import '../../../core/services/database_helper.dart';
import '../widgets/product_card.dart';

class ProductListScreen extends StatefulWidget {
  ProductListScreen({Key? key}) : super(key: key);

  @override
  _ProductListScreenState createState() => _ProductListScreenState();
}

class _ProductListScreenState extends State<ProductListScreen> {
  late Future<List<Product>> _productsFuture;
  late Future<List<Category>> _categoriesFuture;
  String? _selectedCategoryId;

  final DatabaseHelper _dbHelper = DatabaseHelper();

  final List<Category> _mockCategoriesSeed = [
    Category(id: 'cat1', name: 'الکترونیک'),
    Category(id: 'cat2', name: 'پوشاک'),
    Category(id: 'cat3', name: 'خانه و آشپزخانه'),
    Category(id: 'cat4', name: 'کتاب و لوازم التحریر'),
  ];

  final List<Product> _mockProductsSeed = [
    Product(
      id: '1',
      name: 'لپ تاپ حرفه ای با پردازنده قدرتمند',
      description: 'Description for product 1',
      imageUrl: 'https://picsum.photos/seed/lp1/200/200',
      price: 25000000,
      categoryId: 'cat1', // Electronics
    ),
    Product(
      id: '2',
      name: 'گوشی هوشمند جدید با دوربین عالی',
      description: 'Description for product 2',
      imageUrl: 'https://picsum.photos/seed/ph2/200/200',
      price: 15000000,
      categoryId: 'cat1', // Electronics
    ),
    Product(
      id: '3',
      name: 'تیشرت نخی آستین کوتاه مردانه',
      description: 'Description for product 3',
      imageUrl: 'https://picsum.photos/seed/ts3/200/200',
      price: 300000,
      categoryId: 'cat2', // Apparel
    ),
    Product(
      id: '4',
      name: 'سرویس قابلمه ۱۰ پارچه گرانیتی',
      description: 'Description for product 4',
      imageUrl: 'https://picsum.photos/seed/kp4/200/200',
      price: 3500000,
      categoryId: 'cat3', // Home & Kitchen
    ),
    Product(
      id: '5',
      name: 'هدفون بی سیم با کیفیت صدای عالی',
      description: 'Description for product 5',
      imageUrl: 'https://picsum.photos/seed/hp5/200/200',
      price: 1200000,
      categoryId: 'cat1', // Electronics
    ),
     Product(
      id: '6',
      name: 'کتاب مجموعه داستان کوتاه ایرانی',
      description: 'Description for product 6',
      imageUrl: 'https://picsum.photos/seed/bk6/200/200',
      price: 150000,
      categoryId: 'cat4', // Books
    ),
    Product(
      id: '7',
      name: 'کفش ورزشی مخصوص دویدن بانوان',
      description: 'Description for product 7',
      imageUrl: 'https://picsum.photos/seed/sh7/200/200',
      price: 1200000,
      categoryId: 'cat2', // Apparel
    ),
  ];

  @override
  void initState() {
    super.initState();
    _initializeData();
  }

  Future<void> _initializeData() async {
    await _dbHelper.database; // Ensure DB is initialized
    await _seedInitialData();
    _categoriesFuture = _dbHelper.getCategories();
    _productsFuture = _loadProducts();
    // Trigger a rebuild if initState finishes after the first frame
    if (mounted) {
       setState(() {});
    }
  }

  Future<void> _seedInitialData() async {
    List<Category> existingCategories = await _dbHelper.getCategories();
    if (existingCategories.isEmpty) {
      for (var category in _mockCategoriesSeed) {
        await _dbHelper.addCategory(category);
      }
    }

    List<Product> existingProducts = await _dbHelper.getProducts();
    if (existingProducts.isEmpty) {
      for (var product in _mockProductsSeed) {
        await _dbHelper.addProduct(product);
      }
    }
  }

  Future<List<Product>> _loadProducts() async {
    if (_selectedCategoryId == null || _selectedCategoryId == 'all') {
      return _dbHelper.getProducts();
    } else {
      return _dbHelper.getProductsByCategoryId(_selectedCategoryId!);
    }
  }

  void _onCategorySelected(String? categoryId) {
    setState(() {
      _selectedCategoryId = categoryId;
      _productsFuture = _loadProducts();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('محصولات'),
        backgroundColor: Colors.red[700],
      ),
      body: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildCategoryChips(),
          Expanded(
            child: Padding(
              padding: const EdgeInsets.all(8.0),
              child: FutureBuilder<List<Product>>(
                future: _productsFuture,
                builder: (context, snapshot) {
                  if (snapshot.connectionState == ConnectionState.waiting) {
                    return const Center(child: CircularProgressIndicator());
                  } else if (snapshot.hasError) {
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
                  }
                  else {
                    return const Center(child: Text('محصولی یافت نشد.'));
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
    return FutureBuilder<List<Category>>(
      future: _categoriesFuture,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting) {
          return const Padding(
            padding: EdgeInsets.all(8.0),
            child: Center(child: SizedBox(height: 30, width: 30, child: CircularProgressIndicator())),
          );
        } else if (snapshot.hasError) {
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
                          _onCategorySelected(selected ? category.id : null);
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
            child: Text('دسته بندی یافت نشد.'),
          );
        }
      },
    );
  }
}
