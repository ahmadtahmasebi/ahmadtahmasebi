import 'package:flutter/material.dart';
import '../../models/ad_item.dart';
import '../../services/ad_service.dart';

final AdService _adService = AdService();

class AdManagementScreen extends StatefulWidget {
  @override
  _AdManagementScreenState createState() => _AdManagementScreenState();
}

class _AdManagementScreenState extends State<AdManagementScreen> {
  List<AdItem> _ads = [];
  final _titleController = TextEditingController();
  final _imagePathController = TextEditingController();
  final _targetUrlController = TextEditingController();
  AdItem? _selectedAd;

  @override
  void initState() {
    super.initState();
    _loadAds();
  }

  void _loadAds() {
    if (mounted) {
      setState(() {
        _ads = _adService.getAllAds();
      });
    }
  }

  void _showAdForm({AdItem? ad}) {
    _selectedAd = ad;
    _titleController.text = ad?.title ?? '';
    _imagePathController.text = ad?.imagePath ?? '';
    _targetUrlController.text = ad?.targetUrl ?? '';

    showDialog(
      context: context,
      builder: (BuildContext context) {
        return AlertDialog(
          title: Text(ad == null ? 'افزودن تبلیغ جدید' : 'ویرایش تبلیغ'),
          content: SingleChildScrollView(
            child: Column(
              mainAxisSize: MainAxisSize.min,
              children: <Widget>[
                TextField(controller: _titleController, decoration: InputDecoration(labelText: 'عنوان تبلیغ')),
                TextField(controller: _imagePathController, decoration: InputDecoration(labelText: 'مسیر عکس (نمایشی)')),
                TextField(controller: _targetUrlController, decoration: InputDecoration(labelText: 'لینک مقصد (اختیاری)')),
              ],
            ),
          ),
          actions: <Widget>[
            TextButton(child: Text('انصراف'), onPressed: () { Navigator.of(context).pop(); _clearForm(); }),
            ElevatedButton(
              child: Text(ad == null ? 'افزودن' : 'ذخیره'),
              onPressed: () {
                if (_titleController.text.isEmpty || _imagePathController.text.isEmpty) {
                  ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('عنوان و مسیر عکس الزامی است.')));
                  return;
                }
                final adItem = AdItem(
                  id: _selectedAd?.id ?? 'ad_user_${DateTime.now().millisecondsSinceEpoch}',
                  title: _titleController.text,
                  imagePath: _imagePathController.text,
                  targetUrl: _targetUrlController.text.isNotEmpty ? _targetUrlController.text : null,
                );
                if (_selectedAd == null) {
                  _adService.addAd(adItem);
                } else {
                  _adService.updateAd(adItem);
                }
                _loadAds();
                Navigator.of(context).pop();
                _clearForm();
                 ScaffoldMessenger.of(context).showSnackBar(
                    SnackBar(content: Text('عملیات تبلیغ ${ad == null ? "اضافه" : "ویرایش"} شد (در حافظه موقت).')),
                  );
              },
            ),
          ],
        );
      },
    );
  }

  void _clearForm() {
    _titleController.clear();
    _imagePathController.clear();
    _targetUrlController.clear();
    _selectedAd = null;
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('مدیریت تبلیغات'),
        actions: [IconButton(icon: Icon(Icons.add_photo_alternate_outlined), onPressed: () => _showAdForm(), tooltip: 'افزودن تبلیغ')],
      ),
      body: _ads.isEmpty
          ? Center(child: Text('تبلیغی برای نمایش وجود ندارد.'))
          : ListView.builder(
              itemCount: _ads.length,
              itemBuilder: (context, index) {
                final ad = _ads[index];
                return Card(
                  margin: EdgeInsets.symmetric(horizontal: 8, vertical: 4),
                  child: ListTile(
                    leading: SizedBox(width: 50, height: 50, child: Icon(Icons.campaign_outlined, color: Colors.teal, size: 30)),
                    title: Text(ad.title, style: TextStyle(fontWeight: FontWeight.bold)),
                    subtitle: Text('مسیر عکس: ${ad.imagePath}\nلینک: ${ad.targetUrl ?? "ندارد"}'),
                    isThreeLine: true,
                    trailing: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        IconButton(icon: Icon(Icons.edit_outlined, color: Colors.grey[700]), onPressed: () => _showAdForm(ad: ad)),
                        IconButton(
                          icon: Icon(Icons.delete_outline, color: Colors.red[700]),
                          onPressed: () {
                            _adService.deleteAd(ad.id);
                            _loadAds();
                            ScaffoldMessenger.of(context).showSnackBar(SnackBar(content: Text('تبلیغ "${ad.title}" حذف شد (از حافظه موقت).')));
                          },
                        ),
                      ],
                    ),
                  ),
                );
              },
            ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => _showAdForm(),
        tooltip: 'افزودن تبلیغ جدید',
        child: Icon(Icons.add),
      ),
    );
  }
}
