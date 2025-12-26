import 'package:flutter/material.dart';
import '../theme/app_theme.dart';
import '../screens/settings_screen.dart';

/// Sidebar style ChatGPT avec historique et navigation
class AppDrawer extends StatelessWidget {
  final VoidCallback onNewChat;
  final List<ConversationItem> conversations;
  final Function(int) onSelectConversation;
  final int? selectedIndex;

  const AppDrawer({
    super.key,
    required this.onNewChat,
    required this.conversations,
    required this.onSelectConversation,
    this.selectedIndex,
  });

  @override
  Widget build(BuildContext context) {
    return Drawer(
      backgroundColor: AppTheme.surfaceColor,
      child: SafeArea(
        child: Column(
          children: [
            // Header - Nouveau Chat
            _buildHeader(context),
            
            // Historique des conversations
            Expanded(
              child: _buildConversationList(),
            ),
            
            // Footer - Profil & Settings
            _buildFooter(context),
          ],
        ),
      ),
    );
  }

  Widget _buildHeader(BuildContext context) {
    return Padding(
      padding: const EdgeInsets.all(16),
      child: InkWell(
        onTap: () {
          Navigator.pop(context);
          onNewChat();
        },
        borderRadius: BorderRadius.circular(12),
        child: Container(
          padding: const EdgeInsets.symmetric(horizontal: 16, vertical: 14),
          decoration: BoxDecoration(
            border: Border.all(color: AppTheme.textMuted.withValues(alpha: 0.3)),
            borderRadius: BorderRadius.circular(12),
          ),
          child: Row(
            children: [
              Icon(
                Icons.add_rounded,
                color: AppTheme.textPrimary,
                size: 22,
              ),
              const SizedBox(width: 12),
              Text(
                'Nouveau Chat',
                style: TextStyle(
                  color: AppTheme.textPrimary,
                  fontSize: 15,
                  fontWeight: FontWeight.w500,
                ),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildConversationList() {
    if (conversations.isEmpty) {
      return Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            Icon(
              Icons.chat_bubble_outline_rounded,
              color: AppTheme.textMuted,
              size: 48,
            ),
            const SizedBox(height: 12),
            Text(
              'Aucune conversation',
              style: TextStyle(
                color: AppTheme.textMuted,
                fontSize: 14,
              ),
            ),
          ],
        ),
      );
    }

    return ListView.builder(
      padding: const EdgeInsets.symmetric(horizontal: 12),
      itemCount: conversations.length,
      itemBuilder: (context, index) {
        final conv = conversations[index];
        final isSelected = selectedIndex == index;
        
        return Padding(
          padding: const EdgeInsets.only(bottom: 4),
          child: InkWell(
            onTap: () {
              Navigator.pop(context);
              onSelectConversation(index);
            },
            borderRadius: BorderRadius.circular(10),
            child: Container(
              padding: const EdgeInsets.symmetric(horizontal: 14, vertical: 12),
              decoration: BoxDecoration(
                color: isSelected 
                    ? AppTheme.primaryColor.withValues(alpha: 0.15) 
                    : Colors.transparent,
                borderRadius: BorderRadius.circular(10),
              ),
              child: Row(
                children: [
                  Icon(
                    Icons.chat_bubble_outline_rounded,
                    color: isSelected ? AppTheme.primaryColor : AppTheme.textSecondary,
                    size: 18,
                  ),
                  const SizedBox(width: 12),
                  Expanded(
                    child: Text(
                      conv.title,
                      maxLines: 1,
                      overflow: TextOverflow.ellipsis,
                      style: TextStyle(
                        color: isSelected ? AppTheme.primaryColor : AppTheme.textPrimary,
                        fontSize: 14,
                        fontWeight: isSelected ? FontWeight.w500 : FontWeight.w400,
                      ),
                    ),
                  ),
                ],
              ),
            ),
          ),
        );
      },
    );
  }

  Widget _buildFooter(BuildContext context) {
    return Container(
      padding: const EdgeInsets.all(16),
      decoration: BoxDecoration(
        border: Border(
          top: BorderSide(color: AppTheme.textMuted.withValues(alpha: 0.1)),
        ),
      ),
      child: Column(
        children: [
          // Profil utilisateur
          _buildFooterItem(
            icon: Icons.person_outline_rounded,
            label: 'Invité', // Placeholder pour le nom
            onTap: () {
              // TODO: Ouvrir profil ou login
            },
          ),
          const SizedBox(height: 8),
          // Paramètres
          _buildFooterItem(
            icon: Icons.settings_outlined,
            label: 'Paramètres',
            onTap: () {
              Navigator.pop(context);
              Navigator.push(
                context,
                MaterialPageRoute(builder: (_) => const SettingsScreen()),
              );
            },
          ),
          const SizedBox(height: 8),
          // Déconnexion (placeholder)
          _buildFooterItem(
            icon: Icons.logout_rounded,
            label: 'Se connecter',
            onTap: () {
              // TODO: ouvrir login/register
              _showLoginPrompt(context);
            },
          ),
        ],
      ),
    );
  }

  Widget _buildFooterItem({
    required IconData icon,
    required String label,
    required VoidCallback onTap,
  }) {
    return InkWell(
      onTap: onTap,
      borderRadius: BorderRadius.circular(10),
      child: Padding(
        padding: const EdgeInsets.symmetric(horizontal: 12, vertical: 10),
        child: Row(
          children: [
            Icon(icon, color: AppTheme.textSecondary, size: 20),
            const SizedBox(width: 14),
            Text(
              label,
              style: TextStyle(
                color: AppTheme.textPrimary,
                fontSize: 14,
              ),
            ),
          ],
        ),
      ),
    );
  }

  void _showLoginPrompt(BuildContext context) {
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
                color: AppTheme.primaryColor.withValues(alpha: 0.1),
                borderRadius: BorderRadius.circular(10),
              ),
              child: Icon(Icons.login_rounded, color: AppTheme.primaryColor, size: 24),
            ),
            const SizedBox(width: 12),
            const Text('Connexion', style: TextStyle(fontSize: 17)),
          ],
        ),
        content: const Text(
          'La connexion sera disponible bientôt !\n\nVous pourrez sauvegarder votre historique et synchroniser vos favoris.',
          style: TextStyle(color: AppTheme.textSecondary),
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

/// Modèle pour une conversation
class ConversationItem {
  final String id;
  final String title;
  final DateTime lastMessage;

  ConversationItem({
    required this.id,
    required this.title,
    required this.lastMessage,
  });
}
