import 'package:flutter/material.dart';
import 'package:intl/intl.dart'; // For date formatting
import '../../../core/models/news_item_model.dart';
import '../screens/news_item_detail_screen.dart'; // To navigate to detail screen

class NewsItemCard extends StatelessWidget {
  final NewsItem newsItem;

  const NewsItemCard({Key? key, required this.newsItem}) : super(key: key);

  @override
  Widget build(BuildContext context) {
    final DateFormat formatter = DateFormat('yyyy/MM/dd HH:mm', 'fa_IR');
    final String formattedDate = newsItem.createdAt != null
                                 ? formatter.format(newsItem.createdAt.toDate())
                                 : 'تاریخ نامشخص';

    return Card(
      elevation: 3.0,
      margin: const EdgeInsets.symmetric(horizontal: 8.0, vertical: 6.0),
      shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(10.0)),
      child: InkWell(
        onTap: () {
          Navigator.push(
            context,
            MaterialPageRoute(
              builder: (_) => NewsItemDetailScreen(newsItemId: newsItem.id),
            ),
          );
        },
        child: Padding(
          padding: const EdgeInsets.all(12.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: <Widget>[
              if (newsItem.imageUrl != null && newsItem.imageUrl!.isNotEmpty)
                ClipRRect(
                  borderRadius: BorderRadius.circular(8.0),
                  child: Image.network(
                    newsItem.imageUrl!,
                    height: 180,
                    width: double.infinity,
                    fit: BoxFit.cover,
                    errorBuilder: (ctx, err, st) => Container(
                      height: 180,
                      color: Colors.grey[200],
                      child: const Icon(Icons.broken_image, size: 50, color: Colors.grey),
                    ),
                     loadingBuilder: (BuildContext context, Widget child, ImageChunkEvent? loadingProgress) {
                      if (loadingProgress == null) return child;
                      return Container(
                        height: 180,
                        color: Colors.grey[200],
                        child: Center(
                          child: CircularProgressIndicator(
                            strokeWidth: 2.0,
                            value: loadingProgress.expectedTotalBytes != null
                                ? loadingProgress.cumulativeBytesLoaded / loadingProgress.expectedTotalBytes!
                                : null,
                          ),
                        ),
                      );
                    },
                  ),
                ),
              if (newsItem.imageUrl != null && newsItem.imageUrl!.isNotEmpty)
                const SizedBox(height: 12),
              Text(
                newsItem.title,
                style: Theme.of(context).textTheme.titleLarge?.copyWith(fontFamily: 'IranYekan', fontWeight: FontWeight.bold),
                maxLines: 2,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 8),
              Text(
                newsItem.content, // Displaying a snippet of content
                style: Theme.of(context).textTheme.bodyMedium?.copyWith(fontFamily: 'IranYekan', color: Colors.grey[700]),
                maxLines: 3,
                overflow: TextOverflow.ellipsis,
              ),
              const SizedBox(height: 12),
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: <Widget>[
                  Column(
                    crossAxisAlignment: CrossAxisAlignment.start,
                    children: [
                      if (newsItem.author != null && newsItem.author!.isNotEmpty)
                        Text(
                          'نویسنده: ${newsItem.author}',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(fontFamily: 'IranYekan', color: Colors.grey[600]),
                        ),
                      if (newsItem.category != null && newsItem.category!.isNotEmpty)
                         Text(
                          'دسته: ${newsItem.category}',
                          style: Theme.of(context).textTheme.bodySmall?.copyWith(fontFamily: 'IranYekan', color: Colors.grey[600]),
                        ),
                    ],
                  ),
                  Text(
                    formattedDate,
                    style: Theme.of(context).textTheme.bodySmall?.copyWith(fontFamily: 'IranYekan', color: Colors.grey[600]),
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Icon(Icons.remove_red_eye_outlined, size: 16, color: Colors.grey[600]),
                  const SizedBox(width: 4),
                  Text('${newsItem.views} بازدید', style: Theme.of(context).textTheme.bodySmall?.copyWith(fontFamily: 'IranYekan', color: Colors.grey[600])),
                ],
              )
            ],
          ),
        ),
      ),
    );
  }
}
