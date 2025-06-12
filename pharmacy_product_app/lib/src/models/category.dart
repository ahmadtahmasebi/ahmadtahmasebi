class Category {
  String id;
  String name;
  String description;
  String masterTabType; // e.g., 'cosmetics', 'medicines', 'herbal', 'supplements', 'general'

  Category({
    required this.id,
    required this.name,
    this.description = '',
    this.masterTabType = 'general', // Default to general if not specified
  });
}
