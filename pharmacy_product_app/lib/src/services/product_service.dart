import '../models/product.dart';
import 'dart:math'; // For Random

class ProductService {
  final List<Product> _products = [
    // Sample Cosmetics Products
    Product(
      id: 'prod_cos_1',
      name: 'کرم ضد آفتاب SPF 50',
      categoryId: 'cat_cos_1',
      price: 120000.0,
      description: 'کرم ضد آفتاب با محافظت بالا، مناسب انواع پوست، بدون رنگ',
      imagePath: '',
      stock: 50,
      minStock: 10,
      likes: 15,
      viewCount: 120
    ),
    Product(
      id: 'prod_cos_2',
      name: 'رژ لب مایع مات شماره ۱۰۲',
      categoryId: 'cat_cos_2',
      price: 85000.0,
      description: 'رژ لب مایع با دوام بالا و رنگدانه‌های غنی، جلوه مات',
      imagePath: '',
      stock: 30,
      minStock: 5,
      likes: 25,
      viewCount: 200
    ),
    Product(
      id: 'prod_cos_3',
      name: 'شامپو تقویت کننده آرگان',
      categoryId: 'cat_cos_3',
      price: 95000.0,
      description: 'شامپو حاوی روغن آرگان برای تقویت و ترمیم موهای آسیب دیده',
      imagePath: '',
      stock: 40,
      minStock: 8,
      likes: 30,
      viewCount: 150
    ),
    // Sample Medicines Products
    Product(
      id: 'prod_med_1',
      name: 'قرص استامینوفن ۵۰۰ میلی گرم',
      categoryId: 'cat_med_1',
      price: 15000.0,
      description: 'تسکین دهنده درد و تب، هر بسته شامل ۲۰ عدد قرص',
      imagePath: '',
      stock: 100,
      minStock: 20,
      likes: 50,
      viewCount: 350
    ),
    Product(
      id: 'prod_med_2',
      name: 'قرص ویتامین ث جوشان',
      categoryId: 'cat_med_2',
      price: 45000.0,
      description: 'کمک به تقویت سیستم ایمنی، با طعم پرتقال، ۲۰ عدد قرص جوشان',
      imagePath: '',
      stock: 60,
      minStock: 15,
      likes: 40,
      viewCount: 280
    ),
    Product(
      id: 'prod_med_3',
      name: 'اسپری بینی ضد حساسیت رینولکس',
      categoryId: 'cat_med_3',
      price: 70000.0,
      description: 'اسپری بینی برای رفع گرفتگی و علائم حساسیت فصلی',
      imagePath: '',
      stock: 30,
      minStock: 10,
      likes: 22,
      viewCount: 190
    ),
    // Sample Herbal Products
    Product(
      id: 'prod_herb_1',
      name: 'دمنوش آرامبخش گل گاو زبان',
      categoryId: 'cat_herb_1',
      price: 35000.0,
      description: 'ترکیبی از بهترین گیاهان دارویی برای آرامش و خواب راحت',
      imagePath: '',
      stock: 70,
      minStock: 10,
      likes: 18,
      viewCount: 110
    ),
    Product(
      id: 'prod_herb_2',
      name: 'عرق نعنا دو آتیشه ممتاز',
      categoryId: 'cat_herb_2',
      price: 25000.0,
      description: 'عرق نعنا خالص و طبیعی، مفید برای دستگاه گوارش',
      imagePath: '',
      stock: 80,
      minStock: 15,
      likes: 28,
      viewCount: 160
    ),
    // Sample Supplements Products
    Product(
      id: 'prod_sup_1',
      name: 'پودر پروتئین وی ۱۰۰٪ شکلاتی',
      categoryId: 'cat_sup_1', // مکمل های ورزشی
      price: 750000.0,
      description: 'پودر پروتئین وی ایزوله با طعم شکلات، مناسب برای عضله سازی',
      imagePath: '', // Placeholder
      stock: 25,
      minStock: 5,
      likes: 60,
      viewCount: 450
    ),
    Product(
      id: 'prod_sup_2',
      name: 'قرص مولتی ویتامین مینرال آقایان',
      categoryId: 'cat_sup_2', // مکمل های غذایی
      price: 180000.0,
      description: 'تامین کننده ویتامین ها و مواد معدنی ضروری برای آقایان',
      imagePath: '', // Placeholder
      stock: 50,
      minStock: 10,
      likes: 35,
      viewCount: 220
    )
    // All sample products added. Placeholder comment can be removed or kept for future.
  ];
  final Random _random = Random();

  List<Product> getAllProducts() {
    return List.from(_products);
  }

  void addProduct(Product product) {
    final newProduct = Product(
      id: product.id.isEmpty ? 'prod_user_${(_random.nextInt(99999) + _products.length + 1).toString()}' : product.id,
      name: product.name,
      categoryId: product.categoryId,
      price: product.price,
      description: product.description,
      imagePath: product.imagePath,
      stock: product.stock,
      minStock: product.minStock,
      likes: product.likes,
      viewCount: product.viewCount,
    );

    if (product.id.isNotEmpty && _products.any((p) => p.id == newProduct.id)) {
        print("Product with ID ${newProduct.id} already exists. Not adding.");
        return;
    }
    if (_products.any((p) => p.name.toLowerCase() == newProduct.name.toLowerCase() && p.categoryId == newProduct.categoryId)) {
        print("Product with similar name in this category already exists: \"${newProduct.name}\". Not adding.");
        return;
    }
    _products.add(newProduct);
  }

  void updateProduct(Product product) {
    final index = _products.indexWhere((p) => p.id == product.id);
    if (index != -1) {
      _products[index] = product;
    }
  }

  void deleteProduct(String productId) {
    _products.removeWhere((p) => p.id == productId);
  }

  List<Product> getProductsByCategoryId(String categoryId) {
    return _products.where((p) => p.categoryId == categoryId).toList();
  }

  Product? getProductById(String productId) {
    try {
      return _products.firstWhere((p) => p.id == productId);
    } catch (e) {
      return null; // Not found
    }
  }
}
