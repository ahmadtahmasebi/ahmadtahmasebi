class Product {
  String id;
  String name;
  String categoryId; // To link with a Category
  double price;
  String imagePath; // For now, a local path or placeholder URL
  String description;
  int stock;
  int minStock;
  int likes;
  int viewCount;

  Product({
    required this.id,
    required this.name,
    required this.categoryId,
    required this.price,
    this.imagePath = '',
    this.description = '',
    this.stock = 0,
    this.minStock = 5, // Default minStock
    this.likes = 0,
    this.viewCount = 0,
  });
}
