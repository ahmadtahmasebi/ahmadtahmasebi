import 'package:flutter/material.dart';
import '../../../../core/models/drug_model.dart';
import '../../../../core/services/firestore_service.dart';
import '../../../../core/services/drug_service_interface.dart';
import 'admin_add_edit_drug_screen.dart'; // Will be created next

class AdminDrugListScreen extends StatefulWidget {
  const AdminDrugListScreen({Key? key}) : super(key: key);

  @override
  _AdminDrugListScreenState createState() => _AdminDrugListScreenState();
}

class _AdminDrugListScreenState extends State<AdminDrugListScreen> {
  final IDrugService _drugService = FirestoreService();

  void _navigateToAddEditScreen({Drug? drug}) {
    Navigator.push(
      context,
      MaterialPageRoute(
        builder: (_) => AdminAddEditDrugScreen(drugToEdit: drug),
      ),
    ).then((_) {
      // StreamBuilder will handle UI updates if data changes
    });
  }

  Future<void> _deleteDrug(String drugId, String drugName) async {
    final bool? confirmDelete = await showDialog<bool>(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: const Text('تایید حذف', style: TextStyle(fontFamily: 'IranYekan')),
          content: Text('آیا از حذف داروی "$drugName" مطمئن هستید؟', style: const TextStyle(fontFamily: 'IranYekan')),
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
        await _drugService.deleteDrug(drugId);
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('داروی "$drugName" با موفقیت حذف شد.', style: const TextStyle(fontFamily: 'IranYekan'))),
          );
        }
      } catch (e) {
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            SnackBar(content: Text('خطا در حذف دارو: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
          );
        }
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('مدیریت داروها', style: TextStyle(fontFamily: 'IranYekan')),
      ),
      body: StreamBuilder<List<Drug>>(
        stream: _drugService.getDrugs(),
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError) {
            return Center(child: Text('خطا: ${snapshot.error}', style: const TextStyle(fontFamily: 'IranYekan')));
          }
          if (!snapshot.hasData || snapshot.data!.isEmpty) {
            return const Center(child: Text('دارویی یافت نشد. برای افزودن روی + کلیک کنید.', style: TextStyle(fontFamily: 'IranYekan')));
          }

          final drugs = snapshot.data!;

          return ListView.separated(
            itemCount: drugs.length,
            separatorBuilder: (context, index) => const Divider(),
            itemBuilder: (context, index) {
              final drug = drugs[index];
              return ListTile(
                title: Text(drug.genericName, style: const TextStyle(fontFamily: 'IranYekan', fontWeight: FontWeight.bold)),
                subtitle: Text(
                  'نام‌های تجاری: ${drug.brandNames.join(", ")}\nقدرت: ${drug.strength} - اشکال دارویی: ${drug.dosageForms}',
                  style: const TextStyle(fontFamily: 'IranYekan', fontSize: 12),
                ),
                isThreeLine: true,
                trailing: Row(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    IconButton(
                      icon: const Icon(Icons.edit, color: Colors.blue),
                      tooltip: 'ویرایش',
                      onPressed: () => _navigateToAddEditScreen(drug: drug),
                    ),
                    IconButton(
                      icon: const Icon(Icons.delete, color: Colors.red),
                      tooltip: 'حذف',
                      onPressed: () => _deleteDrug(drug.id, drug.genericName),
                    ),
                  ],
                ),
                onTap: () => _navigateToAddEditScreen(drug: drug),
              );
            },
          );
        },
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _navigateToAddEditScreen(),
        tooltip: 'افزودن داروی جدید',
        child: const Icon(Icons.add),
      ),
    );
  }
}
