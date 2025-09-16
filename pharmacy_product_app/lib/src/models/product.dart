import 'comment_model.dart'; // Import the new Comment model

class Product {
  String id;
  String name;
  String categoryId;
  double price;
  String imagePath;
  String description;
  int stock;
  int minStock;
  int likes;
  int viewCount;
  List<Comment> comments; // New field for comments

  Product({
    required this.id,
    required this.name,
    required this.categoryId,
    required this.price,
    this.imagePath = '',
    this.description = '',
    this.stock = 0,
    this.minStock = 5,
    this.likes = 0,
    this.viewCount = 0,
    List<Comment>? comments, // Make comments optional in constructor
  }) : this.comments = comments ?? []; // Initialize with empty list if null
}
