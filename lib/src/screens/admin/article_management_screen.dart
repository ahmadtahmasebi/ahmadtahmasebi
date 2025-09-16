import 'package:flutter/material.dart';
import '../../models/article.dart';
import '../../services/article_service.dart';

// Initialize ArticleService (simple global instance for now)
final ArticleService _articleService = ArticleService();

class ArticleManagementScreen extends StatefulWidget {
  @override
  _ArticleManagementScreenState createState() => _ArticleManagementScreenState();
}

class _ArticleManagementScreenState extends State<ArticleManagementScreen> {
  List<Article> _articles = [];
  final _titleController = TextEditingController();
  final _contentController = TextEditingController();
  Article? _selectedArticle; // For editing

  @override
  void initState() {
    super.initState();
    _loadArticles();
  }

  void _loadArticles() {
    setState(() {
      _articles = _articleService.getAllArticles();
    });
  }

  void _addOrUpdateArticle() {
    if (_titleController.text.isEmpty || _contentController.text.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Title and Content cannot be empty!')),
      );
      return;
    }

    if (_selectedArticle == null) { // Add new
      _articleService.addArticle(_titleController.text, _contentController.text);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Article added!')),
      );
    } else { // Update existing
      final updatedArticle = Article(
        id: _selectedArticle!.id,
        title: _titleController.text,
        content: _contentController.text,
        datePublished: _selectedArticle!.datePublished, // Keep original publish date
      );
      _articleService.updateArticle(updatedArticle);
      ScaffoldMessenger.of(context).showSnackBar(
        SnackBar(content: Text('Article updated!')),
      );
    }
    _clearForm();
    _loadArticles();
  }

  void _deleteArticle(String articleId) {
    _articleService.deleteArticle(articleId);
    _loadArticles();
     ScaffoldMessenger.of(context).showSnackBar(
      SnackBar(content: Text('Article deleted!')),
    );
  }

  void _selectArticleForEditing(Article article) {
    setState(() {
      _selectedArticle = article;
      _titleController.text = article.title;
      _contentController.text = article.content;
    });
  }

  void _clearForm() {
    setState(() {
      _selectedArticle = null;
      _titleController.clear();
      _contentController.clear();
    });
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      appBar: AppBar(
        title: Text('Manage Articles'),
        actions: [
          IconButton(
            icon: Icon(Icons.clear),
            onPressed: _clearForm,
            tooltip: 'Clear Form',
          )
        ],
      ),
      body: Padding(
        padding: const EdgeInsets.all(16.0),
        child: Column(
          children: [
            TextField(
              controller: _titleController,
              decoration: InputDecoration(labelText: 'Article Title'),
            ),
            SizedBox(height: 10),
            TextField(
              controller: _contentController,
              decoration: InputDecoration(labelText: 'Content'),
              maxLines: 5,
            ),
            SizedBox(height: 20),
            ElevatedButton(
              onPressed: _addOrUpdateArticle,
              child: Text(_selectedArticle == null ? 'Add Article' : 'Update Article'),
            ),
            SizedBox(height: 20),
            Text('Existing Articles', style: Theme.of(context).textTheme.headline6),
            Expanded(
              child: _articles.isEmpty
                  ? Center(child: Text('No articles found.'))
                  : ListView.builder(
                      itemCount: _articles.length,
                      itemBuilder: (context, index) {
                        final article = _articles[index];
                        return Card(
                          margin: EdgeInsets.symmetric(vertical: 4.0),
                          child: ListTile(
                            title: Text(article.title),
                            subtitle: Text('Date: ${article.datePublished.toLocal().toString().split(' ')[0]}\n${article.content}', maxLines: 2, overflow: TextOverflow.ellipsis),
                            isThreeLine: true, // Changed to true
                            trailing: Row(
                              mainAxisSize: MainAxisSize.min,
                              children: [
                                IconButton(
                                  icon: Icon(Icons.edit, color: Colors.blue),
                                  onPressed: () => _selectArticleForEditing(article),
                                ),
                                IconButton(
                                  icon: Icon(Icons.delete, color: Colors.red),
                                  onPressed: () => _deleteArticle(article.id),
                                ),
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
