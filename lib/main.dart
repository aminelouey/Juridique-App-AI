import 'package:flutter/material.dart';
import 'screens/chat_screen.dart';
import 'theme/app_theme.dart';

void main() {
  runApp(const ChatbotJuridiqueApp());
}

class ChatbotJuridiqueApp extends StatelessWidget {
  const ChatbotJuridiqueApp({super.key});

  @override
  Widget build(BuildContext context) {
    return MaterialApp(
      title: 'Chatbot Juridique DZ',
      debugShowCheckedModeBanner: false,
      theme: AppTheme.darkTheme,
      home: const ChatScreen(),
    );
  }
}
