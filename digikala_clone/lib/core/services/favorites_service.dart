import 'package:shared_preferences/shared_preferences.dart';

class FavoritesService {
  static const _kFavoriteProductIdsKey = 'favoriteProductIds';

  // Helper method to get SharedPreferences instance
  Future<SharedPreferences> _getPrefs() async {
    return SharedPreferences.getInstance();
  }

  Future<List<String>> getFavoriteProductIds() async {
    final prefs = await _getPrefs();
    return prefs.getStringList(_kFavoriteProductIdsKey) ?? [];
  }

  Future<void> _saveFavoriteProductIds(List<String> ids) async {
    final prefs = await _getPrefs();
    await prefs.setStringList(_kFavoriteProductIdsKey, ids);
  }

  Future<bool> isFavorite(String productId) async {
    final ids = await getFavoriteProductIds();
    return ids.contains(productId);
  }

  Future<void> addFavoriteProductId(String productId) async {
    final ids = await getFavoriteProductIds();
    if (!ids.contains(productId)) {
      ids.add(productId);
      await _saveFavoriteProductIds(ids);
    }
  }

  Future<void> removeFavoriteProductId(String productId) async {
    final ids = await getFavoriteProductIds();
    if (ids.contains(productId)) {
      ids.remove(productId);
      await _saveFavoriteProductIds(ids);
    }
  }

  Future<bool> toggleFavorite(String productId) async {
    final ids = await getFavoriteProductIds();
    bool isCurrentlyFavorite = ids.contains(productId);
    if (isCurrentlyFavorite) {
      ids.remove(productId);
    } else {
      ids.add(productId);
    }
    await _saveFavoriteProductIds(ids);
    return !isCurrentlyFavorite; // Return the new state
  }
}
