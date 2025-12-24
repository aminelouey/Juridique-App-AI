import 'package:flutter/material.dart';
import '../models/chat_message.dart';
import '../theme/app_theme.dart';

class ChatBubble extends StatelessWidget {
  final ChatMessage message;
  final bool showAvatar;

  const ChatBubble({
    super.key,
    required this.message,
    this.showAvatar = true,
  });

  @override
  Widget build(BuildContext context) {
    final isUser = message.isUser;

    return Padding(
      padding: EdgeInsets.only(
        bottom: 12,
        left: isUser ? 60 : 0,
        right: isUser ? 0 : 60,
      ),
      child: Row(
        mainAxisAlignment:
            isUser ? MainAxisAlignment.end : MainAxisAlignment.start,
        crossAxisAlignment: CrossAxisAlignment.end,
        children: [
          if (!isUser && showAvatar) _buildBotAvatar(),
          if (!isUser && !showAvatar) const SizedBox(width: 40),
          Flexible(child: _buildBubble(isUser)),
        ],
      ),
    );
  }

  Widget _buildBotAvatar() {
    return Container(
      width: 32,
      height: 32,
      margin: const EdgeInsets.only(right: 8),
      decoration: BoxDecoration(
        gradient: AppTheme.primaryGradient,
        borderRadius: BorderRadius.circular(10),
        boxShadow: [
          BoxShadow(
            color: AppTheme.primaryColor.withOpacity(0.3),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: const Icon(
        Icons.balance,
        color: Colors.white,
        size: 18,
      ),
    );
  }

  Widget _buildBubble(bool isUser) {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: isUser ? AppTheme.userBubbleColor : AppTheme.botBubbleColor,
        borderRadius: BorderRadius.only(
          topLeft: const Radius.circular(18),
          topRight: const Radius.circular(18),
          bottomLeft: Radius.circular(isUser ? 18 : 4),
          bottomRight: Radius.circular(isUser ? 4 : 18),
        ),
        boxShadow: [
          BoxShadow(
            color: (isUser ? AppTheme.userBubbleColor : Colors.black)
                .withOpacity(0.2),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Column(
        crossAxisAlignment: CrossAxisAlignment.start,
        children: [
          _buildFormattedText(message.text),
          const SizedBox(height: 6),
          Row(
            mainAxisSize: MainAxisSize.min,
            children: [
              Text(
                _formatTime(message.timestamp),
                style: TextStyle(
                  fontSize: 10,
                  color: isUser
                      ? Colors.white.withOpacity(0.7)
                      : AppTheme.textSecondary,
                ),
              ),
              if (message.isLegalInfo) ...[
                const SizedBox(width: 6),
                Container(
                  padding:
                      const EdgeInsets.symmetric(horizontal: 6, vertical: 2),
                  decoration: BoxDecoration(
                    color: AppTheme.primaryColor.withOpacity(0.2),
                    borderRadius: BorderRadius.circular(4),
                  ),
                  child: Row(
                    mainAxisSize: MainAxisSize.min,
                    children: [
                      Icon(
                        Icons.verified,
                        size: 10,
                        color: AppTheme.primaryColor,
                      ),
                      const SizedBox(width: 3),
                      Text(
                        'Source vérifiée',
                        style: TextStyle(
                          fontSize: 9,
                          color: AppTheme.primaryColor,
                        ),
                      ),
                    ],
                  ),
                ),
              ],
            ],
          ),
        ],
      ),
    );
  }

  Widget _buildFormattedText(String text) {
    // Simple markdown-like formatting
    final List<InlineSpan> spans = [];
    final RegExp boldPattern = RegExp(r'\*\*(.+?)\*\*');
    
    int lastEnd = 0;
    for (final match in boldPattern.allMatches(text)) {
      if (match.start > lastEnd) {
        spans.add(TextSpan(
          text: text.substring(lastEnd, match.start),
          style: const TextStyle(color: AppTheme.textPrimary, height: 1.4),
        ));
      }
      spans.add(TextSpan(
        text: match.group(1),
        style: const TextStyle(
          color: AppTheme.textPrimary,
          fontWeight: FontWeight.w600,
          height: 1.4,
        ),
      ));
      lastEnd = match.end;
    }
    
    if (lastEnd < text.length) {
      spans.add(TextSpan(
        text: text.substring(lastEnd),
        style: const TextStyle(color: AppTheme.textPrimary, height: 1.4),
      ));
    }

    if (spans.isEmpty) {
      return Text(
        text,
        style: const TextStyle(color: AppTheme.textPrimary, height: 1.4),
      );
    }

    return RichText(text: TextSpan(children: spans));
  }

  String _formatTime(DateTime time) {
    final hour = time.hour.toString().padLeft(2, '0');
    final minute = time.minute.toString().padLeft(2, '0');
    return '$hour:$minute';
  }
}
