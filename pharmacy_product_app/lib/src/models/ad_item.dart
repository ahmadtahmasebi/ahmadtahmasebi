class AdItem {
  String id;
  String title;
  String imagePath; // Placeholder path or URL
  String? targetUrl; // Optional target URL when ad is tapped

  AdItem({
    required this.id,
    required this.title,
    required this.imagePath,
    this.targetUrl,
  });
}
