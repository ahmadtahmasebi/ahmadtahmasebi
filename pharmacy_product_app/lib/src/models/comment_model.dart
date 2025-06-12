import 'dart:math';

class Comment {
  String id;
  // String productId; // Not strictly needed if comments are stored within the product object
  String username;
  String text;
  DateTime timestamp;

  Comment({
    String? id, // Allow optional ID for new comments
    // required this.productId,
    required this.username,
    required this.text,
    DateTime? timestamp,
  }) : this.id = id ?? 'comment_${Random().nextInt(999999)}', // Generate ID if not provided
       this.timestamp = timestamp ?? DateTime.now();
}
