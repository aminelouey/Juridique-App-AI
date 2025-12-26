import 'package:flutter/material.dart';
import 'dart:async';
import '../theme/app_theme.dart';

/// Widget qui affiche le texte avec effet de streaming (lettre par lettre)
class StreamingText extends StatefulWidget {
  final String text;
  final TextStyle? style;
  final Duration charDelay;
  final VoidCallback? onComplete;
  final bool enableStreaming;

  const StreamingText({
    super.key,
    required this.text,
    this.style,
    this.charDelay = const Duration(milliseconds: 15),
    this.onComplete,
    this.enableStreaming = true,
  });

  @override
  State<StreamingText> createState() => _StreamingTextState();
}

class _StreamingTextState extends State<StreamingText> {
  String _displayedText = '';
  Timer? _timer;
  int _currentIndex = 0;

  @override
  void initState() {
    super.initState();
    if (widget.enableStreaming) {
      _startStreaming();
    } else {
      _displayedText = widget.text;
    }
  }

  @override
  void didUpdateWidget(StreamingText oldWidget) {
    super.didUpdateWidget(oldWidget);
    if (widget.text != oldWidget.text) {
      _stopStreaming();
      _currentIndex = 0;
      _displayedText = '';
      if (widget.enableStreaming) {
        _startStreaming();
      } else {
        _displayedText = widget.text;
      }
    }
  }

  void _startStreaming() {
    _timer = Timer.periodic(widget.charDelay, (timer) {
      if (_currentIndex < widget.text.length) {
        setState(() {
          _displayedText = widget.text.substring(0, _currentIndex + 1);
          _currentIndex++;
        });
      } else {
        _stopStreaming();
        widget.onComplete?.call();
      }
    });
  }

  void _stopStreaming() {
    _timer?.cancel();
    _timer = null;
  }

  @override
  void dispose() {
    _stopStreaming();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return _buildFormattedText(_displayedText);
  }

  Widget _buildFormattedText(String text) {
    final List<InlineSpan> spans = [];
    final RegExp boldPattern = RegExp(r'\*\*(.+?)\*\*');
    final RegExp bulletPattern = RegExp(r'^[•\-]\s*', multiLine: true);
    
    String processedText = text;
    int lastEnd = 0;
    
    for (final match in boldPattern.allMatches(processedText)) {
      if (match.start > lastEnd) {
        spans.add(TextSpan(
          text: processedText.substring(lastEnd, match.start),
          style: widget.style ?? const TextStyle(
            color: AppTheme.textPrimary,
            height: 1.6,
            fontSize: 15,
          ),
        ));
      }
      spans.add(TextSpan(
        text: match.group(1),
        style: (widget.style ?? const TextStyle(
          color: AppTheme.textPrimary,
          height: 1.6,
          fontSize: 15,
        )).copyWith(fontWeight: FontWeight.w600),
      ));
      lastEnd = match.end;
    }
    
    if (lastEnd < processedText.length) {
      spans.add(TextSpan(
        text: processedText.substring(lastEnd),
        style: widget.style ?? const TextStyle(
          color: AppTheme.textPrimary,
          height: 1.6,
          fontSize: 15,
        ),
      ));
    }

    if (spans.isEmpty) {
      return Text(
        text,
        style: widget.style ?? const TextStyle(
          color: AppTheme.textPrimary,
          height: 1.6,
          fontSize: 15,
        ),
      );
    }

    return RichText(text: TextSpan(children: spans));
  }
}
