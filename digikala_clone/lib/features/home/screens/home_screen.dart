import 'package:flutter/material.dart';
import '../../../core/models/news_item_model.dart'; // Import NewsItemType
import '../../../shared/widgets/app_drawer.dart';
import '../../main_sections/placeholder/section_placeholder.dart';
import '../../products/widgets/product_listing_tab_widget.dart';
import '../../news/widgets/news_listing_tab_widget.dart'; // Import NewsListingTabWidget

class HomeScreen extends StatefulWidget {
  const HomeScreen({Key? key}) : super(key: key);

  @override
  _HomeScreenState createState() => _HomeScreenState();
}

class _HomeScreenState extends State<HomeScreen> with SingleTickerProviderStateMixin {
  late TabController _tabController;

  // Define identifiers for categories and types
  static const String drugCategoryId = 'drugs';
  static const String cosmeticsCategoryId = 'cosmetics';
  static const String supplementsCategoryId = 'supplements';
  static const String herbalCategoryId = 'herbal';
  static const String equipmentCategoryId = 'equipment';
  // For news items, we use NewsItemType enum, but can use string identifiers for mapping if preferred
  static const String newsTabId = 'news_tab';
  static const String articlesTabId = 'articles_tab';


  final List<Map<String, dynamic>> _tabInfo = [
    {'text': 'دارویی', 'id': drugCategoryId, 'icon': Icons.local_pharmacy_outlined},
    {'text': 'آرایشی', 'id': cosmeticsCategoryId, 'icon': Icons.brush_outlined},
    {'text': 'مکمل‌ها', 'id': supplementsCategoryId, 'icon': Icons.health_and_safety_outlined},
    {'text': 'گیاهی', 'id': herbalCategoryId, 'icon': Icons.eco_outlined},
    {'text': 'تجهیزات', 'id': equipmentCategoryId, 'icon': Icons.medical_services_outlined},
    {'text': 'اخبار', 'id': newsTabId, 'icon': Icons.article_outlined},
    {'text': 'مقالات', 'id': articlesTabId, 'icon': Icons.school_outlined},
  ];

  late List<Tab> _tabs;
  late List<Widget> _tabViews;

  @override
  void initState() {
    super.initState();
    _tabs = _tabInfo.map((info) => Tab(text: info['text'], icon: Icon(info['icon']))).toList();
    _tabController = TabController(length: _tabs.length, vsync: this);
    _buildTabViews();
  }

  void _buildTabViews() {
    _tabViews = _tabInfo.map((info) {
      String tabId = info['id'];
      String tabText = info['text'];

      if (tabId == cosmeticsCategoryId) {
        return ProductListingTabWidget(mainCategoryIdentifier: cosmeticsCategoryId);
      } else if (tabId == newsTabId) {
        return const NewsListingTabWidget(newsItemType: NewsItemType.news);
      } else if (tabId == articlesTabId) {
        return const NewsListingTabWidget(newsItemType: NewsItemType.article);
      }
      // TODO: Implement specific listing widgets for other product categories (دارویی, مکمل‌ها, etc.)
      // For now, other product-like categories will also use ProductListingTabWidget or placeholders
      // else if (tabId == drugCategoryId || tabId == supplementsCategoryId || tabId == herbalCategoryId || tabId == equipmentCategoryId) {
      //   // return ProductListingTabWidget(mainCategoryIdentifier: tabId); // If using same widget
      //   Color? placeholderColor = (_tabInfo.indexOf(info) % 2 == 0) ? Colors.orange[50] : Colors.green[50];
      //   return SectionPlaceholder(title: tabText, color: placeholderColor);
      // }
      else {
        Color? placeholderColor = (_tabInfo.indexOf(info) % 3 == 0) ? Colors.red[50] : (_tabInfo.indexOf(info) % 3 == 1) ? Colors.blue[50] : Colors.yellow[50];
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
        backgroundColor: Theme.of(context).appBarTheme.backgroundColor ?? Colors.red[700],
        foregroundColor: Theme.of(context).appBarTheme.foregroundColor ?? Colors.white,
        bottom: TabBar(
          controller: _tabController,
          tabs: _tabs,
          isScrollable: true,
          labelStyle: const TextStyle(fontFamily: 'IranYekan', fontWeight: FontWeight.bold),
          unselectedLabelStyle: const TextStyle(fontFamily: 'IranYekan'),
          indicatorColor: Colors.white,
          labelColor: Colors.white,
          unselectedLabelColor: Colors.white70,
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
