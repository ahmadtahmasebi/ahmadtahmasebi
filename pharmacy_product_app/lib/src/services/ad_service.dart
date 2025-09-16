import '../models/ad_item.dart';
import 'dart:math';

class AdService {
  final List<AdItem> _ads = [
    AdItem(id: 'ad_1', title: 'تخفیف ویژه محصولات بهداشتی', imagePath: 'placeholder_ad_health.png', targetUrl: '/products/cosmetics/cat_cos_1'),
    AdItem(id: 'ad_2', title: 'معرفی مکمل های جدید ورزشی', imagePath: 'placeholder_ad_supplements.png', targetUrl: '/products/supplements'),
    AdItem(id: 'ad_3', title: 'نکات مهم سلامتی در فصل بهار', imagePath: 'placeholder_ad_spring.png', targetUrl: '/articles/art_1'),
  ];
  final Random _random = Random();

  List<AdItem> getAllAds() {
    return List.from(_ads);
  }

  void addAd(AdItem ad) {
    // Ensure unique ID if generated here, or that passed ID is not already present
    // This logic assumes user-passed IDs might not follow the 'ad_user_' pattern initially if they try to set it manually
    if (_ads.any((a) => a.id == ad.id)) {
       print('Ad with ID "${ad.id}" already exists.'); return;
    }
    if (_ads.any((a) => a.title.toLowerCase() == ad.title.toLowerCase())) {
       print('Ad with title "${ad.title}" already exists.'); return;
    }

    // If ID was empty or didn't follow a specific pattern, one could generate one.
    // The form logic already generates 'ad_user_...' so this is more of a safeguard.
    final AdItem newAdWithEnsuredId = AdItem(
        id: ad.id.startsWith('ad_user_') ? ad.id : 'ad_user_${(_random.nextInt(9999) + _ads.length + 1).toString()}',
        title: ad.title,
        imagePath: ad.imagePath,
        targetUrl: ad.targetUrl
    );
    _ads.add(newAdWithEnsuredId);
  }

  void updateAd(AdItem ad) {
    final index = _ads.indexWhere((a) => a.id == ad.id);
    if (index != -1) {
      _ads[index] = ad;
    }
  }

  void deleteAd(String adId) {
    _ads.removeWhere((a) => a.id == adId);
  }

  AdItem? getAdById(String adId) {
    try {
      return _ads.firstWhere((a) => a.id == adId);
    } catch (e) {
      return null;
    }
  }
}
