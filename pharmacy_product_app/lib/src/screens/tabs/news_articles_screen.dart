import 'package:flutter/material.dart';
import '../../models/article.dart';
import '../../services/article_service.dart';
import '../details/article_detail_screen.dart';

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
    if (mounted) {
      setState(() {
        _articles = _articleService.getAllArticles();
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('اخبار و مقالات'),
        actions: [
           IconButton(
            icon: Icon(Icons.refresh),
            onPressed: _loadArticles,
            tooltip: 'بارگذاری مجدد',
          )
        ],
      ),
      body: _articles.isEmpty
          ? Center(child: Text('مقاله‌ای برای نمایش وجود ندارد. از پنل مدیریت اضافه کنید.'))
          : ListView.builder(
              padding: EdgeInsets.all(8.0),
              itemCount: _articles.length,
              itemBuilder: (context, index) {
                final article = _articles[index];
                return Card(
                  elevation: 2.0,
                  margin: EdgeInsets.symmetric(vertical: 8.0),
                  child: InkWell(
                    onTap: () {
                      Navigator.push(
                        context,
                        MaterialPageRoute(
                          builder: (context) => ArticleDetailScreen(article: article),
                        ),
                      );
                    },
                    child: Padding(
                      padding: const EdgeInsets.all(12.0),
                      child: Row(
                        crossAxisAlignment: CrossAxisAlignment.start,
                        children: [
                          if (article.imagePath.isNotEmpty)
                            Container(
                              width: 80, height: 80,
                              margin: EdgeInsets.only(left: 12.0, right: 4.0), // Added right margin for Farsi
                              color: Colors.grey[200],
                              child: Icon(Icons.image_outlined, size: 30, color: Colors.grey[500]),
                            )
                          else
                             Container(
                              width: 80, height: 80,
                              margin: EdgeInsets.only(left: 12.0, right: 4.0),
                              color: Colors.grey[100],
                              child: Icon(Icons.article_outlined, size: 30, color: Colors.grey[400]),
                            ),
                          Expanded(
                            child: Column(
                              crossAxisAlignment: CrossAxisAlignment.start,
                              children: [
                                Text(article.title, style: Theme.of(context).textTheme.subtitle1?.copyWith(fontWeight: FontWeight.bold)),
                                SizedBox(height: 4),
                                Text(
                                  'تاریخ انتشار: ${article.datePublished.toLocal().toString().split(" ")[0]}',
                                  style: Theme.of(context).textTheme.caption,
                                ),
                                SizedBox(height: 6),
                                Text(
                                  article.content,
                                  style: Theme.of(context).textTheme.bodyText2,
                                  maxLines: 2,
                                  overflow: TextOverflow.ellipsis,
                                ),
                              ],
                            ),
                          ),
                          Icon(Icons.arrow_forward_ios, size: 16, color: Colors.grey[400]),
                        ],
                      ),
                    ),
                  ),
                );
              },
            ),
    );
  }
}
