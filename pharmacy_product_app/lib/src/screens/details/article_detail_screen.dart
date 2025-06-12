import 'package:flutter/material.dart';
import '../../models/article.dart';

class ArticleDetailScreen extends StatelessWidget {
  final Article article;

  ArticleDetailScreen({required this.article});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text(article.title),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            if (article.imagePath.isNotEmpty)
              Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                child: Container(
                  height: 200,
                  width: double.infinity,
                  color: Colors.grey[200], // Placeholder background for the image
                  child: Icon(Icons.image_outlined, size: 80, color: Colors.grey[500]),
                  // In a real app: Image.asset(article.imagePath) or Image.network(...)
                ),
              )
            else // Optional: show a smaller placeholder or nothing if no image
              Padding(
                padding: const EdgeInsets.only(bottom: 16.0),
                 child: Container(
                  height: 100, // Smaller placeholder if no specific image
                  width: double.infinity,
                  color: Colors.grey[100],
                  alignment: Alignment.center,
                  child: Icon(Icons.article_outlined, size: 50, color: Colors.grey[400]),
                ),
              ),
            Text(
              article.title,
              style: Theme.of(context).textTheme.headline5?.copyWith(fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),
            Text(
              'تاریخ انتشار: ${article.datePublished.toLocal().toString().substring(0, 16)}', // More precise time
              style: Theme.of(context).textTheme.caption?.copyWith(fontSize: 13),
            ),
            SizedBox(height: 16),
            Divider(thickness: 1),
            SizedBox(height: 16),
            Text(
              article.content,
              style: Theme.of(context).textTheme.bodyText1?.copyWith(fontSize: 16, height: 1.6),
            ),
          ],
        ),
      ),
    );
  }
}
