import 'package:firebase_auth/firebase_auth.dart';
import 'package:google_sign_in/google_sign_in.dart';

class AuthService {
  final FirebaseAuth _firebaseAuth = FirebaseAuth.instance;
  final GoogleSignIn _googleSignIn = GoogleSignIn();

  // Stream for authentication state changes
  Stream<User?> get authStateChanges => _firebaseAuth.authStateChanges();

  // Get current user
  User? get currentUser => _firebaseAuth.currentUser;

  // Sign up with email and password
  Future<UserCredential?> signUpWithEmailPassword(String email, String password) async {
    try {
      return await _firebaseAuth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );
    } on FirebaseAuthException catch (e) {
      // Handle specific Firebase Auth errors (e.g., email-already-in-use, weak-password)
      print('Sign up failed: ${e.message}');
      throw e; // Rethrow to be caught by UI
    } catch (e) {
      print('Sign up failed with general error: $e');
      throw e;
    }
  }

  // Sign in with email and password
  Future<UserCredential?> signInWithEmailPassword(String email, String password) async {
    try {
      return await _firebaseAuth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );
    } on FirebaseAuthException catch (e) {
      // Handle errors (e.g., user-not-found, wrong-password)
      print('Sign in failed: ${e.message}');
      throw e;
    } catch (e) {
      print('Sign in failed with general error: $e');
      throw e;
    }
  }

  // Sign out
  Future<void> signOut() async {
    try {
      await _googleSignIn.signOut(); // Sign out from Google if previously signed in
    } catch (e) {
      print('Error signing out from Google: $e');
      // Still proceed to sign out from Firebase
    }
    await _firebaseAuth.signOut();
  }

  // Sign in with Google
  Future<UserCredential?> signInWithGoogle() async {
    try {
      final GoogleSignInAccount? googleUser = await _googleSignIn.signIn();
      if (googleUser == null) {
        // The user canceled the sign-in
        return null;
      }

      final GoogleSignInAuthentication googleAuth = await googleUser.authentication;
      final AuthCredential credential = GoogleAuthProvider.credential(
        accessToken: googleAuth.accessToken,
        idToken: googleAuth.idToken,
      );

      return await _firebaseAuth.signInWithCredential(credential);
    } on FirebaseAuthException catch (e) {
      print('Google sign in failed (Firebase): ${e.message}');
      throw e;
    } catch (e) {
      print('Google sign in failed with general error: $e');
      throw e;
    }
  }

  // Send password reset email
  Future<void> sendPasswordResetEmail(String email) async {
    try {
      await _firebaseAuth.sendPasswordResetEmail(email: email);
    } on FirebaseAuthException catch (e) {
      print('Password reset email failed: ${e.message}');
      throw e;
    } catch (e) {
      print('Password reset email failed with general error: $e');
      throw e;
    }
  }
}
