import 'dart:async';
import 'dart:io';

import 'package:path/path.dart';
import 'package:path_provider/path_provider.dart';
import 'package:sqflite/sqflite.dart';

import '../models/product_model.dart';
import '../models/category_model.dart'; // Import Category model

class DatabaseHelper {
  // Singleton pattern
  static final DatabaseHelper _instance = DatabaseHelper._internal();
  factory DatabaseHelper() => _instance;
  DatabaseHelper._internal();

  static Database? _database;

  static const String _dbName = "products.db";
  static const String _productsTable = "products";
  static const String _categoriesTable = "categories"; // Define categories table name

  Future<Database> get database async {
    if (_database != null) return _database!;
    _database = await _initDB();
    return _database!;
  }

  Future<Database> _initDB() async {
    Directory documentsDirectory = await getApplicationDocumentsDirectory();
    String path = join(documentsDirectory.path, _dbName);
    return await openDatabase(
      path,
      version: 1, // Keep version 1 for now, or increment if schema changes significantly
      onCreate: _onCreate,
      // onUpgrade: _onUpgrade, // Optional: Define if you plan schema migrations
    );
  }

  Future<void> _onCreate(Database db, int version) async {
    await db.execute('''
      CREATE TABLE $_productsTable (
        id TEXT PRIMARY KEY,
        name TEXT,
        description TEXT,
        imageUrl TEXT,
        price REAL,
        categoryId TEXT
      )
    ''');
    //FOREIGN KEY (categoryId) REFERENCES $_categoriesTable(id) // Consider adding FK constraint later

    await db.execute('''
      CREATE TABLE $_categoriesTable (
        id TEXT PRIMARY KEY,
        name TEXT UNIQUE
      )
    ''');
  }

  // Optional: Schema migration (if you change DB version)
  // Future<void> _onUpgrade(Database db, int oldVersion, int newVersion) async {
  //   if (oldVersion < 2) {
  //     // Perform schema migration steps
  //   }
  // }

  // Product Operations
  Future<int> addProduct(Product product) async {
    final db = await database;
    return await db.insert(
      _productsTable,
      product.toJson(),
      conflictAlgorithm: ConflictAlgorithm.replace,
    );
  }

  Future<List<Product>> getProducts() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(_productsTable);

    if (maps.isEmpty) {
      return [];
    }
    return List.generate(maps.length, (i) => Product.fromJson(maps[i]));
  }

  Future<List<Product>> getProductsByCategoryId(String categoryId) async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(
      _productsTable,
      where: 'categoryId = ?',
      whereArgs: [categoryId],
    );

    if (maps.isEmpty) {
      return [];
    }
    return List.generate(maps.length, (i) => Product.fromJson(maps[i]));
  }

  // Category Operations
  Future<int> addCategory(Category category) async {
    final db = await database;
    try {
      return await db.insert(
        _categoriesTable,
        category.toJson(),
        conflictAlgorithm: ConflictAlgorithm.ignore, // Ignore if category name (UNIQUE) already exists
      );
    } catch (e) {
      // Handle or log specific UNIQUE constraint error if needed, though ignore should handle it
      print('Error adding category: $e');
      return -1; // Indicate error or that it was ignored
    }
  }

  Future<List<Category>> getCategories() async {
    final db = await database;
    final List<Map<String, dynamic>> maps = await db.query(_categoriesTable);

    if (maps.isEmpty) {
      return [];
    }
    return List.generate(maps.length, (i) => Category.fromJson(maps[i]));
  }

  Future<int> getProductCountForCategory(String categoryId) async {
    final db = await database;
    final result = await db.rawQuery(
      'SELECT COUNT(*) FROM $_productsTable WHERE categoryId = ?',
      [categoryId],
    );
    return Sqflite.firstIntValue(result) ?? 0;
  }
}
