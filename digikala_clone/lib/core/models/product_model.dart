import 'package:cloud_firestore/cloud_firestore.dart'; // Required for Timestamp and FieldValue

class Product {
  final String id;
  final String name;
  final String description;
  final String imageUrl;
  final double price;
  final String categoryId; // Corresponds to Category model ID

  // New fields
  final String? brand;
  final String? countryOfOrigin;
  final Map<String, String>? specificFeatures;
  final int views;
  final int likes;
  final List<String>? likedBy; // List of user IDs who liked the product
  final Timestamp? createdAt;
  final Timestamp? updatedAt;

  Product({
    required this.id,
    required this.name,
    required this.description,
    required this.imageUrl,
    required this.price,
    required this.categoryId,
    this.brand,
    this.countryOfOrigin,
    this.specificFeatures,
    this.views = 0,
    this.likes = 0,
    this.likedBy = const [],
    this.createdAt,
    this.updatedAt,
  });

  Product copyWith({
    String? id,
    String? name,
    String? description,
    String? imageUrl,
    double? price,
    String? categoryId,
    String? brand,
    String? countryOfOrigin,
    Map<String, String>? specificFeatures,
    int? views,
    int? likes,
    List<String>? likedBy,
    Timestamp? createdAt,
    Timestamp? updatedAt,
  }) {
    return Product(
      id: id ?? this.id,
      name: name ?? this.name,
      description: description ?? this.description,
      imageUrl: imageUrl ?? this.imageUrl,
      price: price ?? this.price,
      categoryId: categoryId ?? this.categoryId,
      brand: brand ?? this.brand,
      countryOfOrigin: countryOfOrigin ?? this.countryOfOrigin,
      specificFeatures: specificFeatures ?? this.specificFeatures,
      views: views ?? this.views,
      likes: likes ?? this.likes,
      likedBy: likedBy ?? this.likedBy,
      createdAt: createdAt ?? this.createdAt,
      updatedAt: updatedAt ?? this.updatedAt,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      // id is not included here as it's the document ID
      'name': name,
      'description': description,
      'imageUrl': imageUrl,
      'price': price,
      'categoryId': categoryId,
      'brand': brand,
      'countryOfOrigin': countryOfOrigin,
      'specificFeatures': specificFeatures,
      'views': views,
      'likes': likes,
      'likedBy': likedBy,
      'createdAt': createdAt ?? FieldValue.serverTimestamp(),
      'updatedAt': FieldValue.serverTimestamp(), // Always update on save
    };
  }

  factory Product.fromJson(Map<String, dynamic> json, String documentId) {
    return Product(
      id: documentId, // Use document ID from Firestore
      name: json['name'] as String? ?? '',
      description: json['description'] as String? ?? '',
      imageUrl: json['imageUrl'] as String? ?? '',
      price: (json['price'] as num? ?? 0).toDouble(),
      categoryId: json['categoryId'] as String? ?? '',
      brand: json['brand'] as String?,
      countryOfOrigin: json['countryOfOrigin'] as String?,
      specificFeatures: json['specificFeatures'] != null
          ? Map<String, String>.from(json['specificFeatures'] as Map)
          : null,
      views: json['views'] as int? ?? 0,
      likes: json['likes'] as int? ?? 0,
      likedBy: List<String>.from(json['likedBy'] as List<dynamic>? ?? []),
      createdAt: json['createdAt'] as Timestamp?,
      updatedAt: json['updatedAt'] as Timestamp?,
    );
  }
}
