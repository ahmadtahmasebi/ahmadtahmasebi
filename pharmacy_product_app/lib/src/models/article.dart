class Article {
  String id;
  String title;
  String content;
  DateTime datePublished;
  String imagePath; // New field for image placeholder path

  Article({
    required this.id,
    required this.title,
    required this.content,
    required this.datePublished,
    this.imagePath = '', // Default to empty string
  });
}
