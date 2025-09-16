import 'package:flutter/material.dart';
import '../../models/product.dart';
import '../../models/category.dart';
import '../../services/product_service.dart';
import '../../services/category_service.dart';
import '../details/product_detail_screen.dart';

// Assuming global service instances are available
final ProductService _productService = ProductService();
final CategoryService _categoryService = CategoryService();

class MedicinesScreen extends StatefulWidget {
  @override
  _MedicinesScreenState createState() => _MedicinesScreenState();
}

class _MedicinesScreenState extends State<MedicinesScreen> {
  List<Category> _allCategories = [];
  List<Category> _displayCategories = [];
  List<Product> _products = [];
  List<Product> _filteredProductsForSelectedCategory = [];
  String? _selectedCategoryId;

  final double _productCardHeight = 280.0;
  final double _productCardWidth = 180.0;
  final String _tabMasterType = 'medicines';

  // PageController for the ad slider
  PageController _adPageController = PageController(viewportFraction: 0.9);

  @override
  void initState() {
    super.initState();
    _loadData();
    // Note: Auto-scroll Timer for ad slider omitted for subtask simplicity for now.
  }

  @override
  void dispose() {
    _adPageController.dispose(); // Dispose controller
    super.dispose();
  }

  void _loadData() {
    if (!mounted) return;
    setState(() {
      _allCategories = _categoryService.getAllCategories();
      _displayCategories = _allCategories.where((cat) =>
          cat.masterTabType.toLowerCase() == _tabMasterType ||
          cat.masterTabType.toLowerCase() == 'general' ||
          cat.masterTabType.isEmpty
      ).toList();

      if (_displayCategories.isEmpty && _allCategories.isNotEmpty) {
          _displayCategories = _allCategories.where((cat) => cat.masterTabType.toLowerCase() == 'general' || cat.masterTabType.isEmpty).toList();
      } else if (_displayCategories.isEmpty && _allCategories.isNotEmpty) {
          // If still empty (no specific or general categories for this tab)
          _displayCategories = []; // Show no category filters
      }

      _products = _productService.getAllProducts();
      _applyCategoryFilter();
    });
  }

  void _applyCategoryFilter() {
    if (!mounted) return;
    if (_selectedCategoryId == null) {
      _filteredProductsForSelectedCategory = [];
    } else {
      _filteredProductsForSelectedCategory = _productService.getProductsByCategoryId(_selectedCategoryId!);
    }
  }

  void _onCategoryChipSelected(String? categoryId) {
    if (!mounted) return;
    setState(() {
      _selectedCategoryId = categoryId;
      _applyCategoryFilter();
    });
  }

