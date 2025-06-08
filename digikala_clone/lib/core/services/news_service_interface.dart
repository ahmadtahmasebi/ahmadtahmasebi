import '../models/news_item_model.dart';
import '../models/user_comment_model.dart';

abstract class INewsService {
  Stream<List<NewsItem>> getNewsItems(NewsItemType type);
  Stream<List<NewsItem>> getNewsItemsByCategory(NewsItemType type, String category);
  Future<NewsItem?> getNewsItemById(String newsItemId);
  Future<void> addNewsItem(NewsItem item); // Typically admin only
  Future<void> updateNewsItem(NewsItem item); // Typically admin only
  Future<void> deleteNewsItem(String newsItemId); // Typically admin only
  Future<void> incrementNewsItemView(String newsItemId);
  Stream<List<UserComment>> getNewsItemComments(String newsItemId);
  Future<void> addNewsItemComment(UserComment comment);
}
