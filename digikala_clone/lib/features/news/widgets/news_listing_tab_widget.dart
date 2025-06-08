import 'package:flutter/material.dart';
import '../../../core/models/news_item_model.dart';
import '../../../core/services/firestore_service.dart';
import '../../../core/services/news_service_interface.dart';
import './news_item_card.dart';

class NewsListingTabWidget extends StatefulWidget {
  final NewsItemType newsItemType; // "news" or "article"

  const NewsListingTabWidget({Key? key, required this.newsItemType}) : super(key: key);

  @override
  _NewsListingTabWidgetState createState() => _NewsListingTabWidgetState();
}

class _NewsListingTabWidgetState extends State<NewsListingTabWidget> {
  late Stream<List<NewsItem>> _newsItemsStream;
  final INewsService _newsService = FirestoreService();
  // TODO: Implement category filtering for news/articles if needed in future
  // String? _selectedNewsCategory;

  @override
  void initState() {
    super.initState();
    _updateNewsStream();
  }

  void _updateNewsStream() {
    // if (_selectedNewsCategory == null || _selectedNewsCategory == 'all') {
    _newsItemsStream = _newsService.getNewsItems(widget.newsItemType);
    // } else {
    //   _newsItemsStream = _newsService.getNewsItemsByCategory(widget.newsItemType, _selectedNewsCategory!);
    // }
    if (mounted) {
      setState(() {}); // Ensure the stream is updated in the StreamBuilder
    }
  }

  // void _onNewsCategorySelected(String? category) {
  //   setState(() {
  //     _selectedNewsCategory = (category == _selectedNewsCategory) ? null : category;
  //     _updateNewsStream();
  //   });
  // }

  @override
  Widget build(BuildContext context) {
    return Column(
      children: [
        // TODO: Add sub-category/filter chips here if news/articles have categories
        // Example: _buildNewsCategoryChips(),
        Expanded(
          child: StreamBuilder<List<NewsItem>>(
            stream: _newsItemsStream,
            builder: (context, snapshot) {
              if (snapshot.connectionState == ConnectionState.waiting) {
                return const Center(child: CircularProgressIndicator());
              }
              if (snapshot.hasError) {
                print("Error loading news items in tab: ${snapshot.error}");
                return Center(child: Text('خطا در بارگذاری موارد: ${snapshot.error}', style: const TextStyle(fontFamily: 'IranYekan')));
              }
              if (!snapshot.hasData || snapshot.data!.isEmpty) {
                final typeText = widget.newsItemType == NewsItemType.news ? 'اخبار' : 'مقالات';
                return Center(child: Text('موردی برای نمایش در بخش $typeText یافت نشد.', style: const TextStyle(fontFamily: 'IranYekan')));
              }
              final newsItems = snapshot.data!;
              return ListView.builder(
                padding: const EdgeInsets.all(8.0),
                itemCount: newsItems.length,
                itemBuilder: (context, index) {
                  return NewsItemCard(newsItem: newsItems[index]);
                },
              );
            },
          ),
        ),
      ],
    );
  }

  // Widget _buildNewsCategoryChips() {
  //   // Placeholder for category chips - would need a stream of news categories
  //   // similar to product categories if this feature is desired.
  //   return const SizedBox(height: 50, child: Center(child: Text("Category Chips Placeholder")));
  // }
}
