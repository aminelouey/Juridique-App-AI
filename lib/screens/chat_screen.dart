import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../models/chat_message.dart';
import '../services/legal_search_service.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/typing_indicator.dart';
import '../widgets/legal_disclaimer.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final LegalSearchService _localSearchService = LegalSearchService();
  final List<ChatMessage> _messages = [];
  bool _isTyping = false;
  bool _useBackend = true; // Toggle between backend API and local search
  bool _backendAvailable = false;
  String _llmProvider = "checking...";

  @override
  void initState() {
    super.initState();
    _checkBackendHealth();
    _addWelcomeMessage();
  }

  Future<void> _checkBackendHealth() async {
    final isHealthy = await ApiService.checkHealth();
    setState(() {
      _backendAvailable = isHealthy;
      _useBackend = isHealthy;
    });
    
    if (isHealthy) {
      // Get LLM provider info
      try {
        final config = await ApiService.getConfig();
        setState(() {
          _llmProvider = config['llm_provider'] ?? 'unknown';
        });
      } catch (e) {
        setState(() {
          _llmProvider = 'unknown';
        });
      }
    }
  }

  void _addWelcomeMessage() {
    _messages.add(ChatMessage(
      text: '''👋 **Bienvenue sur le Chatbot Juridique Algérien!**

Je suis votre assistant IA d'information juridique basé sur le **Code pénal algérien**.

🤖 **Technologie:** RAG + FAISS + LLM

📖 **Posez-moi des questions comme:**
• "Quelle est la peine pour vol en Algérie ?"
• "Explique-moi l'article 350"
• "Quelles sont les sanctions pour corruption ?"

⚠️ Mes réponses sont des **informations générales** et ne constituent pas un avis juridique personnalisé.''',
      type: MessageType.bot,
    ));
  }

  void _sendMessage() async {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    // Add user message
    setState(() {
      _messages.add(ChatMessage(
        text: text,
        type: MessageType.user,
      ));
      _isTyping = true;
    });
    
    _messageController.clear();
    _scrollToBottom();

    String responseText;
    bool isLegalInfo = false;

    try {
      if (_useBackend && _backendAvailable) {
        // Use backend API with LLM
        final apiResponse = await ApiService.sendMessage(text);
        responseText = apiResponse.response;
        isLegalInfo = apiResponse.crimes.isNotEmpty;
      } else {
        // Fallback to local search
        await Future.delayed(const Duration(milliseconds: 500));
        final crimes = await _localSearchService.search(text);
        responseText = _localSearchService.generateResponse(crimes, text);
        isLegalInfo = crimes.isNotEmpty;
      }
    } catch (e) {
      responseText = '''❌ **Erreur de connexion**

Je n'ai pas pu me connecter au serveur IA.

💡 Mode local activé automatiquement.''';
      
      // Fallback to local search
      setState(() {
        _useBackend = false;
        _backendAvailable = false;
      });
      
      final crimes = await _localSearchService.search(text);
      responseText = _localSearchService.generateResponse(crimes, text);
      isLegalInfo = crimes.isNotEmpty;
    }

    setState(() {
      _isTyping = false;
      _messages.add(ChatMessage(
        text: responseText,
        type: MessageType.bot,
        isLegalInfo: isLegalInfo,
      ));
    });

    _scrollToBottom();
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 300),
          curve: Curves.easeOut,
        );
      }
    });
  }

  @override
  void dispose() {
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Container(
        decoration: BoxDecoration(
          gradient: LinearGradient(
            begin: Alignment.topCenter,
            end: Alignment.bottomCenter,
            colors: [
              AppTheme.surfaceColor,
              AppTheme.backgroundColor,
            ],
          ),
        ),
        child: SafeArea(
          child: Column(
            children: [
              _buildAppBar(),
              Expanded(child: _buildChatList()),
              if (_isTyping) const TypingIndicator(),
              const LegalDisclaimer(),
              _buildInputArea(),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 12),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.2),
            blurRadius: 8,
            offset: const Offset(0, 2),
          ),
        ],
      ),
      child: Row(
        children: [
          Container(
            width: 48,
            height: 48,
            decoration: BoxDecoration(
              gradient: AppTheme.primaryGradient,
              borderRadius: BorderRadius.circular(14),
              boxShadow: [
                BoxShadow(
                  color: AppTheme.primaryColor.withValues(alpha: 0.4),
                  blurRadius: 12,
                  offset: const Offset(0, 4),
                ),
              ],
            ),
            child: const Icon(
              Icons.balance,
              color: Colors.white,
              size: 26,
            ),
          ).animate().scale(
            duration: 500.ms,
            curve: Curves.elasticOut,
          ),
          const SizedBox(width: 14),
          Expanded(
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                const Text(
                  'Chatbot Juridique DZ',
                  style: TextStyle(
                    fontSize: 17,
                    fontWeight: FontWeight.w600,
                    color: AppTheme.textPrimary,
                  ),
                ),
                Row(
                  children: [
                    Container(
                      width: 8,
                      height: 8,
                      decoration: BoxDecoration(
                        color: _backendAvailable 
                            ? AppTheme.successColor 
                            : AppTheme.warningColor,
                        shape: BoxShape.circle,
                        boxShadow: [
                          BoxShadow(
                            color: (_backendAvailable 
                                ? AppTheme.successColor 
                                : AppTheme.warningColor).withValues(alpha: 0.5),
                            blurRadius: 6,
                          ),
                        ],
                      ),
                    ),
                    const SizedBox(width: 6),
                    Text(
                      _backendAvailable 
                          ? 'IA: $_llmProvider' 
                          : 'Mode local',
                      style: const TextStyle(
                        fontSize: 12,
                        color: AppTheme.textSecondary,
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          IconButton(
            onPressed: _showInfoDialog,
            icon: const Icon(
              Icons.info_outline,
              color: AppTheme.textSecondary,
            ),
          ),
        ],
      ),
    );
  }

  Widget _buildChatList() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 20),
      itemCount: _messages.length,
      itemBuilder: (context, index) {
        final message = _messages[index];
        return ChatBubble(
          message: message,
          showAvatar: index == 0 || _messages[index - 1].type != message.type,
        ).animate().fadeIn(duration: 300.ms).slideY(
          begin: 0.2,
          end: 0,
          duration: 300.ms,
          curve: Curves.easeOut,
        );
      },
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        color: AppTheme.surfaceColor,
        boxShadow: [
          BoxShadow(
            color: Colors.black.withValues(alpha: 0.2),
            blurRadius: 8,
            offset: const Offset(0, -2),
          ),
        ],
      ),
      child: Row(
        children: [
          Expanded(
            child: Container(
              decoration: BoxDecoration(
                color: AppTheme.cardColor,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(
                  color: AppTheme.primaryColor.withValues(alpha: 0.3),
                  width: 1,
                ),
              ),
              child: TextField(
                controller: _messageController,
                style: const TextStyle(color: AppTheme.textPrimary),
                decoration: const InputDecoration(
                  hintText: 'Posez votre question juridique...',
                  hintStyle: TextStyle(color: AppTheme.textSecondary),
                  border: InputBorder.none,
                  contentPadding: EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 14,
                  ),
                ),
                onSubmitted: (_) => _sendMessage(),
                textInputAction: TextInputAction.send,
              ),
            ),
          ),
          const SizedBox(width: 12),
          GestureDetector(
            onTap: _sendMessage,
            child: Container(
              width: 52,
              height: 52,
              decoration: BoxDecoration(
                gradient: AppTheme.primaryGradient,
                borderRadius: BorderRadius.circular(16),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primaryColor.withValues(alpha: 0.4),
                    blurRadius: 12,
                    offset: const Offset(0, 4),
                  ),
                ],
              ),
              child: const Icon(
                Icons.send_rounded,
                color: Colors.white,
                size: 24,
              ),
            ).animate(
              onPlay: (controller) => controller.repeat(reverse: true),
            ).shimmer(
              duration: 2000.ms,
              color: Colors.white.withValues(alpha: 0.2),
            ),
          ),
        ],
      ),
    );
  }

  void _showInfoDialog() {
    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        backgroundColor: AppTheme.cardColor,
        shape: RoundedRectangleBorder(borderRadius: BorderRadius.circular(20)),
        title: Row(
          children: [
            Container(
              padding: const EdgeInsets.all(8),
              decoration: BoxDecoration(
                gradient: AppTheme.primaryGradient,
                borderRadius: BorderRadius.circular(10),
              ),
              child: const Icon(Icons.info, color: Colors.white, size: 20),
            ),
            const SizedBox(width: 12),
            const Text(
              'À propos',
              style: TextStyle(color: AppTheme.textPrimary),
            ),
          ],
        ),
        content: Column(
          mainAxisSize: MainAxisSize.min,
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            const Text(
              '🤖 Stack Technique:',
              style: TextStyle(
                color: AppTheme.textPrimary,
                fontWeight: FontWeight.bold,
              ),
            ),
            const SizedBox(height: 8),
            Text(
              '• Embeddings: Sentence Transformers\n'
              '• Vector DB: FAISS\n'
              '• LLM: $_llmProvider\n'
              '• Backend: ${_backendAvailable ? "Connecté ✅" : "Hors ligne ❌"}',
              style: const TextStyle(color: AppTheme.textSecondary),
            ),
            const SizedBox(height: 16),
            Container(
              padding: const EdgeInsets.all(12),
              decoration: BoxDecoration(
                color: AppTheme.warningColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(12),
                border: Border.all(
                  color: AppTheme.warningColor.withValues(alpha: 0.3),
                ),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.warning_amber,
                    color: AppTheme.warningColor,
                    size: 20,
                  ),
                  const SizedBox(width: 10),
                  const Expanded(
                    child: Text(
                      'Information générale uniquement.',
                      style: TextStyle(
                        color: AppTheme.warningColor,
                        fontSize: 12,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ],
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Compris'),
          ),
        ],
      ),
    );
  }
}
