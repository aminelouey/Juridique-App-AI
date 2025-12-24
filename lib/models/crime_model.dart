class Crime {
  final int id;
  final String crime;
  final String article;
  final List<String> keywords;
  final String categorie;
  final Penalty penalty;
  final String description;

  Crime({
    required this.id,
    required this.crime,
    required this.article,
    required this.keywords,
    required this.categorie,
    required this.penalty,
    required this.description,
  });

  factory Crime.fromJson(Map<String, dynamic> json) {
    return Crime(
      id: json['id'] as int,
      crime: json['crime'] as String,
      article: json['article'] as String,
      keywords: List<String>.from(json['keywords'] as List),
      categorie: json['categorie'] as String,
      penalty: Penalty.fromJson(json['penalty'] as Map<String, dynamic>),
      description: json['description'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'id': id,
      'crime': crime,
      'article': article,
      'keywords': keywords,
      'categorie': categorie,
      'penalty': penalty.toJson(),
      'description': description,
    };
  }
}

class Penalty {
  final String prison;
  final String amende;

  Penalty({
    required this.prison,
    required this.amende,
  });

  factory Penalty.fromJson(Map<String, dynamic> json) {
    return Penalty(
      prison: json['prison'] as String,
      amende: json['amende'] as String,
    );
  }

  Map<String, dynamic> toJson() {
    return {
      'prison': prison,
      'amende': amende,
    };
  }
}
