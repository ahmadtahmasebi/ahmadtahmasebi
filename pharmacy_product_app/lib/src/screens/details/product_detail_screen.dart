import 'package:flutter/material.dart';
import '../../models/product.dart';
import '../../models/category.dart';
import '../../models/comment_model.dart'; // Import Comment model
import '../../services/category_service.dart';
import '../../services/product_service.dart';

final CategoryService _categoryService = CategoryService();
final ProductService _productService = ProductService();

class ProductDetailScreen extends StatefulWidget {
  final Product product;

  ProductDetailScreen({required this.product});

  @override
  _ProductDetailScreenState createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  late Product _currentProductState;
  bool _isLiked = false;
  final _commentController = TextEditingController(); // Controller for new comment

  @override
  void initState() {
    super.initState();
    // Fetch the most up-to-date product instance from the service
    // This ensures that if comments were added by another "user" (in a real app)
    // or if likes/views were updated elsewhere, we get that.
    // For this in-memory version, it ensures we modify the same instance held by the service.
    Product? serviceProduct = _productService.getProductById(widget.product.id);
    _currentProductState = serviceProduct ?? widget.product; // Fallback if somehow not in service

    // View count was incremented in a previous version of this screen.
    // To avoid double counting or ensure it's handled consistently,
    // this logic should ideally be in the service or a more robust view tracking mechanism.
    // For now, we assume the view count on _currentProductState is what we want to display.
    // If it was just incremented by another screen, this screen will show that.
    // If this screen is the first to "load" it for a while, it might re-increment.
    // Given the previous ProductDetailScreen logic, viewCount was already updated in the service.
    // So, _currentProductState from getProductById should have the updated viewCount.
  }

  @override
  void dispose() {
    _commentController.dispose();
    super.dispose();
  }

  void _toggleLike() {
    if (!mounted) return;
    setState(() {
      _isLiked = !_isLiked;
      if (_isLiked) {
        _currentProductState.likes++;
      } else {
        _currentProductState.likes--;
        if (_currentProductState.likes < 0) _currentProductState.likes = 0;
      }
      _productService.updateProduct(_currentProductState);
    });
  }

  void _addComment() {
    if (_commentController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('نظر شما نمی‌تواند خالی باشد.')),
      );
      return;
    }
    if (!mounted) return;

    final newComment = Comment(
      username: 'کاربر مهمان', // Hardcoded username for now
      text: _commentController.text,
    );

    setState(() {
      // Add to the local state's product instance's comments list
      _currentProductState.comments.add(newComment);
    });
    // Persist the updated product (now with the new comment) back to the service
    _productService.updateProduct(_currentProductState);

    _commentController.clear();
    FocusScope.of(context).unfocus(); // Dismiss keyboard
    ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('نظر شما ثبت شد (در حافظه موقت).')),
    );
  }

  @override
  Widget build(BuildContext context) {
    final Category? category = _categoryService.getCategoryById(_currentProductState.categoryId);

    return Scaffold(
      appBar: AppBar(
        title: Text(_currentProductState.name),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: <Widget>[
            if (_currentProductState.imagePath.isNotEmpty)
              Container(height: 250, width: double.infinity, color: Colors.grey[300], alignment: Alignment.center, child: Icon(Icons.image_outlined, size: 100, color: Colors.grey[600]))
            else
              Container(height: 250, width: double.infinity, color: Colors.grey[200], alignment: Alignment.center, child: Icon(Icons.image_not_supported_outlined, size: 100, color: Colors.grey[500])),
            SizedBox(height: 16),
            Text(_currentProductState.name, style: Theme.of(context).textTheme.headline5?.copyWith(fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('دسته: ${category?.name ?? "نامشخص"}', style: Theme.of(context).textTheme.subtitle1?.copyWith(color: Colors.grey[700])),
            SizedBox(height: 8),
            Text('\$${_currentProductState.price.toStringAsFixed(0)} تومان', style: Theme.of(context).textTheme.headline6?.copyWith(color: Theme.of(context).primaryColor, fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Text('موجودی: ${_currentProductState.stock}', style: Theme.of(context).textTheme.subtitle2),
            SizedBox(height: 16),
            Divider(),
            SizedBox(height: 16),
            Text('توضیحات', style: Theme.of(context).textTheme.headline6),
            SizedBox(height: 8),
            Text(_currentProductState.description.isNotEmpty ? _currentProductState.description : 'توضیحات موجود نیست.', style: Theme.of(context).textTheme.bodyText1?.copyWith(fontSize: 16, height: 1.5)),
            SizedBox(height: 24),

            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: <Widget>[
                Column(children: [IconButton(icon: Icon(_isLiked ? Icons.thumb_up_alt : Icons.thumb_up_alt_outlined, color: _isLiked ? Theme.of(context).primaryColor : Colors.grey[700], size: 28), onPressed: _toggleLike), Text('\${_currentProductState.likes} لایک', style: TextStyle(color: Colors.grey[700]))]),
                Column(children: [Icon(Icons.remove_red_eye_outlined, color: Colors.grey[700], size: 28), SizedBox(height: 4), Text('\${_currentProductState.viewCount} بازدید', style: TextStyle(color: Colors.grey[700]))]),
              ],
            ),
            SizedBox(height: 24),

            Text('نظرات کاربران', style: Theme.of(context).textTheme.headline6),
            SizedBox(height: 8),
            _currentProductState.comments.isEmpty
                ? Container(
                    padding: EdgeInsets.all(12),
                    width: double.infinity,
                    decoration: BoxDecoration(border: Border.all(color: Colors.grey[300]!), borderRadius: BorderRadius.circular(4)),
                    child: Text('هنوز نظری برای این محصول ثبت نشده است.', style: TextStyle(color: Colors.grey[600], fontStyle: FontStyle.italic)),
                  )
                : ListView.builder(
                    shrinkWrap: true,
                    physics: NeverScrollableScrollPhysics(), // Important inside SingleChildScrollView
                    itemCount: _currentProductState.comments.length,
                    itemBuilder: (context, index) {
                      final comment = _currentProductState.comments.reversed.toList()[index]; // Show newest first
                      return Card(
                        elevation: 1,
                        margin: EdgeInsets.symmetric(vertical: 4),
                        child: Padding(
                          padding: const EdgeInsets.all(10.0),
                          child: Column(
                            crossAxisAlignment: CrossAxisAlignment.start,
                            children: [
                              Text(comment.username, style: TextStyle(fontWeight: FontWeight.bold, color: Theme.of(context).primaryColorDark)),
                              SizedBox(height: 4),
                              Text(comment.text, style: Theme.of(context).textTheme.bodyText2),
                              SizedBox(height: 4),
                              Text(
                                '${comment.timestamp.toLocal().toString().substring(0, 16)}',
                                style: Theme.of(context).textTheme.caption?.copyWith(fontSize: 10),
                              ),
                            ],
                          ),
                        ),
                      );
                    },
                  ),
            SizedBox(height: 16),
            TextField(
              controller: _commentController,
              decoration: InputDecoration(
                labelText: 'نظر خود را بنویسید...',
                hintText: 'نظر شما برای دیگران مفید خواهد بود',
                border: OutlineInputBorder(),
                suffixIcon: IconButton(
                  icon: Icon(Icons.send_outlined),
                  onPressed: _addComment,
                  tooltip: 'ارسال نظر',
                ),
              ),
              maxLines: 3,
              minLines: 1,
              textInputAction: TextInputAction.send,
              onSubmitted: (_) => _addComment(),
            ),
          ],
        ),
      ),
    );
  }
}
