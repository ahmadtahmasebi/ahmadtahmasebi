import '../models/article.dart';
import 'dart:math'; // For Random

class ArticleService {
  final List<Article> _articles = [
    Article(
      id: 'art_1',
      title: 'نکات مهم در انتخاب ضد آفتاب مناسب',
      content: 'انتخاب ضد آفتاب مناسب برای پوست شما یکی از مهم‌ترین قدم‌ها برای حفظ سلامت و جوانی پوست است. نور خورشید، با وجود فواید بسیار، می‌تواند باعث آسیب‌های جدی مانند آفتاب سوختگی، پیری زودرس، لک‌های پوستی و حتی سرطان پوست شود. در این مقاله به بررسی نکات کلیدی در انتخاب یک ضد آفتاب خوب می‌پردازیم... (ادامه مطلب)',
      datePublished: DateTime.now().subtract(Duration(days: 5)),
      imagePath: 'placeholder_sunscreen_article.png', // Sample image path
    ),
    Article(
      id: 'art_2',
      title: 'فواید ویتامین C برای بدن و پوست',
      content: 'ویتامین C یک ویتامین محلول در آب و یک آنتی‌اکسیدان قوی است که نقش‌های حیاتی متعددی در بدن ایفا می‌کند. از تقویت سیستم ایمنی گرفته تا کمک به ساخت کلاژن برای پوست، این ویتامین برای سلامتی کلی ضروری است. بیایید نگاهی دقیق‌تر به فواید ویتامین C بیندازیم... (ادامه مطلب)',
      datePublished: DateTime.now().subtract(Duration(days: 2)),
      imagePath: 'placeholder_vitaminc_article.png', // Sample image path
    ),
  ];
  final Random _random = Random();

  List<Article> getAllArticles() {
    return List.from(_articles); // Return a copy
  }

  void addArticle(String title, String content, String imagePath) { // Added imagePath parameter
    if (_articles.any((art) => art.title.toLowerCase() == title.toLowerCase())) {
      print('Article with title "$title" already exists.');
      return;
    }
    final newArticle = Article(
      id: 'art_user_${(_random.nextInt(99999) + _articles.length + 1).toString()}',
      title: title,
      content: content,
      datePublished: DateTime.now(),
      imagePath: imagePath, // Assign imagePath
    );
    _articles.add(newArticle);
  }

  void updateArticle(Article article) { // Article object now includes imagePath
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
      return null; // Not found
    }
  }
}
