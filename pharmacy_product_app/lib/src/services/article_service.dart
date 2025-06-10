import '../models/article.dart';
import 'dart:math'; // For Random

class ArticleService {
  final List<Article> _articles = [];
  final Random _random = Random();

  List<Article> getAllArticles() {
    return List.from(_articles);
  }

  void addArticle(String title, String content) {
    final newArticle = Article(
      id: (_random.nextInt(999999) + 1).toString(), // Simple random ID
      title: title,
      content: content,
      datePublished: DateTime.now(),
    );
    _articles.add(newArticle);
  }

  void updateArticle(Article article) {
    final index = _articles.indexWhere((a) => a.id == article.id);
    if (index != -1) {
      _articles[index] = article;
    }
  }

  void deleteArticle(String articleId) {
    _articles.removeWhere((a) => a.id == articleId);
  }

  Article? getArticleById(String articleId) {
    try {
      return _articles.firstWhere((a) => a.id == articleId);
    } catch (e) {
      return null;
    }
  }
}
