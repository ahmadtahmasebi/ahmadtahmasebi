import 'package:flutter/material.dart';
import '../../models/article.dart';
import '../../services/article_service.dart';

final ArticleService _articleService = ArticleService();

class ArticleManagementScreen extends StatefulWidget {
  @override
  _ArticleManagementScreenState createState() => _ArticleManagementScreenState();
}

class _ArticleManagementScreenState extends State<ArticleManagementScreen> {
  List<Article> _articles = [];
  final _titleController = TextEditingController();
  final _contentController = TextEditingController();
  final _imagePathController = TextEditingController(); // New controller for image path
  Article? _selectedArticle;

  @override
  void initState() {
    super.initState();
    _loadArticles();
  }

  void _loadArticles() {
    if (mounted) {
      setState(() {
        _articles = _articleService.getAllArticles();
      });
    }
  }

  void _addOrUpdateArticle() {
    if (_titleController.text.isEmpty || _contentController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('عنوان و محتوا نمی‌توانند خالی باشند!')),
      );
      return;
    }

    if (_selectedArticle == null) {
      _articleService.addArticle(_titleController.text, _contentController.text, _imagePathController.text);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('مقاله اضافه شد!')),
      );
    } else {
      final updatedArticle = Article(
        id: _selectedArticle!.id,
        title: _titleController.text,
        content: _contentController.text,
        datePublished: _selectedArticle!.datePublished,
        imagePath: _imagePathController.text, // Include imagePath
      );
      _articleService.updateArticle(updatedArticle);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('مقاله به‌روزرسانی شد!')),
      );
    }
    _clearForm();
    _loadArticles();
  }

  void _deleteArticle(String articleId) {
    _articleService.deleteArticle(articleId);
    _loadArticles();
     ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('مقاله حذف شد!')),
    );
  }

  void _selectArticleForEditing(Article article) {
    if (mounted) {
      setState(() {
        _selectedArticle = article;
        _titleController.text = article.title;
        _contentController.text = article.content;
        _imagePathController.text = article.imagePath; // Populate imagePath field
      });
    }
  }

  void _clearForm() {
    if (mounted) {
      setState(() {
        _selectedArticle = null;
        _titleController.clear();
        _contentController.clear();
        _imagePathController.clear(); // Clear imagePath field
      });
    }
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('مدیریت مقالات'),
        actions: [
          IconButton(
            icon: Icon(Icons.clear_all_outlined),
            onPressed: _clearForm,
            tooltip: 'پاک کردن فرم',
          )
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.stretch,
          children: [
            Card( // Form wrapped in a card
              elevation: 2,
              child: Padding(
                padding: const EdgeInsets.all(16.0),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    TextField(
                      controller: _titleController,
                      decoration: InputDecoration(labelText: 'عنوان مقاله'),
                    ),
                    SizedBox(height: 10),
                    TextField(
                      controller: _imagePathController, // Image path field
                      decoration: InputDecoration(labelText: 'مسیر عکس (نمایشی)'),
                    ),
                    SizedBox(height: 10),
                    TextField(
                      controller: _contentController,
                      decoration: InputDecoration(labelText: 'محتوای مقاله'),
                      maxLines: 5,
                      minLines: 3,
                    ),
                    SizedBox(height: 20),
                    ElevatedButton(
                      onPressed: _addOrUpdateArticle,
                      child: Text(_selectedArticle == null ? 'افزودن مقاله' : 'ذخیره تغییرات'),
                    ),
                  ],
                ),
              ),
            ),
            SizedBox(height: 20),
            Text('لیست مقالات موجود', style: Theme.of(context).textTheme.subtitle1?.copyWith(fontWeight: FontWeight.bold)),
            SizedBox(height: 8),
            Expanded(
              child: _articles.isEmpty
                  ? Center(child: Text('مقاله‌ای یافت نشد.'))
                  : ListView.builder(
                      itemCount: _articles.length,
                      itemBuilder: (context, index) {
                        final article = _articles[index];
                        return Card(
                          elevation: 1.5,
                          margin: EdgeInsets.symmetric(vertical: 4.0),
                          child: ListTile(
                            leading: article.imagePath.isNotEmpty
                                ? SizedBox(width: 50, height: 50, child: Icon(Icons.image_outlined, color: Colors.grey[400]))
                                : SizedBox(width: 50, height: 50, child: Icon(Icons.article_outlined, color: Colors.grey[400])),
                            title: Text(article.title, style: TextStyle(fontWeight: FontWeight.bold)),
                            subtitle: Text(
                              "تاریخ: ${article.datePublished.toLocal().toString().split(' ')[0]}",
                              maxLines: 1, overflow: TextOverflow.ellipsis
                            ),
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(icon: Icon(Icons.edit_outlined, color: Colors.blueAccent, size: 20), onPressed: () => _selectArticleForEditing(article)),
                                IconButton(icon: Icon(Icons.delete_outline, color: Colors.redAccent, size: 20), onPressed: () => _deleteArticle(article.id)),
                              ],
                            ),
                            onTap: () => _selectArticleForEditing(article),
                          ),
                        );
                      },
                    ),
            ),
          ],
        ),
      ),
    );
  }
}
