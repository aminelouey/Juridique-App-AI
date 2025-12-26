import 'package:flutter/material.dart';
import 'package:flutter_animate/flutter_animate.dart';
import '../models/chat_message.dart';
import '../services/legal_search_service.dart';
import '../services/api_service.dart';
import '../theme/app_theme.dart';
import '../widgets/chat_bubble.dart';
import '../widgets/streaming_text.dart';
import '../widgets/app_drawer.dart';

class ChatScreen extends StatefulWidget {
  const ChatScreen({super.key});

  @override
  State<ChatScreen> createState() => _ChatScreenState();
}

class _ChatScreenState extends State<ChatScreen> with TickerProviderStateMixin {
  final TextEditingController _messageController = TextEditingController();
  final ScrollController _scrollController = ScrollController();
  final LegalSearchService _localSearchService = LegalSearchService();
  final GlobalKey<ScaffoldState> _scaffoldKey = GlobalKey<ScaffoldState>();
  
  List<ChatMessage> _messages = [];
  bool _isTyping = false;
  bool _useBackend = true;
  bool _backendAvailable = false;
  String _llmProvider = "checking...";
  int? _streamingMessageIndex;
  bool _hasText = false;  // Pour le bouton d'envoi
  
  // Historique des conversations
  List<ConversationItem> _conversations = [];
  int? _currentConversationIndex;

  @override
  void initState() {
    super.initState();
    _checkBackendHealth();
    // Listener pour le bouton d'envoi
    _messageController.addListener(_onTextChanged);
  }

  void _onTextChanged() {
    final hasText = _messageController.text.trim().isNotEmpty;
    if (hasText != _hasText) {
      setState(() => _hasText = hasText);
    }
  }

  Future<void> _checkBackendHealth() async {
    setState(() => _llmProvider = 'connexion...');
    
    final isHealthy = await ApiService.checkHealth();
    
    if (!mounted) return;
    
    setState(() {
      _backendAvailable = isHealthy;
      _useBackend = isHealthy;
    });
    
    if (isHealthy) {
      try {
        final config = await ApiService.getConfig();
        if (mounted) {
          setState(() {
            _llmProvider = config['llm_provider'] ?? 'Groq';
          });
        }
      } catch (e) {
        if (mounted) setState(() => _llmProvider = 'Groq');
      }
    } else {
      if (mounted) setState(() => _llmProvider = 'hors ligne');
    }
  }

  void _startNewChat() {
    setState(() {
      _messages = [];
      _currentConversationIndex = null;
      _streamingMessageIndex = null;
    });
  }

  void _selectConversation(int index) {
    // TODO: Charger les messages de la conversation
    setState(() {
      _currentConversationIndex = index;
    });
  }

  void _sendMessage() async {
    final text = _messageController.text.trim();
    if (text.isEmpty) return;

    // Ajouter à l'historique si nouveau chat
    if (_messages.isEmpty) {
      final newConv = ConversationItem(
        id: DateTime.now().millisecondsSinceEpoch.toString(),
        title: text.length > 30 ? '${text.substring(0, 30)}...' : text,
        lastMessage: DateTime.now(),
      );
      setState(() {
        _conversations.insert(0, newConv);
        _currentConversationIndex = 0;
      });
    }

    setState(() {
      _messages.add(ChatMessage(text: text, type: MessageType.user));
      _isTyping = true;
    });
    
    _messageController.clear();
    _scrollToBottom();

    String responseText;
    bool isLegalInfo = false;

    try {
      if (_useBackend && _backendAvailable) {
        final apiResponse = await ApiService.sendMessage(text);
        responseText = apiResponse.response;
        isLegalInfo = apiResponse.crimes.isNotEmpty;
      } else {
        await Future.delayed(const Duration(milliseconds: 500));
        final crimes = await _localSearchService.search(text);
        responseText = _localSearchService.generateResponse(crimes, text);
        isLegalInfo = crimes.isNotEmpty;
      }
    } catch (e) {
      responseText = '❌ **Erreur de connexion**\n\nImpossible de se connecter au serveur.';
      setState(() {
        _useBackend = false;
        _backendAvailable = false;
      });
    }

    setState(() {
      _isTyping = false;
      _messages.add(ChatMessage(
        text: responseText,
        type: MessageType.bot,
        isLegalInfo: isLegalInfo,
      ));
      _streamingMessageIndex = _messages.length - 1;
    });

    _scrollToBottom();
    
    Future.delayed(Duration(milliseconds: responseText.length * 15 + 500), () {
      if (mounted) setState(() => _streamingMessageIndex = null);
    });
  }

  void _scrollToBottom() {
    WidgetsBinding.instance.addPostFrameCallback((_) {
      if (_scrollController.hasClients) {
        _scrollController.animateTo(
          _scrollController.position.maxScrollExtent,
          duration: const Duration(milliseconds: 400),
          curve: Curves.easeOutCubic,
        );
      }
    });
  }

