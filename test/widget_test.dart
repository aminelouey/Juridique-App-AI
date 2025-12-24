import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';

import 'package:chatbot_juridique_dz/main.dart';

void main() {
  testWidgets('App loads and shows chat screen', (WidgetTester tester) async {
    await tester.pumpWidget(const ChatbotJuridiqueApp());
    
    // Verify the app title is displayed
    expect(find.text('Chatbot Juridique DZ'), findsOneWidget);
    
    // Verify the welcome message is shown
    expect(find.textContaining('Bienvenue'), findsOneWidget);
    
    // Verify input field exists
    expect(find.byType(TextField), findsOneWidget);
  });
}
