class Category {
  String id; // Using String for ID for flexibility with potential future UUIDs
  String name;
  String description;

  Category({
    required this.id,
    required this.name,
    this.description = '',
  });
}
