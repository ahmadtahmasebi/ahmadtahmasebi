import 'package:cloud_firestore/cloud_firestore.dart';
import 'package:flutter/material.dart';
import 'package:intl/intl.dart';
import '../../../core/models/news_item_model.dart';
import '../../../core/models/user_comment_model.dart';
import '../../../core/services/auth_service.dart';
import '../../../core/services/firestore_service.dart';
import '../../../core/services/news_service_interface.dart';

class NewsItemDetailScreen extends StatefulWidget {
  final String newsItemId;

  const NewsItemDetailScreen({Key? key, required this.newsItemId}) : super(key: key);

  @override
  _NewsItemDetailScreenState createState() => _NewsItemDetailScreenState();
}

class _NewsItemDetailScreenState extends State<NewsItemDetailScreen> {
  late Future<NewsItem?> _newsItemFuture;
  late Stream<List<UserComment>> _commentsStream;

  final INewsService _newsService = FirestoreService();
  final AuthService _authService = AuthService();
  String? _currentUserId;

  final TextEditingController _commentController = TextEditingController();
  final FocusNode _commentFocusNode = FocusNode();

  @override
  void initState() {
    super.initState();
    _currentUserId = _authService.currentUser?.uid;
    _loadNewsItemDetails(incrementView: true);
    _commentsStream = _newsService.getNewsItemComments(widget.newsItemId);
  }

  Future<void> _loadNewsItemDetails({bool incrementView = false}) async {
    if (incrementView) {
      _newsService.incrementNewsItemView(widget.newsItemId);
    }
    _newsItemFuture = _newsService.getNewsItemById(widget.newsItemId);
     if (mounted) { // Ensure widget is still in tree before calling setState
      setState(() {}); // To rebuild FutureBuilder if _newsItemFuture is reassigned
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
      id: '', // Firestore will generate ID
      entityId: widget.newsItemId,
      entityType: "newsItem", // Consistent with potential future comment aggregation
      userId: _currentUserId,
      userName: _authService.currentUser?.displayName ?? _authService.currentUser?.email ?? "کاربر ناشناس",
      text: _commentController.text,
      createdAt: Timestamp.now(),
    );

    try {
      await _newsService.addNewsItemComment(newComment);
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
        title: FutureBuilder<NewsItem?>(
          future: _newsItemFuture,
          builder: (context, snapshot) {
            if (snapshot.hasData && snapshot.data != null) {
              return Text(snapshot.data!.title, style: const TextStyle(fontFamily: 'IranYekan'));
            }
            return const Text('جزئیات', style: TextStyle(fontFamily: 'IranYekan'));
          },
        ),
      ),
      body: FutureBuilder<NewsItem?>(
        future: _newsItemFuture,
        builder: (context, snapshot) {
          if (snapshot.connectionState == ConnectionState.waiting) {
            return const Center(child: CircularProgressIndicator());
          }
          if (snapshot.hasError || !snapshot.hasData || snapshot.data == null) {
            return Center(child: Text('خطا در بارگذاری: ${snapshot.error ?? "مورد یافت نشد."}', style: const TextStyle(fontFamily: 'IranYekan')));
          }

          final newsItem = snapshot.data!;
          final DateFormat formatter = DateFormat('yyyy/MM/dd HH:mm', 'fa_IR');
          final String formattedDate = formatter.format(newsItem.createdAt.toDate());

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16.0),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: <Widget>[
                Text(newsItem.title, style: Theme.of(context).textTheme.headlineMedium?.copyWith(fontFamily: 'IranYekan', fontWeight: FontWeight.bold)),
                const SizedBox(height: 8),
                Row(
                  children: [
                    Text(formattedDate, style: Theme.of(context).textTheme.bodySmall?.copyWith(fontFamily: 'IranYekan', color: Colors.grey)),
                    const SizedBox(width: 16),
                    const Icon(Icons.remove_red_eye_outlined, size: 16, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text('${newsItem.views} بازدید', style: Theme.of(context).textTheme.bodySmall?.copyWith(fontFamily: 'IranYekan', color: Colors.grey)),
                  ],
                ),
                if (newsItem.author != null && newsItem.author!.isNotEmpty) ...[
                  const SizedBox(height: 8),
                  Text('نویسنده: ${newsItem.author}', style: Theme.of(context).textTheme.bodySmall?.copyWith(fontFamily: 'IranYekan', fontStyle: FontStyle.italic)),
                ],
                if (newsItem.category != null && newsItem.category!.isNotEmpty) ...[
                  const SizedBox(height: 4),
                  Chip(label: Text(newsItem.category!, style: const TextStyle(fontFamily: 'IranYekan'))),
                ],
                const SizedBox(height: 16),
                if (newsItem.imageUrl != null && newsItem.imageUrl!.isNotEmpty)
                  ClipRRect(
                    borderRadius: BorderRadius.circular(12.0),
                    child: Image.network(
                      newsItem.imageUrl!,
                      width: double.infinity,
                      height: 220,
                      fit: BoxFit.cover,
                       errorBuilder: (ctx, err, st) => Container(
                        height: 220,
                        color: Colors.grey[200],
                        child: const Icon(Icons.broken_image, size: 60, color: Colors.grey),
                      ),
                    ),
                  ),
                const SizedBox(height: 16),
                Text(
                  newsItem.content,
                  style: Theme.of(context).textTheme.bodyLarge?.copyWith(fontFamily: 'IranYekan', fontSize: 16, height: 1.8),
                  textAlign: TextAlign.justify,
                ),
                const SizedBox(height: 24),
                Text('نظرات:', style: Theme.of(context).textTheme.titleLarge?.copyWith(fontFamily: 'IranYekan', fontWeight: FontWeight.bold)),
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
          return const Center(child: Padding(padding: EdgeInsets.all(8.0), child: CircularProgressIndicator()));
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
              elevation: 1,
              margin: const EdgeInsets.symmetric(vertical: 6.0),
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
      padding: const EdgeInsets.symmetric(vertical: 16.0),
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
              maxLines: 3,
              minLines: 1,
            ),
          ),
          const SizedBox(width: 8),
          ElevatedButton(
            onPressed: _addComment,
            style: ElevatedButton.styleFrom(
              backgroundColor: Theme.of(context).colorScheme.primary,
              padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 12),
            ),
            child: const Icon(Icons.send, color: Colors.white),
          ),
        ],
      ),
    );
  }
}
