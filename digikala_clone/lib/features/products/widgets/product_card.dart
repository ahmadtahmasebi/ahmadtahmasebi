import 'package:flutter/material.dart';
import '../../../core/models/product_model.dart';
import '../screens/product_detail_screen.dart'; // Import ProductDetailScreen

class ProductCard extends StatelessWidget {
  final Product product;

  const ProductCard({Key? key, required this.product}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    return GestureDetector(
      onTap: () {
        Navigator.push(
          context,
          MaterialPageRoute(
            builder: (_) => ProductDetailScreen(productId: product.id),
          ),
        );
      },
      child: Card(
        elevation: 2.0,
        shape: RoundedRectangleBorder(
          borderRadius: BorderRadius.circular(10.0),
        ),
        child: SizedBox(
          width: 160,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            mainAxisAlignment: MainAxisAlignment.spaceBetween, // To push price to bottom if card has fixed height
            children: <Widget>[
              Column( // Group for image and name
                crossAxisAlignment: CrossAxisAlignment.start,
                children: [
                  ClipRRect(
                    borderRadius: const BorderRadius.only(
                      topLeft: Radius.circular(10.0),
                      topRight: Radius.circular(10.0),
                    ),
                    child: AspectRatio(
                      aspectRatio: 1.2, // Adjusted for a slightly less square image, common for products
                      child: product.imageUrl.isNotEmpty
                          ? Image.network(
                              product.imageUrl,
                              fit: BoxFit.cover,
                              errorBuilder: (context, error, stackTrace) {
                                return const Icon(Icons.broken_image, size: 50, color: Colors.grey);
                              },
                              loadingBuilder: (BuildContext context, Widget child, ImageChunkEvent? loadingProgress) {
                                if (loadingProgress == null) return child;
                                return Center(
                                  child: CircularProgressIndicator(
                                    strokeWidth: 2.0,
                                    value: loadingProgress.expectedTotalBytes != null
                                        ? loadingProgress.cumulativeBytesLoaded / loadingProgress.expectedTotalBytes!
                                        : null,
                                  ),
                                );
                              },
                            )
                          : Container(
                              color: Colors.grey[200],
                              child: const Icon(Icons.image_not_supported, size: 50, color: Colors.grey),
                            ),
                    ),
                  ),
                  Padding(
                    padding: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 4.0),
                    child: Text(
                      product.name,
                      style: Theme.of(context).textTheme.bodyMedium?.copyWith(
                        fontFamily: 'IranYekan',
                        fontWeight: FontWeight.w500
                      ),
                      maxLines: 2,
                      overflow: TextOverflow.ellipsis,
                    ),
                  ),
                ],
              ),
              Padding(
                padding: const EdgeInsets.all(8.0),
                child: Text(
                  '${product.price.toStringAsFixed(0)} تومان',
                  style: Theme.of(context).textTheme.titleSmall?.copyWith(
                    fontFamily: 'IranYekan',
                    color: Colors.green[800],
                    fontWeight: FontWeight.bold
                  ),
                  textAlign: TextAlign.end, // Align price to the right
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
