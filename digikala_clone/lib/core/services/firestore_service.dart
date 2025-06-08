import 'package:cloud_firestore/cloud_firestore.dart';
import '../models/product_model.dart';
import '../models/category_model.dart';
import '../models/drug_model.dart';
import '../models/news_item_model.dart';
import '../models/user_comment_model.dart';
import 'product_service_interface.dart';
import 'category_service_interface.dart';
import 'drug_service_interface.dart';
import 'news_service_interface.dart';

class FirestoreService implements IProductService, ICategoryService, IDrugService, INewsService {
  final FirebaseFirestore _firestore = FirebaseFirestore.instance;

  late final CollectionReference _productsCollection;
  late final CollectionReference _categoriesCollection;
  late final CollectionReference _drugsCollection;
  late final CollectionReference _newsItemsCollection;

  FirestoreService() {
    _productsCollection = _firestore.collection('products');
    _categoriesCollection = _firestore.collection('categories');
    _drugsCollection = _firestore.collection('drugs');
    _newsItemsCollection = _firestore.collection('newsItems');
  }

  //--- Helper for comments subcollection ---
  CollectionReference _commentsCollection(String entityId, String entityType) {
    return _firestore.collection(entityType).doc(entityId).collection('comments');
  }

  //--- Product Service Methods ---
  @override
  Future<void> addProduct(Product product) {
    return _productsCollection.doc(product.id).set(product.toJson());
  }

  @override
  Future<void> updateProduct(Product product) {
    return _productsCollection.doc(product.id).update(product.toJson());
  }

  @override
  Future<void> deleteProduct(String productId) {
    return _productsCollection.doc(productId).delete();
  }

  @override
  Stream<List<Product>> getProducts() {
    return _productsCollection.snapshots().map((snapshot) {
      return snapshot.docs.map((doc) {
        return Product.fromJson(doc.data() as Map<String, dynamic>, doc.id);
      }).toList();
    });
  }

