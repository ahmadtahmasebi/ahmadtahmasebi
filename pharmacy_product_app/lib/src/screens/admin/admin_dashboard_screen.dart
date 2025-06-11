import 'package:flutter/material.dart';
import '../../services/product_service.dart';
import '../../services/category_service.dart';
import '../../services/article_service.dart';
import '../../models/category.dart';
import '../../models/product.dart'; // For Product type

// Assuming global service instances are available after import
final ProductService _productService = ProductService();
final CategoryService _categoryService = CategoryService();
final ArticleService _articleService = ArticleService();

class AdminDashboardScreen extends StatefulWidget {
  @override
  _AdminDashboardScreenState createState() => _AdminDashboardScreenState();
}

class _AdminDashboardScreenState extends State<AdminDashboardScreen> {
  int _totalProducts = 0;
  int _totalCategories = 0;
  int _totalArticles = 0;
  Map<String, int> _productsPerCategory = {};

  // New state variables for detailed product stats
  Product? _productWithMostStock;
  Product? _productWithLeastStock;
  double _averageProductPrice = 0.0;

  @override
  void initState() {
    super.initState();
    _loadStatistics();
  }

  void _loadStatistics() {
    final products = _productService.getAllProducts();
    final categories = _categoryService.getAllCategories();
    final articles = _articleService.getAllArticles();

    Map<String, int> productsCountMap = {};
    for (Category category in categories) {
      final productsInCat = _productService.getProductsByCategoryId(category.id);
      productsCountMap[category.name] = productsInCat.length;
    }

    // Calculate detailed product stats
    Product? mostStock;
    Product? leastStock;
    double totalPrice = 0;
    double calculatedAveragePrice = 0.0; // Local variable for calculation

    if (products.isNotEmpty) {
      mostStock = products.reduce((curr, next) => curr.stock > next.stock ? curr : next);
      leastStock = products.reduce((curr, next) => curr.stock < next.stock ? curr : next);
      products.forEach((p) => totalPrice += p.price);
      calculatedAveragePrice = totalPrice / products.length;
    }

    if (mounted) {
      setState(() {
        _totalProducts = products.length;
        _totalCategories = categories.length;
        _totalArticles = articles.length;
        _productsPerCategory = productsCountMap;
        _productWithMostStock = mostStock;
        _productWithLeastStock = leastStock;
        _averageProductPrice = calculatedAveragePrice; // Assign calculated value
      });
    }
  }

  Widget _buildStatCard(String title, String value, IconData icon, Color color) {
    return Card(
      elevation: 2.0,
      child: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          crossAxisAlignment: CrossAxisAlignment.center,
          children: <Widget>[
            Icon(icon, size: 36.0, color: color),
            SizedBox(height: 8.0),
            Text(
              value,
              style: TextStyle(fontSize: 22.0, fontWeight: FontWeight.bold, color: color),
              textAlign: TextAlign.center,
            ),
            SizedBox(height: 4.0),
            Text(
              title,
              style: TextStyle(fontSize: 13.0, color: Colors.grey[700]),
              textAlign: TextAlign.center,
            ),
          ],
        ),
      ),
    );
  }

  Widget _buildProductStatItem(String label, String value) {
    return Padding(
      padding: const EdgeInsets.symmetric(vertical: 6.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceBetween,
        children: [
          Text(label, style: TextStyle(fontSize: 14, color: Colors.grey[800])),
          Text(value, style: TextStyle(fontSize: 14, fontWeight: FontWeight.bold)),
        ],
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('داشبورد مدیریت'),
        actions: [
          IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _loadStatistics,
            tooltip: 'Refresh Stats',
          )
        ],
      ),
      body: RefreshIndicator(
        onRefresh: () async => _loadStatistics(),
        child: SingleChildScrollView(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              GridView.count(
                shrinkWrap: true,
                physics: NeverScrollableScrollPhysics(),
                crossAxisCount: MediaQuery.of(context).size.width > 600 ? 3 : 2,
                crossAxisSpacing: 12.0,
                mainAxisSpacing: 12.0,
                childAspectRatio: MediaQuery.of(context).size.width > 600 ? 1.3 : 1.1,
                children: <Widget>[
                  _buildStatCard('مجموع محصولات', _totalProducts.toString(), Icons.shopping_bag_outlined, Colors.blue),
                  _buildStatCard('مجموع دسته‌بندی‌ها', _totalCategories.toString(), Icons.category_outlined, Colors.green),
                  _buildStatCard('مجموع مقالات', _totalArticles.toString(), Icons.article_outlined, Colors.orangeAccent),
                ],
              ),
              SizedBox(height: 20.0),
              Text(
                'محصولات در هر دسته‌بندی',
                style: Theme.of(context).textTheme.subtitle1?.copyWith(fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8.0),
              _productsPerCategory.isEmpty
                  ? Center(child: Padding(padding: const EdgeInsets.symmetric(vertical: 20.0), child: Text('داده‌ای برای نمایش وجود ندارد.')))
                  : Card(
                      elevation: 1.0,
                      child: DataTable(
                        columnSpacing: 20,
                        headingRowHeight: 40,
                        dataRowHeight: 36,
                        columns: const <DataColumn>[
                          DataColumn(label: Text('دسته‌بندی', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14))),
                          DataColumn(label: Text('تعداد', style: TextStyle(fontWeight: FontWeight.bold, fontSize: 14)), numeric: true),
                        ],
                        rows: _productsPerCategory.entries.map(
                          (entry) => DataRow(
                            cells: <DataCell>[
                              DataCell(Text(entry.key, style: TextStyle(fontSize: 13))),
                              DataCell(Text(entry.value.toString(), style: TextStyle(fontSize: 13))),
                            ],
                          ),
                        ).toList(),
                      ),
                    ),
              SizedBox(height: 20.0),
              Text(
                'آمار بیشتر محصولات',
                 style: Theme.of(context).textTheme.subtitle1?.copyWith(fontWeight: FontWeight.bold),
              ),
               Card(
                elevation: 1.0,
                child: Container(
                  width: double.infinity,
                  padding: const EdgeInsets.all(16.0),
                  child: _totalProducts == 0
                    ? Text('محصولی برای نمایش آمار وجود ندارد.', style: TextStyle(fontSize: 13, color: Colors.grey[600]))
                    : Column(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          _buildProductStatItem(
                            'بیشترین موجودی:',
                            _productWithMostStock != null ? '${_productWithMostStock!.name} (${_productWithMostStock!.stock} عدد)' : 'N/A'
                          ),
                          Divider(height: 10, thickness: 0.5),
                          _buildProductStatItem(
                            'کمترین موجودی:',
                            _productWithLeastStock != null ? '${_productWithLeastStock!.name} (${_productWithLeastStock!.stock} عدد)' : 'N/A'
                          ),
                          Divider(height: 10, thickness: 0.5),
                          _buildProductStatItem(
                            'میانگین قیمت محصولات:',
                            _averageProductPrice > 0 ? '${_averageProductPrice.toStringAsFixed(0)} تومان' : 'N/A'
                          ),
                        ],
                      ),
                )
              )
            ],
          ),
        ),
      ),
    );
  }
}
