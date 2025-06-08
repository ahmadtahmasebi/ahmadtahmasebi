import '../models/drug_model.dart';
import '../models/user_comment_model.dart';

abstract class IDrugService {
  Stream<List<Drug>> getDrugs();
  Stream<List<Drug>> getDrugsByCategory(String categoryId); // Assuming Drug has a categoryId
  Future<Drug?> getDrugById(String drugId);
  Future<void> addDrug(Drug drug); // Typically admin only
  Future<void> updateDrug(Drug drug); // Typically admin only
  Future<void> deleteDrug(String drugId); // Typically admin only
  Future<void> incrementDrugView(String drugId);
  Future<void> likeDrug(String drugId, String userId);
  Future<void> unlikeDrug(String drugId, String userId);
  Stream<List<UserComment>> getDrugComments(String drugId);
  Future<void> addDrugComment(UserComment comment);
}