  Widget _buildAdSlider() {
    final List<Widget> _adItems = [
      Container(key: ValueKey('ad1'), color: Colors.blue[100], child: Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(Icons.campaign_outlined, size: 40, color: Colors.blue[700]), SizedBox(height: 8), Text('تبلیغ ۱', style: TextStyle(color: Colors.blue[700], fontFamily: 'Vazir'))]))),
      Container(key: ValueKey('ad2'), color: Colors.green[100], child: Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(Icons.campaign_outlined, size: 40, color: Colors.green[700]), SizedBox(height: 8), Text('تبلیغ ۲', style: TextStyle(color: Colors.green[700], fontFamily: 'Vazir'))]))),
      Container(key: ValueKey('ad3'), color: Colors.orange[100], child: Center(child: Column(mainAxisAlignment: MainAxisAlignment.center, children: [Icon(Icons.campaign_outlined, size: 40, color: Colors.orange[700]), SizedBox(height: 8), Text('تبلیغ ۳', style: TextStyle(color: Colors.orange[700], fontFamily: 'Vazir'))]))),
    ];

    return Container(
      height: 150.0,
      margin: const EdgeInsets.only(top:12.0, bottom: 6.0),
      child: PageView.builder(
        controller: _adPageController,
        itemCount: _adItems.length,
        itemBuilder: (context, index) {
          return Padding(
            padding: const EdgeInsets.symmetric(horizontal: 6.0),
            child: Card(
                elevation: 2.0,
                clipBehavior: Clip.antiAlias,
                child: _adItems[index]
            ),
          );
        },
      ),
    );
  }

  Widget _buildCategoryFilters() {
    if (_displayCategories.isEmpty) {
      return Padding(
        padding: const EdgeInsets.all(8.0),
        child: Text("دسته‌بندی مرتبطی برای این بخش یافت نشد.", textAlign: TextAlign.center),
      );
    }
    List<Widget> filterChips = _displayCategories.map((category) {
      bool isSelected = _selectedCategoryId == category.id;
      return Padding(
        padding: const EdgeInsets.symmetric(horizontal: 4.0),
        child: FilterChip(label: Text(category.name), selected: isSelected, onSelected: (bool selected) => _onCategoryChipSelected(selected ? category.id : null)),
      );
    }).toList();
    filterChips.insert(0, Padding(
      padding: const EdgeInsets.symmetric(horizontal: 4.0),
      child: FilterChip(label: Text("همه این بخش"), selected: _selectedCategoryId == null, onSelected: (bool selected) => _onCategoryChipSelected(null)),
    ));
    return Container(height: 60, child: ListView(scrollDirection: Axis.horizontal, padding: EdgeInsets.symmetric(vertical: 8.0, horizontal: 8.0), children: filterChips));
  }

  Widget _buildProductCard(Product product) {
    final category = _categoryService.getCategoryById(product.categoryId);
    return Container(
      width: _productCardWidth,
      child: Card(
        margin: EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
        clipBehavior: Clip.antiAlias,
        child: InkWell(
          onTap: () => Navigator.push(context, MaterialPageRoute(builder: (context) => ProductDetailScreen(product: product))),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Container(height: 120, width: double.infinity, color: Colors.grey[200], child: product.imagePath.isNotEmpty ? Icon(Icons.image_outlined, size: 40, color: Colors.grey[500]) : Icon(Icons.image_not_supported_outlined, size: 40, color: Colors.grey[400])),
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(product.name, style: Theme.of(context).textTheme.subtitle1?.copyWith(fontWeight: FontWeight.bold), maxLines: 1, overflow: TextOverflow.ellipsis,),
                    SizedBox(height: 2),
                    Text(category?.name ?? 'Uncategorized', style: TextStyle(color: Colors.grey[600], fontSize: 10, fontFamily: 'Vazir')),
                    SizedBox(height: 4),
                    Text(product.description.isNotEmpty ? product.description : 'توضیحات موجود نیست.', maxLines: 2, overflow: TextOverflow.ellipsis, style: Theme.of(context).textTheme.bodyText2?.copyWith(fontSize: 12)),
                    SizedBox(height: 6),
                    Text('${product.price.toStringAsFixed(0)} تومان', style: TextStyle(fontSize: 16, fontWeight: FontWeight.bold, color: Theme.of(context).colorScheme.primary, fontFamily: 'Vazir')),
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
    if (productsInRow.isEmpty) return SizedBox.shrink();

    List<Product> relevantProducts = productsInRow.where((p) {
        final cat = _allCategories.firstWhere((c) => c.id == p.categoryId, orElse: () => Category(id: '', name: '', masterTabType: ''));
        return cat.masterTabType.toLowerCase() == _tabMasterType ||
               cat.masterTabType.toLowerCase() == 'general' ||
               cat.masterTabType.isEmpty;
    }).toList();

    if (relevantProducts.isEmpty) return SizedBox.shrink();

    return Column(
      crossAxisAlignment: CrossAxisAlignment.start,
      children: [
        Padding(padding: const EdgeInsets.symmetric(horizontal: 16.0, vertical: 12.0), child: Text(title, style: Theme.of(context).textTheme.headline6?.copyWith(fontSize: 18))),
        Container(
          height: _productCardHeight,
          child: ListView.builder(scrollDirection: Axis.horizontal, itemCount: relevantProducts.length, itemBuilder: (context, index) => _buildProductCard(relevantProducts[index]), padding: EdgeInsets.symmetric(horizontal: 8.0)),
        ),
        SizedBox(height: 10),
      ],
    );
  }

  Widget _buildProductDisplay() {
    if (_selectedCategoryId != null) {
      if (_filteredProductsForSelectedCategory.isEmpty) {
        return Center(child: Padding(padding: const EdgeInsets.all(16.0), child: Text("محصولی در این دسته‌بندی یافت نشد.", textAlign: TextAlign.center)));
      }
      final categoryName = _categoryService.getCategoryById(_selectedCategoryId!)?.name ?? "دسته‌بندی انتخاب شده";
      return _buildHorizontalProductList(categoryName, _filteredProductsForSelectedCategory);
    } else {
      if (_displayCategories.isEmpty) {
         return Center(child: Padding(padding: const EdgeInsets.all(16.0), child: Text("هیچ دسته‌بندی برای بخش داروها تعریف نشده است.", textAlign: TextAlign.center)));
      }
      List<Widget> categoryRows = _displayCategories.map((category) {
        List<Product> productsForThisCategory = _productService.getProductsByCategoryId(category.id);
        if (productsForThisCategory.isNotEmpty) {
          return _buildHorizontalProductList(category.name, productsForThisCategory);
        }
        return SizedBox.shrink();
      }).toList();

      bool hasContent = categoryRows.any((widget) => widget is! SizedBox);
      if (!hasContent) {
         return Center(child: Padding(padding: const EdgeInsets.all(16.0), child: Text("محصولی در دسته‌بندی‌های این بخش یافت نشد.", textAlign: TextAlign.center)));
      }
      return ListView(children: categoryRows);
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(title: Text("دارو")),
      body: Column(
        children: [
          _buildAdSlider(), // Call the ad slider here
          _buildCategoryFilters(),
          Expanded(child: _buildProductDisplay()),
        ],
      ),
    );
  }
}
