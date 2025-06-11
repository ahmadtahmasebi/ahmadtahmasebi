import 'package:flutter/material.dart';
import '../../models/product.dart';
import '../../models/category.dart';
import '../../services/category_service.dart';
import '../../services/product_service.dart'; // To update product model in memory

// Assuming global service instances
final CategoryService _categoryService = CategoryService();
final ProductService _productService = ProductService(); // For updating likes/views

class ProductDetailScreen extends StatefulWidget {
  final Product product;

  ProductDetailScreen({required this.product});

  @override
  _ProductDetailScreenState createState() => _ProductDetailScreenState();
}

class _ProductDetailScreenState extends State<ProductDetailScreen> {
  late Product _currentProductState;
  bool _isLiked = false; // Local UI state for like button

  @override
  void initState() {
    super.initState();
    _currentProductState = widget.product;
    // Simulate view count increment
    // This directly modifies the product instance from the service if it's not a copy.
    // If ProductService.getAllProducts returns copies, this change won't persist in the list
    // unless the list is refreshed or this specific product instance is updated in the service.
    // For now, we assume direct modification or that ProductService handles updates correctly.
    _currentProductState.viewCount++;
    _productService.updateProduct(_currentProductState); // Ensure change is reflected in service
  }

  void _toggleLike() {
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
              Container(
                height: 250,
                width: double.infinity,
                color: Colors.grey[300],
                alignment: Alignment.center,
                child: Icon(Icons.image, size: 100, color: Colors.grey[600]),
              )
            else
              Container(
                height: 250,
                width: double.infinity,
                color: Colors.grey[200],
                alignment: Alignment.center,
                child: Icon(Icons.image_not_supported, size: 100, color: Colors.grey[500]),
              ),
            SizedBox(height: 16),

            Text(
              _currentProductState.name,
              style: Theme.of(context).textTheme.headline5?.copyWith(fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),

            Text(
              'Category: ${category?.name ?? "Unknown"}',
              style: Theme.of(context).textTheme.subtitle1?.copyWith(color: Colors.grey[700]),
            ),
            SizedBox(height: 8),

            Text(
              '\$${_currentProductState.price.toStringAsFixed(2)}',
              style: Theme.of(context).textTheme.headline6?.copyWith(color: Theme.of(context).primaryColor, fontWeight: FontWeight.bold),
            ),
            SizedBox(height: 8),

            Text(
              'Stock: ${_currentProductState.stock}',
              style: Theme.of(context).textTheme.subtitle2,
            ),
            SizedBox(height: 16),

            Divider(),
            SizedBox(height: 16),

            Text(
              'Description',
              style: Theme.of(context).textTheme.headline6,
            ),
            SizedBox(height: 8),
            Text(
              _currentProductState.description.isNotEmpty ? _currentProductState.description : 'No description available.',
              style: Theme.of(context).textTheme.bodyText1?.copyWith(fontSize: 16, height: 1.5),
            ),
            SizedBox(height: 24),

            // --- User Interactions ---
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceAround,
              children: <Widget>[
                Column(
                  children: [
                    IconButton(
                      icon: Icon(
                        _isLiked ? Icons.thumb_up_alt : Icons.thumb_up_alt_outlined,
                        color: _isLiked ? Theme.of(context).primaryColor : Colors.grey[700],
                        size: 28,
                      ),
                      onPressed: _toggleLike,
                    ),
                    Text('${_currentProductState.likes} Likes', style: TextStyle(color: Colors.grey[700])),
                  ],
                ),
                Column(
                  children: [
                    Icon(Icons.remove_red_eye_outlined, color: Colors.grey[700], size: 28),
                    SizedBox(height: 4),
                    Text('${_currentProductState.viewCount} Views', style: TextStyle(color: Colors.grey[700])),
                  ],
                ),
              ],
            ),
            SizedBox(height: 24),

            Text(
              'Comments',
              style: Theme.of(context).textTheme.headline6,
            ),
            SizedBox(height: 8),
            Container(
              height: 100,
              width: double.infinity,
              padding: EdgeInsets.all(8),
              decoration: BoxDecoration(
                border: Border.all(color: Colors.grey[300]!),
                borderRadius: BorderRadius.circular(4),
              ),
              child: ListView(
                children: [
                  Text('Jane Doe: Great product! (Placeholder)', style: TextStyle(fontSize: 14)),
                  Divider(),
                  Text('John Smith: Could be better. (Placeholder)', style: TextStyle(fontSize: 14)),
                ],
              )
            ),
            SizedBox(height: 16),
            TextField(
              decoration: InputDecoration(
                labelText: 'Add a comment (Placeholder)',
                border: OutlineInputBorder(),
                suffixIcon: IconButton(
                  icon: Icon(Icons.send),
                  onPressed: () {
                     ScaffoldMessenger.of(context).showSnackBar(
                        SnackBar(content: Text('Comment functionality not implemented yet.')),
                      );
                  },
                ),
              ),
            ),
          ],
        ),
      ),
    );
  }
}
