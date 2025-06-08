import 'package:flutter/material.dart';
import '../../../shared/widgets/app_drawer.dart';
import '../../main_sections/placeholder/section_placeholder.dart';
import '../../products/widgets/product_listing_tab_widget.dart'; // Import the new widget

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  // Define identifiers for categories, matching what might be stored in Firestore
  static const String drugCategoryId = 'drugs'; // Example identifier
  static const String cosmeticsCategoryId = 'cosmetics';
  static const String supplementsCategoryId = 'supplements';
  static const String herbalCategoryId = 'herbal';
  static const String equipmentCategoryId = 'equipment';
  static const String newsCategoryId = 'news'; // For news items, not products
  static const String articlesCategoryId = 'articles'; // For articles, not products


  final List<Map<String, dynamic>> _tabInfo = [
    {'text': 'دارویی', 'id': drugCategoryId, 'icon': Icons.local_pharmacy_outlined},
    {'text': 'آرایشی', 'id': cosmeticsCategoryId, 'icon': Icons.brush_outlined},
    {'text': 'مکمل‌ها', 'id': supplementsCategoryId, 'icon': Icons.health_and_safety_outlined},
    {'text': 'گیاهی', 'id': herbalCategoryId, 'icon': Icons.eco_outlined},
    {'text': 'تجهیزات', 'id': equipmentCategoryId, 'icon': Icons.medical_services_outlined},
    {'text': 'اخبار', 'id': newsCategoryId, 'icon': Icons.article_outlined}, // Using news icon
    {'text': 'مقالات', 'id': articlesCategoryId, 'icon': Icons.school_outlined}, // Using articles icon
  ];

  late List<Tab> _tabs;
  late List<Widget> _tabViews;

  @override
  void initState() {
    super.initState();
    _tabs = _tabInfo.map((info) => Tab(text: info['text'], icon: Icon(info['icon']))).toList();
    _tabController = TabController(length: _tabs.length, vsync: this);
    _buildTabViews(); // Initialize tab views
  }

  void _buildTabViews() {
    _tabViews = _tabInfo.map((info) {
      String tabId = info['id'];
      String tabText = info['text'];

      if (tabId == cosmeticsCategoryId) {
        // Cosmetics tab gets the ProductListingTabWidget
        return ProductListingTabWidget(mainCategoryIdentifier: cosmeticsCategoryId);
      }
      // TODO: Implement specific listing widgets for other product categories (دارویی, مکمل‌ها, etc.)
      // For now, other product-like categories will also use ProductListingTabWidget for demonstration
      // if (tabId == drugCategoryId || tabId == supplementsCategoryId || tabId == herbalCategoryId || tabId == equipmentCategoryId) {
      //   return ProductListingTabWidget(mainCategoryIdentifier: tabId);
      // }
      // For News and Articles, they will have their own specific widgets later.
      // else if (tabId == newsCategoryId || tabId == articlesCategoryId) {
      //   return SectionPlaceholder(title: tabText, color: Colors.teal[50]);
      // }
      else {
        // Default placeholder for other tabs
        Color? placeholderColor = (_tabInfo.indexOf(info) % 2 == 0) ? Colors.red[50] : Colors.blue[50];
        return SectionPlaceholder(title: tabText, color: placeholderColor);
      }
    }).toList();
  }


  @override
  void dispose() {
    _tabController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('داروخانه آنلاین', style: TextStyle(fontFamily: 'IranYekan')),
        backgroundColor: Colors.red[700],
        bottom: TabBar(
          controller: _tabController,
          tabs: _tabs,
          isScrollable: true,
          labelStyle: const TextStyle(fontFamily: 'IranYekan', fontWeight: FontWeight.bold),
          unselectedLabelStyle: const TextStyle(fontFamily: 'IranYekan'),
        ),
      ),
      drawer: const AppDrawer(),
      body: TabBarView(
        controller: _tabController,
        children: _tabViews,
      ),
    );
  }
}
