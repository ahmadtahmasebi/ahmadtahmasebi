import 'package:flutter/material.dart';
import '../../models/article.dart';
import '../../services/article_service.dart'; // Assuming global instance
import '../details/article_detail_screen.dart'; // Import detail screen

// This relies on the global _articleService instance being available from article_service.dart
// (as established in previous admin screen implementations)
final ArticleService _articleService = ArticleService();


class NewsArticlesScreen extends StatefulWidget {
  @override
  _NewsArticlesScreenState createState() => _NewsArticlesScreenState();
}

class _NewsArticlesScreenState extends State<NewsArticlesScreen> {
  List<Article> _articles = [];

  @override
  void initState() {
    super.initState();
    _loadArticles();
  }

  void _loadArticles() {
    setState(() {
      // Using the _articleService instance declared at the top of this file.
      _articles = _articleService.getAllArticles();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('اخبار و مقالات (News & Articles)'),
        actions: [
           IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _loadArticles, // Refresh data
            tooltip: 'Refresh Articles',
          )
        ],
      ),
      body: _articles.isEmpty
          ? Center(child: Text('No articles available. Add some in the Admin Panel.'))
          : ListView.builder(
              itemCount: _articles.length,
              itemBuilder: (context, index) {
                final article = _articles[index];
                return Card(
                  margin: EdgeInsets.symmetric(horizontal: 16.0, vertical: 8.0),
                  child: ListTile(
                    title: Text(article.title, style: TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text(
                      'Published: ${article.datePublished.toLocal().toString().substring(0, 10)}',
                      overflow: TextOverflow.ellipsis,
                    ),
                    trailing: Icon(Icons.arrow_forward_ios, size: 16),
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => ArticleDetailScreen(article: article),
                        ),
                      );
                    },
                  ),
                );
              },
            ),
    );
  }
}
