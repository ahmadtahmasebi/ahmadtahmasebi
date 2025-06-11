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
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: SingleChildScrollView( // To allow scrolling for long content
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Text(
                article.title,
                style: Theme.of(context).textTheme.headline5?.copyWith(fontWeight: FontWeight.bold),
              ),
              SizedBox(height: 8),
              Text(
                'Published: ${article.datePublished.toLocal().toString().substring(0, 16)}',
                style: Theme.of(context).textTheme.caption,
              ),
              SizedBox(height: 16),
              Divider(),
              SizedBox(height: 16),
              Text(
                article.content,
                style: Theme.of(context).textTheme.bodyText1?.copyWith(fontSize: 16, height: 1.5),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
