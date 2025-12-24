enum MessageType { user, bot }

class ChatMessage {
  final String text;
  final MessageType type;
  final DateTime timestamp;
  final String? article;
  final String? penalty;
  final String? crime;
  final bool isLegalInfo;

  ChatMessage({
    required this.text,
    required this.type,
    DateTime? timestamp,
    this.article,
    this.penalty,
    this.crime,
    this.isLegalInfo = false,
  }) : timestamp = timestamp ?? DateTime.now();

  bool get isUser => type == MessageType.user;
  bool get isBot => type == MessageType.bot;
}
