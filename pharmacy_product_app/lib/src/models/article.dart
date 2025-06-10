import 'package:flutter/foundation.dart'; // For @required if sticking to older style, or just use required keyword

class Article {
  String id;
  String title;
  String content;
  DateTime datePublished;

  Article({
    required this.id,
    required this.title,
    required this.content,
    required this.datePublished,
  });
}
