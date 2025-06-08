import 'package:flutter/material.dart';
import '../../../../core/models/product_model.dart';
import '../../../../core/services/firestore_service.dart';
import '../../../../core/services/product_service_interface.dart';
import 'admin_add_edit_product_screen.dart'; // Import the screen

class AdminProductListScreen extends StatefulWidget {
  const AdminProductListScreen({Key? key}) : super(key: key);

  @override
  _AdminProductListScreenState createState() => _AdminProductListScreenState();
}

class _AdminProductListScreenState extends State<AdminProductListScreen> {
  final IProductService _productService = FirestoreService();

  void _navigateToAddEditScreen({Product? product}) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => AdminAddEditProductScreen(productToEdit: product),
      ),
    ).then((_) {
      // No explicit setState needed here as StreamBuilder will rebuild if data changes.
      // If you were managing a local list, you'd refresh it here.
      print("Returned from Add/Edit screen");
    });
  }

  Future<void> _deleteProduct(String productId, String productName) async {
    final bool? confirmDelete = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('تایید حذف', style: TextStyle(fontFamily: 'IranYekan')),
          content: Text('آیا از حذف محصول "$productName" مطمئن هستید؟', style: const TextStyle(fontFamily: 'IranYekan')),
          actions: <Widget>[
            TextButton(
              child: const Text('لغو', style: TextStyle(fontFamily: 'IranYekan')),
              onPressed: () => Navigator.of(context).pop(false),
            ),
            TextButton(
              child: const Text('حذف', style: TextStyle(fontFamily: 'IranYekan', color: Colors.red)),
              onPressed: () => Navigator.of(context).pop(true),
            ),
          ],
        );
      },
    );

    if (confirmDelete == true) {
      try {
        await _productService.deleteProduct(productId);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('محصول "$productName" با موفقیت حذف شد.', style: const TextStyle(fontFamily: 'IranYekan'))),
          );
        }
      } catch (e) {
         if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('خطا در حذف محصول: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('مدیریت محصولات', style: TextStyle(fontFamily: 'IranYekan')),
      ),
      body: StreamBuilder<List<Product>>(
        stream: _productService.getProducts(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('خطا: ${snapshot.error}', style: const TextStyle(fontFamily: 'IranYekan')));
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('محصولی یافت نشد. برای افزودن روی + کلیک کنید.', style: TextStyle(fontFamily: 'IranYekan')));
          }

          final products = snapshot.data!;

          return ListView.separated(
            itemCount: products.length,
            separatorBuilder: (context, index) => const Divider(),
            itemBuilder: (context, index) {
              final product = products[index];
              return ListTile(
                leading: product.imageUrl.isNotEmpty
                  ? Image.network(product.imageUrl, width: 50, height: 50, fit: BoxFit.cover, errorBuilder: (c,o,s) => const Icon(Icons.error))
                  : const Icon(Icons.image_not_supported, size: 50),
                title: Text(product.name, style: const TextStyle(fontFamily: 'IranYekan', fontWeight: FontWeight.bold)),
                subtitle: Text('دسته: ${product.categoryId} - قیمت: ${product.price} تومان', style: const TextStyle(fontFamily: 'IranYekan')),
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.edit, color: Colors.blue),
                      tooltip: 'ویرایش',
                      onPressed: () => _navigateToAddEditScreen(product: product),
                    ),
                    IconButton(
                      icon: const Icon(Icons.delete, color: Colors.red),
                      tooltip: 'حذف',
                      onPressed: () => _deleteProduct(product.id, product.name),
                    ),
                  ],
                ),
                onTap: () => _navigateToAddEditScreen(product: product),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _navigateToAddEditScreen(),
        tooltip: 'افزودن محصول جدید',
        child: const Icon(Icons.add),
      ),
    );
  }
}