  @override
  Stream<List<Product>> getProductsByCategory(String categoryId) {
    return _productsCollection
        .where('categoryId', isEqualTo: categoryId)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) {
        return Product.fromJson(doc.data() as Map<String, dynamic>, doc.id);
      }).toList();
    });
  }

  @override
  Future<Product?> getProductById(String productId) async {
    final docSnapshot = await _productsCollection.doc(productId).get();
    if (docSnapshot.exists) {
      return Product.fromJson(docSnapshot.data() as Map<String, dynamic>, docSnapshot.id);
    }
    return null;
  }

  @override
  Future<void> incrementProductView(String productId) {
    return _productsCollection.doc(productId).update({'views': FieldValue.increment(1)});
  }

  @override
  Future<void> likeProduct(String productId, String userId) {
    return _firestore.runTransaction((transaction) async {
      DocumentReference productRef = _productsCollection.doc(productId);
      transaction.update(productRef, {
        'likes': FieldValue.increment(1),
        'likedBy': FieldValue.arrayUnion([userId])
      });
    });
  }

  @override
  Future<void> unlikeProduct(String productId, String userId) {
     return _firestore.runTransaction((transaction) async {
      DocumentReference productRef = _productsCollection.doc(productId);
      transaction.update(productRef, {
        'likes': FieldValue.increment(-1),
        'likedBy': FieldValue.arrayRemove([userId])
      });
    });
  }

  @override
  Stream<List<UserComment>> getProductComments(String productId) {
    return _commentsCollection(productId, 'products')
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) {
        return UserComment.fromJson(doc.data() as Map<String, dynamic>, doc.id);
      }).toList();
    });
  }

  @override
  Future<void> addProductComment(UserComment comment) {
    return _commentsCollection(comment.entityId, 'products')
        .add(comment.toJson()..remove('id')); // Firestore auto-generates comment ID
  }


  //--- Category Service Methods ---
  @override
  Future<void> addCategory(Category category) {
    return _categoriesCollection.doc(category.id).set(category.toJson());
  }

  @override
  Future<void> updateCategory(Category category) {
    return _categoriesCollection.doc(category.id).update(category.toJson());
  }

  @override
  Future<void> deleteCategory(String categoryId) {
    return _categoriesCollection.doc(categoryId).delete();
  }

  @override
  Stream<List<Category>> getCategories() {
    return _categoriesCollection.orderBy('name').snapshots().map((snapshot) { // Ordered by name
      return snapshot.docs.map((doc) {
        return Category.fromJson(doc.data() as Map<String, dynamic>, doc.id);
      }).toList();
    });
  }

  @override
  Future<Category?> getCategoryById(String categoryId) async {
    final docSnapshot = await _categoriesCollection.doc(categoryId).get();
    if (docSnapshot.exists) {
      return Category.fromJson(docSnapshot.data() as Map<String, dynamic>, docSnapshot.id);
    }
    return null;
  }

  //--- Drug Service Methods ---
  @override
  Future<void> addDrug(Drug drug) {
    return _drugsCollection.doc(drug.id).set(drug.toJson());
  }

  @override
  Future<void> updateDrug(Drug drug) {
    return _drugsCollection.doc(drug.id).update(drug.toJson());
  }

  @override
  Future<void> deleteDrug(String drugId) {
    return _drugsCollection.doc(drugId).delete();
  }

  @override
  Stream<List<Drug>> getDrugs() {
    return _drugsCollection.snapshots().map((snapshot) {
      return snapshot.docs.map((doc) {
        return Drug.fromJson(doc.data() as Map<String, dynamic>, doc.id);
      }).toList();
    });
  }

  @override
  Stream<List<Drug>> getDrugsByCategory(String categoryId) {
     return _drugsCollection
        .where('categoryId', isEqualTo: categoryId)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) {
        return Drug.fromJson(doc.data() as Map<String, dynamic>, doc.id);
      }).toList();
    });
  }

  @override
  Future<Drug?> getDrugById(String drugId) async {
    final docSnapshot = await _drugsCollection.doc(drugId).get();
    if (docSnapshot.exists) {
      return Drug.fromJson(docSnapshot.data() as Map<String, dynamic>, docSnapshot.id);
    }
    return null;
  }

  @override
  Future<void> incrementDrugView(String drugId) {
    return _drugsCollection.doc(drugId).update({'views': FieldValue.increment(1)});
  }

  @override
  Future<void> likeDrug(String drugId, String userId) {
    return _firestore.runTransaction((transaction) async {
      DocumentReference drugRef = _drugsCollection.doc(drugId);
      transaction.update(drugRef, {
        'likes': FieldValue.increment(1),
        'likedBy': FieldValue.arrayUnion([userId]) // Assumes Drug model has likedBy
      });
    });
  }

  @override
  Future<void> unlikeDrug(String drugId, String userId) {
    return _firestore.runTransaction((transaction) async {
      DocumentReference drugRef = _drugsCollection.doc(drugId);
      transaction.update(drugRef, {
        'likes': FieldValue.increment(-1),
        'likedBy': FieldValue.arrayRemove([userId]) // Assumes Drug model has likedBy
      });
    });
  }

  @override
  Stream<List<UserComment>> getDrugComments(String drugId) {
    return _commentsCollection(drugId, 'drugs')
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) {
        return UserComment.fromJson(doc.data() as Map<String, dynamic>, doc.id);
      }).toList();
    });
  }

  @override
  Future<void> addDrugComment(UserComment comment) {
     return _commentsCollection(comment.entityId, 'drugs')
        .add(comment.toJson()..remove('id'));
  }

  //--- News Service Methods ---
  @override
  Future<void> addNewsItem(NewsItem item) {
    return _newsItemsCollection.doc(item.id).set(item.toJson());
  }

  @override
  Future<void> updateNewsItem(NewsItem item) {
    return _newsItemsCollection.doc(item.id).update(item.toJson());
  }

  @override
  Future<void> deleteNewsItem(String newsItemId) {
    return _newsItemsCollection.doc(newsItemId).delete();
  }

  @override
  Stream<List<NewsItem>> getNewsItems(NewsItemType type) {
    return _newsItemsCollection
        .where('type', isEqualTo: newsItemTypeToString(type))
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) {
        return NewsItem.fromJson(doc.data() as Map<String, dynamic>, doc.id);
      }).toList();
    });
  }

  @override
  Stream<List<NewsItem>> getNewsItemsByCategory(NewsItemType type, String category) {
    return _newsItemsCollection
        .where('type', isEqualTo: newsItemTypeToString(type))
        .where('category', isEqualTo: category)
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) {
        return NewsItem.fromJson(doc.data() as Map<String, dynamic>, doc.id);
      }).toList();
    });
  }

  @override
  Future<NewsItem?> getNewsItemById(String newsItemId) async {
    final docSnapshot = await _newsItemsCollection.doc(newsItemId).get();
    if (docSnapshot.exists) {
      return NewsItem.fromJson(docSnapshot.data() as Map<String, dynamic>, docSnapshot.id);
    }
    return null;
  }

  @override
  Future<void> incrementNewsItemView(String newsItemId) {
    return _newsItemsCollection.doc(newsItemId).update({'views': FieldValue.increment(1)});
  }

  @override
  Stream<List<UserComment>> getNewsItemComments(String newsItemId) {
    return _commentsCollection(newsItemId, 'newsItems')
        .orderBy('createdAt', descending: true)
        .snapshots()
        .map((snapshot) {
      return snapshot.docs.map((doc) {
        return UserComment.fromJson(doc.data() as Map<String, dynamic>, doc.id);
      }).toList();
    });
  }

  @override
  Future<void> addNewsItemComment(UserComment comment) {
    return _commentsCollection(comment.entityId, 'newsItems')
        .add(comment.toJson()..remove('id'));
  }
}
