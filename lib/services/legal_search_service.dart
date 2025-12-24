import 'dart:convert';
import 'package:flutter/services.dart';
import '../models/crime_model.dart';

class LegalSearchService {
  List<Crime> _crimes = [];
  bool _isLoaded = false;

  /// Load the JSON data from assets
  Future<void> loadData() async {
    if (_isLoaded) return;
    
    try {
      final String jsonString = await rootBundle.loadString('assets/data/code_penal.json');
      final List<dynamic> jsonData = json.decode(jsonString);
      _crimes = jsonData.map((e) => Crime.fromJson(e)).toList();
      _isLoaded = true;
    } catch (e) {
      throw Exception('Erreur lors du chargement des données juridiques: $e');
    }
  }

  /// Search for crimes matching the query (RAG-like simulation)
  Future<List<Crime>> search(String query) async {
    await loadData();
    
    final queryLower = _normalizeText(query);
    final queryWords = queryLower.split(RegExp(r'\s+'));
    
    // Score each crime based on keyword matches
    final scoredCrimes = <MapEntry<Crime, double>>[];
    
    for (final crime in _crimes) {
      double score = 0;
      
      // Check crime name
      if (_normalizeText(crime.crime).contains(queryLower)) {
        score += 10;
      }
      
      // Check keywords
      for (final keyword in crime.keywords) {
        final keywordNorm = _normalizeText(keyword);
        for (final word in queryWords) {
          if (keywordNorm.contains(word) || word.contains(keywordNorm)) {
            score += 5;
          }
        }
      }
      
      // Check description
      for (final word in queryWords) {
        if (word.length > 3 && _normalizeText(crime.description).contains(word)) {
          score += 2;
        }
      }
      
      // Check article number
      if (query.contains(RegExp(r'\d+'))) {
        final numbers = RegExp(r'\d+').allMatches(query).map((m) => m.group(0)).toList();
        for (final num in numbers) {
          if (crime.article.contains(num!)) {
            score += 8;
          }
        }
      }
      
      if (score > 0) {
        scoredCrimes.add(MapEntry(crime, score));
      }
    }
    
    // Sort by score descending
    scoredCrimes.sort((a, b) => b.value.compareTo(a.value));
    
    // Return top results
    return scoredCrimes.take(3).map((e) => e.key).toList();
  }

  /// Normalize text for comparison
  String _normalizeText(String text) {
    return text
        .toLowerCase()
        .replaceAll(RegExp(r'[éèêë]'), 'e')
        .replaceAll(RegExp(r'[àâä]'), 'a')
        .replaceAll(RegExp(r'[îï]'), 'i')
        .replaceAll(RegExp(r'[ôö]'), 'o')
        .replaceAll(RegExp(r'[ùûü]'), 'u')
        .replaceAll(RegExp(r'[ç]'), 'c')
        .replaceAll(RegExp(r'[^a-z0-9\s]'), '');
  }

  /// Get all crimes
  Future<List<Crime>> getAllCrimes() async {
    await loadData();
    return _crimes;
  }

  /// Generate a formatted response for found crimes
  String generateResponse(List<Crime> crimes, String originalQuery) {
    if (crimes.isEmpty) {
      return '''Je n'ai pas trouvé d'information correspondant à votre recherche dans le Code pénal algérien.

💡 Essayez avec des termes comme :
• Vol, meurtre, escroquerie
• Coups et blessures
• Faux témoignage
• Corruption, drogue

Ou recherchez par numéro d'article (ex: "Article 350")''';
    }

    final buffer = StringBuffer();
    
    for (int i = 0; i < crimes.length; i++) {
      final crime = crimes[i];
      
      if (i > 0) buffer.writeln('\n━━━━━━━━━━━━━━━━━━━━━\n');
      
      buffer.writeln('⚖️ **${crime.crime}**');
      buffer.writeln('');
      buffer.writeln('📜 ${crime.article}');
      buffer.writeln('📂 Catégorie: ${crime.categorie}');
      buffer.writeln('');
      buffer.writeln('🔒 **Sanctions:**');
      buffer.writeln('• Prison: ${crime.penalty.prison}');
      if (crime.penalty.amende != 'N/A') {
        buffer.writeln('• Amende: ${crime.penalty.amende}');
      }
      buffer.writeln('');
      buffer.writeln('📝 ${crime.description}');
    }

    return buffer.toString();
  }
}
