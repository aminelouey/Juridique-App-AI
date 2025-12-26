import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../theme/app_theme.dart';
import 'streaming_text.dart';

/// Chat bubble moderne style Gemini - sans cadre
class ChatBubble extends StatelessWidget {
  final ChatMessage message;
  final bool showAvatar;
  final bool isNewMessage;

  const ChatBubble({
    super.key,
    required this.message,
    this.showAvatar = true,
    this.isNewMessage = false,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;

    return Padding(
      padding: EdgeInsets.only(
        bottom: 20,
        left: isUser ? 48 : 0,
        right: isUser ? 0 : 48,
      ),
      child: Row(
        mainAxisAlignment: isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          if (!isUser && showAvatar) _buildBotAvatar(),
          if (!isUser && !showAvatar) const SizedBox(width: 44),
          const SizedBox(width: 10),
          Flexible(child: _buildMessage(isUser)),
          if (isUser) const SizedBox(width: 10),
          if (isUser && showAvatar) _buildUserAvatar(),
        ],
      ),
    );
  }

  Widget _buildBotAvatar() {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        gradient: AppTheme.botAvatarGradient,
        borderRadius: BorderRadius.circular(10),
      ),
      child: const Center(
        child: Text('⚖️', style: TextStyle(fontSize: 16)),
      ),
    );
  }

  Widget _buildUserAvatar() {
    return Container(
      width: 32,
      height: 32,
      decoration: BoxDecoration(
        color: AppTheme.primaryColor,
        borderRadius: BorderRadius.circular(10),
      ),
      child: const Icon(
        Icons.person,
        color: Colors.white,
        size: 18,
      ),
    );
  }

  Widget _buildMessage(bool isUser) {
    // Style sans bulle pour le bot (comme Gemini)
    if (!isUser) {
      return Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          // Contenu du message
          if (isNewMessage)
            StreamingText(
              text: message.text,
              style: const TextStyle(
                color: AppTheme.textPrimary,
                height: 1.6,
                fontSize: 15,
              ),
            )
          else
            _buildFormattedText(message.text),
          const SizedBox(height: 8),
          _buildFooter(isUser),
        ],
      );
    }

    // Style bulle simple pour l'utilisateur
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: AppTheme.primaryColor,
        borderRadius: BorderRadius.circular(18),
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          Text(
            message.text,
            style: const TextStyle(
              color: Colors.white,
              fontSize: 15,
              height: 1.5,
            ),
          ),
          const SizedBox(height: 4),
          Text(
            _formatTime(message.timestamp),
            style: TextStyle(
              fontSize: 11,
              color: Colors.white.withValues(alpha: 0.7),
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildFormattedText(String text) {
    final List<InlineSpan> spans = [];
    final RegExp boldPattern = RegExp(r'\*\*(.+?)\*\*');
    
    int lastEnd = 0;
    for (final match in boldPattern.allMatches(text)) {
      if (match.start > lastEnd) {
        spans.add(TextSpan(
          text: text.substring(lastEnd, match.start),
          style: const TextStyle(
            color: AppTheme.textPrimary,
            height: 1.6,
            fontSize: 15,
          ),
        ));
      }
      spans.add(TextSpan(
        text: match.group(1),
        style: const TextStyle(
          color: AppTheme.textPrimary,
          fontWeight: FontWeight.w600,
          height: 1.6,
          fontSize: 15,
        ),
      ));
      lastEnd = match.end;
    }
    
    if (lastEnd < text.length) {
      spans.add(TextSpan(
        text: text.substring(lastEnd),
        style: const TextStyle(
          color: AppTheme.textPrimary,
          height: 1.6,
          fontSize: 15,
        ),
      ));
    }

    if (spans.isEmpty) {
      return Text(
        text,
        style: const TextStyle(
          color: AppTheme.textPrimary,
          height: 1.6,
          fontSize: 15,
        ),
      );
    }

    return RichText(text: TextSpan(children: spans));
  }

  Widget _buildFooter(bool isUser) {
    return Row(
      mainAxisSize: MainAxisSize.min,
      children: [
        Text(
          _formatTime(message.timestamp),
          style: const TextStyle(
            fontSize: 11,
            color: AppTheme.textMuted,
          ),
        ),
        if (message.isLegalInfo) ...[
          const SizedBox(width: 8),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Icon(
                Icons.verified_rounded,
                size: 12,
                color: AppTheme.successColor,
              ),
              const SizedBox(width: 4),
              Text(
                'Vérifié',
                style: TextStyle(
                  fontSize: 10,
                  color: AppTheme.successColor,
                ),
              ),
            ],
          ),
        ],
      ],
    );
  }

  String _formatTime(DateTime time) {
    final hour = time.hour.toString().padLeft(2, '0');
    final minute = time.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }
}
