import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/models/product_model.dart';
import '../../../core/models/user_comment_model.dart';
import '../../../core/services/auth_service.dart'; // Import AuthService
import '../../../core/services/firestore_service.dart';
import '../../../core/services/product_service_interface.dart';
import '../../../core/services/favorites_service.dart';

class ProductDetailScreen extends StatefulWidget {
  final String productId;

  const ProductDetailScreen({Key? key, required this.productId}) : super(key: key);

  @override
  _ProductDetailScreenState createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  late Future<Product?> _productFuture;
  late Stream<List<UserComment>> _commentsStream;

  bool _isCloudLiked = false;
  int _cloudLikesCount = 0;
  bool _isUserFavorite = false; // Renamed from _isLocalFavorite

  String? _currentUserId; // Will be fetched from AuthService
  final IProductService _productService = FirestoreService();
  final FavoritesService _favoritesService = FavoritesService();
  final AuthService _authService = AuthService(); // Instantiate AuthService

  final TextEditingController _commentController = TextEditingController();
  final FocusNode _commentFocusNode = FocusNode();

  @override
  void initState() {
    super.initState();
    _currentUserId = _authService.currentUser?.uid;
    _loadProductDetails(incrementView: true);
    _commentsStream = _productService.getProductComments(widget.productId);
    if (_currentUserId != null) {
      _loadFavoriteStatus();
    }
  }

  Future<void> _loadProductDetails({bool incrementView = false}) async {
    if (incrementView && _currentUserId != null) { // Only increment if user is logged in? Or for any view?
      _productService.incrementProductView(widget.productId);
    }
    _productFuture = _productService.getProductById(widget.productId);
    _productFuture.then((product) {
      if (mounted && product != null) {
        setState(() {
          if (_currentUserId != null) {
            _isCloudLiked = product.likedBy?.contains(_currentUserId!) ?? false;
          } else {
            _isCloudLiked = false;
          }
          _cloudLikesCount = product.likes;
        });
      }
    });
  }

  Future<void> _loadFavoriteStatus() async {
    if (_currentUserId == null) return;
    _isUserFavorite = await _favoritesService.isFavorite(_currentUserId!, widget.productId);
    if (mounted) {
      setState(() {});
    }
  }

