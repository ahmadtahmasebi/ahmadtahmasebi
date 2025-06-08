import 'package:cloud_firestore/cloud_firestore.dart';
// import 'package:firebase_auth/firebase_auth.dart'; // Not strictly needed here if userId is passed in
// No longer using shared_preferences for this service

class FavoritesService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;
  static const String _usersCollectionName = 'users';
  static const String _favoriteProductIdsField = 'favoriteProductIds';

  DocumentReference _userDocRef(String userId) {
    return _firestore.collection(_usersCollectionName).doc(userId);
  }

  Future<List<String>> getFavoriteProductIds(String userId) async {
    if (userId.isEmpty) return []; // Or handle unauthenticated user as needed
    try {
      final docSnapshot = await _userDocRef(userId).get();
      if (docSnapshot.exists) {
        final data = docSnapshot.data() as Map<String, dynamic>?;
        if (data != null && data.containsKey(_favoriteProductIdsField)) {
          // Ensure the data is correctly cast to List<String>
          final favs = data[_favoriteProductIdsField] as List<dynamic>?;
          return favs?.map((e) => e.toString()).toList() ?? [];
        }
      }
      return []; // Return empty list if no document or no field
    } catch (e) {
      print('Error getting favorite product IDs: $e');
      return []; // Return empty on error
    }
  }

  Future<void> addFavoriteProductId(String userId, String productId) async {
    if (userId.isEmpty) return;
    try {
      await _userDocRef(userId).set(
        {_favoriteProductIdsField: FieldValue.arrayUnion([productId])},
        SetOptions(merge: true), // Creates document if it doesn't exist, merges fields
      );
    } catch (e) {
      print('Error adding favorite product ID: $e');
      rethrow; // Allow UI to handle
    }
  }

  Future<void> removeFavoriteProductId(String userId, String productId) async {
    if (userId.isEmpty) return;
    try {
      await _userDocRef(userId).update(
        {_favoriteProductIdsField: FieldValue.arrayRemove([productId])},
      );
    } catch (e) {
      print('Error removing favorite product ID: $e');
      rethrow; // Allow UI to handle
    }
  }

  Future<bool> isFavorite(String userId, String productId) async {
    if (userId.isEmpty) return false;
    final ids = await getFavoriteProductIds(userId);
    return ids.contains(productId);
  }

  Future<bool> toggleFavorite(String userId, String productId) async {
    if (userId.isEmpty) {
      throw Exception("User not logged in. Cannot toggle favorite.");
    }
    final isCurrentlyFavorite = await isFavorite(userId, productId);
    if (isCurrentlyFavorite) {
      await removeFavoriteProductId(userId, productId);
      return false; // New state: not favorite
    } else {
      await addFavoriteProductId(userId, productId);
      return true; // New state: is favorite
    }
  }
}
