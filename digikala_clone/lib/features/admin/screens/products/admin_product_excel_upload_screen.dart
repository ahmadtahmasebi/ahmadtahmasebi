import 'package:flutter/material.dart';
import 'package:file_picker/file_picker.dart';
import '../../../../core/services/admin_product_upload_service.dart';

class AdminProductExcelUploadScreen extends StatefulWidget {
  const AdminProductExcelUploadScreen({Key? key}) : super(key: key);

  @override
  _AdminProductExcelUploadScreenState createState() => _AdminProductExcelUploadScreenState();
}

class _AdminProductExcelUploadScreenState extends State<AdminProductExcelUploadScreen> {
  final AdminProductUploadService _uploadService = AdminProductUploadService();
  PlatformFile? _selectedFile;
  bool _isUploading = false;
  String? _uploadMessage;

  Future<void> _pickFile() async {
    try {
      FilePickerResult? result = await FilePicker.platform.pickFiles(
        type: FileType.custom,
        allowedExtensions: ['xlsx', 'xls', 'csv'], // Common Excel/spreadsheet extensions
      );

      if (result != null) {
        setState(() {
          _selectedFile = result.files.first;
          _uploadMessage = null; // Clear previous messages
        });
      } else {
        // User canceled the picker
        if (mounted) {
          ScaffoldMessenger.of(context).showSnackBar(
            const SnackBar(content: Text('انتخاب فایل لغو شد.', style: TextStyle(fontFamily: 'IranYekan'))),
          );
        }
      }
    } catch (e) {
      print('Error picking file: $e');
      if (mounted) {
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text('خطا در انتخاب فایل: $e', style: const TextStyle(fontFamily: 'IranYekan'))),
        );
      }
    }
  }

  Future<void> _uploadAndProcessFile() async {
    if (_selectedFile == null) return;

    setState(() {
      _isUploading = true;
      _uploadMessage = null;
    });

    try {
      final resultMessage = await _uploadService.uploadProductExcel(_selectedFile!);
      if (mounted) {
        setState(() {
          _uploadMessage = resultMessage;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(resultMessage, style: const TextStyle(fontFamily: 'IranYekan'))),
        );
      }
    } catch (e) {
      final errorMessage = 'خطا در آپلود و پردازش فایل: $e';
      if (mounted) {
        setState(() {
          _uploadMessage = errorMessage;
        });
        ScaffoldMessenger.of(context).showSnackBar(
          SnackBar(content: Text(errorMessage, style: const TextStyle(fontFamily: 'IranYekan'))),
        );
      }
    } finally {
      if (mounted) {
        setState(() {
          _isUploading = false;
        });
      }
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: const Text('آپلود محصولات با اکسل', style: TextStyle(fontFamily: 'IranYekan')),
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: <Widget>[
            ElevatedButton.icon(
              icon: const Icon(Icons.file_upload_outlined),
              label: const Text('انتخاب فایل اکسل (.xlsx, .xls, .csv)', style: TextStyle(fontFamily: 'IranYekan')),
              onPressed: _pickFile,
              style: ElevatedButton.styleFrom(padding: const EdgeInsets.symmetric(vertical: 12)),
            ),
            const SizedBox(height: 20),
            if (_selectedFile != null)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(12.0),
                  child: Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      Text('فایل انتخاب شده:', style: Theme.of(context).textTheme.titleMedium?.copyWith(fontFamily: 'IranYekan')),
                      const SizedBox(height: 8),
                      Text('نام: ${_selectedFile!.name}', style: const TextStyle(fontFamily: 'IranYekan')),
                      Text('حجم: ${(_selectedFile!.size / 1024).toStringAsFixed(2)} KB', style: const TextStyle(fontFamily: 'IranYekan')),
                    ],
                  ),
                ),
              ),
            const SizedBox(height: 20),
            if (_selectedFile != null)
              ElevatedButton.icon(
                icon: const Icon(Icons.cloud_upload_outlined),
                label: const Text('آپلود و پردازش', style: TextStyle(fontFamily: 'IranYekan', fontSize: 16)),
                onPressed: _isUploading ? null : _uploadAndProcessFile,
                style: ElevatedButton.styleFrom(
                  backgroundColor: Colors.green,
                  padding: const EdgeInsets.symmetric(vertical: 12),
                ),
              ),
            if (_isUploading)
              const Padding(
                padding: EdgeInsets.only(top: 20.0),
                child: Center(child: CircularProgressIndicator()),
              ),
            if (_uploadMessage != null && !_isUploading)
              Padding(
                padding: const EdgeInsets.only(top: 20.0),
                child: Text(
                  _uploadMessage!,
                  textAlign: TextAlign.center,
                  style: TextStyle(
                    fontFamily: 'IranYekan',
                    color: _uploadMessage!.startsWith('خطا') ? Colors.red : Colors.green,
                    fontSize: 16,
                  ),
                ),
              ),
            const Spacer(),
            const Padding(
              padding: EdgeInsets.all(8.0),
              child: Text(
                'راهنما: فایل اکسل باید دارای ستون‌های مشخصی باشد (مانند: id, name, description, imageUrl, price, categoryId, brand, countryOfOrigin, specificFeatures_key1, specificFeatures_value1, ...). لطفاً از قالب نمونه استفاده کنید.',
                style: TextStyle(fontFamily: 'IranYekan', color: Colors.grey, fontSize: 12),
                textAlign: TextAlign.justify,
              ),
            )
          ],
        ),
      ),
    );
  }
}
