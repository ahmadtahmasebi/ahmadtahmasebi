import 'package:cloud_firestore/cloud_firestore.dart';

class UserComment {
  final String id; // Firestore document ID for the comment itself
  final String entityId; // ID of the product, drug, or news item
  final String entityType; // "product", "drug", "news_item"
  final String? userId; // Can be device ID or actual user ID later
  final String userName; // Display name of the commenter
  final String text;
  final Timestamp createdAt;

  UserComment({
    required this.id,
    required this.entityId,
    required this.entityType,
    this.userId,
    required this.userName,
    required this.text,
    required this.createdAt,
  });

  Map<String, dynamic> toJson() {
    return {
      // id is not included here as it's the document ID in its own subcollection
      'entityId': entityId,
      'entityType': entityType,
      'userId': userId,
      'userName': userName,
      'text': text,
      'createdAt': createdAt, // Typically set with FieldValue.serverTimestamp() on creation
    };
  }

  factory UserComment.fromJson(Map<String, dynamic> json, String documentId) {
    return UserComment(
      id: documentId,
      entityId: json['entityId'] as String? ?? '',
      entityType: json['entityType'] as String? ?? '',
      userId: json['userId'] as String?,
      userName: json['userName'] as String? ?? 'ناشناس', // Anonymous
      text: json['text'] as String? ?? '',
      createdAt: json['createdAt'] as Timestamp? ?? Timestamp.now(), // Provide a default or ensure it's always set
    );
  }
}
