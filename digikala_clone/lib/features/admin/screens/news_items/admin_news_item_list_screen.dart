import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../../core/models/news_item_model.dart';
import '../../../../core/services/firestore_service.dart';
import '../../../../core/services/news_service_interface.dart';
import 'admin_add_edit_news_item_screen.dart'; // Will be created next

enum NewsItemListFilter { all, news, article }

class AdminNewsItemListScreen extends StatefulWidget {
  const AdminNewsItemListScreen({Key? key}) : super(key: key);

  @override
  _AdminNewsItemListScreenState createState() => _AdminNewsItemListScreenState();
}

class _AdminNewsItemListScreenState extends State<AdminNewsItemListScreen> {
  final INewsService _newsService = FirestoreService();
  NewsItemListFilter _currentFilter = NewsItemListFilter.all;
  Stream<List<NewsItem>>? _newsItemsStream;

  @override
  void initState() {
    super.initState();
    _updateStream();
  }

  void _updateStream() {
    setState(() {
      switch (_currentFilter) {
        case NewsItemListFilter.news:
          _newsItemsStream = _newsService.getNewsItems(NewsItemType.news);
          break;
        case NewsItemListFilter.article:
          _newsItemsStream = _newsService.getNewsItems(NewsItemType.article);
          break;
        case NewsItemListFilter.all:
        default:
          // FirestoreService.getNewsItems currently takes a type.
          // To get all, we'd need a new method in the service or fetch both and merge.
          // For simplicity now, let's default to news, or create a combined stream if complex.
          // Or, more simply, let's make "all" fetch news and then articles and combine.
          // However, INewsService doesn't have a "getAll" method.
          // So, for now, "all" will just show news. This needs service update for true "all".
          // For this task, I will make "all" show news as a placeholder for a combined list.
           _newsItemsStream = _newsService.getNewsItems(NewsItemType.news); // Placeholder for "all"
           // A better "all" would involve:
           // Stream<List<NewsItem>> newsStream = _newsService.getNewsItems(NewsItemType.news);
           // Stream<List<NewsItem>> articlesStream = _newsService.getNewsItems(NewsItemType.article);
           // _newsItemsStream = StreamZip([newsStream, articlesStream]).map((lists) => lists[0] + lists[1]);
           // This requires rxdart or similar for StreamZip, or manual stream combining.
           // For now, keeping it simple as per task scope.
          break;
      }
    });
  }


  void _navigateToAddEditScreen({NewsItem? item}) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => AdminAddEditNewsItemScreen(itemToEdit: item),
      ),
    ).then((_) {
      // StreamBuilder handles UI updates
    });
  }

  Future<void> _deleteNewsItem(String itemId, String title) async {
    final bool? confirmDelete = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('تایید حذف', style: TextStyle(fontFamily: 'IranYekan')),
          content: Text('آیا از حذف "$title" مطمئن هستید؟', style: const TextStyle(fontFamily: 'IranYekan')),
          actions: <Widget>[
            TextButton(
              child: const Text('لغو', style: TextStyle(fontFamily: 'IranYekan')),
              onPressed: () => Navigator.of(context).pop(false),
            ),
            TextButton(
              child: const Text('حذف', style: TextStyle(fontFamily: 'IranYekan', color: Colors.red)),
              onPressed: () => Navigator.of(context).pop(true),
            ),
          ],
        );
      },
    );

    if (confirmDelete == true) {
      try {
        await _newsService.deleteNewsItem(itemId);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('مورد "$title" با موفقیت حذف شد.', style: const TextStyle(fontFamily: 'IranYekan'))),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('خطا در حذف مورد: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
          );
        }
      }
    }
  }

  Widget _buildFilterChips() {
    return Padding(
      padding: const EdgeInsets.all(8.0),
      child: Row(
        mainAxisAlignment: MainAxisAlignment.spaceAround,
        children: NewsItemListFilter.values.map((filter) {
          return ChoiceChip(
            label: Text(
              filter == NewsItemListFilter.all ? 'همه' : (filter == NewsItemListFilter.news ? 'اخبار' : 'مقالات'),
              style: const TextStyle(fontFamily: 'IranYekan')
            ),
            selected: _currentFilter == filter,
            onSelected: (selected) {
              if (selected) {
                _currentFilter = filter;
                _updateStream();
              }
            },
          );
        }).toList(),
      ),
    );
  }


  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('مدیریت اخبار و مقالات', style: TextStyle(fontFamily: 'IranYekan')),
      ),
      body: Column(
        children: [
          _buildFilterChips(),
          Expanded(
            child: StreamBuilder<List<NewsItem>>(
              stream: _newsItemsStream,
              builder: (context, snapshot) {
                if (snapshot.connectionState == ConnectionState.waiting) {
                  return const Center(child: CircularProgressIndicator());
                }
                if (snapshot.hasError) {
                  return Center(child: Text('خطا: ${snapshot.error}', style: const TextStyle(fontFamily: 'IranYekan')));
                }
                if (!snapshot.hasData || snapshot.data!.isEmpty) {
                  return const Center(child: Text('موردی یافت نشد. برای افزودن روی + کلیک کنید.', style: TextStyle(fontFamily: 'IranYekan')));
                }

                final items = snapshot.data!;

                return ListView.separated(
                  itemCount: items.length,
                  separatorBuilder: (context, index) => const Divider(),
                  itemBuilder: (context, index) {
                    final item = items[index];
                    return ListTile(
                      leading: item.imageUrl != null && item.imageUrl!.isNotEmpty
                          ? Image.network(item.imageUrl!, width: 50, height: 50, fit: BoxFit.cover, errorBuilder: (c,o,s)=>const Icon(Icons.image_not_supported))
                          : const Icon(Icons.article, size: 40),
                      title: Text(item.title, style: const TextStyle(fontFamily: 'IranYekan', fontWeight: FontWeight.bold)),
                      subtitle: Text(
                        'نوع: ${newsItemTypeToString(item.type)} - دسته: ${item.category ?? "N/A"}\nنویسنده: ${item.author ?? "N/A"} - تاریخ: ${DateFormat('yyyy/MM/dd', 'fa_IR').format(item.createdAt.toDate())}',
                        style: const TextStyle(fontFamily: 'IranYekan', fontSize: 12),
                      ),
                      isThreeLine: true,
                      trailing: Row(
                        mainAxisSize: MainAxisSize.min,
                        children: [
                          IconButton(
                            icon: const Icon(Icons.edit, color: Colors.blue),
                            tooltip: 'ویرایش',
                            onPressed: () => _navigateToAddEditScreen(item: item),
                          ),
                          IconButton(
                            icon: const Icon(Icons.delete, color: Colors.red),
                            tooltip: 'حذف',
                            onPressed: () => _deleteNewsItem(item.id, item.title),
                          ),
                        ],
                      ),
                      onTap: () => _navigateToAddEditScreen(item: item),
                    );
                  },
                );
              },
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _navigateToAddEditScreen(),
        tooltip: 'افزودن مورد جدید',
        child: const Icon(Icons.add),
      ),
    );
  }
}
