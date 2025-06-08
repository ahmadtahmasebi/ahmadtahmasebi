import 'package:cloud_firestore/cloud_firestore.dart';

class Drug {
  final String id;
  final String genericName;
  final List<String> brandNames;
  final String dosageForms; // e.g., "Tablet, Syrup, Injection"
  final String strength; // e.g., "500mg", "10mg/5ml"
  final String pharmacology;
  final String indications;
  final String contraindications;
  final String sideEffects;
  final String drugInteractions;
  final double? price;
  final String? categoryId; // Internal categorization (e.g., "Analgesics", "Antibiotics")
  final String? imageUrl;
  final int views;
  final int likes;
  final Timestamp? createdAt;
  final Timestamp? updatedAt;

  Drug({
    required this.id,
    required this.genericName,
    this.brandNames = const [],
    required this.dosageForms,
    required this.strength,
    this.pharmacology = '',
    this.indications = '',
    this.contraindications = '',
    this.sideEffects = '',
    this.drugInteractions = '',
    this.price,
    this.categoryId,
    this.imageUrl,
    this.views = 0,
    this.likes = 0,
    this.createdAt,
    this.updatedAt,
  });

  Map<String, dynamic> toJson() {
    return {
      'genericName': genericName,
      'brandNames': brandNames,
      'dosageForms': dosageForms,
      'strength': strength,
      'pharmacology': pharmacology,
      'indications': indications,
      'contraindications': contraindications,
      'sideEffects': sideEffects,
      'drugInteractions': drugInteractions,
      'price': price,
      'categoryId': categoryId,
      'imageUrl': imageUrl,
      'views': views,
      'likes': likes,
      'createdAt': createdAt ?? FieldValue.serverTimestamp(), // Set on create
      'updatedAt': updatedAt ?? FieldValue.serverTimestamp(), // Set on create/update
      // id is not included here as it's used as document ID in Firestore
    };
  }

  factory Drug.fromJson(Map<String, dynamic> json, String documentId) {
    return Drug(
      id: documentId,
      genericName: json['genericName'] as String? ?? '',
      brandNames: List<String>.from(json['brandNames'] as List<dynamic>? ?? []),
      dosageForms: json['dosageForms'] as String? ?? '',
      strength: json['strength'] as String? ?? '',
      pharmacology: json['pharmacology'] as String? ?? '',
      indications: json['indications'] as String? ?? '',
      contraindications: json['contraindications'] as String? ?? '',
      sideEffects: json['sideEffects'] as String? ?? '',
      drugInteractions: json['drugInteractions'] as String? ?? '',
      price: (json['price'] as num?)?.toDouble(),
      categoryId: json['categoryId'] as String?,
      imageUrl: json['imageUrl'] as String?,
      views: json['views'] as int? ?? 0,
      likes: json['likes'] as int? ?? 0,
      createdAt: json['createdAt'] as Timestamp?,
      updatedAt: json['updatedAt'] as Timestamp?,
    );
  }
}
