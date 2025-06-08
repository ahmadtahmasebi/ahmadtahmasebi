import 'package:cloud_firestore/cloud_firestore.dart';

enum NewsItemType { news, article }

String newsItemTypeToString(NewsItemType type) {
  switch (type) {
    case NewsItemType.news:
      return 'news';
    case NewsItemType.article:
      return 'article';
  }
}

NewsItemType newsItemTypeFromString(String? typeString) {
  if (typeString == 'news') {
    return NewsItemType.news;
  } else if (typeString == 'article') {
    return NewsItemType.article;
  }
  return NewsItemType.news; // Default or throw error
}

class NewsItem {
  final String id;
  final String title;
  final String content;
  final String? author;
  final NewsItemType type;
  final String? category; // e.g., "Health News", "Scientific Article", "Pharmacy Updates"
  final String? imageUrl;
  final Timestamp createdAt;
  final Timestamp? updatedAt;
  final int views;

  NewsItem({
    required this.id,
    required this.title,
    required this.content,
    this.author,
    required this.type,
    this.category,
    this.imageUrl,
    required this.createdAt,
    this.updatedAt,
    this.views = 0,
  });

  Map<String, dynamic> toJson() {
    return {
      // id is not included here as it's the document ID
      'title': title,
      'content': content,
      'author': author,
      'type': newsItemTypeToString(type),
      'category': category,
      'imageUrl': imageUrl,
      'createdAt': createdAt, // Should be set on creation, can use FieldValue.serverTimestamp() if not set
      'updatedAt': FieldValue.serverTimestamp(), // Always update on save
      'views': views,
    };
  }

  factory NewsItem.fromJson(Map<String, dynamic> json, String documentId) {
    return NewsItem(
      id: documentId,
      title: json['title'] as String? ?? '',
      content: json['content'] as String? ?? '',
      author: json['author'] as String?,
      type: newsItemTypeFromString(json['type'] as String?),
      category: json['category'] as String?,
      imageUrl: json['imageUrl'] as String?,
      createdAt: json['createdAt'] as Timestamp? ?? Timestamp.now(), // Provide a default or ensure it's always set
      updatedAt: json['updatedAt'] as Timestamp?,
      views: json['views'] as int? ?? 0,
    );
  }
}