  Future<void> _toggleCloudLike() async {
    if (_currentUserId == null) {
       ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('برای لایک کردن ابتدا وارد شوید.', style: TextStyle(fontFamily: 'IranYekan'))),
      );
      return;
    }
    Product? product = await _productFuture;
    if (product == null) return;

    bool newLikedState = !_isCloudLiked;
    int newLikesCount = _cloudLikesCount + (newLikedState ? 1 : -1);

    if (mounted) {
      setState(() {
        _isCloudLiked = newLikedState;
        _cloudLikesCount = newLikesCount;
      });
    }

    try {
      if (newLikedState) {
        await _productService.likeProduct(widget.productId, _currentUserId!);
      } else {
        await _productService.unlikeProduct(widget.productId, _currentUserId!);
      }
    } catch (e) {
      if (mounted) {
        setState(() {
          _isCloudLiked = !newLikedState;
          _cloudLikesCount = _cloudLikesCount + (newLikedState ? -1 : 1);
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطا در بروزرسانی لایک: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
        );
      }
    }
  }

  Future<void> _toggleFavorite() async { // Renamed from _toggleLocalFavorite
    if (_currentUserId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('برای افزودن به علاقه‌مندی‌ها ابتدا وارد شوید.', style: TextStyle(fontFamily: 'IranYekan'))),
      );
      return;
    }
    try {
      final newFavoriteState = await _favoritesService.toggleFavorite(_currentUserId!, widget.productId);
      if (mounted) {
        setState(() {
          _isUserFavorite = newFavoriteState;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(
            newFavoriteState ? 'به علاقه‌مندی‌ها اضافه شد' : 'از علاقه‌مندی‌ها حذف شد',
            style: const TextStyle(fontFamily: 'IranYekan'))),
        );
      }
    } catch (e) {
       if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطا: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
        );
      }
    }
  }


  Future<void> _addComment() async {
    if (_commentController.text.isEmpty) return;
     if (_currentUserId == null) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('برای ثبت نظر ابتدا وارد شوید.', style: TextStyle(fontFamily: 'IranYekan'))),
      );
      return;
    }

    final newComment = UserComment(
      id: '',
      entityId: widget.productId,
      entityType: "product",
      userId: _currentUserId,
      userName: _authService.currentUser?.displayName ?? _authService.currentUser?.email ?? "کاربر ناشناس",
      text: _commentController.text,
      createdAt: Timestamp.now(),
    );

    try {
      await _productService.addProductComment(newComment);
      _commentController.clear();
      _commentFocusNode.unfocus();
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('نظر شما ثبت شد.', style: TextStyle(fontFamily: 'IranYekan'))),
      );
    } catch (e) {
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطا در ثبت نظر: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
        );
      }
    }
  }

  @override
  void dispose() {
    _commentController.dispose();
    _commentFocusNode.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: FutureBuilder<Product?>(
          future: _productFuture,
          builder: (context, snapshot) {
            if (snapshot.hasData && snapshot.data != null) {
              return Text(snapshot.data!.name, style: const TextStyle(fontFamily: 'IranYekan'));
            }
            return const Text('جزئیات محصول', style: TextStyle(fontFamily: 'IranYekan'));
          },
        ),
        backgroundColor: Colors.red[700],
        actions: [
          if (_currentUserId != null) // Only show favorite button if user is logged in
            FutureBuilder<Product?>(
              future: _productFuture,
              builder: (context, snapshot) {
                if (snapshot.hasData && snapshot.data != null) {
                  return IconButton(
                    icon: Icon(
                      _isUserFavorite ? Icons.bookmark : Icons.bookmark_border, // Updated state variable
                      color: Colors.white,
                    ),
                    onPressed: _toggleFavorite, // Updated method name
                    tooltip: 'علاقه‌مندی',
                  );
                }
                return const SizedBox.shrink();
              }
            )
          else
            IconButton(
              icon: const Icon(Icons.bookmark_border, color: Colors.white54),
              tooltip: 'برای افزودن به علاقه‌مندی‌ها وارد شوید',
              onPressed: () {
                 ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('برای افزودن به علاقه‌مندی‌ها ابتدا وارد شوید.', style: TextStyle(fontFamily: 'IranYekan'))),
                  );
              },
            )
        ],
      ),
      body: FutureBuilder<Product?>(
        future: _productFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError || !snapshot.hasData || snapshot.data == null) {
            return Center(child: Text('خطا در بارگذاری محصول: ${snapshot.error ?? "محصول یافت نشد."}', style: const TextStyle(fontFamily: 'IranYekan')));
          }

          final product = snapshot.data!;

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                if (product.imageUrl.isNotEmpty)
                  Center(
                    child: Image.network(
                      product.imageUrl,
                      height: 250,
                      fit: BoxFit.contain,
                      errorBuilder: (ctx, err, st) => const Icon(Icons.broken_image, size: 100, color: Colors.grey),
                    ),
                  ),
                const SizedBox(height: 16),
                Text(product.name, style: Theme.of(context).textTheme.headlineSmall?.copyWith(fontFamily: 'IranYekan', fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Text(
                  '${NumberFormat.currency(locale: 'fa_IR', symbol: 'تومان', decimalDigits: 0).format(product.price)}',
                  style: Theme.of(context).textTheme.titleLarge?.copyWith(color: Colors.green[700], fontFamily: 'IranYekan'),
                ),
                const SizedBox(height: 16),
                Row(
                  children: [
                    IconButton(
                      icon: Icon(_isCloudLiked ? Icons.favorite : Icons.favorite_border, color: Colors.red),
                      onPressed: _toggleCloudLike,
                    ),
                    Text('$_cloudLikesCount لایک', style: const TextStyle(fontFamily: 'IranYekan')),
                    const SizedBox(width: 16),
                    const Icon(Icons.remove_red_eye_outlined, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text('${product.views} بازدید', style: const TextStyle(fontFamily: 'IranYekan')),
                  ],
                ),
                const SizedBox(height: 16),
                if (product.brand != null && product.brand!.isNotEmpty)
                  Text('برند: ${product.brand}', style: const TextStyle(fontFamily: 'IranYekan', fontSize: 16)),
                if (product.countryOfOrigin != null && product.countryOfOrigin!.isNotEmpty)
                  Text('کشور سازنده: ${product.countryOfOrigin}', style: const TextStyle(fontFamily: 'IranYekan', fontSize: 16)),
                const SizedBox(height: 16),
                Text('توضیحات:', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontFamily: 'IranYekan', fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Text(product.description, style: const TextStyle(fontFamily: 'IranYekan', fontSize: 16)),
                if (product.specificFeatures != null && product.specificFeatures!.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  Text('ویژگی‌های خاص:', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontFamily: 'IranYekan', fontWeight: FontWeight.bold)),
                  const SizedBox(height: 8),
                  ...product.specificFeatures!.entries.map((entry) => Padding(
                        padding: const EdgeInsets.only(bottom: 4.0),
                        child: Text('• ${entry.key}: ${entry.value}', style: const TextStyle(fontFamily: 'IranYekan', fontSize: 16)),
                      )),
                ],
                const SizedBox(height: 24),
                Text('نظرات:', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontFamily: 'IranYekan', fontWeight: FontWeight.bold)),
                _buildCommentsSection(),
                _buildAddCommentField(),
              ],
            ),
          );
        },
      ),
    );
  }

  Widget _buildCommentsSection() {
    return StreamBuilder<List<UserComment>>(
      stream: _commentsStream,
      builder: (context, snapshot) {
        if (snapshot.connectionState == ConnectionState.waiting && !snapshot.hasData) {
          return const Center(child: CircularProgressIndicator());
        }
        if (snapshot.hasError) {
          return Text('خطا در بارگذاری نظرات: ${snapshot.error}', style: const TextStyle(fontFamily: 'IranYekan'));
        }
        if (!snapshot.hasData || snapshot.data!.isEmpty) {
          return const Padding(
            padding: EdgeInsets.symmetric(vertical: 16.0),
            child: Text('هنوز نظری ثبت نشده است.', style: TextStyle(fontFamily: 'IranYekan')),
          );
        }
        final comments = snapshot.data!;
        return ListView.builder(
          shrinkWrap: true,
          physics: const NeverScrollableScrollPhysics(),
          itemCount: comments.length,
          itemBuilder: (context, index) {
            final comment = comments[index];
            return Card(
              margin: const EdgeInsets.symmetric(vertical: 4.0),
              child: ListTile(
                title: Text(comment.userName, style: const TextStyle(fontFamily: 'IranYekan', fontWeight: FontWeight.bold)),
                subtitle: Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  children: [
                    Text(comment.text, style: const TextStyle(fontFamily: 'IranYekan')),
                    const SizedBox(height: 4),
                    Text(
                      DateFormat('yyyy/MM/dd HH:mm', 'fa_IR').format(comment.createdAt.toDate()),
                      style: Theme.of(context).textTheme.bodySmall?.copyWith(fontFamily: 'IranYekan', color: Colors.grey),
                    ),
                  ],
                ),
              ),
            );
          },
        );
      },
    );
  }

  Widget _buildAddCommentField() {
    return Padding(
      padding: const EdgeInsets.only(top: 16.0, bottom: 8.0),
      child: Row(
        children: [
          Expanded(
            child: TextField(
              controller: _commentController,
              focusNode: _commentFocusNode,
              decoration: InputDecoration(
                hintText: 'نظر خود را بنویسید...',
                hintStyle: const TextStyle(fontFamily: 'IranYekan'),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(8.0),
                ),
              ),
              style: const TextStyle(fontFamily: 'IranYekan'),
              textDirection: TextDirection.rtl,
            ),
          ),
          const SizedBox(width: 8),
          ElevatedButton(
            onPressed: _addComment,
            style: ElevatedButton.styleFrom(backgroundColor: Colors.red[700]),
            child: const Text('ارسال', style: TextStyle(fontFamily: 'IranYekan', color: Colors.white)),
          ),
        ],
      ),
    );
  }
}
