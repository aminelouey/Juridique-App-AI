import 'dart:convert';
import 'package:http/http.dart' as http;

class ApiService {
  // URL du backend en production (Render)
  static const String baseUrl = 'https://chatbot-juridique-api.onrender.com';
  // Émulateur Android: 'http://10.0.2.2:8000'
  // Production: 'https://your-backend.railway.app'

  /// Send a chat message to the backend and get RAG + LLM response
  static Future<ChatApiResponse> sendMessage(String question) async {
    try {
      final response = await http.post(
        Uri.parse('$baseUrl/chat'),
        headers: {'Content-Type': 'application/json'},
        body: jsonEncode({
          'question': question,
          'use_llm': true,
        }),
      ).timeout(const Duration(seconds: 60));

      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return ChatApiResponse.fromJson(data);
      } else {
        throw Exception('Erreur API: ${response.statusCode}');
      }
    } catch (e) {
      throw Exception('Erreur de connexion: $e');
    }
  }

  /// Check if backend is healthy (with longer timeout for Render cold start)
  static Future<bool> checkHealth() async {
    // Render free tier can take 30-60 seconds to wake up
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/health'),
      ).timeout(const Duration(seconds: 60));
      
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['status'] == 'healthy' && data['rag_ready'] == true;
      }
      return false;
    } catch (e) {
      return false;
    }
  }

  /// Get backend configuration
  static Future<Map<String, dynamic>> getConfig() async {
    try {
      final response = await http.get(
        Uri.parse('$baseUrl/config'),
      ).timeout(const Duration(seconds: 5));
      
      if (response.statusCode == 200) {
        return jsonDecode(response.body);
      }
      return {};
    } catch (e) {
      return {};
    }
  }

  /// Get all crimes from the database
  static Future<List<dynamic>> getAllCrimes() async {
    try {
      final response = await http.get(Uri.parse('$baseUrl/crimes'));
      if (response.statusCode == 200) {
        final data = jsonDecode(response.body);
        return data['crimes'];
      }
      return [];
    } catch (e) {
      return [];
    }
  }
}

class ChatApiResponse {
  final String response;
  final List<CrimeApiResult> crimes;
  final String llmProvider;
  final String disclaimer;

  ChatApiResponse({
    required this.response,
    required this.crimes,
    required this.llmProvider,
    required this.disclaimer,
  });

  factory ChatApiResponse.fromJson(Map<String, dynamic> json) {
    return ChatApiResponse(
      response: json['response'] as String,
      llmProvider: json['llm_provider'] as String? ?? 'unknown',
      disclaimer: json['disclaimer'] as String,
      crimes: (json['crimes'] as List)
          .map((c) => CrimeApiResult.fromJson(c))
          .toList(),
    );
  }
}

class CrimeApiResult {
  final int id;
  final String crime;
  final String article;
  final String categorie;
  final String prison;
  final String amende;
  final String description;
  final double score;

  CrimeApiResult({
    required this.id,
    required this.crime,
    required this.article,
    required this.categorie,
    required this.prison,
    required this.amende,
    required this.description,
    required this.score,
  });

  factory CrimeApiResult.fromJson(Map<String, dynamic> json) {
    return CrimeApiResult(
      id: json['id'] as int,
      crime: json['crime'] as String,
      article: json['article'] as String,
      categorie: json['categorie'] as String,
      prison: json['prison'] as String,
      amende: json['amende'] as String,
      description: json['description'] as String,
      score: (json['score'] as num).toDouble(),
    );
  }
}