  @override
  void dispose() {
    _messageController.removeListener(_onTextChanged);
    _messageController.dispose();
    _scrollController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      key: _scaffoldKey,
      resizeToAvoidBottomInset: true,
      backgroundColor: AppTheme.backgroundColor,
      drawer: AppDrawer(
        onNewChat: _startNewChat,
        conversations: _conversations,
        onSelectConversation: _selectConversation,
        selectedIndex: _currentConversationIndex,
      ),
      body: SafeArea(
        child: Column(
          children: [
            _buildAppBar(),
            Expanded(
              child: RefreshIndicator(
                onRefresh: _checkBackendHealth,
                color: AppTheme.primaryColor,
                backgroundColor: AppTheme.cardColor,
                child: _messages.isEmpty 
                    ? _buildEmptyStateScrollable() 
                    : _buildChatArea(),
              ),
            ),
            if (_isTyping) _buildTypingIndicator(),
            _buildInputArea(),
          ],
        ),
      ),
    );
  }

  Widget _buildAppBar() {
    return Container(
      padding: const EdgeInsets.symmetric(horizontal: 8, vertical: 10),
      child: Row(
        children: [
          // Menu burger pour sidebar
          IconButton(
            onPressed: () => _scaffoldKey.currentState?.openDrawer(),
            icon: const Icon(Icons.menu_rounded),
            color: AppTheme.textPrimary,
          ),
          const SizedBox(width: 8),
          // Titre
          Expanded(
            child: Row(
              children: [
                Container(
                  width: 36,
                  height: 36,
                  decoration: BoxDecoration(
                    gradient: AppTheme.primaryGradient,
                    borderRadius: BorderRadius.circular(10),
                  ),
                  child: const Center(
                    child: Text('⚖️', style: TextStyle(fontSize: 18)),
                  ),
                ),
                const SizedBox(width: 12),
                Column(
                  crossAxisAlignment: CrossAxisAlignment.start,
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    const Text(
                      'Code Pénal DZ',
                      style: TextStyle(
                        fontSize: 16,
                        fontWeight: FontWeight.w600,
                        color: AppTheme.textPrimary,
                      ),
                    ),
                    GestureDetector(
                      onTap: !_backendAvailable ? _checkBackendHealth : null,
                      child: Row(
                        children: [
                          Container(
                            width: 6,
                            height: 6,
                            decoration: BoxDecoration(
                              color: _backendAvailable 
                                  ? AppTheme.successColor 
                                  : AppTheme.warningColor,
                              shape: BoxShape.circle,
                            ),
                          ),
                          const SizedBox(width: 6),
                          Text(
                            _backendAvailable ? 'IA: $_llmProvider' : '$_llmProvider ↻',
                            style: const TextStyle(
                              fontSize: 11,
                              color: AppTheme.textMuted,
                            ),
                          ),
                        ],
                      ),
                    ),
                  ],
                ),
              ],
            ),
          ),
          // Nouveau chat
          IconButton(
            onPressed: _startNewChat,
            icon: const Icon(Icons.edit_note_rounded),
            color: AppTheme.textSecondary,
          ),
        ],
      ),
    );
  }

  // Version scrollable pour RefreshIndicator
  Widget _buildEmptyStateScrollable() {
    return LayoutBuilder(
      builder: (context, constraints) {
        return SingleChildScrollView(
          physics: const AlwaysScrollableScrollPhysics(),
          child: ConstrainedBox(
            constraints: BoxConstraints(minHeight: constraints.maxHeight),
            child: _buildEmptyState(),
          ),
        );
      },
    );
  }

  Widget _buildEmptyState() {
    return Center(
      child: Padding(
        padding: const EdgeInsets.all(40),
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            // Logo
            Container(
              width: 72,
              height: 72,
              decoration: BoxDecoration(
                gradient: AppTheme.primaryGradient,
                borderRadius: BorderRadius.circular(20),
                boxShadow: [
                  BoxShadow(
                    color: AppTheme.primaryColor.withValues(alpha: 0.3),
                    blurRadius: 24,
                    offset: const Offset(0, 8),
                  ),
                ],
              ),
              child: const Center(
                child: Text('⚖️', style: TextStyle(fontSize: 36)),
              ),
            ).animate().scale(
              duration: 600.ms,
              curve: Curves.elasticOut,
            ),
            const SizedBox(height: 32),
            // Message principal - GROS et CENTRÉ
            const Text(
              'Comment puis-je\nvous aider ?',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 28,
                fontWeight: FontWeight.w700,
                color: AppTheme.textPrimary,
                height: 1.2,
              ),
            ).animate().fadeIn(duration: 400.ms, delay: 200.ms),
            const SizedBox(height: 16),
            // Sous-titre
            Text(
              'Assistant juridique basé sur le Code Pénal Algérien',
              textAlign: TextAlign.center,
              style: TextStyle(
                fontSize: 14,
                color: AppTheme.textSecondary,
              ),
            ).animate().fadeIn(duration: 400.ms, delay: 400.ms),
            const SizedBox(height: 40),
            // Suggestions de questions
            _buildSuggestionChips().animate().fadeIn(duration: 400.ms, delay: 600.ms),
          ],
        ),
      ),
    );
  }

  Widget _buildSuggestionChips() {
    final suggestions = [
      'Peine pour vol ?',
      'Article 350',
      'Corruption',
    ];

    return Wrap(
      spacing: 10,
      runSpacing: 10,
      alignment: WrapAlignment.center,
      children: suggestions.map((s) => InkWell(
        onTap: () {
          _messageController.text = s;
          _sendMessage();
        },
        borderRadius: BorderRadius.circular(20),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 10),
          decoration: BoxDecoration(
            color: AppTheme.cardColor,
            borderRadius: BorderRadius.circular(20),
            border: Border.all(color: AppTheme.textMuted.withValues(alpha: 0.2)),
          ),
          child: Text(
            s,
            style: const TextStyle(
              color: AppTheme.textSecondary,
              fontSize: 13,
            ),
          ),
        ),
      )).toList(),
    );
  }

  Widget _buildChatArea() {
    return ListView.builder(
      controller: _scrollController,
      padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 24),
      itemCount: _messages.length,
      itemBuilder: (context, index) {
        final message = _messages[index];
        final showAvatar = index == 0 || _messages[index - 1].type != message.type;
        final isNewMessage = index == _streamingMessageIndex;
        
        return ChatBubble(
          message: message,
          showAvatar: showAvatar,
          isNewMessage: isNewMessage,
        ).animate().fadeIn(duration: 350.ms).slideY(
          begin: 0.1,
          end: 0,
          duration: 350.ms,
          curve: Curves.easeOutCubic,
        );
      },
    );
  }

  Widget _buildTypingIndicator() {
    return Padding(
      padding: const EdgeInsets.symmetric(horizontal: 20, vertical: 12),
      child: Row(
        children: [
          Container(
            width: 32,
            height: 32,
            decoration: BoxDecoration(
              gradient: AppTheme.botAvatarGradient,
              borderRadius: BorderRadius.circular(10),
            ),
            child: const Center(
              child: Text('⚖️', style: TextStyle(fontSize: 16)),
            ),
          ),
          const SizedBox(width: 12),
          Row(
            children: List.generate(3, (index) {
              return Container(
                margin: const EdgeInsets.symmetric(horizontal: 2),
                width: 8,
                height: 8,
                decoration: BoxDecoration(
                  color: AppTheme.textMuted,
                  shape: BoxShape.circle,
                ),
              ).animate(
                onPlay: (c) => c.repeat(),
              ).scale(
                begin: const Offset(0.7, 0.7),
                end: const Offset(1.2, 1.2),
                duration: 600.ms,
                delay: Duration(milliseconds: index * 150),
              ).then().scale(
                begin: const Offset(1.2, 1.2),
                end: const Offset(0.7, 0.7),
                duration: 600.ms,
              );
            }),
          ),
        ],
      ),
    );
  }

  Widget _buildInputArea() {
    return Container(
      padding: const EdgeInsets.fromLTRB(16, 12, 16, 16),
      child: Row(
        children: [
          Expanded(
            child: Container(
              constraints: const BoxConstraints(maxHeight: 120),
              decoration: BoxDecoration(
                color: AppTheme.cardColor,
                borderRadius: BorderRadius.circular(24),
                border: Border.all(
                  color: AppTheme.textMuted.withValues(alpha: 0.15),
                ),
              ),
              child: TextField(
                controller: _messageController,
                enabled: !_isTyping,
                style: const TextStyle(
                  color: AppTheme.textPrimary,
                  fontSize: 15,
                ),
                decoration: InputDecoration(
                  hintText: _isTyping ? 'L\'IA répond...' : 'Posez votre question juridique...',
                  hintStyle: const TextStyle(color: AppTheme.textMuted),
                  border: InputBorder.none,
                  contentPadding: const EdgeInsets.symmetric(
                    horizontal: 20,
                    vertical: 14,
                  ),
                ),
                onSubmitted: (_) => _sendMessage(),
                textInputAction: TextInputAction.send,
                maxLines: 4,
                minLines: 1,
              ),
            ),
          ),
          const SizedBox(width: 10),
          // Bouton STOP ou SEND
          GestureDetector(
            onTap: _isTyping ? _stopGeneration : (_hasText ? _sendMessage : null),
            child: AnimatedContainer(
              duration: const Duration(milliseconds: 200),
              width: 48,
              height: 48,
              decoration: BoxDecoration(
                gradient: (_isTyping || _hasText) ? AppTheme.primaryGradient : null,
                color: (!_isTyping && !_hasText) ? AppTheme.cardColor : null,
                borderRadius: BorderRadius.circular(16),
              ),
              child: Icon(
                _isTyping 
                    ? Icons.stop_rounded 
                    : Icons.arrow_upward_rounded,
                color: (_isTyping || _hasText) ? Colors.white : AppTheme.textMuted,
                size: 24,
              ),
            ),
          ),
        ],
      ),
    );
  }

  void _stopGeneration() {
    setState(() {
      _isTyping = false;
      _streamingMessageIndex = null;
    });
  }
}
